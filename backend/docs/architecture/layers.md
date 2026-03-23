# Layer Reference

Deep-dive into each of the four layers. Assumes you have read
[concepts.md](concepts.md) first.

---

## 5. Domain layer in depth

Files: `app/users/domain/models.py`, `events.py`, `repositories.py`

### Value Objects

A **value object** is an immutable object defined entirely by its data. Two value objects with
the same data are identical — there is no notion of "which one" matters.

```python
# app/users/domain/models.py

@dataclass(frozen=True)   # frozen=True makes all fields immutable after creation
class Email:
    value: str

    def __post_init__(self) -> None:
        lowered = self.value.lower()
        object.__setattr__(self, "value", lowered)  # see python-concepts.md for why
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", lowered):
            raise ValueError(f"Invalid email address: {lowered}")
```

`Email` is a value object because:
- It is `frozen=True` — you cannot change it after creation.
- It validates itself. An `Email` that exists is by definition valid.
- Two `Email("a@b.com")` instances are equal to each other.

Compare this to using a raw `str`. A raw `str` can be anything — `""`, `"not-an-email"`,
`"UPPER@CASE.COM"`. Every piece of code that receives a raw email string has to either trust
that someone else validated it, or repeat the validation itself. With a value object, if the
type is `Email`, it is already validated and normalised.

`GoogleID` follows the same pattern — non-empty, treated as an opaque identifier.

### Aggregate root

An **aggregate** is a cluster of objects that must always be consistent together. The
**aggregate root** is the single entry point — external code can only hold a reference to the
root, never to its internal parts directly.

```python
@dataclass          # NOT frozen — a User can be updated (name, picture)
class User:
    id: uuid.UUID
    google_id: GoogleID   # value object, not a raw str
    email: Email          # value object, not a raw str
    name: str
    picture_url: str
    created_at: datetime
```

`User` is the aggregate root of the users context. Notice it holds `GoogleID` and `Email` value
objects — not raw strings. This means a `User` can never exist with an invalid email or an empty
Google ID. The invariant is enforced at construction time.

### Factory method

Creating a `User` from scratch requires more than just filling in fields — it also generates a
UUID and records a domain event. This logic belongs on the aggregate as a **factory classmethod**.

```python
@classmethod
def register_via_google(
    cls,
    google_id: str,
    email: str,
    name: str,
    picture_url: str,
) -> tuple["User", UserRegisteredViaGoogle]:
    user_id = uuid.uuid4()
    now = datetime.now(tz=timezone.utc)
    user = cls(
        id=user_id,
        google_id=GoogleID(value=google_id),
        email=Email(value=email),
        ...
    )
    event = UserRegisteredViaGoogle(user_id=user_id, ...)
    return user, event
```

The caller gets back both the user and a domain event. The factory method ensures that
registration always produces both — you cannot register a user without the event being raised.

### Domain events

A **domain event** records that something meaningful happened in the domain.

```python
# app/users/domain/events.py

@dataclass(frozen=True)
class UserRegisteredViaGoogle:
    user_id: uuid.UUID
    email: str
    google_id: str
    occurred_at: datetime
```

Events are frozen dataclasses — they are records of the past and should never be mutated.
Right now the event is created but its second value (`_`) is discarded by the use case. In a
more complete system you would publish it to a message bus, emit it to an analytics service,
or trigger side effects (welcome email, audit log).

### Repository interface

The domain needs to persist and retrieve users, but it must not know about SQLAlchemy or
PostgreSQL. The solution is to define an **abstract interface** in the domain layer.

```python
# app/users/domain/repositories.py

class UserRepository(ABC):
    @abstractmethod
    def get_by_google_id(self, google_id: str) -> User | None: ...

    @abstractmethod
    def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    @abstractmethod
    def save(self, user: User) -> None: ...
```

`ABC` stands for Abstract Base Class. `@abstractmethod` means any class that inherits from
`UserRepository` must implement these methods or Python will raise a `TypeError` at class
definition time. The domain says "I need something that can do these things" — it does not care
how it is done.

`UserNotFoundError` also lives here. Domain exceptions are part of the domain vocabulary.
The API layer catches them and translates to HTTP status codes.

---

## 6. Application layer in depth

Files: `app/users/application/use_cases.py`, `schemas.py`

### Use cases (application services)

An **application service** (called a use case here) orchestrates one user-facing operation.
It calls the domain, calls the repository, and coordinates the result. It contains no business
logic of its own.

```python
# app/users/application/use_cases.py

class RegisterOrRetrieveUser:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo           # takes the abstract interface, not the concrete class

    def execute(self, google_id: str, email: str, name: str, picture_url: str) -> User:
        existing = self._repo.get_by_google_id(google_id)
        if existing is None:
            user, _ = User.register_via_google(...)   # domain logic lives here
            self._repo.save(user)
            return user
        existing.update_profile(name=name, picture_url=picture_url)
        self._repo.save(existing)
        return existing
```

Key observations:

1. The constructor takes `UserRepository` (the abstract class from the domain layer), not
   `SqlAlchemyUserRepository`. The use case does not know or care about SQLAlchemy.
2. The business decisions ("create if not found, update if found") are in the domain model's
   methods — `register_via_google` and `update_profile`. The use case just calls them.
3. There is no HTTP, no SQL, no JSON. Just Python objects.

### Schemas (DTOs)

**Data Transfer Objects** (DTOs) are Pydantic models that define the shape of data entering
and leaving the API. They are explicitly separate from domain models.

```python
# app/users/application/schemas.py

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str      # plain str — callers do not need to know about the Email value object
    name: str
    picture_url: str
    created_at: datetime
```

Notice that the response schema uses `str` for `email`, not the `Email` value object. The
value object is an internal detail of the domain. The API consumer gets a plain string.

The router manually maps from domain model to schema:

```python
return UserProfileResponse(
    id=current_user.id,
    email=current_user.email.value,   # unwrap the value object here
    ...
)
```

This explicit mapping is intentional. When the domain model changes, the schema does not
have to change with it, and vice versa.

---

## 7. Infrastructure layer in depth

Files: `orm_models.py`, `repositories.py`, `auth.py`, `google_oauth.py`,
`narrator.py`, `prompts/assembler.py`

### ORM model vs domain model

There are two completely separate Python classes for "a user":

| Class | File | Purpose |
|---|---|---|
| `User` | `domain/models.py` | Domain aggregate. Business rules live here. |
| `UserORM` | `infrastructure/orm_models.py` | SQLAlchemy model. Database columns live here. |

```python
# app/users/infrastructure/orm_models.py

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    google_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    picture_url: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
```

`UserORM` inherits from `Base` (the SQLAlchemy declarative base). The `Mapped[T]` annotation
is SQLAlchemy 2.0 style — it tells SQLAlchemy and mypy simultaneously what type the column
holds. `mapped_column(...)` provides the database-specific details (constraints, index, type).

`UserORM` knows nothing about value objects or business rules. It is a flat representation
of a database row.

### Concrete repository

```python
# app/users/infrastructure/repositories.py

class SqlAlchemyUserRepository(UserRepository):   # implements the domain interface
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_google_id(self, google_id: str) -> User | None:
        stmt = select(UserORM).where(UserORM.google_id == google_id)
        row = self._session.execute(stmt).scalar_one_or_none()
        if row is None:
            return None
        return self._to_domain(row)   # converts ORM row to domain object before returning
```

The repository:
1. Speaks SQLAlchemy (ORM queries, sessions).
2. Returns domain objects (`User`), not ORM objects (`UserORM`).
3. The caller (use case) only ever sees `User`. The ORM is completely hidden.

`save()` uses `session.merge()` rather than `session.add()`. `merge()` checks if a row with
that primary key already exists in the session or database — if it does, it updates; if not,
it inserts. This is correct for our use case because `save()` is called for both new and
existing users.

`_to_domain()` is the mapping step in the other direction: ORM row to domain object.

```python
@staticmethod
def _to_domain(orm: UserORM) -> User:
    return User(
        id=orm.id,
        google_id=GoogleID(value=orm.google_id),   # wrap raw str back into value object
        email=Email(value=orm.email),               # same
        ...
    )
```

### JWT utilities

```python
# app/users/infrastructure/auth.py

def create_access_token(data: dict[str, object], expires_delta: timedelta | None = None) -> str:
    to_encode: dict[str, object] = data.copy()
    ...
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

A JWT is a signed token containing a JSON payload. Our token contains:
- `sub` — the user's UUID (standard JWT claim for "subject")
- `exp` — expiry timestamp (standard claim)

The `SECRET_KEY` signs the token. Anyone who receives the token can read its payload (it is
base64-encoded, not encrypted), but cannot forge a valid signature without the secret key.

`decode_access_token` reverses this — it verifies the signature and expiry, then returns the
UUID from the `sub` claim. If anything is wrong (tampered token, expired, missing claim), it
raises `HTTPException(401)`.

### Google OAuth / OIDC

```python
# app/users/infrastructure/google_oauth.py

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
```

OAuth2 is a protocol for delegating authentication to a third party. The flow:

1. User visits `/auth/google`.
2. Our server redirects them to Google's consent screen (with our `client_id` and a `state`
   cookie to prevent CSRF).
3. User approves. Google redirects back to `/auth/google/callback` with an authorisation code.
4. Our server exchanges the code (plus our `client_secret`) for an ID token.
5. The ID token contains the user's `sub` (Google's permanent user ID), `email`, `name`,
   and `picture`.

`server_metadata_url` points to Google's OIDC Discovery document. Authlib fetches it
automatically to find the token endpoint, JWKS (public keys for ID token verification), and
other details. We do not have to hardcode any Google URLs.

`SessionMiddleware` in `app/main.py` provides a signed cookie that authlib uses to store and
verify the `state` parameter between the redirect and the callback. Without it, the OAuth
handshake cannot complete.

### Narrator Port pattern (LLM integration)

The `dungeons` context needs to call Google Gemini to generate dungeon content. This raises
a question: where does the LLM client live?

**Not in the domain layer.** The domain layer must be pure Python with no external dependencies.
Gemini is an external I/O side-effect, not a business rule.

**Not as a domain repository interface either.** A repository abstracts *storage* — it reads
and writes domain aggregates to a data store. Gemini does not store anything; it *generates*
new domain objects from a prompt. The concept is different.

The solution is an **application-layer port**: an abstract interface defined in the
`application/` layer that the infrastructure layer implements. This keeps the dependency rule
intact (application → domain only; infrastructure implements application interfaces) while
making clear that the LLM is an output port, not a data store.

```python
# app/dungeons/application/narrator_port.py

class DungeonNarratorPort(ABC):
    @abstractmethod
    def generate_dungeon(
        self,
        settings: DungeonSettings,
        world: World,
        campaign: Campaign,
    ) -> Dungeon: ...
```

Two implementations live in `app/dungeons/infrastructure/narrator.py`:

| Class | Purpose |
|---|---|
| `StubDungeonNarrator` | Deterministic templates keyed by `CampaignTone`. No LLM calls. Used in dev and tests. |
| `GeminiDungeonNarrator` | Calls Google Gemini (`gemini-2.0-flash`). Requires `GEMINI_API_KEY`. |

`GeminiDungeonNarrator` does not build the prompt itself — that responsibility is split into
`PromptAssembler` (`app/dungeons/infrastructure/prompts/assembler.py`), which combines World
lore, Campaign context, and DungeonSettings into a structured prompt string. Separating the
prompt from the API call makes each piece independently testable.

The full prompt-to-dungeon pipeline:

```
use case
  -> DungeonNarratorPort.generate_dungeon(settings, world, campaign)
       -> PromptAssembler.build(settings, world, campaign)   # builds prompt string
       -> genai.Client.models.generate_content(prompt)       # calls Gemini API
       -> GeminiDungeonNarrator._parse_dungeon(json_response) # JSON -> Dungeon aggregate
```

`GEMINI_API_KEY` is a required field in `app/core/config.py`. The application will refuse to
start if the key is absent. A dummy value satisfies the startup check but real LLM calls will
fail at runtime.

---

## 8. API layer in depth

Files: `app/users/api/router.py`, `dependencies.py`

### Dependency injection

FastAPI's `Depends()` is the mechanism for providing objects to route handlers without those
handlers having to create them. Think of it as a factory that FastAPI calls automatically.

```python
# app/users/api/dependencies.py

def get_user_repository(
    db: Session = Depends(get_db),          # FastAPI calls get_db() for us
) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session=db)
```

When a route handler declares `user_repo: SqlAlchemyUserRepository = Depends(get_user_repository)`,
FastAPI:
1. Calls `get_db()` to get a session.
2. Passes the session to `get_user_repository()`.
3. Passes the result to your route handler.

This is dependency injection without a framework-specific container. The benefits:
- Each request gets its own session (request-scoped, as required).
- Route handlers do not import globals or call constructors manually.
- In tests, you can override dependencies with fakes.

### Authentication dependency

```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_repo: SqlAlchemyUserRepository = Depends(get_user_repository),
) -> User:
    user_id = decode_access_token(credentials.credentials)   # raises 401 if invalid
    try:
        return GetCurrentUser(repo=user_repo).execute(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
```

`HTTPBearer()` (assigned to `bearer_scheme`) extracts the token from the `Authorization: Bearer
<token>` header. If the header is missing, FastAPI returns 403 automatically.

The route handler for `/users/me` just declares this dependency:

```python
@users_router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email.value,
        ...
    )
```

The handler is four lines. No SQL, no JWT parsing, no error handling — all of that is in the
dependency chain. The handler's only job is to map the domain object to the response schema.

### Thin router

Notice what the callback route does:

```python
@auth_router.get("/google/callback", name="google_callback")
async def google_callback(request, db, user_repo) -> RedirectResponse:
    user_info = await exchange_code_for_user_info(request)   # infrastructure
    use_case = RegisterOrRetrieveUser(repo=user_repo)
    user = use_case.execute(**user_info)                     # application
    db.commit()                                              # commit the session
    token = create_access_token(data={"sub": str(user.id)}) # infrastructure
    return RedirectResponse(url=f"{settings.FRONTEND_URL}?token={token}")
```

The router:
- Calls infrastructure to get user info from Google.
- Calls the application use case (which calls the domain).
- Commits the session (transaction boundary is at the API layer).
- Redirects the user with a JWT.

No business logic here. No "if user has role admin" — that belongs in the domain. No raw SQL.
The router is a coordinator, not a decision-maker.

---

## Index

| Entity | Documentation |
|--------|---------------|
| DDD / Domain-Driven Design | docs/architecture/concepts.md |
| Dependency rule | docs/architecture/concepts.md#2-the-dependency-rule |
| Bounded context | docs/architecture/concepts.md#3-bounded-contexts |
| Four layers | docs/architecture/concepts.md#4-the-four-layers |
| Value Object | docs/architecture/layers.md#value-objects |
| Email (value object) | docs/architecture/layers.md#value-objects |
| GoogleID (value object) | docs/architecture/layers.md#value-objects |
| InviteCode (value object) | docs/architecture/file-reference.md |
| Aggregate root | docs/architecture/layers.md#aggregate-root |
| User (aggregate) | docs/architecture/layers.md#aggregate-root |
| Factory method | docs/architecture/layers.md#factory-method |
| Domain event | docs/architecture/layers.md#domain-events |
| UserRegisteredViaGoogle | docs/architecture/layers.md#domain-events |
| Repository interface | docs/architecture/layers.md#repository-interface |
| UserRepository | docs/architecture/layers.md#repository-interface |
| Use case / Application service | docs/architecture/layers.md#use-cases-application-services |
| RegisterOrRetrieveUser | docs/architecture/layers.md#use-cases-application-services |
| GetCurrentUser | docs/architecture/layers.md#authentication-dependency |
| DTO / Schema | docs/architecture/layers.md#schemas-dtos |
| UserProfileResponse | docs/architecture/layers.md#schemas-dtos |
| ORM model vs domain model | docs/architecture/layers.md#orm-model-vs-domain-model |
| UserORM | docs/architecture/layers.md#orm-model-vs-domain-model |
| Concrete repository | docs/architecture/layers.md#concrete-repository |
| SqlAlchemyUserRepository | docs/architecture/layers.md#concrete-repository |
| session.merge() | docs/architecture/layers.md#concrete-repository |
| _to_domain() | docs/architecture/layers.md#concrete-repository |
| JWT | docs/architecture/layers.md#jwt-utilities |
| create_access_token | docs/architecture/layers.md#jwt-utilities |
| decode_access_token | docs/architecture/layers.md#jwt-utilities |
| SECRET_KEY | docs/architecture/layers.md#jwt-utilities |
| Google OAuth / OIDC | docs/architecture/layers.md#google-oauth--oidc |
| SessionMiddleware | docs/architecture/layers.md#google-oauth--oidc |
| Narrator Port pattern | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| DungeonNarratorPort | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| StubDungeonNarrator | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| GeminiDungeonNarrator | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| PromptAssembler | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| GEMINI_API_KEY | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| Dependency injection (FastAPI Depends) | docs/architecture/layers.md#dependency-injection |
| get_current_user | docs/architecture/layers.md#authentication-dependency |
| Thin router | docs/architecture/layers.md#thin-router |
| Request lifecycle | docs/architecture/lifecycle.md |
| Dataclasses | docs/architecture/python-concepts.md#dataclasses |
| object.__setattr__ | docs/architecture/python-concepts.md#objectsetattr-in-frozen-dataclasses |
| Abstract Base Classes | docs/architecture/python-concepts.md#abstract-base-classes |
| Type hints / X | None | docs/architecture/python-concepts.md#type-hints-and-x--none |
| Classmethods as factories | docs/architecture/python-concepts.md#classmethods-as-factories |
| Generators (session lifecycle) | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| cast() | docs/architecture/python-concepts.md#cast-for-type-narrowing |
| File reference | docs/architecture/file-reference.md |
| Dependency diagram | docs/architecture/file-reference.md#dependency-diagram-users-excerpt |

# Project Architecture: DDD with FastAPI

This document explains every architectural decision in this project. It is written as a
tutorial — each section builds on the last. Read it top to bottom the first time.

---

## Table of Contents

1. [The core problem DDD solves](#1-the-core-problem-ddd-solves)
2. [The dependency rule](#2-the-dependency-rule)
3. [Bounded contexts](#3-bounded-contexts)
4. [The four layers](#4-the-four-layers)
5. [Domain layer in depth](#5-domain-layer-in-depth)
6. [Application layer in depth](#6-application-layer-in-depth)
7. [Infrastructure layer in depth](#7-infrastructure-layer-in-depth)
8. [API layer in depth](#8-api-layer-in-depth)
9. [Request lifecycle: sign in with Google](#9-request-lifecycle-sign-in-with-google)
10. [Python concepts used in this project](#10-python-concepts-used-in-this-project)
11. [File reference](#11-file-reference)

---

## 1. The core problem DDD solves

In a typical beginner FastAPI project you end up with something like this:

```python
# BAD - everything mixed together
@app.post("/users")
def create_user(email: str, db: Session = Depends(get_db)):
    if "@" not in email:
        raise HTTPException(400, "bad email")
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(409, "exists")
    new_user = User(email=email)
    db.add(new_user)
    db.commit()
    return new_user
```

This works for one endpoint. When you have fifty, you have a problem:

- The business rule "email must contain @" is buried in a route handler. If you add a second
  way to create a user (admin panel, import script), you must remember to copy that rule.
- The database query is written directly in the router. To test whether the email validation
  works, you need a running database.
- `User` is the SQLAlchemy ORM model. It leaks database details (columns, relationships)
  into every part of the code that touches it.

**Domain-Driven Design (DDD)** is a set of patterns that solve this by separating concerns into
layers with strict rules about which layer is allowed to depend on which.

---

## 2. The dependency rule

This is the single most important concept. Read it twice.

```
API layer
  depends on ->  Application layer
                   depends on ->  Domain layer
                                    depends on ->  nothing
Infrastructure layer
  depends on ->  Domain layer (implements its interfaces)
```

The **domain layer has no dependencies on anything outside itself**. It does not know about
FastAPI, SQLAlchemy, HTTP, or databases. It is pure Python classes and logic.

Every other layer points inward toward the domain. The domain never points outward.

Why does this matter? Because it means you can:
- Test your business rules with plain Python — no database, no HTTP server, no mocking needed.
- Swap PostgreSQL for a different database without touching a single line of business logic.
- Swap FastAPI for another framework without rewriting your core rules.

---

## 3. Bounded contexts

A **bounded context** is a section of the system that owns a specific part of the domain. This
project currently has one: `users`.

```
app/
  users/         <-- the "users" bounded context
    domain/
    application/
    infrastructure/
    api/
```

When this project grows to include D&D characters and campaigns, those will be separate contexts:

```
app/
  users/
  characters/
  campaigns/
```

Each context owns its own models, its own database tables, and its own vocabulary. The `users`
context has no business looking inside `characters`. If they need to communicate, they do so
through well-defined interfaces, not by importing each other's internals.

The practical benefit right now: when you open `app/users/`, everything that matters for the
"user" concept is right there. You do not have to hunt through the whole codebase.

---

## 4. The four layers

Each bounded context has four sub-folders. Here is what each one is responsible for.

```
app/users/
  domain/          Pure business rules. No framework code.
  application/     Orchestration. Calls the domain. No business rules.
  infrastructure/  Database, external APIs, JWT. Implements domain interfaces.
  api/             FastAPI routes and dependencies. Thin layer.
```

A rough analogy: if the application were a restaurant —

- **Domain** is the recipe book. It says what a dish is and what rules it must follow.
- **Application** is the head chef who reads the recipe and coordinates the kitchen.
- **Infrastructure** is the kitchen equipment (ovens, refrigerators, delivery drivers).
- **API** is the front-of-house staff who take orders and pass them to the kitchen.

The recipe book (domain) does not care what brand of oven you use. The front-of-house staff
(API) do not decide what ingredients go in the dish.

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
        object.__setattr__(self, "value", lowered)  # see Python section for why this is needed
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

Files: `orm_models.py`, `repositories.py`, `auth.py`, `google_oauth.py`

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

## 9. Request lifecycle: sign in with Google

Tracing a full request through all layers.

```
Browser                  API Layer              Application           Domain            Infrastructure
   |                         |                      |                   |                    |
   |-- GET /api/v1/auth/google -->                  |                   |                    |
   |                         |                      |                   |                    |
   |                 google_oauth.py                |                   |                    |
   |                 builds redirect URL            |                   |                    |
   |<-- 302 to accounts.google.com ---------------  |                   |                    |
   |                         |                      |                   |                    |
   |    (user approves)      |                      |                   |                    |
   |                         |                      |                   |                    |
   |-- GET /api/v1/auth/google/callback?code=... -->|                   |                    |
   |                         |                      |                   |                    |
   |               exchange_code_for_user_info()    |                   |                    |
   |                         |-- POST token endpoint (Google) -------->|                    |
   |                         |<-- {id_token, access_token} -----------|                    |
   |                         |                      |                   |                    |
   |               RegisterOrRetrieveUser.execute() |                   |                    |
   |                         |-- repo.get_by_google_id() ------------>|                    |
   |                         |                      |         SqlAlchemyUserRepository       |
   |                         |                      |         SELECT from users              |
   |                         |                      |<-------- None (first login) ----------|
   |                         |                      |                   |                    |
   |                         |         User.register_via_google()       |                    |
   |                         |                      |-- Email("x@y.com")                    |
   |                         |                      |   validates + lowercases               |
   |                         |                      |-- GoogleID("123")                      |
   |                         |                      |   validates non-empty                  |
   |                         |                      |-- uuid4()                              |
   |                         |                      |<-- (User, UserRegisteredViaGoogle)     |
   |                         |                      |                   |                    |
   |                         |-- repo.save(user) -------------------- |                    |
   |                         |                      |         session.merge() + flush()      |
   |                         |                      |                   |                    |
   |               db.commit()                      |                   |                    |
   |               create_access_token(sub=user.id) |                   |                    |
   |<-- 302 to frontend?token=<jwt> --------------- |                   |                    |
```

On subsequent requests to `/api/v1/users/me`:

```
Browser                  API Layer              Application           Domain            Infrastructure
   |                         |                      |                   |                    |
   |-- GET /me  Authorization: Bearer <jwt> ------->|                   |                    |
   |                         |                      |                   |                    |
   |               HTTPBearer extracts token        |                   |                    |
   |               decode_access_token()            |                   |                    |
   |               -- verifies signature, expiry    |                   |                    |
   |               -- returns uuid.UUID             |                   |                    |
   |                         |                      |                   |                    |
   |               GetCurrentUser.execute(uuid)     |                   |                    |
   |                         |-- repo.get_by_id() ------------------- |                    |
   |                         |                      |         SELECT from users              |
   |                         |                      |<-------- UserORM row ----------------- |
   |                         |                      |         _to_domain() wraps into User   |
   |                         |<-- User -------------|                   |                    |
   |                         |                      |                   |                    |
   |               UserProfileResponse(...)         |                   |                    |
   |<-- 200 {"id": "...", "email": "..."} --------- |                   |                    |
```

---

## 10. Python concepts used in this project

### Dataclasses

`@dataclass` generates `__init__`, `__repr__`, and `__eq__` from class-level annotations.
`frozen=True` additionally generates `__hash__` and makes all fields read-only.

```python
@dataclass(frozen=True)
class GoogleID:
    value: str
```

is equivalent to writing roughly:

```python
class GoogleID:
    def __init__(self, value: str) -> None:
        object.__setattr__(self, "value", value)
    def __eq__(self, other: object) -> bool:
        return isinstance(other, GoogleID) and self.value == other.value
    def __hash__(self) -> int:
        return hash(self.value)
    def __setattr__(self, name: str, value: object) -> None:
        raise FrozenInstanceError(...)
```

### `object.__setattr__` in frozen dataclasses

Frozen dataclasses override `__setattr__` to raise an error. But `__post_init__` runs after
`__init__` and sometimes needs to normalise a value (like lowercasing an email). The only way
to do this is to call the base `object.__setattr__` directly, bypassing the frozen guard:

```python
def __post_init__(self) -> None:
    lowered = self.value.lower()
    object.__setattr__(self, "value", lowered)   # approved bypass
```

This is a well-known idiom in Python for immutable validation/normalisation.

### Abstract Base Classes

`ABC` (from `abc` module) allows you to define interfaces — classes that describe what methods
must exist without implementing them.

```python
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...
```

If a class inherits from `UserRepository` and does not implement `save`, Python raises
`TypeError: Can't instantiate abstract class X with abstract methods save`.

This enforces the contract at the class level, not at runtime when the method is first called.

### Type hints and `X | None`

```python
def get_by_google_id(self, google_id: str) -> User | None: ...
```

`User | None` (Python 3.10+, equivalent to `Optional[User]`) means the function can return
either a `User` object or `None`. Mypy enforces that callers handle the `None` case:

```python
existing = self._repo.get_by_google_id(google_id)
if existing is None:       # mypy requires this check before using `existing` as a User
    ...
```

### Classmethods as factories

```python
@classmethod
def register_via_google(cls, ...) -> tuple["User", UserRegisteredViaGoogle]:
    user = cls(...)   # cls is the class itself — so this calls User(...)
    ...
```

`@classmethod` receives the class (`cls`) as its first argument instead of an instance
(`self`). This is the idiomatic Python way to write named constructors / factory methods.
It is preferred over `__init__` overloading (which Python does not support directly) or
standalone factory functions (which would not have access to `cls` if the class is subclassed).

### Generators for session lifecycle

```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db          # caller uses db here
    finally:
        db.close()        # always runs, even if the caller raised an exception
```

`yield` turns a function into a generator. FastAPI's `Depends()` understands generators —
it runs the code up to `yield`, injects the yielded value, runs the route handler, then resumes
the generator (running the `finally` block). This guarantees `db.close()` is always called,
even on errors.

### `cast()` for type narrowing

```python
from typing import cast

return cast(RedirectResponse, await oauth.google.authorize_redirect(...))
```

`cast(T, x)` is a pure type-hint instruction to mypy. At runtime it is a no-op — it returns
`x` unchanged. It tells mypy "trust me, this value is of type `T`". It is used here because
the authlib library's return type annotation is `Any`, but we know the actual value is a
`RedirectResponse`.

---

## 11. File reference

```
app/
  core/
    config.py              Settings loaded from .env via pydantic-settings.
                           All configuration accessed through the `settings` singleton.

  db/
    base.py                SQLAlchemy DeclarativeBase. All ORM models inherit from Base.
                           Imports orm_models so Alembic can discover tables.
    session.py             Creates the engine and provides get_db() for dependency injection.

  api/
    v1/
      router.py            Top-level router. Includes all context routers.

  main.py                  FastAPI app creation. Adds SessionMiddleware. Includes api_router.

  users/                   The "users" bounded context.
    domain/
      events.py            UserRegisteredViaGoogle domain event.
      models.py            Email (value object), GoogleID (value object), User (aggregate root).
      repositories.py      UserRepository (abstract interface), UserNotFoundError.

    application/
      schemas.py           TokenResponse, UserProfileResponse (Pydantic DTOs).
      use_cases.py         RegisterOrRetrieveUser, GetCurrentUser (application services).

    infrastructure/
      orm_models.py        UserORM (SQLAlchemy model — database detail, not domain).
      repositories.py      SqlAlchemyUserRepository (concrete implementation of UserRepository).
      auth.py              create_access_token(), decode_access_token() — JWT utilities.
      google_oauth.py      OAuth client setup, redirect helper, token exchange.

    api/
      dependencies.py      get_user_repository(), get_current_user() — FastAPI dependencies.
      router.py            auth_router (/auth/google, /auth/google/callback),
                           users_router (/users/me).

alembic/
  env.py                   Wired to settings.DATABASE_URL and Base.metadata for autogenerate.

tests/                     (to be added) — domain layer tests only.
```

### Dependency diagram

```
app/main.py
  -> app/api/v1/router.py
       -> app/users/api/router.py
            -> app/users/api/dependencies.py
                 -> app/users/application/use_cases.py
                      -> app/users/domain/models.py
                      -> app/users/domain/repositories.py (interface only)
                 -> app/users/infrastructure/auth.py
                      -> app/core/config.py
            -> app/users/infrastructure/repositories.py  (implements domain interface)
                 -> app/users/infrastructure/orm_models.py
                 -> app/users/domain/models.py
            -> app/users/infrastructure/google_oauth.py
                 -> app/core/config.py
            -> app/users/application/schemas.py

  domain/models.py and domain/repositories.py import nothing from app/
```

The last line is the proof that the dependency rule is respected. Open `app/users/domain/models.py`
and `app/users/domain/repositories.py` — their imports are only standard library modules
(`uuid`, `abc`, `re`, `datetime`). No FastAPI, no SQLAlchemy, no authlib.

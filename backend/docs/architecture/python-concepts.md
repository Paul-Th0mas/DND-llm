# Python Concepts

Python-specific patterns used in this project. Useful when reading unfamiliar code.

---

## Dataclasses

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

---

## `object.__setattr__` in frozen dataclasses

Frozen dataclasses override `__setattr__` to raise an error. But `__post_init__` runs after
`__init__` and sometimes needs to normalise a value (like lowercasing an email). The only way
to do this is to call the base `object.__setattr__` directly, bypassing the frozen guard:

```python
def __post_init__(self) -> None:
    lowered = self.value.lower()
    object.__setattr__(self, "value", lowered)   # approved bypass
```

This is a well-known idiom in Python for immutable validation/normalisation.

---

## Abstract Base Classes

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

---

## Type hints and `X | None`

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

---

## Classmethods as factories

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

---

## Generators for session lifecycle

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

---

## `cast()` for type narrowing

```python
from typing import cast

return cast(RedirectResponse, await oauth.google.authorize_redirect(...))
```

`cast(T, x)` is a pure type-hint instruction to mypy. At runtime it is a no-op — it returns
`x` unchanged. It tells mypy "trust me, this value is of type `T`". It is used here because
the authlib library's return type annotation is `Any`, but we know the actual value is a
`RedirectResponse`.

---

## Index

| Entity | Documentation |
|--------|---------------|
| DDD / Domain-Driven Design | docs/architecture/concepts.md |
| Dependency rule | docs/architecture/concepts.md#2-the-dependency-rule |
| Bounded context | docs/architecture/concepts.md#3-bounded-contexts |
| Four layers | docs/architecture/concepts.md#4-the-four-layers |
| Value Object | docs/architecture/layers.md#value-objects |
| Aggregate root | docs/architecture/layers.md#aggregate-root |
| Factory method | docs/architecture/layers.md#factory-method |
| Domain event | docs/architecture/layers.md#domain-events |
| Repository interface | docs/architecture/layers.md#repository-interface |
| Use case / Application service | docs/architecture/layers.md#use-cases-application-services |
| DTO / Schema | docs/architecture/layers.md#schemas-dtos |
| ORM model vs domain model | docs/architecture/layers.md#orm-model-vs-domain-model |
| Concrete repository | docs/architecture/layers.md#concrete-repository |
| JWT | docs/architecture/layers.md#jwt-utilities |
| Google OAuth / OIDC | docs/architecture/layers.md#google-oauth--oidc |
| Narrator Port pattern | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| Dependency injection (FastAPI Depends) | docs/architecture/layers.md#dependency-injection |
| Thin router | docs/architecture/layers.md#thin-router |
| Request lifecycle | docs/architecture/lifecycle.md |
| Dataclasses | docs/architecture/python-concepts.md#dataclasses |
| object.__setattr__ | docs/architecture/python-concepts.md#objectsetattr-in-frozen-dataclasses |
| Abstract Base Classes | docs/architecture/python-concepts.md#abstract-base-classes |
| Type hints / X | None | docs/architecture/python-concepts.md#type-hints-and-x--none |
| Classmethods as factories | docs/architecture/python-concepts.md#classmethods-as-factories |
| Generators (session lifecycle) | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| get_db() | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| cast() | docs/architecture/python-concepts.md#cast-for-type-narrowing |
| File reference | docs/architecture/file-reference.md |
| Dependency diagram | docs/architecture/file-reference.md#dependency-diagram-users-excerpt |

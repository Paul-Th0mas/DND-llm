# Project Instructions for Claude

## General Rules

- No emojis in any output, code, or communication.
- Add comments to code when the logic is not immediately obvious, or when introducing a
  FastAPI/SQLAlchemy/DDD concept the user may not yet know. Comments are for learning.
- Keep solutions minimal. Do not add features, abstractions, or refactors that were not asked for.
- Never auto-commit. Always confirm before any destructive or shared-state action.

---

## Architecture: Domain-Driven Design (DDD)

All code must follow Domain-Driven Design principles. This is non-negotiable.

### Core Concepts to Enforce

**Domain** is king. The domain layer contains the business rules and must never depend on
infrastructure (FastAPI, SQLAlchemy, etc.). Dependencies always point inward.

**Bounded Contexts** group related domain concepts. Each context owns its models, logic, and
vocabulary. Do not share ORM models across contexts.

**Ubiquitous Language** means code names (classes, methods, variables) must match the language
of the domain. If the domain says "Character", do not call it "UserEntity" or "PlayerModel".

**Aggregates** are clusters of domain objects treated as a unit. Only the aggregate root is
referenced from outside. Enforce invariants (business rules) inside the aggregate, not in
services or endpoints.

**Value Objects** are immutable, identity-less objects defined by their attributes. Use them
instead of raw primitives (e.g. `HitPoints(value=10)` not just `int`).

**Domain Events** represent something meaningful that happened in the domain (e.g.
`CharacterLeveledUp`). Raise them from aggregates, handle them in application services.

**Repositories** abstract persistence. The domain defines the repository interface; the
infrastructure layer implements it. Never query the database directly from endpoints or services.

**Application Services** (not domain services) orchestrate use cases. They call repositories,
coordinate aggregates, and dispatch events. They contain no business logic themselves.

**Domain Services** hold business logic that does not naturally belong to a single aggregate.
Keep them rare - prefer putting logic in the aggregate.

---

## Project Layer Structure

```
app/
  {context}/               # One folder per bounded context (e.g. characters, campaigns)
    domain/
      models.py            # Aggregates, Entities, Value Objects (pure Python, no ORM)
      repositories.py      # Abstract repository interfaces (ABC)
      services.py          # Domain services (rare - only stateless cross-aggregate logic)
      events.py            # Domain events (dataclasses or Pydantic models)
    application/
      use_cases.py         # Application services / use case handlers
      schemas.py           # Input/output DTOs (Pydantic) - NOT the same as domain models
    infrastructure/
      orm_models.py        # SQLAlchemy ORM models (infrastructure detail, not domain)
      repositories.py      # Concrete repository implementations using SQLAlchemy
    api/
      router.py            # FastAPI router - thin layer, delegates to application services
      dependencies.py      # FastAPI dependency injection (get_db, get_repository, etc.)
  core/
    config.py              # App settings via pydantic-settings
  db/
    base.py                # SQLAlchemy DeclarativeBase
    session.py             # Engine + get_db() session dependency
  main.py                  # FastAPI app creation and router registration
```

---

## FastAPI Best Practices

- **Routers are thin.** Endpoints validate input (via Pydantic schemas), call one application
  service or use case, and return a response. No business logic in routers.

- **Dependency injection** via `Depends()` is the FastAPI way to provide repositories, sessions,
  and services to endpoints. Always use it rather than importing globals.

- **Pydantic schemas** are DTOs (Data Transfer Objects). They live in the application layer and
  are separate from both ORM models and domain models. A request schema is never an ORM model.

- **Response models** should be explicit. Always declare `response_model=` on endpoints so
  FastAPI validates and serializes the output.

- **Status codes** should be explicit. Use `status_code=201` for creation, `404` for not found,
  etc. Never rely on the default 200 for everything.

- **Async is optional but intentional.** Use `async def` only when the operation is truly async
  (e.g. async DB driver, external HTTP call). SQLAlchemy sync sessions with `def` is fine.

- **Settings via pydantic-settings.** All configuration comes from environment variables loaded
  through `app/core/config.py`. Never hardcode secrets or connection strings.

---

## SQLAlchemy Best Practices

- **ORM models are infrastructure.** They live in `infrastructure/orm_models.py` and should not
  leak into the domain layer. Map them to domain models in the repository implementation.

- **Use SQLAlchemy 2.0 style.** Use `select()`, `session.execute()`, and typed columns
  (`mapped_column`, `Mapped`). Avoid the legacy 1.x query API.

- **Sessions are request-scoped.** Use the `get_db()` generator from `db/session.py` via
  `Depends()`. Never create sessions manually inside business logic.

- **Alembic manages migrations.** Never use `Base.metadata.create_all()` in production code.
  All schema changes go through Alembic migration scripts.

---

## Python Best Practices

- **Type hints everywhere.** Every function signature must have full type annotations.
  mypy runs in strict mode - no `Any`, no untyped functions.

- **Dataclasses or Pydantic for value objects and events.** Prefer `@dataclass(frozen=True)`
  for domain value objects (immutable by design).

- **No mutable default arguments.** Never use `def f(x=[])` or `def f(x={})`.

- **Explicit over implicit.** Avoid magic. If something non-obvious is happening, add a comment.

- **One responsibility per class/function.** If a function does two things, split it.

- **Raise domain-specific exceptions.** Define exceptions in the domain layer
  (e.g. `CharacterNotFoundError`). Catch and translate them to HTTP responses at the API layer.

---

## What Claude Must NOT Do

- Do not put business logic in routers or endpoints.
- Do not import ORM models into the domain layer.
- Do not share a single "models.py" file for both ORM and domain models.
- Do not use raw dicts where a schema or value object should exist.
- Do not skip type annotations to save time.
- Do not use `Base.metadata.create_all()` as a substitute for Alembic migrations.
- Do not add unrequested abstractions, helpers, or "nice to have" features.

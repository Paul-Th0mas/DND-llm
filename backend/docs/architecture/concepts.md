# DDD Concepts

Covers the core theory behind this project's architecture. Read this first.

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
project has six active bounded contexts:

```
app/
  users/       Authentication, Google OAuth, JWT issuance, user profile.
  campaigns/   Campaign aggregate — tone, themes, level range, content boundaries.
  worlds/      World aggregate — lore, factions, bosses. Admin-seeded content.
  dungeons/    Dungeon generation — the primary LLM-integration context.
               Owns DungeonNarratorPort and the Gemini narrator implementation.
  combat/      Combat encounters — initiative, turn order, dice rolling.
  rooms/       Multiplayer rooms — invite codes, WebSocket presence, player membership.
```

Each context has the same four-layer structure (`domain/`, `application/`, `infrastructure/`,
`api/`) and owns its own models, database tables, and vocabulary. The `users` context has no
business looking inside `campaigns`. If they need to communicate, they do so through
well-defined interfaces, not by importing each other's internals.

There is one deliberate exception in a monolith: the `dungeons` application layer imports
`World` (from `worlds/domain`) and `Campaign` (from `campaigns/domain`) because generating a
dungeon requires both. This cross-context read at the application layer is acceptable — the
domain layer of `dungeons` imports nothing from sibling contexts.

The practical benefit: when you open `app/campaigns/`, everything that matters for the
"campaign" concept is right there. You do not have to hunt through the whole codebase.

---

## 4. The four layers

Each bounded context has four sub-folders. Here is what each one is responsible for.

```
app/dungeons/
  domain/          Pure business rules. No framework code.
  application/     Orchestration. Calls the domain. No business rules.
                   Also defines the DungeonNarratorPort (LLM interface).
  infrastructure/  Gemini API client, stub narrator, prompt assembler.
                   Implements the narrator port.
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

## Index

| Entity | Documentation |
|--------|---------------|
| DDD / Domain-Driven Design | docs/architecture/concepts.md |
| Dependency rule | docs/architecture/concepts.md#2-the-dependency-rule |
| Bounded context | docs/architecture/concepts.md#3-bounded-contexts |
| Four layers (domain / application / infrastructure / api) | docs/architecture/concepts.md#4-the-four-layers |
| Value Object | docs/architecture/layers.md#value-objects |
| Aggregate root | docs/architecture/layers.md#aggregate-root |
| Factory method | docs/architecture/layers.md#factory-method |
| Domain event | docs/architecture/layers.md#domain-events |
| Repository interface | docs/architecture/layers.md#repository-interface |
| Use case / Application service | docs/architecture/layers.md#use-cases-application-services |
| DTO / Schema | docs/architecture/layers.md#schemas-dtos |
| ORM model vs domain model | docs/architecture/layers.md#orm-model-vs-domain-model |
| Concrete repository | docs/architecture/layers.md#concrete-repository |
| JWT utilities | docs/architecture/layers.md#jwt-utilities |
| Google OAuth / OIDC | docs/architecture/layers.md#google-oauth--oidc |
| Narrator Port pattern | docs/architecture/layers.md#narrator-port-pattern-llm-integration |
| Dependency injection (FastAPI) | docs/architecture/layers.md#dependency-injection |
| Thin router | docs/architecture/layers.md#thin-router |
| Request lifecycle | docs/architecture/lifecycle.md |
| Dataclasses | docs/architecture/python-concepts.md#dataclasses |
| Abstract Base Classes | docs/architecture/python-concepts.md#abstract-base-classes |
| Generators (session lifecycle) | docs/architecture/python-concepts.md#generators-for-session-lifecycle |
| cast() | docs/architecture/python-concepts.md#cast-for-type-narrowing |
| File reference | docs/architecture/file-reference.md |
| Dependency diagram | docs/architecture/file-reference.md#dependency-diagram-users-excerpt |

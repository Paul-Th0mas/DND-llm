# DnD Project - Claude Instructions

## --- BACKEND INSTRUCTIONS ---
# Project Instructions for Claude

## General Rules

- No emojis in any output, code, or communication.
- Add comments to code when the logic is not immediately obvious, or when introducing a
  FastAPI/SQLAlchemy/DDD concept the user may not yet know. Comments are for learning.
- Keep solutions minimal. Do not add features, abstractions, or refactors that were not asked for.
- Never auto-commit. Always confirm before any destructive or shared-state action.
- **Add logging everywhere for debugging.** Every module must have a module-level logger created
  with `logger = logging.getLogger(__name__)`. Log at appropriate levels:
  - `logger.debug(...)` for detailed flow (function entry, variable values)
  - `logger.info(...)` for significant events (user created, request received)
  - `logger.warning(...)` for unexpected but recoverable situations
  - `logger.error(...)` for caught exceptions and failures
  Never use `print()` for debugging. Always use the logger.

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

## Error Handling

All error handling must be centralized and consistent. Never catch domain exceptions ad-hoc
inside routers, dependencies, or application services and convert them to `HTTPException`
manually. Use the global handler mechanism instead.

### Exception Hierarchy

Domain exceptions live in `app/core/exceptions.py` and carry **no HTTP knowledge**:

```
DomainError          → HTTP 400 (fallback for any unhandled domain error)
  NotFoundError      → HTTP 404
  AuthenticationError → HTTP 401
```

Every bounded context defines its own specific exceptions that inherit from the appropriate
base class (e.g. `UserNotFoundError(NotFoundError)`). The global handler catches the base
class and returns the correct status code automatically.

### Global Handlers

All handlers live in `app/core/error_handlers.py` and are registered in `app/main.py` via
`app.add_exception_handler()`. Registration order is **most-specific first**, so subclasses
match before their parents.

Handler responsibilities:
- `handle_not_found` → 404, logs at `WARNING`
- `handle_authentication_error` → 401 with `WWW-Authenticate: Bearer`, logs at `WARNING`
- `handle_domain_error` → 400 (fallback), logs at `WARNING`
- `handle_unhandled_exception` → 500, logs full traceback at `ERROR`

### Rules

- **Never raise `HTTPException` from infrastructure or domain layers.** Only the API layer
  (routers) may raise `HTTPException`, and only for HTTP-specific concerns (e.g. missing
  headers). Domain errors must propagate as domain exceptions.
- **Infrastructure wraps third-party errors.** When a library raises its own exception
  (e.g. `authlib.OAuthError`, `jose.JWTError`), the infrastructure layer catches it, logs
  it at `ERROR`, and re-raises as the appropriate domain exception.
- **All error responses use `{"detail": "..."}`.** This matches FastAPI's built-in
  `HTTPException` format so clients always see a consistent response shape.
- **Every domain exception must be tested.** See Testing Guidelines below.

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

## Linting and Formatting

All Python code must pass **Black** (formatting) and **MyPy** (type checking) before a task is
considered complete. Run both after every task, without exception.

### Black

Black enforces consistent formatting. Configuration lives in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
target-version = ["py311"]
```

Run:
```bash
black app/
```

Black must report no changes. If it reformats anything, the code was not properly formatted.

### MyPy

MyPy runs in strict mode. All type errors must be resolved - do not suppress with `# type: ignore`
unless there is a documented reason.

Configuration in `mypy.ini` (already present):
```ini
[mypy]
strict = true
```

Run:
```bash
mypy app/
```

### Additional Linting Rules

- **No unused imports.** Remove them - MyPy strict mode will catch most, but review manually.
- **No wildcard imports.** Never use `from module import *`.
- **No shadowing builtins.** Do not name variables `id`, `type`, `list`, `input`, etc.
- **Cyclomatic complexity.** Functions must not exceed 10 branches. If they do, split them.
- **Line length.** Black enforces 88 characters. Do not exceed it.
- **String formatting.** Use f-strings. Do not use `%` formatting or `.format()`.

### After Every Task

Before considering any task done, Claude must run:
```bash
black app/ && mypy app/
```
Both must pass with zero errors. Fix any issues before reporting the task complete.

---

## Testing Guidelines

All tests use **pytest**. Tests cover the **domain layer only** - aggregates, entities, value
objects, domain services, and domain events. Do not write tests for routers, ORM models, or
application services unless explicitly asked.

### Test Structure

```
tests/
  {context}/
    domain/
      test_models.py       # Tests for aggregates, entities, value objects
      test_services.py     # Tests for domain services (if any exist)
      test_events.py       # Tests for domain event construction and fields
  conftest.py              # Shared fixtures
```

### Rules

- **Test file naming:** `test_<module>.py`. Test function naming: `test_<what_it_does>`.
- **One assertion per test** where possible. A test that checks ten things tests nothing clearly.
- **Arrange / Act / Assert.** Structure every test in these three sections, separated by a blank
  line.
- **No logic in tests.** Tests must not contain loops, conditionals, or helper computation. If
  setup is complex, extract a pytest fixture.
- **Test invariants, not implementation.** Test that a domain rule is enforced, not how it is
  implemented internally.
- **Use `@dataclass(frozen=True)` value objects.** Tests should confirm immutability raises
  `FrozenInstanceError` where appropriate.
- **Domain exceptions must be tested.** Every custom domain exception must have at least one test
  that verifies it is raised under the correct condition.
- **No mocking of domain objects.** Domain models are pure Python - instantiate them directly.
  Only mock infrastructure (repositories) when testing application services.

### Running Tests

```bash
pytest tests/ -v
```

All tests must pass before a task is complete.

---

## What Claude Must NOT Do

- Do not put business logic in routers or endpoints.
- Do not import ORM models into the domain layer.
- Do not share a single "models.py" file for both ORM and domain models.
- Do not use raw dicts where a schema or value object should exist.
- Do not skip type annotations to save time.
- Do not use `Base.metadata.create_all()` as a substitute for Alembic migrations.
- Do not add unrequested abstractions, helpers, or "nice to have" features.


## --- FRONTEND INSTRUCTIONS ---
# DnD Frontend - Claude Instructions

## Project Overview
A Next.js frontend application built using Domain Driven Design principles.
All code must be written in TypeScript with strict typing.

---

## Tech Stack

- **Framework**: Next.js (App Router)
- **Language**: TypeScript (strict mode)
- **UI Library**: Material UI (MUI) v7
- **Styling**: Tailwind CSS v4
- **State Management**: Zustand v5
- **Testing**: Vitest + React Testing Library
- **Bundler (tests)**: Vite / RSPack
- **Package Manager**: Yarn (never use npm for this project)

---

## Architecture: Domain Driven Design (DDD)

Structure all code around business domains, not technical layers.

### Folder Structure
```
app/                        # Next.js App Router pages and layouts
  (domain)/                 # Route groups per domain
    page.tsx
    layout.tsx

domains/                    # Core DDD layer
  <domain-name>/
    components/             # UI components scoped to this domain
    hooks/                  # Domain-specific React hooks
    services/               # Business logic and API calls
    types/                  # Domain types and interfaces
    constants/              # Domain-scoped constants
    utils/                  # Domain-scoped utility functions
    __tests__/              # Tests co-located with domain

shared/                     # Cross-domain shared code
  components/               # Reusable UI components
  hooks/                    # Shared hooks
  types/                    # Shared TypeScript types
  utils/                    # Shared utility functions
  constants/                # App-wide constants
  store/                    # Zustand store slices shared across domains

lib/                        # External library configuration
  mui/                      # MUI theme setup
  api/                      # API client setup
```

### DDD Rules
- Each domain owns its own types, services, components, and constants.
- Domains must NOT import directly from other domains. Use shared/ for cross-domain code.
- Business logic lives in services/, not in components or hooks.
- Hooks are thin wrappers that connect components to services.
- Do not bleed domain logic into pages — pages only compose domain components.

---

## TypeScript Rules

- Always use `strict: true` (already set in tsconfig.json).
- Never use `any`. Use `unknown` and narrow the type.
- All function parameters and return types must be explicitly typed.
- Prefer `interface` for object shapes and `type` for unions/intersections.
- Use `as const` for constant objects and arrays.
- Never use non-null assertion (`!`) unless unavoidable — add a comment explaining why.
- Use `readonly` for props and data that should not be mutated.

---

## Commenting Rules

- **No emojis in comments.**
- Every exported function must have a JSDoc comment describing what it does, its parameters, and its return value.
- Every React component (including page components) must have a JSDoc comment describing its purpose and props.
- Every constant that is exported or non-obvious must have an inline comment or JSDoc.
- Keep comments factual and concise. Do not restate the code — explain intent or non-obvious behavior.

### Comment Format

```ts
/**
 * Fetches the character list for a given campaign.
 * @param campaignId - The unique identifier of the campaign.
 * @returns A promise resolving to an array of Character objects.
 */
export async function getCharactersByCampaign(campaignId: string): Promise<Character[]> { ... }
```

```tsx
/**
 * Displays the character card with name, class, and level.
 * Used in the campaign overview and character selection screens.
 */
export function CharacterCard({ character }: CharacterCardProps) { ... }
```

```ts
// Maximum number of players allowed in a single campaign session.
export const MAX_PLAYERS = 6 as const;
```

---

## Next.js Best Practices

- Use **Server Components** by default. Only add `"use client"` when the component needs interactivity (state, effects, browser APIs).
- Keep `"use client"` components as small and leaf-level as possible.
- Use **Route Handlers** (`app/api/`) only for BFF (backend-for-frontend) logic. Never call internal route handlers from server components — call services directly.
- Use `generateMetadata` for all pages that need SEO metadata.
- All data fetching in server components must use `async/await` directly — no `useEffect` for server-fetched data.
- Use `loading.tsx` and `error.tsx` for each route segment.
- Use `next/image` for all images. Never use raw `<img>` tags.
- Use `next/link` for all internal navigation. Never use raw `<a>` tags.
- Do not put business logic inside `page.tsx` or `layout.tsx` files.
- Environment variables that are public must be prefixed with `NEXT_PUBLIC_`.
- Never expose private environment variables to client components.
- Use `unstable_cache` or `revalidate` options for caching server data.

---

## Material UI + Tailwind Rules

- MUI handles **component-level** styling (variants, states, spacing within components).
- Tailwind handles **layout and composition** (grid, flex, spacing between components, responsive breakpoints).
- Do not mix MUI `sx` prop with Tailwind on the same element for the same property. Pick one.
- Define the MUI theme in `lib/mui/theme.ts` using the project palette. Do not hardcode colors inline.
- Use MUI `ThemeProvider` in the root layout.
- All MUI theme colors must map to the project palette below.

### Color Palette
| Token         | Hex       | Usage                  |
|---------------|-----------|------------------------|
| parchment-50  | #F9F8F6   | Page background        |
| parchment-100 | #EFE9E3   | Surface / card         |
| parchment-200 | #D9CFC7   | Borders / dividers     |
| parchment-300 | #C9B59C   | Muted text / secondary |
| parchment-400 | #b89a7e   | Hover states           |
| parchment-500 | #a07d60   | Primary accent         |
| parchment-600 | #7d5e45   | Active / pressed       |
| parchment-700 | #5c4230   | Dark accent            |
| parchment-800 | #3a2820   | Rich text              |
| parchment-900 | #1e1410   | Foreground / headings  |

---

## Zustand State Management Rules

- Use Zustand for all global and cross-component client-side state.
- Do NOT use React context for global state — use Zustand stores.
- Local UI state (open/close, hover) that does not leave the component may use `useState`.
- Each domain owns its own store slice, located at `domains/<domain>/store/<domain>.store.ts`.
- Shared store slices that span multiple domains live in `shared/store/`.
- Never import a domain store from another domain. If two domains need shared state, move it to `shared/store/`.

### Store Structure per Domain
```
domains/<domain>/
  store/
    <domain>.store.ts       # Zustand slice definition
    <domain>.store.types.ts # State and action types
    __tests__/
      <domain>.store.test.ts
```

### Store Rules

- Define state and actions as separate TypeScript interfaces before creating the store.
- Actions must be defined inside the store (not as separate functions) to keep state mutation co-located.
- Never mutate state directly — always use `set()`.
- Use `immer` middleware only when state shape is deeply nested and direct mutation would be clearer.
- Use `devtools` middleware in development for all stores.
- Keep stores lean — derived values belong in selectors, not in state.
- Selectors must be defined outside the store as pure functions.
- Never call a store inside a Server Component — stores are client-side only.
- Components that use a store must be `"use client"`.

### Store Naming Convention
- File: `<domain>.store.ts`
- Hook: `use<Domain>Store`
- State type: `<Domain>State`
- Actions type: `<Domain>Actions`

### Store Template

```ts
import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { ExampleState, ExampleActions } from "./example.store.types";

// Combined store type merging state shape and actions.
type ExampleStore = ExampleState & ExampleActions;

/**
 * Zustand store for the Example domain.
 * Manages [describe what this store manages].
 */
export const useExampleStore = create<ExampleStore>()(
  devtools(
    (set) => ({
      // initial state
      items: [],

      // actions
      setItems: (items) => set({ items }, false, "example/setItems"),
      clearItems: () => set({ items: [] }, false, "example/clearItems"),
    }),
    { name: "ExampleStore" }
  )
);

/**
 * Selects the items array from the Example store.
 * @param state - The current Example store state.
 * @returns The list of example items.
 */
export const selectItems = (state: ExampleStore): ExampleState["items"] =>
  state.items;
```

### Store Types Template

```ts
// State shape for the Example domain store.
export interface ExampleState {
  readonly items: readonly ExampleItem[];
}

// Actions available on the Example domain store.
export interface ExampleActions {
  setItems: (items: readonly ExampleItem[]) => void;
  clearItems: () => void;
}
```

---

## Testing Rules

- Every domain service must have unit tests in `__tests__/`.
- Every shared utility function must have unit tests.
- React components use React Testing Library — test behavior, not implementation.
- Do not test internal state — test what the user sees and can interact with.
- Mock all network calls. Never make real API calls in tests.
- Test file naming: `<name>.test.ts` or `<name>.test.tsx`.
- Run tests with: `yarn test` (watch) or `yarn test:run` (single run).

---

## General Code Rules

- Never commit `console.log` statements.
- No unused imports or variables — the linter will catch these.
- Prefer named exports over default exports for components and functions (except Next.js page/layout files, which require default exports).
- Keep files focused — one primary export per file.
- Avoid deeply nested ternaries. Use early returns or helper variables.
- Do not use `index.ts` barrel files unless a domain explicitly needs a public API surface.

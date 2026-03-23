# DnD LLM - Frontend

The Next.js frontend for the DnD LLM project. Built with TypeScript strict mode, Material UI, Tailwind CSS, and Zustand following Domain Driven Design principles.

## Tech Stack

- **Next.js** (App Router) — server-first React framework
- **TypeScript** (strict mode) — all code is fully typed
- **Material UI v7** — component-level styling and theming
- **Tailwind CSS v4** — layout, spacing, and responsive breakpoints
- **Zustand v5** — client-side global state management
- **Vitest + React Testing Library** — unit and component testing
- **Yarn** — the only supported package manager for this project

## Local Development

Install dependencies:

```bash
yarn install
```

Start the development server:

```bash
yarn dev
```

The application is served at [http://localhost:3000](http://localhost:3000).

## Running Tests

Single run (CI):

```bash
yarn test:run
```

Watch mode (development):

```bash
yarn test
```

## Folder Structure

```
app/                        # Next.js App Router pages and layouts
  (domain)/                 # Route groups per domain

domains/                    # Core DDD layer — one folder per business domain
  <domain-name>/
    components/             # UI components scoped to this domain
    hooks/                  # Domain-specific React hooks
    services/               # Business logic and API calls
    store/                  # Zustand store slice for this domain
    types/                  # Domain types and interfaces
    constants/              # Domain-scoped constants
    utils/                  # Domain-scoped utility functions
    __tests__/              # Tests co-located with the domain

shared/                     # Code shared across multiple domains
  components/               # Reusable UI components
  hooks/                    # Shared React hooks
  types/                    # Shared TypeScript types
  utils/                    # Shared utility functions
  constants/                # App-wide constants
  store/                    # Zustand slices used across domains

lib/                        # External library configuration
  mui/                      # MUI theme definition
  api/                      # API client setup
```

### Key conventions

- Domains must not import directly from other domains. Use `shared/` for cross-domain code.
- Business logic belongs in `services/`, not in components or hooks.
- Components marked `"use client"` should be as small and leaf-level as possible.
- Never use `npm`, `pnpm`, or `bun` — use `yarn` exclusively.

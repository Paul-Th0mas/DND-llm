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

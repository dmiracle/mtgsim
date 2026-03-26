# MTG Sim Frontend

Monorepo containing the shared UI component library and application packages.

## Structure

```
frontend/
  packages/
    ui/           # Shared component library, types, fixtures, styles, API client
    app-v1/       # Original MTG viewer app (pages, routes, API hooks)
    app-v2/       # New app shell (imports from @mtgsim/ui)
```

### `@mtgsim/ui`

Shared package containing all reusable pieces:

- **Components** — 74 React components (cards, decks, filters, charts, layouts)
- **Types** — API response types and flashcard types
- **Fixtures** — Mock data for Storybook and development
- **Styles** — Tailwind config, 18 color themes, 19 font themes
- **API client** — `apiFetch` and query hooks
- **Storybook** — Component library browser on port 6006

### `@mtgsim/app-v1`

The current MTG card viewer/deck manager/flashcard study app. Uses `@/` imports that resolve to local files, with symlinks to `@mtgsim/ui` for shared code.

- Pages, routes, context providers
- Runs on port 5173, proxies `/api` to backend on 8001

### `@mtgsim/app-v2`

Skeleton for the new app. Imports shared components from `@mtgsim/ui`.

- Runs on port 5174, proxies `/api` to backend on 8001

## Commands

From the root `frontend/` directory:

```bash
# Install all dependencies
npm install

# Development
npm run dev          # Start app-v1 on :5173
npm run dev:v2       # Start app-v2 on :5174
npm run storybook    # Start Storybook on :6006

# Type checking
npm run typecheck    # Check all workspaces

# Build
npm run build        # Build app-v1
npm run build:v2     # Build app-v2
```

Or run directly in a workspace:

```bash
npm run dev -w @mtgsim/app-v1
npm run storybook -w @mtgsim/ui
```

## Adding Components

New shared components go in `packages/ui/src/components/`. Add the export to `packages/ui/src/index.ts`.

App-specific pages and routes go in the relevant app package under `packages/app-v1/src/pages/` or `packages/app-v2/src/pages/`.

## Dependency Graph

```
@mtgsim/app-v1  ──depends on──>  @mtgsim/ui
@mtgsim/app-v2  ──depends on──>  @mtgsim/ui
```

Both apps share React, React Query, React Router, Tailwind CSS, and all UI components. Each app has its own Vite config, entry point, and routing.

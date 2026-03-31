# MTG Sim Frontend

Monorepo containing the shared UI component library and application packages.

## Structure

```
frontend/
  packages/
    ui/           # Shared component library, types, fixtures, styles, API client
    viewer/       # Full-featured MTG card browser, deck manager, set explorer
    flashcards/   # Mobile-first flashcard study app
```

### `@mtgsim/ui`

Shared package containing all reusable pieces:

- **Components** — React components (cards, decks, filters, charts, layouts, flashcards)
- **Types** — API response types and flashcard types
- **Fixtures** — Mock data for Storybook and development
- **Styles** — Tailwind config, 18 color themes, 19 font themes
- **API client** — `apiFetch` and query hooks
- **Storybook** — Component library browser on port 6006

### `@mtgsim/viewer`

The full MTG card viewer/deck manager/flashcard study app with sidebar navigation, card browser, set explorer, price tracker, draft simulator, and reference tools.

- Runs on port 5173, proxies `/api` to backend on 8001

### `@mtgsim/flashcards`

Mobile-first flashcard study app. Collection picker, card recall with traffic light rating, SRS-scheduled review.

- Runs on port 5174, proxies `/api` to backend on 8001

## Commands

From the root `frontend/` directory:

```bash
# Install all dependencies
npm install

# Development
npm run dev              # Start viewer on :5173
npm run dev:flashcards   # Start flashcards on :5174
npm run storybook        # Start Storybook on :6006

# Type checking
npm run typecheck        # Check all workspaces

# Build
npm run build            # Build viewer
npm run build:flashcards # Build flashcards
```

Or run directly in a workspace:

```bash
npm run dev -w @mtgsim/viewer
npm run dev -w @mtgsim/flashcards
npm run storybook -w @mtgsim/ui
```

## Adding Components

New shared components go in `packages/ui/src/components/`. Add the export to `packages/ui/src/index.ts`.

App-specific pages and routes go in the relevant app package under `packages/viewer/src/pages/` or `packages/flashcards/src/pages/`.

## Dependency Graph

```
@mtgsim/viewer     ──depends on──>  @mtgsim/ui
@mtgsim/flashcards ──depends on──>  @mtgsim/ui
```

Both apps share React, React Query, React Router, Tailwind CSS, and all UI components. Each app has its own Vite config, entry point, and routing.

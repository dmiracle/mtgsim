# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from `frontend/`:

```bash
npm install                      # Install all workspace dependencies
npm run dev                      # Viewer dev server on :5173
npm run dev:flashcards           # Flashcards dev server on :5174
npm run storybook                # Storybook on :6006
npm run typecheck                # Type check all workspaces
npm run lint                     # ESLint across all packages
npm run build                    # Build viewer (tsc -b && vite build)
npm run build:flashcards         # Build flashcards
```

Run in a specific workspace: `npm run dev -w @mtgsim/viewer`

The backend API runs separately on :8001 (`uv run mtgsim-api` from repo root). Both apps proxy `/api` to the backend via Vite config.

## Architecture

npm workspaces monorepo with three packages:

```
@mtgsim/ui         → Shared library: components, types, API client, styles, fixtures, Storybook
@mtgsim/viewer     → Full MTG browser app (cards, decks, sets, prices, draft, flashcards)
@mtgsim/flashcards → Mobile-first flashcard study app
```

**Dependency flow:** viewer and flashcards both depend on `@mtgsim/ui`. They share React, React Query, React Router, and Tailwind CSS. Both apps import from `@mtgsim/ui` via path alias (`@mtgsim/ui` → `../ui/src`).

### API layer (`packages/ui/src/api/`)

- `client.ts` — `apiFetch()` wrapper and `buildParams()` utility. Base URL from `VITE_API_URL` env or `/api`.
- `hooks.ts` — TanStack React Query hooks for all server data (decks, cards, sets, prices, boosters, keywords, stats).
- `flashcard-hooks.ts` — Query hooks for flashcard collections, reviews, analytics, generation.

All server state goes through React Query (configured in each app's `App.tsx` with 30s staleTime, 1 retry). No Redux or Zustand — client state uses React Context (`ActiveDeckContext` for deck picker) and `useState`.

### Component library (`packages/ui/src/components/`)

Each component lives in its own directory with `index.ts` re-export. All shared components are exported from `packages/ui/src/index.ts` — new components must be added there.

### Routing (`packages/viewer/src/routes.tsx`)

React Router v7 with `AppLayout` wrapper. Routes: `/`, `/decks`, `/decks/:file`, `/cards`, `/cards/:uuid`, `/sets`, `/sets/:code`, `/prices`, `/draft`, `/reference`, `/flashcards`, `/flashcards/study`, `/flashcards/generate`.

Page components live in `packages/viewer/src/pages/` as `*Route` exports.

### Styling

Tailwind CSS 4 via `@tailwindcss/vite` plugin. Theme system with 18+ color themes and font themes defined in `packages/ui/src/themes.css`. CSS custom properties for all colors (bg-primary, text-primary, accent, etc.).

## Scope Rules

- **Frontend only** — sessions in this directory must never modify backend code (anything outside `frontend/`).
- If a backend change is needed (new API endpoint, schema change, etc.), create a GitHub issue in `dmiracle/mtgsim` describing the requirement instead of making the change.

## Key Conventions

- **TypeScript strict mode** — target ES2023, JSX react-jsx, noEmit (Vite handles transpilation)
- **Path aliases** — `@/*` maps to `src/*`, `@mtgsim/ui` maps to `../ui/src` in each app
- **Types** — API response types in `packages/ui/src/types/api.ts`, flashcard types in `types/flashcards.ts`
- **Vite** — React + Tailwind plugins, dev servers bound to `0.0.0.0` with Tailscale host allowlist
- **ESLint** — flat config with TypeScript ESLint, React hooks, React Refresh, and Storybook plugins

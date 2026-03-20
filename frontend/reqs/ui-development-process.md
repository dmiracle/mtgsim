# UI Development Process

A repeatable process for building frontend applications iteratively using a component library approach. This document captures the methodology used to build the MTG Deck Viewer frontend and generalizes it for reuse across projects.

---

## Overview

The core idea: **build the UI bottom-up in isolation before composing it into an application.** Every component is viewable, testable, and themeable in a library browser (Storybook) before it touches a page layout or API call.

The process has 7 stages:

1. Requirements analysis and component breakdown
2. Project scaffolding with design infrastructure
3. Type definitions and fixture data
4. Component library (bottom-up, in phases)
5. Design system (themes, typography, icons)
6. Page composition
7. Routing and API wiring

---

## Stage 1: Requirements Analysis

**Input:** Feature requirements document + backend API definition

**Process:**
- Read the requirements end-to-end
- Identify every distinct UI element mentioned
- Categorize into: shared/reusable components, page-level layouts, feature-specific components
- Write a component breakdown document that maps each component to the requirement section it addresses and the API endpoint it consumes

**Output:** `ui-components.md` — a catalog of every component needed, organized by category, with a proposed build order

**Key decisions at this stage:**
- What is shared vs. page-specific (e.g., a card filter bar used in 3 places is shared)
- What data each component needs (props interface)
- Which components compose into which (e.g., CardGrid contains CardGridItem contains ManaSymbols)
- A phased build order that starts with primitives and ends with pages

---

## Stage 2: Project Scaffolding

**Stack choices:**
- Vite + React + TypeScript (fast dev server, type safety)
- Tailwind CSS (utility-first styling, works well with theme variables)
- Storybook (component library browser with controls, docs, and addons)

**Setup steps:**
1. Scaffold with Vite (`create vite` with react-ts template)
2. Install Tailwind CSS via Vite plugin
3. Initialize Storybook (`storybook init`)
4. Configure path aliases (`@/` → `src/`)
5. Import Storybook's preview to include global CSS

**Why Storybook:**
- Every component gets a `.stories.tsx` file with multiple variants
- Visual browser at `localhost:6006` for design review
- Toolbar plugins for theme/font switching
- Components are developed in isolation — no need for routing, API, or app state
- Stories double as living documentation

---

## Stage 3: Types and Fixtures

**Before writing any components**, define the data shapes and create fixture data.

### Type definitions
Derive TypeScript types directly from the backend API definition. Every API response shape becomes a type. This ensures the frontend and backend speak the same language from day one.

```
src/types/api.ts — all API response types
```

### Fixture data
Create realistic mock data for every type. Fixtures are used by:
- Storybook stories (component previews)
- Route wrappers (before API is wired)
- Tests (when added later)

```
src/fixtures/
  cards.ts      — CardSummary[], CardDetail
  decks.ts      — DeckSummary[], DeckDetail
  sets.ts       — SetSummary[], SetDetail
  stats.ts      — HomeStats
  keywords.ts   — KeywordsResponse
  prices.ts     — PriceSummary[]
  index.ts      — barrel export
```

**Key principle:** Components receive data as props. They never fetch data. This separation means components work identically with fixtures or real API data.

---

## Stage 4: Component Library (Phased)

Build components bottom-up in phases. Each phase delivers visible, testable components in Storybook.

### Phase structure
1. **Foundation** — layout shell, navigation, primitive display components (icons, symbols, badges), basic inputs (search, pagination), stat cards, charts
2. **Filters & Controls** — all filter/input components that will be composed into filter bars
3. **Detail sub-components** — all the pieces that make up a detail view (identity, text, metadata, prices, etc.)
4. **Feature composites** — list items, stat dashboards, modals
5. **Domain-specific** — components tied to specific features (draft simulator, price explorer)
6. **Reference & polish** — browsers, viewers, remaining shared utilities

### Per-component workflow
For each component:
1. Create the component file (`.tsx`)
2. Create the stories file (`.stories.tsx`) with multiple variants
3. Run TypeScript check to verify
4. View in Storybook, iterate on design

### Story patterns
Each story file should include:
- A default/happy-path story
- Edge cases (empty data, long text, single item, many items)
- Interactive stories using `useState` for stateful components
- Size/variant stories if the component has size props

---

## Stage 5: Design System

### Theme system
Use CSS custom properties for all design tokens. Themes are applied via a `data-theme` attribute on the root element.

**Color tokens:**
```
--color-bg-primary, --color-bg-secondary, --color-bg-tertiary
--color-text-primary, --color-text-secondary, --color-text-muted
--color-border, --color-border-hover
--color-accent, --color-accent-hover, --color-accent-muted
--color-success, --color-warning, --color-danger
```

**Typography tokens:**
```
--font-heading, --font-body, --font-mono
--font-weight-heading, --font-letter-heading
--font-size-base, --font-line-height
```

Components reference these tokens via Tailwind utilities (`bg-bg-primary`, `text-text-secondary`, etc.) registered through Tailwind's `@theme` directive.

### Storybook toolbar integration
Add global toolbar controls for switching themes and fonts independently. This uses Storybook's `globalTypes` + decorators:

```typescript
globalTypes: {
  theme: { toolbar: { title: 'Theme', icon: 'paintbrush', items: THEMES } },
  font: { toolbar: { title: 'Font', icon: 'document', items: FONTS } },
},
decorators: [
  (Story, context) => {
    document.documentElement.setAttribute('data-theme', context.globals.theme);
    document.documentElement.setAttribute('data-font', context.globals.font);
    return Story();
  },
],
```

### Typography specimen
Create a dedicated story that shows all typographic elements (heading scale, body text, card context, labels, monospace, numbers) so font themes can be evaluated at a glance.

### Icon fonts
For domain-specific iconography (MTG mana symbols, set icons, card type icons), use established icon fonts rather than custom SVGs. This ensures consistency and coverage. When icon fonts have hardcoded colors that conflict with theming, override them with `color: inherit !important` in global CSS.

### Design iteration
The Storybook toolbar approach allows rapid exploration:
- Designers/stakeholders can switch themes without touching code
- Every component and page automatically respects the active theme
- Color and font are independent axes — any combination works
- Specimen stories make it easy to evaluate typography at a glance

---

## Stage 6: Page Composition

Pages are components that arrange other components into layouts. They receive all data as props — no fetching logic.

```
src/pages/
  HomePage/
    HomePage.tsx          — composes StatCard, BarChart, SetBadge, etc.
    HomePage.stories.tsx  — passes fixture data
    HomeRoute.tsx         — route wrapper (added in stage 7)
```

### Page story pattern
Page stories use fixture data and Storybook's `parameters: { layout: "padded" }` for proper presentation. They show the full composed layout exactly as a user would see it.

### Tabbed layouts
For detail pages with multiple views (stats/cards), use local `useState` for tab state. The page component manages which tab is visible; the tab content components are pure renderers.

---

## Stage 7: Routing and API Wiring

### Routing
Install a router (React Router) and create a route configuration. The app shell (`AppLayout`) uses `<Outlet />` to render child routes. Navigation components use router hooks (`useNavigate`, `useLocation`) instead of callback props.

### Route wrappers
Each page gets a thin "Route" component that:
1. Extracts URL params (`useParams`)
2. Calls API hooks (`useQuery`, `useMutation`)
3. Passes data to the pure page component
4. Wires navigation callbacks

```
HomeRoute.tsx:
  const { data } = useHomeStats();
  return <HomePage stats={data ?? fallback} onSetClick={(code) => navigate(`/sets/${code}`)} />;
```

### API client
A single `apiFetch` function handles base URL, headers, and error handling. Query hooks wrap this with TanStack Query for caching, deduplication, and background refetching.

### Proxy configuration
During development, configure the dev server to proxy `/api` requests to the backend. This avoids CORS issues and mirrors the production setup where a reverse proxy or same-origin serves both frontend and API.

### Fallback strategy
Route wrappers use fixture data as fallback while the API loads (`data ?? fallback`). This means the UI is always visible — it shows fixture data instantly, then swaps to real data when the API responds.

---

## Summary of Principles

1. **Bottom-up construction** — primitives first, compositions later, pages last
2. **Props-driven components** — components never fetch data, they receive it
3. **Fixture-first development** — realistic mock data enables development without a running backend
4. **Visual-first iteration** — every component is viewable in Storybook before it enters the app
5. **Theme as infrastructure** — CSS custom properties + Storybook toolbar = instant design exploration
6. **Thin route wrappers** — routing and data fetching are a thin layer on top of pure page components
7. **Phased delivery** — each phase produces a visible, reviewable increment
8. **Type safety throughout** — API types derived from backend docs, shared across fixtures, components, and hooks

---

## Checklist for New Projects

- [ ] Write feature requirements document
- [ ] Document backend API (or define it if building both)
- [ ] Create component breakdown with phased build order
- [ ] Scaffold: Vite + React + TS + Tailwind + Storybook
- [ ] Define API types from backend spec
- [ ] Create fixture data for all types
- [ ] Set up theme system (color tokens + typography tokens)
- [ ] Add Storybook toolbar for theme/font switching
- [ ] Build Phase 1: foundation components + stories
- [ ] Design review in Storybook, iterate
- [ ] Build remaining phases
- [ ] Create typography specimen, evaluate font options
- [ ] Compose pages from components + stories
- [ ] Add routing
- [ ] Create API client + query hooks
- [ ] Wire route wrappers to API
- [ ] Configure dev proxy
- [ ] End-to-end test with real backend

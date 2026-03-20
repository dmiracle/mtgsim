# MTG Deck Viewer - UI Component Breakdown

This document proposes the React component tree needed to implement the feature requirements. Components are grouped into **shared/reusable**, **page-level**, and **feature-specific** categories. Each component lists what it renders, its data source, and which requirement section it addresses.

---

## 1. App Shell

### 1.1 `AppLayout`
- Top-level layout wrapper: sidebar navigation + main content area
- Renders the active page based on route
- Req: all sections

### 1.2 `SidebarNav`
- Navigation links: Home, Decks, Cards, Sets, Prices, Draft, Reference
- Active state indicator
- Req: all sections

### 1.3 `PageHeader`
- Page title, breadcrumbs, back navigation
- Req: 4 (Card Detail back button), general navigation

---

## 2. Shared / Reusable Components

### 2.1 Display Components

#### `CardGridItem`
- Card image (lazy loaded, fallback), name, mana cost, type line, oracle text, P/T, quantity badge, set link, rarity, color identity symbols, price, pin/unpin button, add-to-deck button, UUID copy, raw JSON toggle
- Req: 11 (Card Display)

#### `CardGrid`
- Responsive grid layout of `CardGridItem` components
- Accepts card array + pagination props
- Req: 3, 5.2.2, 2.4.2

#### `ManaSymbols`
- Renders mana cost string (e.g. `{2}{W}{U}`) as inline icon images
- Used in card displays, oracle text, detail views
- Req: 12 (Mana symbol rendering)

#### `SetIcon`
- Renders set keyrune icon from set code
- Tooltip with full set name on hover
- Navigable to set detail
- Req: 12 (Set icons)

#### `RawJsonViewer`
- Collapsible JSON tree with syntax highlighting
- Accepts any JSON object
- Req: 12 (Raw JSON viewer)

#### `Pagination`
- Page controls: prev/next, page numbers, items-per-page
- Consistent across all list views
- Req: 12 (Pagination)

#### `StatCard`
- Single aggregate stat display (label + value)
- Used on Home, Price Explorer, detail pages
- Req: 1, 6.2

#### `BarChart` / `Histogram`
- Reusable chart for mana curve, price distribution, rarity breakdown, type distribution, color distribution
- Req: 1, 2.4.1, 5.2.1

#### `KeywordCloud`
- Interactive word cloud for keyword frequencies
- Grouped by category (abilities, actions, ability words)
- Click to toggle keyword filter
- Hover for definition + count
- Req: 3.2, 2.4.1, 5.2.1

#### `FormatLegalityBadges`
- Grid of format badges showing legal/restricted/banned/not-legal status
- Sorted: legal first, then alphabetical
- Req: 4.6, 2.4.1

### 2.2 Filter & Input Components

#### `CardFilterBar`
- Shared filter toolbar used across card browser, deck cards, and set cards
- Contains: oracle text search, rarity multi-select, color identity picker, card type multi-select, oracle tags dropdown, ownership toggle, sort selector, unique cards toggle, result count
- Req: 8 (Shared Card Filtering & Sorting)

#### `ColorIdentityPicker`
- WUBRG + colorless toggle buttons
- Multi-select
- Req: 8, 2.1

#### `SearchInput`
- Debounced text input (300ms)
- Used for all search fields
- Req: 12 (Debounced input)

#### `OracleTagsDropdown`
- Dynamically populated dropdown with contextual tag counts
- Fetched from `GET /api/cards/tags` with current filter context
- Multi-select
- Req: 8

#### `PriceRangeFilter`
- Preset price range buttons (Under $1 ... $1000+)
- Req: 6.1, 2.1

### 2.3 Action Components

#### `AddToDeckModal`
- Deck selector (from user decks list), board picker (Main/Side/Commander), quantity input
- Quick-create new deck inline
- Success/failure feedback
- Req: 10

#### `PinButton`
- Toggle pin state on a card
- Persists to localStorage
- Req: 3.3

#### `CopyUuidButton`
- Copies card UUID to clipboard on click
- Req: 12 (Clipboard)

---

## 3. Page Components

### 3.1 Home Page

#### `HomePage`
- Renders: `StatCard` grid (total decks, sets, cards with prices), format legality distribution chart, recent sets list (clickable), deck price distribution histogram
- Data: `GET /api/stats/home`
- Req: 1

### 3.2 Decks Pages

#### `DeckBrowserPage`
- Search bar, filter sidebar (format, source, set, size category, price range, color identity), sort controls, paginated deck list
- Data: `GET /api/decks`
- Req: 2.1

#### `DeckListItem`
- Deck name, set, card count, colors, price, format badges
- Clickable to deck detail
- Req: 2.1

#### `DeckCreateModal`
- Form: name, format dropdown, description textarea
- Data: `POST /api/decks/create`
- Req: 2.2

#### `DeckImportModal`
- Text area for paste, file drop zone, file browse button
- Auto-populate name from filename
- Import results panel: exact/fuzzy/unresolved sections with confidence scores
- Format legality results
- "View Deck" navigation button
- Data: `POST /api/decks/import`
- Req: 2.3

#### `DeckDetailPage`
- Deck header (name, set, release date), raw JSON toggle
- Tabs or sections: Statistics, Cards
- Data: `GET /api/decks/{file}`
- Req: 2.4

#### `DeckStats`
- Total/unique card counts, price breakdown table, mana curve chart, price distribution, color distribution, type distribution (top 6), rarity distribution, format legality badges, keyword frequency breakdown
- Req: 2.4.1

#### `DeckCards`
- Sections: Commander, Main Board, Sideboard
- `CardFilterBar` for filtering/sorting
- Oracle tag counts from deck context
- `CardGrid` for each section
- Req: 2.4.2

### 3.3 Card Pages

#### `CardBrowserPage`
- `SearchInput` for name, format filter, set codes input
- `CardFilterBar` for shared filters
- `KeywordCloud` sidebar for keyword filtering
- `CardGrid` with pagination
- Requires at least one active filter
- Data: `GET /api/cards`, `GET /api/cards/keyword-frequencies`
- Req: 3.1, 3.2, 3.3

#### `CardDetailPage`
- Back button (navigation history)
- Data: `GET /api/cards/{uuid}` + `GET /api/keywords` (parallel)
- Composed of the following sub-components:
- Req: 4

#### `CardIdentity`
- Name, mana cost (rendered), type line, P/T, loyalty, defense, mana value, add-to-deck button
- Req: 4.1

#### `CardOracleText`
- Oracle text with inline mana symbols, flavor text (styled)
- Req: 4.2

#### `QuadrantRating`
- Four sliders (Developing, Ahead, Behind, Parity): 0-5 range, 0.5 increments
- Notes textarea
- Save button with status feedback
- Data: `PUT /api/cards/{uuid}/rating`
- Req: 4.3

#### `CardKeywords`
- Keywords grouped by type
- Hover tooltip with definition
- Req: 4.4

#### `CardMetadata`
- Set (linked), rarity, collector number, artist, layout, frame version, border color, finishes, flags (reprint, reserved, promo)
- Req: 4.5

#### `CardPrices`
- Table of prices by provider, finish, listing type
- Req: 4.7

#### `OtherPrintings`
- List of other printings: image thumbnail, set icon, owned indicator
- Each navigable to its detail view
- Req: 4.8

#### `DeckAppearances`
- List of decks containing this card with count
- Each navigable to deck detail
- Req: 4.9

#### `CollectionStatus`
- If not owned: "Add to Collection" button (`POST /api/cards/{uuid}/collection`)
- If owned: quantity owned, foil owned, wanted, wanted foil, condition, notes
- Req: 4.10

#### `CardRawData`
- Copy UUID button, raw JSON viewer
- Req: 4.11

### 3.4 Sets Pages

#### `SetBrowserPage`
- Search by name, type filter dropdown, sort controls, paginated set list
- Data: `GET /api/sets`
- Req: 5.1

#### `SetListItem`
- Set icon, name, type, release date, base/total size
- Clickable to set detail
- Req: 5.1

#### `SetDetailPage`
- Set header (name, type, release date, block), raw JSON toggle
- Tabs or sections: Statistics, Cards
- Data: `GET /api/sets/{code}`
- Req: 5.2

#### `SetStats`
- Base/total set size, price breakdown, rarity breakdown, keyword frequencies
- Req: 5.2.1

#### `SetCards`
- `CardFilterBar` (with collector number sort option added)
- Oracle tags dropdown (set-scoped)
- Unique cards toggle (default on)
- `CardGrid` with pagination
- Req: 5.2.2

### 3.5 Prices Pages

#### `PriceExplorerPage`
- Landing view: aggregate stats, top 10 most expensive cards chart
- Search mode: name search, sort (price high/low, name), price range filter, set filter, paginated results
- Clicking a result navigates to `CardDetailPage`
- Data: `GET /api/stats/home` (landing), `GET /api/prices` (search)
- Req: 6

#### `PriceListItem`
- Card name, average price, set code, rarity
- Req: 6.1

### 3.6 Draft Simulator Page

#### `DraftSimulatorPage`
- Pack configuration panel + pack display area + pack history sidebar
- Data: `GET /api/boosters/{set_code}`, `GET /api/boosters/{set_code}/batch`
- Req: 7

#### `PackConfigPanel`
- Set selector (searchable dropdown from `GET /api/sets`), booster type picker, pack count picker
- "Open Packs" button
- Req: 7.1

#### `PackDisplay`
- Grid of cards from opened pack: image, name, slot, rarity, foil indicator
- Each card navigable to detail
- Req: 7.2

#### `PackHistory`
- Sidebar list of opened packs in session
- Each labeled by rare/mythic pull
- Click to switch displayed pack
- Req: 7.3

### 3.7 Reference Pages

#### `ReferencePage`
- Tabs: Keywords, Glossary
- Req: 9

#### `KeywordBrowser`
- Browse all keywords with definitions
- Search by name or definition text
- Filter by category (abilities, actions, ability words)
- Result count
- Data: `GET /api/keywords`
- Req: 9.1

#### `GlossaryBrowser`
- Searchable list of MTG terms: zones, card types, formats, keywords
- Search across name, definition, category
- Req: 9.2

---

## 4. Suggested Build Order

Iterative phases, each delivering visible, testable functionality:

### Phase 1: Foundation
1. `AppLayout` + `SidebarNav` + routing
2. `SearchInput`, `Pagination`, `ManaSymbols`, `SetIcon`
3. `CardGridItem` + `CardGrid`
4. `StatCard`, `BarChart`

### Phase 2: Core Browsing
5. `HomePage` (stats + charts)
6. `SetBrowserPage` + `SetListItem`
7. `SetDetailPage` + `SetStats` + `SetCards`
8. `CardFilterBar` + `ColorIdentityPicker` + `OracleTagsDropdown`

### Phase 3: Cards
9. `CardBrowserPage` + `KeywordCloud`
10. `CardDetailPage` + all sub-components (Identity, Oracle, Metadata, Legalities, Prices, Printings)
11. `QuadrantRating`
12. `CollectionStatus`
13. `PinButton` + localStorage persistence

### Phase 4: Decks
14. `DeckBrowserPage` + `DeckListItem`
15. `DeckDetailPage` + `DeckStats` + `DeckCards`
16. `DeckCreateModal`
17. `DeckImportModal`
18. `AddToDeckModal`

### Phase 5: Prices & Draft
19. `PriceExplorerPage` + `PriceListItem`
20. `DraftSimulatorPage` + `PackConfigPanel` + `PackDisplay` + `PackHistory`

### Phase 6: Reference & Polish
21. `KeywordBrowser` + `GlossaryBrowser`
22. `RawJsonViewer` (integrate across all detail views)
23. `FormatLegalityBadges` (integrate across detail views)
24. Cross-cutting: caching, keyboard shortcuts, error states

---

## 5. Component Count Summary

| Category | Count |
|----------|-------|
| App Shell | 3 |
| Shared Display | 10 |
| Shared Filters/Input | 5 |
| Shared Actions | 3 |
| Home | 1 |
| Decks | 7 |
| Cards | 11 |
| Sets | 5 |
| Prices | 2 |
| Draft | 3 |
| Reference | 3 |
| **Total** | **53** |

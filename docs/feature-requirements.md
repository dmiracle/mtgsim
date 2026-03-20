# MTG Deck Viewer - Feature Requirements

## 1. Home Dashboard

- Display aggregate statistics: total decks, total sets, total cards with prices
- Show format legality distribution across all decks
- Show recent sets (clickable to set detail)
- Show deck price distribution

---

## 2. Decks

### 2.1 Deck Browsing
- Search decks by name
- Filter by format legality (Standard, Pioneer, Modern, Legacy, Vintage, Commander, Brawl, Historic, Pauper)
- Filter by source (Preconstructed, User created, Imported, Test)
- Filter by set
- Filter by deck size category (Land Pack, Sample, Limited, Constructed, Commander, Large, Cube)
- Filter by deck price range
- Filter by color identity (W/U/B/R/G/C)
- Sort by name, release date, or card count (ascending/descending)
- Paginated results

### 2.2 Deck Creation
- Create a new deck with name, format, and optional description

### 2.3 Deck Import
- Import decks from MTGA-format text exports
- Accept pasted text, drag-and-drop files, or file browse (.txt/.dec/.dek)
- Auto-populate deck name from filename
- Show import results: exact matches, fuzzy matches with confidence score, and unresolved cards (placeholders)
- Show format legality results after import
- Navigate to the imported deck

### 2.4 Deck Detail
- Display deck name, set, and release date
- View raw deck JSON data

#### 2.4.1 Deck Statistics
- Total cards and unique card count
- Price breakdown by source with total
- Mana curve distribution by mana value
- Price distribution
- Color distribution with counts
- Card type distribution (top 6)
- Rarity distribution
- Format legality for all major formats
- Keyword frequency breakdown: keyword abilities, keyword actions, ability words

#### 2.4.2 Deck Cards
- Cards organized by section: Commander, Main Board, Sideboard
- Full card filtering and sorting (see Section 8)
- Oracle tag counts derived from the deck's cards

---

## 3. Card Browser

### 3.1 Search & Filtering
- Search cards by name
- Filter by format
- Filter by set codes (comma-separated)
- Full card filtering and sorting (see Section 8)
- Requires at least one active filter or search term
- Paginated results

### 3.2 Keyword Filtering
- Display keyword frequencies for the current filter context, grouped by keyword abilities, keyword actions, and ability words
- Select/deselect keywords to filter card results (multi-select across groups)
- Show keyword definition and count on hover

### 3.3 Card Pinning
- Pin/unpin cards; pinned cards sort to the top of results
- Pinned state persists across sessions (localStorage)

---

## 4. Card Detail

- Navigation history: back button returns to previous card or originating view
- Navigate between related cards (other printings)

### 4.1 Card Identity
- Card name, mana cost (rendered as symbols), type line
- Power/toughness, loyalty, defense, mana value
- Add to deck action

### 4.2 Oracle Text & Flavor
- Full oracle text with mana symbols rendered inline
- Flavor text

### 4.3 Quadrant Rating
- Rate a card on four axes: Developing, Ahead, Behind, Parity (0-5, 0.5 increments)
- Add free-text rating notes
- Persist ratings via API

### 4.4 Keywords
- Display card keywords grouped by type (Keyword Abilities, Keyword Actions, Ability Words)
- Show keyword definition on hover

### 4.5 Card Metadata
- Set (navigable to set view), rarity, collector number, artist, layout, frame version, border color, finishes
- Flags: Reprint, Reserved List, Promo

### 4.6 Format Legalities
- Show legality status (Legal, Restricted, Banned, Not Legal) for all formats
- Sorted: legal first, then alphabetically

### 4.7 Prices
- All available prices by provider, finish, and listing type

### 4.8 Other Printings
- List all other printings with image, set, and owned indicator
- Navigate to any printing's detail view

### 4.9 Deck Appearances
- List all decks containing this card with count per deck
- Navigate to any listed deck

### 4.10 Collection Status
- If not in collection: add to collection
- If in collection: display quantity owned, foil owned, wanted, wanted foil, condition, notes

### 4.11 Raw Data
- Copy card UUID to clipboard
- View full card JSON

---

## 5. Sets

### 5.1 Set Browsing
- Search sets by name
- Filter by type (Core, Expansion, Masters, Draft Innovation, Commander, Starter, Promo, Token, Memorabilia)
- Sort by release date or name (ascending/descending)
- Paginated results

### 5.2 Set Detail
- Display set name, type, release date, block
- View raw set JSON

#### 5.2.1 Set Statistics
- Base set size and total size (with variants)
- Price total and breakdown by source
- Rarity breakdown
- Keyword frequency: abilities, actions, ability words

#### 5.2.2 Set Cards
- Paginated card grid
- Full card filtering and sorting (see Section 8) with additional collector number sort
- Oracle tag counts for the set context
- Unique cards toggle (default on)

---

## 6. Prices

### 6.1 Price Search
- Search cards by name
- Sort by price (highest/lowest) or name
- Filter by price range (Under $1 through $1000+)
- Filter by set
- Paginated results

### 6.2 Price Explorer Home
- Display aggregate stats: cards with prices, decks, sets
- Show the top 10 most expensive cards (navigable to card detail)

### 6.3 Price Navigation
- Selecting a price result navigates to the full card detail view

---

## 7. Draft Simulator

### 7.1 Pack Configuration
- Select a set (searchable, all sets available)
- Select booster type: Auto-detect, Play Booster, Draft Booster
- Select pack count: 1, 3, 6 (sealed), 12, 24 (box), 36 (box)

### 7.2 Pack Contents
- Display all cards in an opened pack with: name, image, slot, rarity, foil status
- Navigate to card detail from any card in the pack

### 7.3 Pack History
- Track all packs opened in the current session
- Label each pack with its rare/mythic pull
- Switch between previously opened packs

---

## 8. Shared Card Filtering & Sorting

Reusable across deck cards, card browser, and set cards:

- Filter by oracle text (free text search)
- Filter by rarity (Common, Uncommon, Rare, Mythic)
- Filter by color identity (W/U/B/R/G, multi-select)
- Filter by card type (Creature, Instant, Sorcery, Enchantment, Artifact, Planeswalker, Land)
- Filter by oracle tags (dynamically populated with contextual counts)
- Filter by ownership (All / Owned / Not Owned)
- Sort by: Name, Mana Value, Rarity, Price (each ascending/descending)
- Unique cards toggle (where applicable)
- Display count of matching results

---

## 9. Reference

### 9.1 Keyword Reference
- Browse all MTG keywords with definitions
- Search by keyword name or definition text
- Filter by category: Keyword Abilities, Keyword Actions, Ability Words
- Display count of matching keywords

### 9.2 Glossary
- Searchable reference of MTG game terms: zones, card types, formats, and all keywords
- Search across term name, definition, and category
- Accessible from any view

---

## 10. Add to Deck

- Available from card grid items and card detail view
- Select target deck from all user-created decks
- Choose board: Main Board, Sideboard, Commander
- Set quantity (1-99)
- Feedback on success/failure
- Quick-create a new deck from within the flow

---

## 11. Card Display (Shared)

Wherever a card appears in a list or grid, display:

- Card image (lazy loaded, fallback when unavailable)
- Name, mana cost, type line, oracle text
- Power/toughness
- Quantity (when > 1)
- Set (navigable to set view)
- Rarity
- Color identity symbols
- Price
- Pin/unpin action
- Add to deck action
- UUID (copyable)
- View raw JSON

---

## 12. Cross-Cutting Capabilities

- **Mana symbol rendering**: all mana symbols in costs and oracle text rendered as icons
- **Set icons**: set codes rendered with set-specific icons; hovering shows full set name
- **Clipboard**: copy card UUIDs from any card context
- **Raw JSON viewer**: collapsible JSON tree with syntax highlighting for any card, deck, or set
- **Keyboard shortcut**: Escape dismisses overlays
- **Debounced input**: all text search fields debounced (300ms)
- **Pagination**: consistent across all list/browse views
- **Caching**: set names prefetched on load; keyword categories cached from API

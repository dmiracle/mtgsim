# MTG Deck Viewer - Backend API Definition

This document defines the backend API as consumed by the frontend. Each endpoint documents its purpose, parameters, response shape, and where the frontend calls it.

Endpoints in the OpenAPI spec that are **not called** by the frontend are listed in Section 8.

---

## 1. Decks

### 1.1 List Decks

`GET /api/decks`

Returns a paginated, filterable list of decks.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | no | Search by deck name or code |
| format | string | no | Filter by format legality |
| source | string | no | Filter by source (precon, user, import, test) |
| set | string | no | Filter by set code |
| colors | string | no | Filter by color identity (e.g. "WU", "BRG") |
| card_count_min | integer | no | Minimum card count |
| card_count_max | integer | no | Maximum card count |
| price_min | number | no | Minimum deck price |
| price_max | number | no | Maximum deck price |
| sort | string | no | Sort field (default: "name") |
| order | string | no | "asc" or "desc" (default: "asc") |
| page | integer | no | Page number (default: 1) |
| limit | integer | no | Items per page (default: 50, max: 100) |

**Response:** `DeckListResponse`
- `data`: array of `DeckSummary` — file, name, code, deck_type, card_count, colors, price, release_date, legality, source
- `pagination`: page, limit, total, pages
- `filters`: available sets, formats, color combinations

**Frontend logic:** The frontend builds filter params from sidebar controls and sends them all in one request. The `filters.sets` from the response populates the set filter dropdown on first load.

> **In use:** index.html line 2029

---

### 1.2 Get Deck Detail

`GET /api/decks/{file}`

Returns full deck data including all cards and computed statistics.

**Path params:** `file` (string) — deck file identifier

**Response:** `DeckDetail`
- `meta`: name, file, code, release_date, description, format, source
- `legality`: boolean per format (standard, pioneer, modern, legacy, vintage, commander, brawl, historic, pauper)
- `colors`: array of color codes
- `price`: total + breakdown by source (tcgplayer, cardkingdom, cardsphere, cardmarket, mtgo)
- `commander`, `main_board`, `side_board`: arrays of `DeckCard` — uuid, name, count, board, mana_cost, mana_value, type, types, colors, rarity, tags, text, price, image_url, owns_enough, owned_count, missing_count
- `stats`:
  - total_cards, unique_cards
  - mana_curve: dict of mana_value → count
  - type_distribution, rarity_distribution, color_distribution: dict of label → count
  - price_histogram: array of {range, count}
  - keywords: {ability_words, keyword_abilities, keyword_actions} each dict of keyword → count

**Frontend logic:** The frontend stores all deck cards in `window._deckCards` for client-side filtering/sorting. Statistics are rendered as visualizations (mana curve chart, histograms, word clouds). Tags are extracted client-side from the card data for the tag filter dropdown.

> **In use:** index.html line 2114

---

### 1.3 Create Deck

`POST /api/decks/create`

Creates a new empty user deck.

**Request body:** `DeckCreateRequest`
- `name`: string (required)
- `format`: string | null
- `description`: string | null

**Response:** `UserDeckResponse` — id, name, description, format, source, card_count

**Frontend logic:** Called from both the "New Deck" modal (with all fields) and the quick-create flow inside the deck picker (name only). On success, the deck list is refreshed and the new deck is loaded.

> **In use:** index.html line 4044 (quick-create), line 4078 (full create modal)

---

### 1.4 Import Deck

`POST /api/decks/import`

Imports a deck from MTGA-format text. The backend parses the text, resolves card names (exact and fuzzy matching), creates placeholder cards for unresolved names, and checks format legality.

**Request body:** `DeckImportRequest`
- `text`: string (required) — MTGA export text
- `name`: string (required) — deck name

**Response:** (untyped object)
- `deck_id`: identifier for the created deck
- `deck_name`: string
- `total_cards`: integer
- `resolved`: array of {name, matched_name, match_type ("exact"|"fuzzy"|"created"), match_score, count}
- `legality`: array of {format, legal, reason}

**Frontend logic:** The frontend displays import results categorized by match type. Fuzzy matches show the confidence percentage. Unresolved cards are flagged as placeholders. A "View Deck" button navigates to the imported deck via `loadDeck(result.deck_id)`.

> **In use:** index.html line 3924

---

### 1.5 List User Decks

`GET /api/decks/user/list`

Returns a lightweight list of all user-created decks, used to populate the deck picker when adding cards to decks.

**Response:** array of `UserDeckResponse` — id, name, description, format, source, card_count

> **In use:** index.html line 3978

---

### 1.6 Add Card to Deck

`POST /api/decks/{deck_id}/cards`

Adds a card to a user deck.

**Path params:** `deck_id` (integer)

**Request body:** `AddCardRequest`
- `card_uuid`: string (required)
- `count`: integer (default: 1)
- `board`: string (default: "main") — "main", "side", or "commander"

**Frontend logic:** Called from the deck picker modal. On success, the user deck cache is invalidated and the modal auto-closes after a delay.

> **In use:** index.html line 4024

---

## 2. Cards

### 2.1 Search Cards

`GET /api/cards`

Searches and filters cards with pagination.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | no | Search by card name |
| text | string | no | Filter by oracle text |
| sets | string | no | Comma-separated set codes |
| rarity | string | no | Filter by rarity |
| type | string | no | Filter by card type |
| colors | string | no | Filter by color identity |
| format | string | no | Filter by format legality |
| keywords | string | no | Comma-separated keywords |
| tags | string | no | Comma-separated oracle tags |
| owns | boolean | no | Filter by ownership |
| unique | boolean | no | One printing per card name (default: false) |
| sort | string | no | Sort field (default: "name") |
| order | string | no | "asc" or "desc" (default: "asc") |
| page | integer | no | Page number (default: 1) |
| limit | integer | no | Items per page (default: 50, max: 100) |

**Response:** `CardListResponse`
- `data`: array of `CardSummary` — uuid, name, type, mana_cost, mana_value, rarity, set_code, color_identity, tags, text, price, image_url, owns, wants, total_owned, total_wanted
- `pagination`: page, limit, total, pages

**Frontend logic:** The frontend requires at least one active filter before sending this request. Pinned cards (stored in localStorage) are re-sorted to the top client-side after the response arrives.

> **In use:** index.html line 2531

---

### 2.2 Get Card Detail

`GET /api/cards/{uuid}`

Returns full card data including legalities, all prices, other printings, deck appearances, collection status, and quadrant rating.

**Path params:** `uuid` (string)

**Response:** `CardDetail`
- Identity: uuid, name, mana_cost, mana_value, type, types, subtypes, supertypes, text, flavor_text, rarity, set_code, set_name, color_identity, colors, keywords, tags, power, toughness, loyalty, defense
- Metadata: artist, number, layout, finishes, border_color, frame_version, is_reprint, is_reserved, is_promo
- image_url
- legalities: dict of format → status string
- all_prices: array of {provider, finish, listing_type, price}
- appears_in_decks: array of {file, name, count}
- other_printings: array of {set_code, set_name, uuid, rarity, number, image_url, owns, total_owned}
- Collection: owns, wants, total_owned, total_wanted, collection (quantity_owned, quantity_owned_foil, quantity_wanted, quantity_wanted_foil, condition, notes)
- quadrant_rating: developing, ahead, behind, parity, notes

**Frontend logic:** This is the primary data source for the card detail view. The response populates the set name cache for any set codes encountered. Other printings are navigable (calling this same endpoint for a different uuid). The keyword type cache is also ensured on this call (parallel fetch to `/keywords`).

> **In use:** card-detail.js line 16

---

### 2.3 Get Card Tags

`GET /api/cards/tags`

Returns available oracle tags with card counts, optionally filtered by context.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| set | string | no | Filter by set code |
| format | string | no | Filter by format legality |
| colors | string | no | Filter by color identity |
| type | string | no | Filter by card type |
| rarity | string | no | Filter by rarity |

**Response:** array of {tag, count}

**Frontend logic:** Called to populate the oracle tags dropdown in the shared card filter bar. Counts are contextual — when viewing a set, tags reflect that set; when browsing cards, tags reflect the active format/set/color filters.

> **In use:** index.html line 3260

---

### 2.4 Get Keyword Frequencies

`GET /api/cards/keyword-frequencies`

Returns keyword frequency maps for a filtered card population, categorized by keyword type.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| format | string | no | Filter by format legality |
| sets | string | no | Comma-separated set codes |
| rarity | string | no | Filter by rarity |
| colors | string | no | Filter by color identity |
| type | string | no | Filter by card type |

**Response:** (untyped object)
- `keyword_abilities`: dict of keyword → count
- `keyword_actions`: dict of keyword → count
- `ability_words`: dict of keyword → count

**Frontend logic:** Called in the card browser tab whenever filters change. The three frequency maps are rendered as interactive word clouds. Clicking a keyword in the cloud adds it to the `selectedKeywords` array and triggers a new card search with those keywords as a filter.

> **In use:** index.html line 2423

---

### 2.5 Add Card to Collection

`POST /api/cards/{uuid}/collection`

Adds a card to the user's collection with default quantities.

**Path params:** `uuid` (string)

**Response:** `CollectionResponse` — success, message, card

**Frontend logic:** Called from the card detail view "Add to Collection" button with an empty body (defaults to 1 owned). On success, the card detail view is refreshed to show the updated collection status.

> **In use:** card-detail.js line 334

---

### 2.6 Save Quadrant Rating

`PUT /api/cards/{uuid}/rating`

Saves a quadrant theory rating for a card.

**Path params:** `uuid` (string)

**Request body:** `QuadrantRatingRequest`
- `developing`: number | null (0-5, 0.5 increments; null if 0)
- `ahead`: number | null
- `behind`: number | null
- `parity`: number | null
- `notes`: string | null

**Response:** `QuadrantRatingResponse` — same shape as request

**Frontend logic:** Called when the user clicks "Save Rating" or changes the notes field. Slider values of 0 are sent as null. The UI shows save status feedback (Saving → Saved / Error).

> **In use:** card-detail.js line 427

---

## 3. Sets

### 3.1 List Sets

`GET /api/sets`

Returns a paginated, filterable list of sets.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | no | Search by set name or code |
| type | string | no | Filter by set type |
| sort | string | no | Sort field (default: "release_date") |
| order | string | no | "asc" or "desc" (default: "desc") |
| page | integer | no | Page number (default: 1) |
| limit | integer | no | Items per page (default: 50, max: 100) |

**Response:** `SetListResponse`
- `data`: array of `SetSummary` — code, name, type, release_date, base_set_size, total_set_size, block, keyrune_code, collection_stats
- `pagination`: page, limit, total, pages
- `filters`: available types, blocks

**Frontend logic:** Called in multiple contexts:
1. Sets tab browsing — with user's search/filter/sort params
2. Price set filter population — paginated fetch of all sets (limit:100, sorted by release_date desc)
3. Draft set population — same paginated fetch of all sets
4. Set name prefetch on app load — paginated fetch of all sets (limit:100) to populate the `setNameCache` for set icon tooltips

> **In use:** index.html lines 2599, 2994, 3006, 4118, 4263

---

### 3.2 Get Set Detail

`GET /api/sets/{code}`

Returns full set data including statistics and a paginated, filterable card list.

**Path params:** `code` (string) — set code

**Parameters (card filtering):**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| rarity | string | no | Filter cards by rarity |
| colors | string | no | Filter cards by color identity |
| type | string | no | Filter cards by type |
| text | string | no | Filter cards by oracle text |
| tags | string | no | Filter by oracle tags |
| owns | boolean | no | Filter by ownership |
| wants | boolean | no | Filter by wanted status |
| sort | string | no | Card sort field (default: "number") |
| order | string | no | "asc" or "desc" (default: "asc") |
| unique | boolean | no | One printing per card name (default: false) |
| card_page | integer | no | Card page number (default: 1) |
| card_limit | integer | no | Cards per page (default: 50, max: 100) |

**Response:** `SetDetail`
- `meta`: code, name, type, release_date, base_set_size, total_set_size, block
- `stats`:
  - rarity_count: dict of rarity → count
  - price: total + breakdown by source
  - keywords: {ability_words, keyword_abilities, keyword_actions} each dict → count
- `cards`:
  - data: array of `SetCard` — uuid, name, mana_cost, mana_value, type, rarity, color_identity, colors, power, toughness, number, text, price, image_url, owns, wants, total_owned, total_wanted
  - pagination: page, limit, total, pages

**Frontend logic:** On initial load, all stats and the first page of cards are rendered. When the user changes card filters or pages, the endpoint is re-called with `_cardsOnly` flag (frontend-only) so only the card grid is re-rendered — stats stay in place. The `unique` parameter defaults to true in the frontend.

> **In use:** index.html line 2684

---

## 4. Prices

### 4.1 Search Prices

`GET /api/prices`

Searches card price data with pagination.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | no | Search by card name |
| set | string | no | Filter by set code |
| price_min | number | no | Minimum price |
| price_max | number | no | Maximum price |
| sort | string | no | Sort field (default: "average_usd") |
| order | string | no | "asc" or "desc" (default: "desc") |
| page | integer | no | Page number (default: 1) |
| limit | integer | no | Items per page (default: 50, max: 100) |

**Response:** `PriceListResponse`
- `data`: array of `PriceSummary` — uuid, name, set_code, rarity, image_url, prices (by source), average_usd
- `pagination`: page, limit, total, pages
- `meta`: last_updated, total_cards_with_prices

**Frontend logic:** The price list in the sidebar shows name, average_usd, set_code, and rarity. Clicking a result navigates to the full card detail view (not the price detail endpoint).

> **In use:** index.html line 2867

---

## 5. Statistics

### 5.1 Home Stats

`GET /api/stats/home`

Returns aggregate statistics for the home dashboard and price explorer.

**Response:** `HomeStats`
- `total_decks`: integer
- `total_sets`: integer
- `total_cards`: integer
- `total_cards_with_prices`: integer
- `format_distribution`: dict of format → deck count
- `price_histogram`: array of {range, count}
- `recent_sets`: array of {code, name, release_date}
- `most_expensive_cards`: array of {name, price, set_code}

**Frontend logic:** Called in two contexts:
1. Home screen — renders all stats, format distribution, recent sets, and price histogram
2. Price explorer landing — renders aggregate counts and the most expensive cards chart

> **In use:** index.html lines 3027, 3090

---

## 6. Boosters

### 6.1 Open Single Booster

`GET /api/boosters/{set_code}`

Generates a single random booster pack.

**Path params:** `set_code` (string)

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | no | "play" or "draft" (auto-detects if omitted) |

**Response:** `BoosterPack`
- `set_code`, `set_name`, `booster_type`
- `cards`: array of `BoosterCard` — uuid, name, set_code, rarity, slot, number, is_foil, image_url, mana_cost, mana_value, type_line, colors

**Frontend logic:** Called when pack count is 1. The single pack is wrapped in an array and treated the same as batch results.

> **In use:** index.html line 4178

---

### 6.2 Open Multiple Boosters

`GET /api/boosters/{set_code}/batch`

Generates multiple booster packs.

**Path params:** `set_code` (string)

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| count | integer | no | Number of packs (default: 6, max: 36) |
| type | string | no | "play" or "draft" (auto-detects if omitted) |

**Response:** array of `BoosterPack`

**Frontend logic:** Called when pack count > 1. Results are stored in `draftOpenedPacks`. The pack history sidebar shows each pack labeled by its rare/mythic pull. Clicking any card navigates to the card detail view.

> **In use:** index.html line 4183

---

## 7. Keywords

### 7.1 Get Keywords

`GET /api/keywords`

Returns all MTG keywords grouped by category.

**Response:** `KeywordsResponse`
- `keyword_abilities`: array of {term, definition}
- `keyword_actions`: array of {term, definition}
- `ability_words`: array of {term, definition}

**Frontend logic:** Called in two contexts:
1. Card detail view — called in parallel with the card fetch to build the `keywordTypeCache` (maps keyword → category) used for grouping keywords on card display
2. Reference tab — populates the keyword browser list, merged with local definitions from `keyword-definitions.js`

> **In use:** index.html lines 1905, 3722

---

## 8. API Endpoints Not Used by Frontend

The following endpoints exist in the OpenAPI spec but have **no corresponding call** in the frontend code:

| Method | Path | Description |
|--------|------|-------------|
| DELETE | `/api/decks/{deck_id}/cards/{card_uuid}` | Remove card from deck |
| DELETE | `/api/decks/{deck_id}` | Delete a user deck |
| GET | `/api/decks/{file}/raw` | Get raw deck JSON |
| GET | `/api/sets/{code}/raw` | Get raw set JSON |
| GET | `/api/prices/{uuid}` | Get detailed price data for a card |
| DELETE | `/api/cards/{uuid}/collection` | Remove card from collection |
| GET | `/api/cards/{uuid}/rating` | Get quadrant rating (read-only) |
| GET | `/api/stats/decks` | Aggregate deck statistics |
| GET | `/api/stats/corpus-wordfreq` | Corpus word frequencies |
| GET | `/api/keywords/search` | Search keywords by partial match |
| GET | `/api/keywords/stats` | Keyword count statistics |
| GET | `/api/keywords/formats` | Format information with descriptions |
| GET | `/` | Redirect to webapp |
| GET | `/api` | API info endpoint |
| GET | `/health` | Health check |
| GET | `/app` | Serve webapp |

**Notes on unused endpoints:**
- The frontend renders raw JSON for decks/sets/cards using data already fetched from the detail endpoints — it does **not** call the `/raw` endpoints.
- The frontend has no UI for removing cards from decks, deleting decks, or removing cards from collection.
- `GET /api/prices/{uuid}` is unused because clicking a price result navigates to the card detail view (`/api/cards/{uuid}`) instead.
- `GET /api/cards/{uuid}/rating` is unused because the rating comes embedded in the card detail response.
- The keyword search, stats, and formats endpoints have no corresponding UI in the frontend.
- The stats/decks and corpus-wordfreq endpoints appear to be backend-only or intended for future use.

---

## 9. API Parameters Not Used by Frontend

These parameters exist on endpoints the frontend **does** call, but the frontend never sends them:

| Endpoint | Unused Parameter | Notes |
|----------|-----------------|-------|
| `GET /api/decks` | `type` | Deck type (60, 100) — frontend uses card_count_min/max ranges instead |
| `GET /api/sets` | `block` | Block filter exists in API but no UI control |
| `GET /api/sets` | `has_owned_cards` | Ownership filter for sets not exposed |
| `GET /api/cards` | `set` (singular) | Frontend uses `sets` (plural, comma-separated) instead |
| `GET /api/cards` | `price_min`, `price_max` | Price range filtering on cards not exposed |
| `GET /api/cards` | `wants` | Wants filter not exposed (only owns is used) |
| `GET /api/sets/{code}` | `wants` | Wants filter for set cards not exposed |
| `GET /api/prices` | `rarity` | Rarity filter for prices not exposed |

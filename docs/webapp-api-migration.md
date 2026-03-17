# Webapp to API Migration

This document indexes all webapp data retrievals and maps them to existing API endpoints, identifying gaps that need to be addressed.

## Executive Summary

| Generator | Can Use API? | Gaps |
|-----------|--------------|------|
| `generate_index.py` (decks) | **Partial** | Missing `format_legalities` in deck list response |
| `generate_card_index.py` (cards) | **No** | Needs bulk export endpoint (paginated API insufficient for full index) |
| `generate_set_index.py` (sets) | **Yes** | No gaps |

---

## 1. Deck Index Generator (`generate_index.py`)

### Current Data Retrieval

| Data Retrieved | Source | Fields |
|----------------|--------|--------|
| Deck files | `resources/AllDeckFiles/*.json` | Raw JSON files |
| Set release dates | `resources/AllSetFiles/*.json` | `code`, `releaseDate` |

### Output Fields Per Deck

```json
{
  "file": "DeckName_ABC.json",
  "name": "Deck Name",
  "code": "ABC",
  "cardCount": 100,
  "legality": {
    "standard": true,
    "pioneer": false,
    "modern": true,
    "legacy": true,
    "vintage": true,
    "commander": true,
    "brawl": false,
    "historic": true,
    "pauper": false
  },
  "releaseDate": "2024-01-01"
}
```

### API Mapping: `GET /api/decks`

The API endpoint currently returns:

```json
{
  "uuid": "...",
  "file": "DeckName_ABC.json",
  "name": "Deck Name",
  "code": "ABC",
  "type": "Commander Deck",
  "release_date": "2024-01-01",
  "main_board_count": 99,
  "side_board_count": 0,
  "commander_count": 1,
  "card_count": 100,
  "colors": ["W", "U", "B"],
  "price": 150.00,
  "source": "precon"
}
```

### Field Mapping

| Webapp Field | API Field | Status |
|--------------|-----------|--------|
| `file` | `file` | ✅ Available |
| `name` | `name` | ✅ Available (from DB, better quality) |
| `code` | `code` | ✅ Available |
| `cardCount` | `card_count` | ✅ Available |
| `releaseDate` | `release_date` | ✅ Available |
| `legality` | — | ❌ **Missing** |

### Gap: Format Legalities

The API needs to return a `format_legalities` dict showing which formats each deck is legal in.

**Required addition to response:**
```json
{
  "format_legalities": {
    "standard": true,
    "pioneer": false,
    "modern": true,
    "legacy": true,
    "vintage": true,
    "commander": true,
    "brawl": false,
    "historic": true,
    "pauper": false
  }
}
```

---

## 2. Card Index Generator (`generate_card_index.py`)

### Current Data Retrieval

| Data Retrieved | Source | Query |
|----------------|--------|-------|
| All English cards | `resources/AllPrintings.sqlite` | JOIN `cards` + `cardIdentifiers` |

### SQL Query Used

```sql
SELECT c.uuid, c.name, c.type, c.manaCost, c.rarity,
       c.setCode, c.power, c.toughness, c.colorIdentity, i.scryfallId
FROM cards c
LEFT JOIN cardIdentifiers i ON c.uuid = i.uuid
WHERE c.language = 'English' OR c.language IS NULL
```

### Output Format (Compressed Keys)

```json
{
  "uuid-here": {
    "n": "Card Name",
    "t": "Creature — Human Wizard",
    "m": "{1}{U}{U}",
    "r": "rare",
    "s": "ABC",
    "p": "2",
    "o": "3",
    "c": ["U"],
    "i": "scryfall-id-here"
  }
}
```

Key mapping:
- `n` → name
- `t` → type
- `m` → manaCost
- `r` → rarity
- `s` → setCode
- `p` → power
- `o` → toughness
- `c` → colorIdentity
- `i` → scryfallId

### API Mapping: `GET /api/cards`

The API endpoint returns (per card):

```json
{
  "uuid": "...",
  "name": "Card Name",
  "mana_cost": "{1}{U}{U}",
  "mana_value": 3.0,
  "type": "Creature — Human Wizard",
  "types": ["Creature"],
  "subtypes": ["Human", "Wizard"],
  "supertypes": [],
  "oracle_text": "...",
  "flavor_text": "...",
  "power": "2",
  "toughness": "3",
  "loyalty": null,
  "defense": null,
  "colors": ["U"],
  "color_identity": ["U"],
  "keywords": ["Flying"],
  "rarity": "rare",
  "set_code": "ABC",
  "set_name": "Set Name",
  "number": "123",
  "artist": "Artist Name",
  "layout": "normal",
  "border_color": "black",
  "frame_version": "2015",
  "has_foil": true,
  "has_non_foil": true,
  "is_reprint": false,
  "is_reserved": false,
  "is_promo": false,
  "image_url": "https://cards.scryfall.io/...",
  "prices": {...},
  "owns": false,
  "wants": false,
  "total_owned": 0,
  "total_wanted": 0,
  "collection": null
}
```

### Field Mapping

| Webapp Field | API Field | Status |
|--------------|-----------|--------|
| `n` (name) | `name` | ✅ Available |
| `t` (type) | `type` | ✅ Available |
| `m` (manaCost) | `mana_cost` | ✅ Available |
| `r` (rarity) | `rarity` | ✅ Available |
| `s` (setCode) | `set_code` | ✅ Available |
| `p` (power) | `power` | ✅ Available |
| `o` (toughness) | `toughness` | ✅ Available |
| `c` (colorIdentity) | `color_identity` | ✅ Available |
| `i` (scryfallId) | `image_url` | ✅ Available (as full URL) |

### Gap: Bulk Export

All individual fields are available, but the webapp generates a **full card index** (~100k+ cards) as a static JSON file. The API is paginated (max 100 per page).

**Challenge:** The webapp needs either:
1. A bulk export endpoint returning all cards
2. Or continue static generation from the unified DB

### Required New Endpoint: `GET /api/cards/export`

Returns all cards in compressed format for static index generation:

```json
{
  "cards": {
    "uuid1": {"n": "Card Name", "t": "Type", "m": "{1}{U}", ...},
    "uuid2": {...}
  },
  "count": 100000,
  "generated_at": "2024-01-01T00:00:00Z"
}
```

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | `full` (all fields) or `minimal` (compressed keys) |
| `language` | string | Filter by language (default: `English`) |

---

## 3. Set Index Generator (`generate_set_index.py`)

### Current Data Retrieval

| Data Retrieved | Source |
|----------------|--------|
| All set metadata | `resources/AllSetFiles/*.json` |

### Output Fields Per Set

```json
{
  "code": "ABC",
  "name": "Set Name",
  "type": "expansion",
  "releaseDate": "2024-01-01",
  "baseSetSize": 250,
  "totalSetSize": 300,
  "block": "Block Name",
  "keyruneCode": "abc"
}
```

### API Mapping: `GET /api/sets`

The API endpoint returns:

```json
{
  "code": "ABC",
  "name": "Set Name",
  "type": "expansion",
  "release_date": "2024-01-01",
  "base_set_size": 250,
  "total_set_size": 300,
  "block": "Block Name",
  "parent_code": null,
  "keyrune_code": "abc",
  "is_foil_only": false,
  "is_online_only": false,
  "is_partial_preview": false,
  "collection_stats": {
    "total_cards": 300,
    "owned_cards": 50,
    "owned_percentage": 16.7,
    "wanted_cards": 10
  }
}
```

### Field Mapping

| Webapp Field | API Field | Status |
|--------------|-----------|--------|
| `code` | `code` | ✅ Available |
| `name` | `name` | ✅ Available |
| `type` | `type` | ✅ Available |
| `releaseDate` | `release_date` | ✅ Available |
| `baseSetSize` | `base_set_size` | ✅ Available |
| `totalSetSize` | `total_set_size` | ✅ Available |
| `block` | `block` | ✅ Available |
| `keyruneCode` | `keyrune_code` | ✅ Available |

### Gap: None

All required fields are available via the existing API. The set index generator can be converted to use the API directly.

---

## Required API Changes

### 1. Add `format_legalities` to Deck List Response

**Files to modify:**
- `src/mtgsim/api/data/decks.py`
- `src/mtgsim/api/models/deck.py`

**Implementation:**
Calculate format legality by checking all cards in deck against their individual legalities.

### 2. Add Bulk Card Export Endpoint

**Files to create/modify:**
- `src/mtgsim/api/routers/cards.py` - add new route
- `src/mtgsim/api/data/cards.py` - add export method
- `src/mtgsim/api/services/card_service.py` - add export service method

**Endpoint specification:**
```
GET /api/cards/export
```

**Query parameters:**
- `format`: `minimal` | `full` (default: `minimal`)
- `language`: string (default: `English`)

**Response:**
```json
{
  "cards": { ... },
  "count": 100000,
  "generated_at": "2024-01-01T00:00:00Z"
}
```

---

## Migration Plan

### Phase 1: API Changes
1. Add `format_legalities` to deck list endpoint
2. Add `/api/cards/export` bulk endpoint

### Phase 2: Update Generators
1. Update `generate_set_index.py` to use `GET /api/sets`
2. Update `generate_index.py` to use `GET /api/decks`
3. Update `generate_card_index.py` to use `GET /api/cards/export`

### Phase 3: Cleanup
1. Remove direct database access from webapp generators
2. Update documentation
3. Consider deprecating static JSON generation in favor of dynamic API calls

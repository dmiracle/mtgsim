# Sync Methods and Table Documentation

This document catalogs all sync methods, the tables they create/populate, and their data sources.

## Database Overview

**Single unified database:** `~/.mtgsim/mtgsim.sqlite`

All path aliases point to the same file:
- `DB_PATH` = `~/.mtgsim/mtgsim.sqlite`
- `USER_DB_PATH` = same
- `DOMAIN_DB_PATH` = same
- `MERGED_DB_PATH` = same

---

## MTGJSON Source Files

Downloaded to `~/.mtgsim/reference/mtgjson/`:

| File | URL | Contents |
|------|-----|----------|
| `AllPrintings.sqlite` | `mtgjson.com/api/v5/AllPrintings.sqlite.xz` | Cards, Sets, Identifiers, Legalities |
| `AllPricesToday.sqlite` | `mtgjson.com/api/v5/AllPricesToday.sqlite.xz` | Current price data |
| `AllDeckFiles/` | `mtgjson.com/api/v5/AllDeckFiles.tar.xz` | Preconstructed deck JSON files |

---

## Sync Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    mtgsim db sync                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Download MTGJSON files (if needed)                          │
│     ├── AllPrintings.sqlite.xz → extract                        │
│     ├── AllPricesToday.sqlite.xz → extract                      │
│     └── AllDeckFiles.tar.xz → extract                           │
│                                                                  │
│  2. sync_sets(AllPrintings.sqlite)                              │
│     └── mj_set                                                  │
│                                                                  │
│  3. sync_cards(AllPrintings.sqlite)                             │
│     ├── mj_card                                                 │
│     ├── mj_card_identifier                                      │
│     └── mj_card_legality                                        │
│                                                                  │
│  4. sync_prices(AllPricesToday.sqlite)                          │
│     └── mj_card_price                                           │
│                                                                  │
│  5. sync_decks(AllDeckFiles/)                                   │
│     ├── mj_deck                                                 │
│     └── mj_deck_card                                            │
│                                                                  │
│  6. compute_corpus_wordfreq()                                   │
│     └── ~/.mtgsim/corpus_wordfreq.json                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sync Methods Detail

### `sync_all(force: bool)`
**File:** `src/mtgsim/sync/unified.py`
**Command:** `mtgsim db sync`

Orchestrates the full sync pipeline. Downloads MTGJSON files if needed, then calls individual sync functions.

---

### `sync_sets(source_db: Path)`
**File:** `src/mtgsim/sync/unified.py:91`

| Target Table | Source Table | Source DB |
|--------------|--------------|-----------|
| `mj_set` | `sets` | `AllPrintings.sqlite` |

**Source query:**
```sql
SELECT code, name, type, releaseDate, baseSetSize, totalSetSize,
       block, parentCode, keyruneCode,
       isFoilOnly, isOnlineOnly, isPartialPreview
FROM sets
```

**Field mapping:**

| Source Column | Target Column |
|---------------|---------------|
| `code` | `code` (PK) |
| `name` | `name` |
| `type` | `type` |
| `releaseDate` | `release_date` |
| `baseSetSize` | `base_set_size` |
| `totalSetSize` | `total_set_size` |
| `block` | `block` |
| `parentCode` | `parent_code` |
| `keyruneCode` | `keyrune_code` |
| `isFoilOnly` | `is_foil_only` |
| `isOnlineOnly` | `is_online_only` |
| `isPartialPreview` | `is_partial_preview` |

---

### `sync_cards(source_db: Path)`
**File:** `src/mtgsim/sync/unified.py:140`

| Target Table | Source Table | Source DB |
|--------------|--------------|-----------|
| `mj_card` | `cards` | `AllPrintings.sqlite` |

**Source query:**
```sql
SELECT uuid, name, setCode, manaCost, manaValue, type, text,
       power, toughness, loyalty, defense, rarity, number, artist,
       layout, borderColor, frameVersion,
       colors, colorIdentity, types, subtypes, supertypes, keywords,
       hasFoil, hasNonFoil, isReprint, isReserved, isPromo, flavorText
FROM cards
```

**Field mapping:**

| Source Column | Target Column | Notes |
|---------------|---------------|-------|
| `uuid` | `uuid` (PK) | |
| `name` | `name` | Indexed |
| `setCode` | `set_code` | Indexed |
| `manaCost` | `mana_cost` | |
| `manaValue` | `mana_value` | |
| `type` | `type_line` | |
| `text` | `oracle_text` | |
| `power` | `power` | |
| `toughness` | `toughness` | |
| `loyalty` | `loyalty` | |
| `defense` | `defense` | |
| `rarity` | `rarity` | Indexed |
| `number` | `number` | |
| `artist` | `artist` | |
| `layout` | `layout` | |
| `borderColor` | `border_color` | |
| `frameVersion` | `frame_version` | |
| `flavorText` | `flavor_text` | |
| `colors` | `colors` | JSON array |
| `colorIdentity` | `color_identity` | JSON array |
| `types` | `types` | JSON array |
| `subtypes` | `subtypes` | JSON array |
| `supertypes` | `supertypes` | JSON array |
| `keywords` | `keywords` | JSON array |
| `hasFoil` | `has_foil` | Boolean |
| `hasNonFoil` | `has_non_foil` | Boolean |
| `isReprint` | `is_reprint` | Boolean |
| `isReserved` | `is_reserved` | Boolean |
| `isPromo` | `is_promo` | Boolean |

---

### `_sync_card_identifiers(conn, engine)`
**File:** `src/mtgsim/sync/unified.py:222`

| Target Table | Source Table | Source DB |
|--------------|--------------|-----------|
| `mj_card_identifier` | `cardIdentifiers` | `AllPrintings.sqlite` |

**Source query:**
```sql
SELECT uuid, scryfallId, scryfallOracleId, scryfallIllustrationId,
       tcgplayerProductId, tcgplayerEtchedProductId,
       mcmId, cardsphereId,
       mtgoId, mtgoFoilId, mtgjsonV4Id, multiverseId
FROM cardIdentifiers
```

**Field mapping:**

| Source Column | Target Column |
|---------------|---------------|
| `uuid` | `card_uuid` (FK) |
| `scryfallId` | `scryfall_id` |
| `scryfallOracleId` | `scryfall_oracle_id` |
| `scryfallIllustrationId` | `scryfall_illustration_id` |
| `tcgplayerProductId` | `tcgplayer_product_id` |
| `tcgplayerEtchedProductId` | `tcgplayer_etched_product_id` |
| `mcmId` | `cardmarket_id` |
| `cardsphereId` | `cardsphere_id` |
| `mtgoId` | `mtgo_id` |
| `mtgoFoilId` | `mtgo_foil_id` |
| `mtgjsonV4Id` | `mtgjson_v4_id` |
| `multiverseId` | `multiverse_id` |

---

### `_sync_card_legalities(conn, engine)`
**File:** `src/mtgsim/sync/unified.py:263`

| Target Table | Source Table | Source DB |
|--------------|--------------|-----------|
| `mj_card_legality` | `cardLegalities` | `AllPrintings.sqlite` |

**Source schema:** Dynamic columns per format (standard, modern, legacy, etc.)

**Target schema:** Normalized rows with `card_uuid`, `format`, `status`

Each row in source with format columns becomes multiple rows in target:
```
Source: uuid=X, standard=Legal, modern=Banned, legacy=Legal
Target:
  - card_uuid=X, format=standard, status=Legal
  - card_uuid=X, format=modern, status=Banned
  - card_uuid=X, format=legacy, status=Legal
```

---

### `sync_prices(source_db: Path)`
**File:** `src/mtgsim/sync/unified.py:297`

| Target Table | Source Table | Source DB |
|--------------|--------------|-----------|
| `mj_card_price` | `cardPrices` | `AllPricesToday.sqlite` |

**Source query:**
```sql
SELECT uuid, priceProvider, providerListing, cardFinish, currency, date, price
FROM cardPrices
WHERE price IS NOT NULL
```

**Field mapping:**

| Source Column | Target Column |
|---------------|---------------|
| `uuid` | `card_uuid` (FK) |
| `priceProvider` | `provider` |
| `providerListing` | `listing_type` |
| `cardFinish` | `finish` |
| `currency` | `currency` |
| `price` | `price` |
| `date` | `updated_at` |

---

### `sync_decks(deck_dir: Path)`
**File:** `src/mtgsim/sync/unified.py:348`

| Target Table | Source | Source Format |
|--------------|--------|---------------|
| `mj_deck` | `AllDeckFiles/*.json` | JSON files |
| `mj_deck_card` | `AllDeckFiles/*.json` | JSON files |

**Deck JSON structure:**
```json
{
  "data": {
    "name": "Deck Name",
    "code": "SET",
    "type": "Commander Deck",
    "releaseDate": "2024-01-01",
    "mainBoard": [{"name": "...", "count": 1, "uuid": "...", ...}],
    "sideBoard": [...],
    "commander": [...]
  }
}
```

**mj_deck field mapping:**

| Source Field | Target Column |
|--------------|---------------|
| (generated) | `uuid` (PK) |
| (filename) | `file_name` |
| `data.name` | `name` |
| `data.code` | `code` |
| `data.type` | `type` |
| `data.releaseDate` | `release_date` |
| (calculated) | `main_board_count` |
| (calculated) | `side_board_count` |
| (calculated) | `commander_count` |

**mj_deck_card field mapping:**

| Source Field | Target Column |
|--------------|---------------|
| (generated) | `id` (PK) |
| (parent deck) | `deck_uuid` (FK) |
| `card.uuid` | `card_uuid` |
| `card.name` | `name` |
| (board name) | `board` |
| `card.count` | `count` |
| `card.manaCost` | `mana_cost` |
| `card.manaValue` | `mana_value` |
| `card.colors` | `colors` |
| `card.types` | `types` |

---

### `compute_corpus_wordfreq()`
**File:** `src/mtgsim/sync/unified.py:425`

**Input:** `mj_card.oracle_text` (all cards)
**Output:** `~/.mtgsim/corpus_wordfreq.json`

Computes word frequencies from all card oracle text for wordcloud baseline calculation.

---

## Complete Table Inventory

### Reference Tables (Synced from MTGJSON)

| Table | Primary Key | Sync Method | Source |
|-------|-------------|-------------|--------|
| `mj_set` | `code` | `sync_sets()` | `AllPrintings.sqlite:sets` |
| `mj_card` | `uuid` | `sync_cards()` | `AllPrintings.sqlite:cards` |
| `mj_card_identifier` | `id` | `sync_cards()` | `AllPrintings.sqlite:cardIdentifiers` |
| `mj_card_legality` | `id` | `sync_cards()` | `AllPrintings.sqlite:cardLegalities` |
| `mj_card_price` | `id` | `sync_prices()` | `AllPricesToday.sqlite:cardPrices` |
| `mj_deck` | `uuid` | `sync_decks()` | `AllDeckFiles/*.json` |
| `mj_deck_card` | `id` | `sync_decks()` | `AllDeckFiles/*.json` |
| `mj_keyword` | `id` | `sync_keywords()` | `Keywords.json` |

### User Tables (Created empty, populated by user)

| Table | Primary Key | Purpose |
|-------|-------------|---------|
| `user_card` | `id` | User's card collection (owned + wanted) |
| `user_deck` | `id` | User-created decks |
| `user_deck_card` | `id` | Cards in user decks |

---

## Table Relationships

```
mj_set
  └── mj_card.set_code (implicit, no FK constraint)

mj_card (uuid)
  ├── mj_card_identifier.card_uuid
  ├── mj_card_legality.card_uuid
  ├── mj_card_price.card_uuid
  ├── mj_deck_card.card_uuid
  ├── user_card.card_uuid
  └── user_deck_card.card_uuid

mj_deck (uuid)
  └── mj_deck_card.deck_uuid

user_deck (id)
  └── user_deck_card.deck_id
```

---

## Legacy/Unused Tables

The following models exist in code but may create tables that aren't used by the main sync:

### Domain Models (`db/domain_models.py`)
Created by `domain init` command (if run separately):

| Table | Purpose | Status |
|-------|---------|--------|
| `domain_card` | Enhanced card data | Unused by API |
| `domain_set` | Enhanced set data | Unused by API |
| `domain_deck` | Enhanced deck data | Unused by API |
| `domain_deck_card` | Enhanced deck cards | Unused by API |
| `domain_card_color_link` | M:N color relationship | Unused by API |
| `domain_card_type_link` | M:N type relationship | Unused by API |
| `domain_card_supertype_link` | M:N supertype relationship | Unused by API |
| `domain_card_subtype_link` | M:N subtype relationship | Unused by API |

### Reference Models (`db/reference_models.py`)
Alternative MTGJSON model set:

| Table | Purpose | Status |
|-------|---------|--------|
| `mtgjson_card` | Card reference data | Duplicate of mj_card |
| `mtgjson_set` | Set reference data | Duplicate of mj_set |
| `mtgjson_deck` | Deck reference data | Duplicate of mj_deck |
| `mtgjson_deckcard` | Deck card reference | Duplicate of mj_deck_card |
| `mtgjson_cardPrices` | Price reference data | Duplicate of mj_card_price |

### Migration Models (`db/migration_models.py`)
System tracking tables:

| Table | Purpose | Status |
|-------|---------|--------|
| `migration_log` | Track sync operations | Used by domain CLI |
| `schema_version` | Track schema versions | Used by domain CLI |
| `data_integrity_check` | Validation results | Used by domain CLI |

### Legacy Models (`db/models_legacy.py`)

| Table | Purpose | Status |
|-------|---------|--------|
| `carddb` | Legacy card model | Deprecated |
| `cardcolorlink` | Legacy color link | Deprecated |
| `cardtypelink` | Legacy type link | Deprecated |
| `cardsupertypelink` | Legacy supertype link | Deprecated |
| `cardsubtypelink` | Legacy subtype link | Deprecated |
| `cardlegalitylink` | Legacy legality link | Deprecated |
| `allprintingsmetadata` | Legacy sync tracking | Deprecated |

---

## Sync Behavior Notes

1. **Full replace on sync:** All `sync_*` functions DELETE existing data before inserting new data
2. **Commit batching:** Large syncs commit every 10,000-50,000 rows for performance
3. **JSON arrays:** Colors, types, keywords stored as JSON arrays (not normalized)
4. **Denormalization:** `mj_deck_card` includes `mana_cost`, `colors`, `types` copied from card data
5. **Generated UUIDs:** `mj_deck.uuid` is generated at sync time (not from MTGJSON)
6. **Price filtering:** Only prices with non-null values are synced

---

## CLI Commands

| Command | Sync Function | Tables Affected |
|---------|---------------|-----------------|
| `mtgsim db init` | `init_db()` | Creates all tables (empty) |
| `mtgsim db sync` | `sync_all()` | All `mj_*` tables |
| `mtgsim db sync --sets` | `sync_sets()` | `mj_set` |
| `mtgsim db sync --cards` | `sync_cards()` | `mj_card`, `mj_card_identifier`, `mj_card_legality` |
| `mtgsim db sync --prices` | `sync_prices()` | `mj_card_price` |
| `mtgsim db sync --decks` | `sync_decks()` | `mj_deck`, `mj_deck_card` |
| `mtgsim db sync --keywords` | `sync_keywords()` | `mj_keyword` |
| `mtgsim db reset` | Delete + `init_db()` | All tables (recreated empty) |

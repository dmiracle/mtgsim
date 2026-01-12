# Database Access Audit

This document catalogs all database access patterns across the webapp, API, and CLI components.

## Executive Summary

| Component | Database | Session Module | Primary Models |
|-----------|----------|----------------|----------------|
| **Web Viewer** (`web/`) | API only | N/A | N/A |
| **Webapp Generators** (`webapp/`) | Direct SQLite + JSON | `sqlite3` raw | Raw SQL queries |
| **API Data Layer** (`api/data/`) | `mtgsim.sqlite` | `db.session` | `MJ*`, `UserCard` |
| **CLI Commands** | Mixed | `db.session`, `domain_session`, `session_legacy` | Multiple model sets |

---

## Webapp Analysis

### Web Viewer (`web/index.html`)

**Status: API-only**

The main web viewer fetches all data from the API:

```javascript
const API_BASE = '/api';
// All data fetched via fetch() calls to API endpoints
```

**Endpoints used:**
- `/api/decks` - List decks
- `/api/decks/{file}` - Get deck details
- `/api/sets` - List sets
- `/api/cards/search` - Search cards
- `/api/prices/stats` - Price statistics

### Webapp Generators (`webapp/`)

**Status: Direct database access (bypasses API)**

| File | Data Source | Issue |
|------|-------------|-------|
| `generate_index.py` | Direct SQLite (`reference/mtgjson/AllPrintings.sqlite`) | Bypasses API |
| `generate_card_index.py` | Direct SQLite (`AllPrintings.sqlite`) | Bypasses API |
| `generate_set_index.py` | Direct SQLite (`AllPrintings.sqlite`) | Bypasses API |

These generators read directly from MTGJSON reference files, not through the API or unified database.

---

## API Data Layer

**Database:** `~/.mtgsim/mtgsim.sqlite`
**Session:** `mtgsim.db.session.get_session()`
**Models:** Unified schema from `mtgsim.db.models`

### Models Used by API

| Data Module | Read Models | Write Models |
|-------------|-------------|--------------|
| `cards.py` | `MJCard`, `MJCardIdentifier`, `MJCardPrice`, `MJSet`, `MJDeck`, `MJDeckCard`, `UserCard` | `UserCard` |
| `decks.py` | `MJDeck`, `MJDeckCard`, `MJCard`, `MJCardIdentifier`, `MJCardPrice`, `UserCard`, `UserDeck`, `UserDeckCard` | `UserDeck`, `UserDeckCard` |
| `sets.py` | `MJSet`, `MJCard`, `MJCardIdentifier`, `UserCard` | None |
| `prices.py` | `MJCard`, `MJCardPrice` | None |
| `keywords.py` | None (uses `ref_db` raw SQL) | None |

### API Database Operations Summary

| Operation | Tables Accessed | Type |
|-----------|-----------------|------|
| Search cards | `mj_card`, `mj_card_identifier`, `user_card` | SELECT + JOIN |
| Get card | `mj_card`, `mj_card_identifier`, `mj_card_price`, `mj_set`, `user_card` | SELECT + JOIN |
| Card printings | `mj_card`, `mj_card_identifier`, `mj_deck`, `mj_deck_card`, `user_card` | SELECT + JOIN |
| Add to collection | `mj_card`, `user_card` | SELECT + INSERT/UPDATE |
| List decks | `mj_deck`, `mj_deck_card`, `mj_card_price`, `user_deck`, `user_deck_card` | SELECT |
| Get deck | `mj_deck`, `mj_deck_card`, `mj_card_identifier`, `mj_card_price`, `user_card` | SELECT + JOIN |
| Create user deck | `user_deck`, `user_deck_card` | INSERT |
| List sets | `mj_set`, `mj_card`, `user_card` | SELECT + JOIN |
| Get set cards | `mj_card`, `mj_card_identifier`, `user_card` | SELECT + JOIN |
| Search by price | `mj_card`, `mj_card_price` | SELECT + JOIN |
| Get keywords | `keyword` (via `ref_db`) | Raw SQL SELECT |

### Keywords Data - Special Case

`keywords.py` uses a separate database connection:
```python
from mtgsim.reference import ref_db
cursor = ref_db.conn.execute("SELECT keyword FROM keyword WHERE type = ?", [keyword_type])
```

This bypasses the standard session and accesses the reference database directly.

---

## CLI Commands

### Primary CLI Database Access

| Command Group | File | Session Module | Database |
|---------------|------|----------------|----------|
| `db` | `db_commands.py` | `db.session` | `mtgsim.sqlite` |
| `domain` | `domain_commands.py` | `db.domain_session` | `domain.sqlite` |
| `card` | `card_commands.py` | `db.session_legacy` | Legacy DB |
| `mtgjson` | `mtgjson_commands.py` | Raw `sqlite3` | `mtgjson-merged.sqlite` |

### CLI Command Details

#### `db` Commands (`db_commands.py`)

| Command | Database Access | Models/Tables |
|---------|-----------------|---------------|
| `db init` | `init_db()` | Creates all `mj_*`, `user_*` tables |
| `db sync` | `sync_all()` | Populates `mj_card`, `mj_set`, `mj_deck`, etc. |
| `db stats` | Raw `sqlite3` | Counts all tables |
| `db reset` | `init_db()` | Recreates schema |

#### `domain` Commands (`domain_commands.py`)

| Command | Database Access | Models/Tables |
|---------|-----------------|---------------|
| `domain init` | `init_domain_db()` | Creates `domain_*`, `mtgjson_*` tables |
| `domain status` | `get_domain_session()` | `DomainCard`, `DomainSet`, `DomainDeck`, `MigrationLog` |
| `domain sync-reference` | Direct `sqlite3` copy | Copies `cards` → `mtgjson_cards`, etc. |
| `domain add-card` | `get_domain_session()` | `MTGJsonCard` → `DomainCard` + link tables |
| `domain add-set` | `get_domain_session()` | `MTGJsonSet`, `MTGJsonCard` → `DomainSet`, `DomainCard` |
| `domain add-deck` | `get_domain_session()` | `MTGJsonDeck`, `MTGJsonDeckCard` → `DomainDeck`, `DomainDeckCard` |
| `domain collect-card` | `get_domain_session()` | `DomainCard` (ownership fields) |
| `domain collection-stats` | `get_domain_session()` | `DomainCard`, `DomainSet`, `DomainDeck` |

#### `card` Commands (`card_commands.py`)

| Command | Database Access | Models/Tables |
|---------|-----------------|---------------|
| `card` | None | Creates domain `Card` object (in-memory) |
| `extract --save` | `session_legacy.get_session()` | `CardRepository` → `CardDB` |

Uses **legacy** session and `CardRepository` with `CardDB` model.

#### `mtgjson` Commands (`mtgjson_commands.py`)

| Command | Database Access | Models/Tables |
|---------|-----------------|---------------|
| `mtgjson info` | File system only | Lists `.sqlite` and `.json` files |
| `mtgjson stats` | Raw `sqlite3` | `cards` table in `mtgjson-merged.sqlite` |

---

## Model Usage Matrix

### By Module

| Model | API | CLI db | CLI domain | CLI card | CLI mtgjson |
|-------|-----|--------|------------|----------|-------------|
| `MJCard` | ✅ | ✅ | - | - | - |
| `MJCardIdentifier` | ✅ | ✅ | - | - | - |
| `MJCardLegality` | - | ✅ | - | - | - |
| `MJCardPrice` | ✅ | ✅ | - | - | - |
| `MJSet` | ✅ | ✅ | - | - | - |
| `MJDeck` | ✅ | ✅ | - | - | - |
| `MJDeckCard` | ✅ | ✅ | - | - | - |
| `UserCard` | ✅ | ✅ | - | - | - |
| `UserDeck` | ✅ | - | - | - | - |
| `UserDeckCard` | ✅ | - | - | - | - |
| `DomainCard` | - | - | ✅ | - | - |
| `DomainSet` | - | - | ✅ | - | - |
| `DomainDeck` | - | - | ✅ | - | - |
| `DomainDeckCard` | - | - | ✅ | - | - |
| `MTGJsonCard` | - | - | ✅ | - | - |
| `MTGJsonSet` | - | - | ✅ | - | - |
| `MTGJsonDeck` | - | - | ✅ | - | - |
| `CardDB` (legacy) | - | - | - | ✅ | - |
| `MigrationLog` | - | - | ✅ | - | - |
| `SchemaVersion` | - | - | ✅ | - | - |
| Raw SQL | (keywords) | - | ✅ | - | ✅ |

---

## Session/Engine Usage

| Session Type | Module | Database Path |
|--------------|--------|---------------|
| `get_session()` | `db.session` | `~/.mtgsim/mtgsim.sqlite` |
| `get_domain_session()` | `db.domain_session` | `~/.mtgsim/domain.sqlite` |
| `get_session()` (legacy) | `db.session_legacy` | `~/.mtgsim/mtgsim.sqlite` |
| `ref_db.conn` | `reference` | `~/.mtgsim/reference/mtgjson/*.sqlite` |
| Raw `sqlite3` | N/A | Various paths |

---

## Issues Identified

### 1. Webapp Generators Bypass API

The `webapp/generate_*.py` scripts read directly from `AllPrintings.sqlite` instead of using the API or unified database. This creates:
- Data inconsistency (different source than API)
- No user collection data
- Maintenance burden (two data paths)

### 2. Multiple Session Types

Four different session/connection types are in use:
1. `db.session.get_session()` - Main unified DB
2. `db.domain_session.get_domain_session()` - Domain DB
3. `db.session_legacy.get_session()` - Legacy DB
4. Raw `sqlite3.connect()` - Various files

### 3. Duplicate Model Hierarchies

The codebase has parallel model definitions:
- `MJ*` models (API primary)
- `Domain*` models (CLI domain)
- `MTGJson*` models (domain reference)
- `CardDB` (legacy)

### 4. Keywords Uses Separate Database

`KeywordsData` uses `ref_db` with raw SQL instead of the unified database session.

### 5. Domain Commands Use Separate Database

The `domain` CLI creates and manages a completely separate `domain.sqlite` database with its own schema, not the unified `mtgsim.sqlite` used by the API.

---

## Recommendations

1. **Migrate webapp generators** to use API endpoints or the unified database
2. **Consolidate sessions** to a single session factory
3. **Choose canonical models** and deprecate duplicates
4. **Migrate keywords** to unified database schema
5. **Evaluate domain database** - either merge into unified DB or document as intentional separation
6. **Remove legacy session** and `CardDB` model if unused elsewhere

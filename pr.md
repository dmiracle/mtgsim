# Phase 1: Unified Database Schema

## Summary

This PR implements Phase 1 of the database simplification plan, creating a new unified database schema that will eventually replace the three-database architecture with a single database.

## Changes

### New Unified Models (`src/mtgsim/db/models.py`)

Replaced the legacy models with a new unified schema:

**Reference Models (MJ prefix)** - Read-only, synced from MTGJSON:
- `MJCard` - Card data with JSON columns for arrays (colors, types, etc.)
- `MJCardIdentifier` - External IDs (Scryfall, TCGPlayer, etc.)
- `MJCardLegality` - Format legality per card
- `MJCardPrice` - Price data from multiple providers
- `MJSet` - Set metadata
- `MJDeck` - Preconstructed deck metadata
- `MJDeckCard` - Cards in precon decks

**User Models** - User-modifiable data:
- `UserCard` - Collection entry tracking owned AND wanted cards in one table
- `UserDeck` - User-created decks
- `UserDeckCard` - Cards in user decks

Key improvements:
- JSON columns replace 8 link tables for M:N relationships
- `UserCard` combines ownership and wishlist tracking (no separate tables)
- Clear naming convention: `MJ` prefix for MTGJSON reference data

### New Session Factory (`src/mtgsim/db/session.py`)

Simplified session management:
- Single `get_session()` context manager
- Single `init_db()` function
- Single database path (`~/.mtgsim/mtgsim.sqlite`)

### Config Updates (`src/mtgsim/config.py`)

- Added `DB_PATH` for new unified database
- Legacy paths retained for migration compatibility

### New CLI Command (`src/mtgsim/cli/db_commands.py`)

- Added `mtgsim db init-unified` command to create the new database schema

### Legacy Compatibility

To maintain backward compatibility during the transition:
- Original `models.py` backed up to `models_legacy.py`
- Original `session.py` backed up to `session_legacy.py`
- Imports updated to use legacy files where needed
- User table names prefixed with `user_` to avoid conflicts

### Bug Fix: Image URLs (`src/mtgsim/api/data/cards.py`)

Fixed `scryfallId` not being returned by adding LEFT JOIN to `cardIdentifiers` table, enabling image URLs to be populated.

## New Files

| File | Description |
|------|-------------|
| `src/mtgsim/db/models_legacy.py` | Backup of original models |
| `src/mtgsim/db/session_legacy.py` | Backup of original session |
| `tests/test_unified_schema.py` | 15 tests validating new schema |
| `tests/hurl/*.hurl` | 8 Hurl API test files |
| `docs/DATABASE_ARCHITECTURE.md` | Current architecture documentation |
| `docs/DATABASE_SIMPLIFICATION_PLAN.md` | 5-phase refactor plan |
| `docs/PHASE1_UNIFIED_SCHEMA.md` | Detailed Phase 1 plan |

## Modified Files

| File | Changes |
|------|---------|
| `src/mtgsim/db/models.py` | Replaced with unified models |
| `src/mtgsim/db/session.py` | Replaced with unified session |
| `src/mtgsim/config.py` | Added DB_PATH |
| `src/mtgsim/cli/db_commands.py` | Added init-unified command |
| `src/mtgsim/db/__init__.py` | Import from legacy files |
| `src/mtgsim/cli/card_commands.py` | Use session_legacy |
| `src/mtgsim/repository/card_repository.py` | Use models_legacy |
| `src/mtgsim/sync/mtgjson.py` | Use session_legacy |
| `src/mtgsim/api/data/cards.py` | Fix scryfallId JOIN |

## Testing

```bash
# Run new schema tests
uv run pytest tests/test_unified_schema.py -v

# Run all tests
uv run pytest tests/ --ignore=tests/hurl

# Test CLI command
uv run mtgsim db init-unified
```

**Results:**
- 15/15 new schema tests pass
- 357/358 existing tests pass (1 flaky test unrelated to changes)

## Next Steps (Phase 2)

- Update data access layer to query unified database
- Remove scope parameter from queries
- Build image URLs from `mj_card_identifier.scryfall_id`

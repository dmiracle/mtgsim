# Phase 4: Simplify Sync Pipeline

## Overview

This phase updates the sync pipeline to write directly to the unified database (`mj_*` tables) instead of the legacy merged database. The goal is to populate the unified schema with MTGJSON reference data so the API layer (updated in Phases 2-3) can serve actual data.

**Goal**: Sync MTGJSON data to unified database, single `mtgsim db sync` command

**Prerequisites**: Phases 1-3 complete (unified schema exists, API layer updated)

---

## Current State

### Sync Pipeline Flow (Legacy)
```
MTGJSON Downloads
    ↓
AllPrintings.sqlite.xz → Extract → Copy tables to mtgjson-merged.sqlite
AllPricesToday.sqlite.xz → Extract → Copy cardPrices table
DeckList.json.xz → Extract → Populate DeckList table (legacy model)
AllDeckFiles.tar.xz → Extract → Populate Deck/DeckCard tables (legacy models)
AllSetFiles/ → Process → Populate SetDB/SetCardDB tables (legacy models)
Keywords.json.xz → Extract → Populate Keyword table
```

### Current Database Files
| File | Tables | Used By |
|------|--------|---------|
| `~/.mtgsim/reference/mtgjson/mtgjson-merged.sqlite` | cards, sets, cardPrices, etc. | Old API (raw MTGJSON tables) |
| `~/.mtgsim/mtgsim.sqlite` | mj_*, user_* | New unified schema (empty) |

### Legacy Models Used
- `Deck`, `DeckCard`, `DeckList` - in `deck_models.py`
- `SetDB`, `SetCardDB` - in `set_models.py`
- `Keyword` - in `keyword_models.py`

---

## Target State

### New Sync Pipeline Flow
```
MTGJSON Downloads
    ↓
AllPrintings.sqlite.xz → Extract → Parse → Write to mj_card, mj_card_identifier, mj_card_legality
AllPricesToday.sqlite.xz → Extract → Parse → Write to mj_card_price
AllDeckFiles.tar.xz → Extract → Parse → Write to mj_deck, mj_deck_card
Sets (from AllPrintings) → Parse → Write to mj_set
    ↓
All data in ~/.mtgsim/mtgsim.sqlite
```

### Single Database
All reference data goes into `~/.mtgsim/mtgsim.sqlite`:
- `mj_card` - Card data
- `mj_card_identifier` - External IDs (Scryfall, TCGPlayer)
- `mj_card_legality` - Format legality
- `mj_card_price` - Prices
- `mj_set` - Set data
- `mj_deck` - Precon decks
- `mj_deck_card` - Cards in precon decks

---

## Implementation Tasks

### Task 4.1: Create Unified Sync Module

**File**: `src/mtgsim/sync/unified.py` (new)

Create a new sync module that writes to the unified database:

```python
"""Unified sync pipeline - writes to mj_* tables in unified database."""

import logging
from pathlib import Path

from sqlmodel import Session

from mtgsim.config import DB_PATH
from mtgsim.db.models import (
    MJCard, MJCardIdentifier, MJCardLegality, MJCardPrice,
    MJSet, MJDeck, MJDeckCard,
)
from mtgsim.db.session import get_engine, init_db

logger = logging.getLogger(__name__)


def sync_all(force: bool = False):
    """Run full sync to unified database.

    1. Download MTGJSON files if needed
    2. Sync cards from AllPrintings
    3. Sync sets from AllPrintings
    4. Sync prices from AllPricesToday
    5. Sync decks from AllDeckFiles
    """
    from .mtgjson import download_and_extract, ensure_dirs

    ensure_dirs()
    init_db()

    # Download sources
    # ... download code ...

    # Sync in order (sets first, then cards that reference sets)
    sync_sets(force)
    sync_cards(force)
    sync_prices(force)
    sync_decks(force)

    logger.info(f"Unified sync complete. Data in {DB_PATH}")


def sync_cards(source_db: Path):
    """Sync cards from AllPrintings.sqlite to mj_card + related tables."""
    pass


def sync_sets(source_db: Path):
    """Sync sets from AllPrintings.sqlite to mj_set."""
    pass


def sync_prices(source_db: Path):
    """Sync prices from AllPricesToday.sqlite to mj_card_price."""
    pass


def sync_decks(deck_dir: Path):
    """Sync decks from AllDeckFiles to mj_deck + mj_deck_card."""
    pass
```

---

### Task 4.2: Implement Card Sync

**Function**: `sync_cards()` in `unified.py`

Parse AllPrintings.sqlite and write to mj_card, mj_card_identifier, mj_card_legality:

```python
def sync_cards(source_db: Path):
    """Sync cards from AllPrintings.sqlite to unified database."""
    import sqlite3

    logger.info("Syncing cards from AllPrintings...")

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing data
        session.exec(delete(MJCard))
        session.exec(delete(MJCardIdentifier))
        session.exec(delete(MJCardLegality))
        session.commit()

        # Query cards table from AllPrintings
        cursor = conn.execute("""
            SELECT
                uuid, name, setCode, manaCost, manaValue, type, text,
                power, toughness, loyalty, defense, rarity, number, artist,
                layout, borderColor, frameVersion,
                colors, colorIdentity, types, subtypes, supertypes, keywords,
                hasFoil, hasNonFoil, isReprint, isReserved, isPromo,
                flavorText
            FROM cards
        """)

        cards_added = 0
        for row in cursor:
            card = MJCard(
                uuid=row["uuid"],
                name=row["name"],
                set_code=row["setCode"],
                mana_cost=row["manaCost"],
                mana_value=row["manaValue"],
                type_line=row["type"],
                oracle_text=row["text"],
                power=row["power"],
                toughness=row["toughness"],
                loyalty=row["loyalty"],
                defense=row["defense"],
                rarity=row["rarity"],
                number=row["number"],
                artist=row["artist"],
                layout=row["layout"],
                border_color=row["borderColor"],
                frame_version=row["frameVersion"],
                flavor_text=row["flavorText"],
                colors=_parse_json_or_list(row["colors"]),
                color_identity=_parse_json_or_list(row["colorIdentity"]),
                types=_parse_json_or_list(row["types"]),
                subtypes=_parse_json_or_list(row["subtypes"]),
                supertypes=_parse_json_or_list(row["supertypes"]),
                keywords=_parse_json_or_list(row["keywords"]),
                has_foil=bool(row["hasFoil"]),
                has_non_foil=bool(row["hasNonFoil"]),
                is_reprint=bool(row["isReprint"]),
                is_reserved=bool(row["isReserved"]),
                is_promo=bool(row["isPromo"]),
            )
            session.add(card)
            cards_added += 1

            if cards_added % 10000 == 0:
                session.commit()
                logger.info(f"Synced {cards_added} cards...")

        session.commit()
        logger.info(f"Synced {cards_added} total cards")

    # Sync identifiers
    _sync_card_identifiers(conn, engine)

    # Sync legalities
    _sync_card_legalities(conn, engine)

    conn.close()


def _sync_card_identifiers(conn, engine):
    """Sync cardIdentifiers table to mj_card_identifier."""
    logger.info("Syncing card identifiers...")

    cursor = conn.execute("""
        SELECT
            uuid, scryfallId, scryfallOracleId, scryfallIllustrationId,
            tcgplayerProductId, tcgplayerEtchedProductId,
            cardmarketId, cardsphereId,
            mtgoId, mtgoFoilId, mtgjsonV4Id, multiverseId
        FROM cardIdentifiers
    """)

    with Session(engine) as session:
        count = 0
        for row in cursor:
            identifier = MJCardIdentifier(
                card_uuid=row["uuid"],
                scryfall_id=row["scryfallId"],
                scryfall_oracle_id=row["scryfallOracleId"],
                scryfall_illustration_id=row["scryfallIllustrationId"],
                tcgplayer_product_id=row["tcgplayerProductId"],
                tcgplayer_etched_product_id=row["tcgplayerEtchedProductId"],
                cardmarket_id=row["cardmarketId"],
                cardsphere_id=row["cardsphereId"],
                mtgo_id=row["mtgoId"],
                mtgo_foil_id=row["mtgoFoilId"],
                mtgjson_v4_id=row["mtgjsonV4Id"],
                multiverse_id=row["multiverseId"],
            )
            session.add(identifier)
            count += 1

            if count % 10000 == 0:
                session.commit()

        session.commit()
        logger.info(f"Synced {count} card identifiers")


def _sync_card_legalities(conn, engine):
    """Sync cardLegalities table to mj_card_legality."""
    logger.info("Syncing card legalities...")

    cursor = conn.execute("SELECT uuid, format, status FROM cardLegalities")

    with Session(engine) as session:
        count = 0
        for row in cursor:
            legality = MJCardLegality(
                card_uuid=row["uuid"],
                format=row["format"],
                status=row["status"],
            )
            session.add(legality)
            count += 1

            if count % 50000 == 0:
                session.commit()

        session.commit()
        logger.info(f"Synced {count} card legalities")
```

---

### Task 4.3: Implement Set Sync

**Function**: `sync_sets()` in `unified.py`

Parse sets table from AllPrintings.sqlite:

```python
def sync_sets(source_db: Path):
    """Sync sets from AllPrintings.sqlite to mj_set."""
    import sqlite3

    logger.info("Syncing sets from AllPrintings...")

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing
        session.exec(delete(MJSet))
        session.commit()

        cursor = conn.execute("""
            SELECT
                code, name, type, releaseDate, baseSetSize, totalSetSize,
                block, parentCode, keyruneCode,
                isFoilOnly, isOnlineOnly, isPartialPreview
            FROM sets
        """)

        count = 0
        for row in cursor:
            set_obj = MJSet(
                code=row["code"],
                name=row["name"],
                type=row["type"],
                release_date=row["releaseDate"],
                base_set_size=row["baseSetSize"] or 0,
                total_set_size=row["totalSetSize"] or 0,
                block=row["block"],
                parent_code=row["parentCode"],
                keyrune_code=row["keyruneCode"],
                is_foil_only=bool(row["isFoilOnly"]),
                is_online_only=bool(row["isOnlineOnly"]),
                is_partial_preview=bool(row["isPartialPreview"]),
            )
            session.add(set_obj)
            count += 1

        session.commit()
        logger.info(f"Synced {count} sets")

    conn.close()
```

---

### Task 4.4: Implement Price Sync

**Function**: `sync_prices()` in `unified.py`

Parse AllPricesToday.sqlite:

```python
def sync_prices(source_db: Path):
    """Sync prices from AllPricesToday.sqlite to mj_card_price."""
    import sqlite3
    import json
    from datetime import datetime

    logger.info("Syncing prices from AllPricesToday...")

    conn = sqlite3.connect(source_db)
    conn.row_factory = sqlite3.Row

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing
        session.exec(delete(MJCardPrice))
        session.commit()

        # cardPrices table has: uuid, prices (JSON blob)
        cursor = conn.execute("SELECT uuid, prices FROM cardPrices")

        count = 0
        for row in cursor:
            card_uuid = row["uuid"]
            prices_json = row["prices"]

            if not prices_json:
                continue

            try:
                prices = json.loads(prices_json)
            except json.JSONDecodeError:
                continue

            # Parse nested price structure
            # { "paper": { "tcgplayer": { "retail": { "normal": { "2024-01-01": 1.23 } } } } }
            for game_type, providers in prices.items():  # paper, mtgo
                for provider, listings in providers.items():  # tcgplayer, cardmarket
                    for listing_type, finishes in listings.items():  # retail, buylist
                        for finish, dates in finishes.items():  # normal, foil
                            if dates:
                                # Get latest price
                                latest_date = max(dates.keys())
                                price_value = dates[latest_date]

                                price_obj = MJCardPrice(
                                    card_uuid=card_uuid,
                                    provider=provider,
                                    listing_type=listing_type,
                                    finish=finish,
                                    currency="USD",
                                    price=price_value,
                                    updated_at=datetime.fromisoformat(latest_date),
                                )
                                session.add(price_obj)
                                count += 1

            if count % 50000 == 0:
                session.commit()
                logger.info(f"Synced {count} price entries...")

        session.commit()
        logger.info(f"Synced {count} total price entries")

    conn.close()
```

---

### Task 4.5: Implement Deck Sync

**Function**: `sync_decks()` in `unified.py`

Parse AllDeckFiles JSON:

```python
def sync_decks(deck_dir: Path):
    """Sync decks from AllDeckFiles to mj_deck + mj_deck_card."""
    import json
    import uuid as uuid_lib

    logger.info(f"Syncing decks from {deck_dir}...")

    if not deck_dir.exists():
        logger.warning(f"Deck directory not found: {deck_dir}")
        return

    files = list(deck_dir.glob("*.json"))
    logger.info(f"Found {len(files)} deck files")

    engine = get_engine()

    with Session(engine) as session:
        # Clear existing
        session.exec(delete(MJDeckCard))
        session.exec(delete(MJDeck))
        session.commit()

        for i, file_path in enumerate(files):
            if i % 100 == 0 and i > 0:
                logger.info(f"Processed {i}/{len(files)} decks")
                session.commit()

            _process_deck_file(session, file_path)

        session.commit()
        logger.info(f"Synced {len(files)} decks")


def _process_deck_file(session: Session, file_path: Path):
    """Process a single deck JSON file."""
    import json
    import uuid as uuid_lib

    try:
        with open(file_path) as f:
            content = json.load(f)

        data = content.get("data", {})
        file_name = file_path.stem

        # Count cards in each board
        main_count = sum(c.get("count", 1) for c in data.get("mainBoard", []))
        side_count = sum(c.get("count", 1) for c in data.get("sideBoard", []))
        commander_count = sum(c.get("count", 1) for c in data.get("commander", []))

        deck = MJDeck(
            uuid=str(uuid_lib.uuid4()),
            file_name=file_name,
            name=data.get("name", file_name),
            code=data.get("code", ""),
            type=data.get("type"),
            release_date=data.get("releaseDate"),
            main_board_count=main_count,
            side_board_count=side_count,
            commander_count=commander_count,
        )
        session.add(deck)

        # Add cards from all boards
        for board_name in ["mainBoard", "sideBoard", "commander"]:
            for card_data in data.get(board_name, []):
                deck_card = MJDeckCard(
                    deck_uuid=deck.uuid,
                    card_uuid=card_data.get("uuid"),
                    name=card_data.get("name", ""),
                    board=board_name,
                    count=card_data.get("count", 1),
                    mana_cost=card_data.get("manaCost"),
                    mana_value=card_data.get("manaValue"),
                    colors=card_data.get("colors", []),
                    types=card_data.get("types", []),
                )
                session.add(deck_card)

    except Exception as e:
        logger.warning(f"Error processing {file_path.name}: {e}")
```

---

### Task 4.6: Add Helper Functions

**File**: `unified.py`

```python
import json


def _parse_json_or_list(value) -> list:
    """Parse a JSON string or return list as-is."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return []
```

---

### Task 4.7: Update CLI Command

**File**: `src/mtgsim/cli/db_commands.py`

Update or add `sync-unified` command:

```python
@db_app.command("sync-unified")
def db_sync_unified(
    force: bool = typer.Option(False, "--force", "-f", help="Force sync even if up to date"),
    cards_only: bool = typer.Option(False, "--cards", help="Sync only cards"),
    sets_only: bool = typer.Option(False, "--sets", help="Sync only sets"),
    prices_only: bool = typer.Option(False, "--prices", help="Sync only prices"),
    decks_only: bool = typer.Option(False, "--decks", help="Sync only decks"),
):
    """Sync MTGJSON data to unified database.

    Downloads latest MTGJSON data and populates mj_* tables in the unified
    database at ~/.mtgsim/mtgsim.sqlite.

    By default syncs all data. Use flags to sync specific data types.
    """
    from mtgsim.sync.unified import sync_all, sync_cards, sync_sets, sync_prices, sync_decks

    try:
        if cards_only or sets_only or prices_only or decks_only:
            # Selective sync
            from mtgsim.sync.mtgjson import download_and_extract, MTGJSON_DIR
            from mtgsim.config import ALL_PRINTINGS_URL, ALL_PRICES_URL

            printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
            prices_db = MTGJSON_DIR / "AllPricesToday.sqlite"

            if cards_only or sets_only:
                download_and_extract(ALL_PRINTINGS_URL, printings_db, force)
                if sets_only:
                    sync_sets(printings_db)
                if cards_only:
                    sync_cards(printings_db)

            if prices_only:
                download_and_extract(ALL_PRICES_URL, prices_db, force)
                sync_prices(prices_db)

            if decks_only:
                # Download deck files
                # sync_decks(...)
                pass
        else:
            sync_all(force=force)

        typer.echo(f"Sync complete. Data stored in {DB_PATH}")
    except Exception as e:
        typer.echo(f"Error during sync: {e}")
        raise typer.Exit(1)
```

---

### Task 4.8: Add Progress Reporting

Add progress indicators for long-running syncs:

```python
def sync_cards_with_progress(source_db: Path, callback=None):
    """Sync cards with progress callback."""
    # ... same as sync_cards but with:
    if callback:
        callback(cards_added, total_estimate)
```

CLI with progress bar:

```python
from rich.progress import Progress

@db_app.command("sync-unified")
def db_sync_unified(...):
    with Progress() as progress:
        task = progress.add_task("Syncing cards...", total=None)

        def update_progress(current, total):
            if total:
                progress.update(task, total=total, completed=current)

        sync_cards_with_progress(source_db, callback=update_progress)
```

---

### Task 4.9: Optional - Migrate User Collection

**File**: `src/mtgsim/sync/migrate_collection.py` (new, optional)

Migrate existing user collection data to `user_card` table:

```python
def migrate_user_collection():
    """Migrate user collection from legacy database to unified user_card table."""
    from mtgsim.config import USER_DB_PATH, DOMAIN_DB_PATH
    from mtgsim.db.models import UserCard
    from mtgsim.db.session import get_engine

    # Check if legacy databases exist
    if not USER_DB_PATH.exists() and not DOMAIN_DB_PATH.exists():
        logger.info("No legacy collection data to migrate")
        return

    # ... migration logic ...
```

This is optional for Phase 4 and can be deferred to Phase 5.

---

## File Changes Summary

### New Files

| File | Purpose |
|------|---------|
| `src/mtgsim/sync/unified.py` | Unified sync pipeline |
| `src/mtgsim/sync/migrate_collection.py` | Optional collection migration |

### Modified Files

| File | Changes |
|------|---------|
| `src/mtgsim/cli/db_commands.py` | Add `sync-unified` command |
| `src/mtgsim/sync/__init__.py` | Export new functions |

---

## Testing Strategy

### Unit Tests

Test sync functions with small sample databases:

```python
def test_sync_cards_creates_mj_card_entries(tmp_path):
    """Verify cards are synced to mj_card table."""
    # Create sample AllPrintings.sqlite with a few cards
    # Run sync_cards()
    # Verify mj_card table has expected entries
    pass


def test_sync_prices_parses_nested_json():
    """Verify price JSON parsing handles nested structure."""
    pass
```

### Integration Tests

Test full sync with real (or subset) MTGJSON data:

```python
def test_full_sync_populates_all_tables():
    """Full sync populates all mj_* tables."""
    sync_all(force=True)

    with get_session() as session:
        assert session.exec(select(func.count(MJCard.uuid))).one() > 0
        assert session.exec(select(func.count(MJSet.code))).one() > 0
        assert session.exec(select(func.count(MJDeck.uuid))).one() > 0
```

### API Integration

After sync, verify API returns data:

```python
def test_api_returns_cards_after_sync(client):
    """API returns cards after unified sync."""
    sync_all()

    response = client.get("/api/cards?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) > 0
```

---

## Acceptance Criteria

1. [ ] `mtgsim db sync-unified` downloads and syncs all MTGJSON data
2. [ ] `mj_card` table populated with all cards from AllPrintings
3. [ ] `mj_card_identifier` table populated with Scryfall IDs, etc.
4. [ ] `mj_card_legality` table populated with format legalities
5. [ ] `mj_card_price` table populated with current prices
6. [ ] `mj_set` table populated with all sets
7. [ ] `mj_deck` and `mj_deck_card` tables populated with precon decks
8. [ ] API endpoints return data after sync
9. [ ] Sync is idempotent (can run multiple times safely)
10. [ ] Progress reporting for long-running operations

---

## Performance Considerations

### Bulk Inserts

Use bulk insert patterns for large tables:

```python
# Instead of individual session.add() calls
session.bulk_insert_mappings(MJCard, cards_list)
```

### Transaction Batching

Commit in batches to avoid memory issues:

```python
BATCH_SIZE = 10000

for i, row in enumerate(cursor):
    session.add(...)
    if i % BATCH_SIZE == 0:
        session.commit()
```

### Index Management

Consider dropping indexes before bulk insert and recreating after:

```python
# Drop indexes
session.execute("DROP INDEX IF EXISTS ix_mj_card_name")

# Bulk insert

# Recreate indexes
session.execute("CREATE INDEX ix_mj_card_name ON mj_card(name)")
```

---

## Dependencies

### From Phase 1
- Unified models defined in `models.py`
- Session factory in `session.py`
- Database path in `config.py`

### For Phase 5
- Legacy sync code can be removed after Phase 4 verified
- Legacy models can be deleted

---

## Rollback Plan

1. Keep legacy `sync` command functional during Phase 4
2. Old merged database untouched
3. If unified sync fails, API can fall back to legacy queries
4. Add `--dry-run` flag to preview changes without writing

---

## Notes

### MTGJSON Data Structure

AllPrintings.sqlite tables:
- `cards` - Main card data (name, mana, type, etc.)
- `cardIdentifiers` - External IDs keyed by uuid
- `cardLegalities` - Format legality keyed by uuid
- `sets` - Set metadata
- `tokens` - Token cards (optional)

AllPricesToday.sqlite tables:
- `cardPrices` - uuid + JSON blob of prices

AllDeckFiles/:
- Individual JSON files per deck
- Nested structure with mainBoard, sideBoard, commander arrays

### Data Volume Estimates

| Table | Estimated Rows |
|-------|----------------|
| mj_card | ~80,000 |
| mj_card_identifier | ~80,000 |
| mj_card_legality | ~800,000 (10 formats × 80k cards) |
| mj_card_price | ~200,000 (multiple providers/finishes) |
| mj_set | ~800 |
| mj_deck | ~1,500 |
| mj_deck_card | ~150,000 |

### Sync Time Estimates

- Cards: 2-5 minutes
- Legalities: 1-2 minutes
- Prices: 2-3 minutes
- Decks: 1-2 minutes
- Total: ~10 minutes first run, faster with caching

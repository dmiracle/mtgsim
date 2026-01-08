# Phase 1: Unified Database Schema

## Overview

This phase creates the new unified database schema and models. No migration or data access changes yet - just the foundation.

**Goal**: Define new simplified schema with clear naming conventions

**Deliverables**:
1. `src/mtgsim/db/models.py` - Unified models (replaces all existing model files)
2. `src/mtgsim/db/session.py` - Single session factory (replaces all existing sessions)
3. `src/mtgsim/config.py` - Updated paths

---

## Naming Conventions

### Model Naming

| Type | Prefix | Example | Table Name |
|------|--------|---------|------------|
| Reference (MTGJSON) | `MJ` | `MJCard` | `mj_card` |
| User data | None | `Card` | `card` |

### Reference Models (Read-only, synced from MTGJSON)
- `MJCard` - Card data from AllPrintings
- `MJCardIdentifier` - External IDs (Scryfall, TCGPlayer, etc.)
- `MJCardLegality` - Format legality per card
- `MJCardPrice` - Current prices from multiple providers
- `MJSet` - Set metadata
- `MJDeck` - Preconstructed deck metadata
- `MJDeckCard` - Cards in precon decks

### User Models (User-modifiable)
- `Card` - User's collection entry (owns/wants cards)
- `Deck` - User-created decks
- `DeckCard` - Cards in user decks

---

## Database Schema

### Target Location
```
~/.mtgsim/mtgsim.sqlite
```

### Table Structure

```
mj_card              # Reference card data
mj_card_identifier   # External IDs (scryfall, tcgplayer, etc.)
mj_card_legality     # Format legality
mj_card_price        # Prices from providers
mj_set               # Reference set data
mj_deck              # Reference precon deck data
mj_deck_card         # Cards in precon decks

card                 # User collection (owns + wants)
deck                 # User custom decks
deck_card            # Cards in user decks
```

---

## Model Definitions

### Reference Models

```python
# src/mtgsim/db/models.py

from datetime import datetime
from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


# =============================================================================
# Reference Models (MJ prefix) - Read-only, synced from MTGJSON
# =============================================================================

class MJCard(SQLModel, table=True):
    """Card data from MTGJSON AllPrintings."""
    __tablename__ = "mj_card"

    uuid: str = Field(primary_key=True)
    name: str = Field(index=True)
    set_code: str = Field(index=True)

    # Card text
    mana_cost: str | None = None
    mana_value: float | None = None
    type_line: str | None = None
    oracle_text: str | None = None
    flavor_text: str | None = None

    # Stats
    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None

    # Metadata
    rarity: str | None = Field(default=None, index=True)
    number: str | None = None
    artist: str | None = None
    layout: str | None = None
    border_color: str | None = None
    frame_version: str | None = None

    # JSON arrays (replaces link tables)
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    subtypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    supertypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Flags
    has_foil: bool = False
    has_non_foil: bool = False
    is_reprint: bool = False
    is_reserved: bool = False
    is_promo: bool = False


class MJCardIdentifier(SQLModel, table=True):
    """External identifiers for cards (Scryfall, TCGPlayer, etc.)."""
    __tablename__ = "mj_card_identifier"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    scryfall_id: str | None = Field(default=None, index=True)
    scryfall_oracle_id: str | None = None
    scryfall_illustration_id: str | None = None

    tcgplayer_product_id: str | None = None
    tcgplayer_etched_product_id: str | None = None

    cardmarket_id: str | None = None
    cardsphere_id: str | None = None

    mtgo_id: str | None = None
    mtgo_foil_id: str | None = None

    mtgjson_v4_id: str | None = None
    multiverse_id: str | None = None


class MJCardLegality(SQLModel, table=True):
    """Format legality for cards."""
    __tablename__ = "mj_card_legality"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)
    format: str = Field(index=True)  # standard, modern, legacy, etc.
    status: str  # Legal, Banned, Restricted, Not Legal


class MJCardPrice(SQLModel, table=True):
    """Price data from multiple providers."""
    __tablename__ = "mj_card_price"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    provider: str = Field(index=True)  # tcgplayer, cardmarket, cardsphere, cardkingdom
    listing_type: str  # retail, buylist
    finish: str  # normal, foil, etched
    currency: str = "USD"
    price: float | None = None

    updated_at: datetime | None = None


class MJSet(SQLModel, table=True):
    """Set data from MTGJSON."""
    __tablename__ = "mj_set"

    code: str = Field(primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)

    release_date: str | None = Field(default=None, index=True)
    base_set_size: int = 0
    total_set_size: int = 0

    block: str | None = Field(default=None, index=True)
    parent_code: str | None = None
    keyrune_code: str | None = None

    is_foil_only: bool = False
    is_online_only: bool = False
    is_partial_preview: bool = False


class MJDeck(SQLModel, table=True):
    """Preconstructed deck data from MTGJSON."""
    __tablename__ = "mj_deck"

    uuid: str = Field(primary_key=True)
    file_name: str = Field(index=True, unique=True)
    name: str = Field(index=True)
    code: str = Field(index=True)

    type: str | None = None
    release_date: str | None = None

    main_board_count: int = 0
    side_board_count: int = 0
    commander_count: int = 0


class MJDeckCard(SQLModel, table=True):
    """Cards in preconstructed decks."""
    __tablename__ = "mj_deck_card"

    id: int | None = Field(default=None, primary_key=True)
    deck_uuid: str = Field(foreign_key="mj_deck.uuid", index=True)
    card_uuid: str | None = Field(default=None, index=True)

    name: str = Field(index=True)
    board: str = Field(index=True)  # mainBoard, sideBoard, commander
    count: int = 1

    # Denormalized for query performance
    mana_cost: str | None = None
    mana_value: float | None = None
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))


# =============================================================================
# User Models - User-modifiable data
# =============================================================================

class Card(SQLModel, table=True):
    """User's card collection entry.

    Tracks both owned cards and wishlist in a single table.
    A card can be owned, wanted, or both.
    """
    __tablename__ = "card"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    # Ownership
    quantity_owned: int = 0
    quantity_owned_foil: int = 0

    # Wishlist
    quantity_wanted: int = 0
    quantity_wanted_foil: int = 0

    # Purchase tracking
    purchase_price: float | None = None
    purchase_date: datetime | None = None

    # Condition (for owned cards)
    condition: str = "NM"  # NM, LP, MP, HP, DMG

    # Notes
    notes: str | None = None

    # Timestamps
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def owns(self) -> bool:
        """True if user owns any copies."""
        return (self.quantity_owned + self.quantity_owned_foil) > 0

    @property
    def wants(self) -> bool:
        """True if user wants any copies."""
        return (self.quantity_wanted + self.quantity_wanted_foil) > 0

    @property
    def total_owned(self) -> int:
        """Total owned copies (regular + foil)."""
        return self.quantity_owned + self.quantity_owned_foil

    @property
    def total_wanted(self) -> int:
        """Total wanted copies (regular + foil)."""
        return self.quantity_wanted + self.quantity_wanted_foil


class Deck(SQLModel, table=True):
    """User-created deck."""
    __tablename__ = "deck"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None

    format: str | None = None  # standard, modern, commander, etc.

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DeckCard(SQLModel, table=True):
    """Card entry in a user deck."""
    __tablename__ = "deck_card"

    id: int | None = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="deck.id", index=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    board: str = "main"  # main, side, commander, maybe
    count: int = 1
    is_foil: bool = False
```

### Session Factory

```python
# src/mtgsim/db/session.py

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from mtgsim.config import DB_PATH


_engine: Engine | None = None


def get_engine(db_path: Path | None = None) -> Engine:
    """Get or create the database engine."""
    global _engine

    if _engine is None:
        path = db_path or DB_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )

    return _engine


def init_db(db_path: Path | None = None) -> None:
    """Initialize database with all tables."""
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session(db_path: Path | None = None):
    """Get a database session."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        yield session


def close_db() -> None:
    """Close database connection."""
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None
```

### Config Updates

```python
# src/mtgsim/config.py (relevant parts)

from pathlib import Path

# Base directory
MTGSIM_DIR = Path.home() / ".mtgsim"

# Single unified database
DB_PATH = MTGSIM_DIR / "mtgsim.sqlite"

# MTGJSON source files (downloaded, not created by us)
MTGJSON_DIR = MTGSIM_DIR / "mtgjson"
MTGJSON_ALLPRINTINGS = MTGJSON_DIR / "AllPrintings.sqlite"
MTGJSON_ALLPRICES = MTGJSON_DIR / "AllPricesToday.sqlite"
MTGJSON_ALLDECKS = MTGJSON_DIR / "AllDecks.sqlite"
MTGJSON_DECKFILES = MTGJSON_DIR / "AllDeckFiles"

# Legacy paths (for migration, to be removed later)
LEGACY_DB_PATH = MTGSIM_DIR / "mtgsim.db"
DOMAIN_DB_PATH = MTGSIM_DIR / "domain" / "mtgsim.sqlite"
REFERENCE_DB_PATH = MTGSIM_DIR / "reference" / "mtgjson" / "mtgjson-merged.sqlite"
```

---

## Tasks

### Task 1.1: Create New Models File

**File**: `src/mtgsim/db/models.py`

**Actions**:
1. Backup existing `models.py` to `models_legacy.py`
2. Create new `models.py` with all models defined above
3. Ensure all imports work

**Validation**:
```python
from mtgsim.db.models import MJCard, MJSet, Card, Deck
```

---

### Task 1.2: Create New Session File

**File**: `src/mtgsim/db/session.py`

**Actions**:
1. Backup existing `session.py` to `session_legacy.py`
2. Create new `session.py` with unified session factory
3. Remove old session factories from other files

**Validation**:
```python
from mtgsim.db.session import get_session, init_db

init_db()
with get_session() as session:
    # Should work
    pass
```

---

### Task 1.3: Update Config

**File**: `src/mtgsim/config.py`

**Actions**:
1. Add `DB_PATH` for unified database
2. Add `MTGJSON_DIR` and source file paths
3. Keep legacy paths (marked for migration)

**Validation**:
```python
from mtgsim.config import DB_PATH, MTGJSON_DIR
assert DB_PATH.suffix == ".sqlite"
```

---

### Task 1.4: Create Database Initialization

**Actions**:
1. Add CLI command `mtgsim db init` that creates empty unified database
2. Creates all tables defined in models

**Validation**:
```bash
mtgsim db init
sqlite3 ~/.mtgsim/mtgsim.sqlite ".tables"
# Should show: card, deck, deck_card, mj_card, mj_card_identifier, etc.
```

---

### Task 1.5: Verify Schema

**Actions**:
1. Write test that creates database and verifies all tables exist
2. Verify indexes are created
3. Verify foreign keys work

**Test file**: `tests/test_unified_schema.py`

```python
def test_schema_creates_all_tables():
    """Verify all tables are created."""
    init_db(test_db_path)

    with get_session(test_db_path) as session:
        # Check reference tables
        session.exec(select(MJCard)).first()
        session.exec(select(MJSet)).first()
        session.exec(select(MJDeck)).first()

        # Check user tables
        session.exec(select(Card)).first()
        session.exec(select(Deck)).first()

def test_card_collection_entry():
    """Verify Card model works for collection tracking."""
    with get_session(test_db_path) as session:
        # Create a reference card first
        mj_card = MJCard(uuid="test-123", name="Test Card", set_code="TST")
        session.add(mj_card)
        session.commit()

        # Add to collection
        card = Card(
            card_uuid="test-123",
            quantity_owned=4,
            quantity_wanted=2,
        )
        session.add(card)
        session.commit()

        assert card.owns == True
        assert card.wants == True
        assert card.total_owned == 4
```

---

## File Changes Summary

### New Files
| File | Description |
|------|-------------|
| `src/mtgsim/db/models.py` | Unified models (MJ* + user models) |
| `src/mtgsim/db/session.py` | Single session factory |
| `tests/test_unified_schema.py` | Schema validation tests |

### Modified Files
| File | Changes |
|------|---------|
| `src/mtgsim/config.py` | Add DB_PATH, MTGJSON_DIR |

### Backup Files (temporary)
| Original | Backup |
|----------|--------|
| `src/mtgsim/db/models.py` | `src/mtgsim/db/models_legacy.py` |
| `src/mtgsim/db/session.py` | `src/mtgsim/db/session_legacy.py` |

---

## Acceptance Criteria

1. [ ] `mtgsim db init` creates `~/.mtgsim/mtgsim.sqlite`
2. [ ] All 10 tables are created (7 MJ* + 3 user)
3. [ ] `Card` model supports both `owns` and `wants` tracking
4. [ ] All tests pass
5. [ ] No changes to existing API behavior (yet)

---

## Next Phase Dependencies

Phase 2 (Data Access) will need:
- Queries that join `mj_card` with `card` for collection status
- Image URL built from `mj_card_identifier.scryfall_id`
- Price lookup from `mj_card_price`

Phase 4 (Sync) will need:
- Sync to write to `mj_*` tables
- Clear and replace strategy for reference data

# Phase 2: Simplify Data Access Layer

## Overview

This phase rewrites the data access layer to use the unified database schema from Phase 1. The goal is to eliminate the `scope` parameter, remove code duplication, and create a simpler query pattern that naturally joins reference data with user collection data.

**Goal**: Single data access pattern, remove scope parameter, query unified schema

**Prerequisites**: Phase 1 complete (unified models and session in place)

---

## Current State Problems

### 1. Triple Code Paths
Every method has three implementations:
```python
def search_cards(self, ..., scope: str = "user"):
    if scope == "reference":
        return self._search_reference_cards(...)
    elif scope == "combined":
        return self._search_combined_cards(...)
    else:
        return self._search_domain_cards(...)
```

### 2. Multiple Session Factories
- `get_domain_session()` - Domain database
- `ref_db.conn` - Direct SQLite connection to reference
- `db.prices` / `db.sets` - Legacy database connections

### 3. Model Conversion Overhead
- `converters.py` has 486 lines of conversion functions
- `domain_card_to_api_dict()`, `reference_card_to_api_dict()`, etc.
- Each model type needs its own converter

### 4. Duplicated Query Logic
Same filters applied differently in each scope:
- SQLModel queries for domain
- Raw SQL for reference
- In-memory merging for combined

---

## Target Architecture

### Single Query Pattern

All queries follow this pattern:
```python
def get_cards(...):
    """Get cards with collection status automatically included."""
    with get_session() as session:
        query = (
            select(MJCard, MJCardIdentifier, UserCard)
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
        )
        # Apply filters...
        results = session.exec(query).all()
        return [_to_api_dict(mj_card, identifier, user_card) for mj_card, identifier, user_card in results]
```

### New Response Shape

Every card response includes collection status:
```python
{
    "uuid": "abc-123",
    "name": "Lightning Bolt",
    # ... card data from mj_card ...
    "image_url": "https://cards.scryfall.io/...",  # from mj_card_identifier
    "prices": {...},  # from mj_card_price
    # Collection status (computed from user_card join)
    "owns": True,
    "wants": False,
    "total_owned": 4,
    "total_wanted": 0,
    "collection": {  # Only present if user has this card
        "quantity_owned": 3,
        "quantity_owned_foil": 1,
        "quantity_wanted": 0,
        "quantity_wanted_foil": 0,
        "condition": "NM",
        "notes": null
    }
}
```

### Filter by Collection Status

Instead of scope, use explicit filters:
```python
# Old: scope="user" (only cards user owns)
# New: owns=True

# Old: scope="reference" (all cards)
# New: (no filter, shows all)

# Old: scope="combined" (all cards with collection status)
# New: (this is now the default behavior)
```

---

## Implementation Tasks

### Task 2.1: Create Unified Cards Data Module

**File**: `src/mtgsim/api/data/cards.py`

**Changes**:
1. Remove `scope` parameter from all methods
2. Use `get_session()` from unified session
3. Query `MJCard` joined with `MJCardIdentifier` and `UserCard`
4. Add `owns` and `wants` filter parameters
5. Remove all `_search_domain_*`, `_search_reference_*`, `_search_combined_*` methods
6. Single `_to_api_dict()` helper for response formatting

**New Interface**:
```python
class CardsData:
    def search_cards(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        owns: bool | None = None,      # Filter to owned cards
        wants: bool | None = None,     # Filter to wanted cards
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """Search cards with automatic collection status."""

    def get_card(self, uuid: str) -> dict | None:
        """Get single card with collection status."""

    def get_cards_by_name(self, name: str) -> list[dict]:
        """Get all printings of a card."""

    def get_card_appearances(self, uuid: str) -> list[dict]:
        """Get decks containing this card."""

    def get_other_printings(self, uuid: str) -> list[dict]:
        """Get other printings of same card."""

    # Collection management
    def add_to_collection(self, card_uuid: str, **kwargs) -> bool:
        """Add/update card in user collection."""

    def remove_from_collection(self, card_uuid: str) -> bool:
        """Remove card from user collection."""
```

**Query Example**:
```python
def search_cards(self, q: str | None = None, owns: bool | None = None, ...):
    with get_session() as session:
        # Base query with joins
        query = (
            select(MJCard, MJCardIdentifier, UserCard)
            .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
            .outerjoin(UserCard, MJCard.uuid == UserCard.card_uuid)
        )

        # Text search
        if q:
            query = query.where(
                (MJCard.name.contains(q)) | (MJCard.type_line.contains(q))
            )

        # Collection filters
        if owns is True:
            query = query.where(
                (UserCard.quantity_owned > 0) | (UserCard.quantity_owned_foil > 0)
            )
        elif owns is False:
            query = query.where(
                (UserCard.id.is_(None)) |
                ((UserCard.quantity_owned == 0) & (UserCard.quantity_owned_foil == 0))
            )

        # ... other filters ...

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        total = session.exec(count_query).one()

        # Sort and paginate
        query = query.order_by(...)
        query = query.offset((page - 1) * limit).limit(limit)

        results = session.exec(query).all()
        return [self._to_api_dict(mj, ident, user) for mj, ident, user in results], total
```

---

### Task 2.2: Create Unified Sets Data Module

**File**: `src/mtgsim/api/data/sets.py`

**Changes**:
1. Remove `scope` parameter
2. Query `MJSet` directly
3. Join with card counts and user collection stats
4. Remove triple code paths

**New Interface**:
```python
class SetsData:
    def list_sets(
        self,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        has_owned_cards: bool | None = None,  # Filter to sets with owned cards
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """List sets with collection stats."""

    def get_set(self, code: str) -> dict | None:
        """Get set metadata with collection stats."""

    def get_set_cards(
        self,
        code: str,
        owns: bool | None = None,
        ...
    ) -> tuple[list[dict], int]:
        """Get cards in a set with collection status."""

    def get_set_stats(self, code: str) -> dict:
        """Calculate set statistics."""
```

**Set Response with Collection Stats**:
```python
{
    "code": "MH2",
    "name": "Modern Horizons 2",
    # ... set data from mj_set ...
    # Collection stats (computed from user_card join)
    "collection_stats": {
        "total_cards": 303,
        "owned_cards": 47,
        "owned_percentage": 15.5,
        "wanted_cards": 12
    }
}
```

---

### Task 2.3: Create Unified Decks Data Module

**File**: `src/mtgsim/api/data/decks.py`

**Changes**:
1. Remove `scope` parameter
2. Query `MJDeck` and `MJDeckCard`
3. Compute card ownership for deck cards
4. Support user decks (`UserDeck`, `UserDeckCard`)
5. Remove triple code paths

**New Interface**:
```python
class DecksData:
    def list_decks(
        self,
        q: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        source: str | None = None,  # "precon" or "user" or None for all
        ...
    ) -> tuple[list[dict], int]:
        """List decks (precon and user)."""

    def get_deck(self, identifier: str) -> dict | None:
        """Get deck by file_name (precon) or id (user)."""

    def get_deck_cards(self, deck_uuid: str, board: str | None = None) -> list[dict]:
        """Get cards in deck with ownership status."""

    # User deck management
    def create_user_deck(self, name: str, format: str | None = None) -> dict:
        """Create new user deck."""

    def add_card_to_deck(self, deck_id: int, card_uuid: str, **kwargs) -> bool:
        """Add card to user deck."""

    def remove_card_from_deck(self, deck_id: int, card_uuid: str) -> bool:
        """Remove card from user deck."""
```

**Deck Card Response with Ownership**:
```python
{
    "card_uuid": "abc-123",
    "name": "Lightning Bolt",
    "count": 4,
    "board": "mainBoard",
    # ... card data ...
    "owns_enough": True,  # User owns >= count needed
    "owned_count": 8,     # Total owned by user
    "missing_count": 0    # count - min(count, owned_count)
}
```

---

### Task 2.4: Create Unified Prices Data Module

**File**: `src/mtgsim/api/data/prices.py`

**Changes**:
1. Query `MJCardPrice` instead of legacy price database
2. Simplify to direct model queries
3. Remove raw SQL connections

**New Interface**:
```python
class PricesData:
    def get_card_prices(self, uuid: str) -> dict | None:
        """Get all prices for a card."""

    def get_price(
        self,
        uuid: str,
        provider: str = "tcgplayer",
        finish: str = "normal"
    ) -> float | None:
        """Get specific price for a card."""

    def search_by_price(
        self,
        price_min: float | None = None,
        price_max: float | None = None,
        provider: str = "tcgplayer",
        ...
    ) -> tuple[list[dict], int]:
        """Search cards by price range."""
```

**Price Query**:
```python
def get_card_prices(self, uuid: str) -> dict | None:
    with get_session() as session:
        query = select(MJCardPrice).where(MJCardPrice.card_uuid == uuid)
        results = session.exec(query).all()

        if not results:
            return None

        # Structure by provider/finish
        prices = {}
        for price in results:
            key = f"{price.provider}_{price.finish}"
            prices[key] = price.price

        return {
            "tcgplayer": {
                "normal": prices.get("tcgplayer_normal"),
                "foil": prices.get("tcgplayer_foil"),
            },
            "cardmarket": {
                "normal": prices.get("cardmarket_normal"),
                "foil": prices.get("cardmarket_foil"),
            },
            # ...
        }
```

---

### Task 2.5: Create Helper Module

**File**: `src/mtgsim/api/data/helpers.py`

Shared utilities for the data layer:

```python
def build_image_url(scryfall_id: str | None) -> str | None:
    """Build Scryfall image URL from identifier."""
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"


def parse_json_column(value: str | list | None, default=None) -> list:
    """Parse JSON column value (handles both string and list)."""
    if value is None:
        return default if default is not None else []
    if isinstance(value, list):
        return value
    try:
        import json
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def apply_pagination(query, page: int, limit: int):
    """Apply pagination to query."""
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit)


def apply_sorting(query, model, sort: str, order: str, sort_map: dict):
    """Apply sorting to query."""
    sort_field = sort_map.get(sort, sort_map.get("name"))
    if order == "desc":
        return query.order_by(sort_field.desc())
    return query.order_by(sort_field.asc())
```

---

### Task 2.6: Update Data Layer Index

**File**: `src/mtgsim/api/data/__init__.py`

```python
"""Data access layer for mtgsim API.

All data access goes through unified database schema.
No scope parameter - collection status is automatic.
"""

from .cards import cards_data
from .sets import sets_data
from .decks import decks_data
from .prices import prices_data
from .helpers import build_image_url, parse_json_column

__all__ = [
    "cards_data",
    "sets_data",
    "decks_data",
    "prices_data",
    "build_image_url",
    "parse_json_column",
]
```

---

### Task 2.7: Remove Deprecated Files

After the new data modules are working:

**Files to delete**:
- `src/mtgsim/api/data/converters.py` (486 lines)
- `src/mtgsim/api/data/database.py` (legacy connections)

**Imports to update**:
- Remove all imports from `domain_models`, `reference_models`
- Remove all imports from `domain_session`
- Use `from mtgsim.db.models import MJCard, MJSet, UserCard, ...`
- Use `from mtgsim.db.session import get_session`

---

## Testing Strategy

### Unit Tests

**File**: `tests/api/test_data_access.py`

```python
import pytest
from mtgsim.db.session import get_session, init_db
from mtgsim.db.models import MJCard, MJCardIdentifier, UserCard
from mtgsim.api.data.cards import cards_data


@pytest.fixture
def test_db(tmp_path):
    """Create test database with sample data."""
    db_path = tmp_path / "test.sqlite"
    init_db(db_path)

    with get_session(db_path) as session:
        # Add reference card
        card = MJCard(
            uuid="test-uuid-1",
            name="Lightning Bolt",
            set_code="LEB",
            mana_cost="{R}",
            mana_value=1.0,
            type_line="Instant",
            rarity="common",
        )
        session.add(card)

        # Add identifier
        ident = MJCardIdentifier(
            card_uuid="test-uuid-1",
            scryfall_id="abc123def456"
        )
        session.add(ident)
        session.commit()

    return db_path


def test_search_cards_returns_all(test_db):
    """Search returns all cards by default."""
    results, total = cards_data.search_cards()
    assert total == 1
    assert results[0]["name"] == "Lightning Bolt"
    assert results[0]["owns"] is False


def test_search_cards_with_collection(test_db):
    """Search includes collection status."""
    # Add to collection
    with get_session(test_db) as session:
        user_card = UserCard(
            card_uuid="test-uuid-1",
            quantity_owned=4,
        )
        session.add(user_card)
        session.commit()

    results, total = cards_data.search_cards()
    assert results[0]["owns"] is True
    assert results[0]["total_owned"] == 4


def test_search_cards_filter_owns(test_db):
    """Filter by ownership status."""
    results, total = cards_data.search_cards(owns=True)
    assert total == 0  # No owned cards yet

    # Add to collection
    with get_session(test_db) as session:
        user_card = UserCard(card_uuid="test-uuid-1", quantity_owned=1)
        session.add(user_card)
        session.commit()

    results, total = cards_data.search_cards(owns=True)
    assert total == 1
```

### Integration Tests

Test that the full flow works with real data:

```python
def test_card_flow_with_prices(test_db):
    """Test card search includes prices."""
    with get_session(test_db) as session:
        price = MJCardPrice(
            card_uuid="test-uuid-1",
            provider="tcgplayer",
            listing_type="retail",
            finish="normal",
            price=0.99
        )
        session.add(price)
        session.commit()

    card = cards_data.get_card("test-uuid-1")
    assert card["prices"]["tcgplayer"]["normal"] == 0.99
```

---

## Migration Steps

### Step 1: Create New Files (Parallel)
Create new implementations without removing old ones:
- `src/mtgsim/api/data/cards_v2.py`
- `src/mtgsim/api/data/sets_v2.py`
- `src/mtgsim/api/data/decks_v2.py`
- `src/mtgsim/api/data/prices_v2.py`

### Step 2: Add Tests
Write comprehensive tests for new implementations.

### Step 3: Switch Imports
Update `__init__.py` to export from v2 modules:
```python
from .cards_v2 import cards_data  # Was from .cards
```

### Step 4: Test Full System
Run all API tests to verify behavior.

### Step 5: Remove Old Files
Delete old implementations and v2 suffix.

---

## File Changes Summary

### New Files
| File | Description | Lines (est) |
|------|-------------|-------------|
| `src/mtgsim/api/data/cards.py` | Unified cards data access | ~200 |
| `src/mtgsim/api/data/sets.py` | Unified sets data access | ~150 |
| `src/mtgsim/api/data/decks.py` | Unified decks data access | ~250 |
| `src/mtgsim/api/data/prices.py` | Unified prices data access | ~100 |
| `src/mtgsim/api/data/helpers.py` | Shared utilities | ~50 |
| `tests/api/test_data_access.py` | Unit tests | ~200 |

### Modified Files
| File | Changes |
|------|---------|
| `src/mtgsim/api/data/__init__.py` | Update exports |

### Deleted Files
| File | Lines Removed |
|------|---------------|
| `src/mtgsim/api/data/converters.py` | 486 |
| `src/mtgsim/api/data/database.py` | ~100 |

### Net Change
- **Before**: ~3,000 lines across data layer
- **After**: ~750 lines (75% reduction)

---

## Acceptance Criteria

1. [ ] All data access methods work without `scope` parameter
2. [ ] Every card response includes collection status (`owns`, `wants`, etc.)
3. [ ] `owns=True` filter returns only owned cards
4. [ ] `owns=False` filter returns only un-owned cards
5. [ ] Image URLs built from `mj_card_identifier.scryfall_id`
6. [ ] Prices loaded from `mj_card_price` table
7. [ ] All existing API tests pass (after router updates in Phase 3)
8. [ ] No imports from `domain_models`, `reference_models`, `domain_session`
9. [ ] `converters.py` deleted

---

## Dependencies on Other Phases

### From Phase 1 (Required)
- `MJCard`, `MJCardIdentifier`, `MJCardLegality`, `MJCardPrice` models
- `MJSet`, `MJDeck`, `MJDeckCard` models
- `UserCard`, `UserDeck`, `UserDeckCard` models
- `get_session()` from unified session

### For Phase 3 (API Layer)
- Data layer must be stable before updating routers
- New filter parameters (`owns`, `wants`) must be ready

### For Phase 4 (Sync)
- Sync must populate `mj_*` tables for data layer to work

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Query performance regression | High | Add indexes, benchmark queries |
| Missing data in unified DB | High | Run sync (Phase 4) before testing |
| Breaking API contracts | Medium | Keep response shapes compatible |
| Complex join queries | Medium | Use SQLModel relationships |

---

## Notes

### JSON Columns
The new `MJCard` model uses JSON columns for arrays:
```python
colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
```

SQLite JSON queries:
```python
# Check if color in list
from sqlalchemy import func
query.where(func.json_extract(MJCard.colors, "$").contains('"R"'))
```

### User Model Naming
Phase 1 used `UserCard`, `UserDeck`, `UserDeckCard` (not `Card`, `Deck`, `DeckCard` as originally planned). This is more explicit and avoids confusion with reference models.

### Image URL Generation
Always build from `MJCardIdentifier.scryfall_id`:
```python
def build_image_url(scryfall_id: str | None) -> str | None:
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"
```

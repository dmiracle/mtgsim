# Phase 3: Update API Layer

## Overview

This phase updates the API response models and tests to use the new collection status fields. Phase 2 already removed the `scope` parameter from routers and services. Phase 3 focuses on:

1. Updating response models with collection status fields
2. Removing the legacy `in_collection` boolean in favor of richer status
3. Updating Hurl tests for the new API behavior
4. Simplifying the services layer where possible

**Goal**: Response models reflect collection status, Hurl tests pass, services layer simplified

**Prerequisites**: Phase 2 complete (data access layer using unified schema)

---

## Current State

### Models Using `in_collection: bool`

| Model | File | Usage |
|-------|------|-------|
| `CardSummary` | `models/card.py` | Card list items |
| `CardDetail` | `models/card.py` | Single card detail |
| `CardPrinting` | `models/card.py` | Other printings |
| `SetSummary` | `models/set.py` | Set list items |
| `SetMeta` | `models/set.py` | Set metadata |
| `SetCard` | `models/set.py` | Cards within set |
| `DeckSummary` | `models/deck.py` | Deck list items |
| `DeckMeta` | `models/deck.py` | Deck metadata |
| `DeckCard` | `models/deck.py` | Cards within deck |

### Hurl Tests Using `scope` Parameter

All tests in `tests/hurl/cards.hurl`, `sets.hurl`, `decks.hurl` use `scope=reference` or `scope=combined`.

---

## Target State

### New Collection Status Model

```python
class CollectionStatus(BaseModel):
    """User's collection status for an item."""

    owns: bool = False                    # User owns at least one copy
    wants: bool = False                   # User wants at least one copy
    total_owned: int = 0                  # Total copies owned (regular + foil)
    total_wanted: int = 0                 # Total copies wanted (regular + foil)


class CollectionDetail(BaseModel):
    """Detailed collection quantities (only present if in collection)."""

    quantity_owned: int = 0
    quantity_owned_foil: int = 0
    quantity_wanted: int = 0
    quantity_wanted_foil: int = 0
    condition: str | None = None
    notes: str | None = None
```

### Updated Card Response

```json
{
  "uuid": "abc-123",
  "name": "Lightning Bolt",
  "mana_cost": "{R}",
  "type": "Instant",
  "rarity": "common",
  "set_code": "LEA",
  "image_url": "https://cards.scryfall.io/...",
  "owns": true,
  "wants": false,
  "total_owned": 4,
  "total_wanted": 0,
  "collection": {
    "quantity_owned": 3,
    "quantity_owned_foil": 1,
    "quantity_wanted": 0,
    "quantity_wanted_foil": 0,
    "condition": "NM",
    "notes": null
  }
}
```

### Updated Deck Card Response

```json
{
  "card_uuid": "abc-123",
  "name": "Lightning Bolt",
  "count": 4,
  "owns_enough": true,
  "owned_count": 8,
  "missing_count": 0
}
```

---

## Implementation Tasks

### Task 3.1: Add Collection Status Models

**File**: `src/mtgsim/api/models/common.py`

Add shared collection status models:

```python
class CollectionStatus(BaseModel):
    """User's collection status for an item."""

    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0


class CollectionDetail(BaseModel):
    """Detailed collection quantities."""

    quantity_owned: int = 0
    quantity_owned_foil: int = 0
    quantity_wanted: int = 0
    quantity_wanted_foil: int = 0
    condition: str | None = None
    notes: str | None = None
```

---

### Task 3.2: Update Card Models

**File**: `src/mtgsim/api/models/card.py`

**Changes**:

1. Replace `in_collection: bool` with collection status fields
2. Add optional `collection` detail for CardDetail
3. Update CardPrinting to use `owns` instead of `in_collection`

```python
class CardSummary(BaseModel):
    """Summary card information for list views."""

    uuid: str
    name: str
    type: str | None = None
    mana_cost: str | None = None
    mana_value: float | None = None
    rarity: str | None = None
    set_code: str | None = None
    color_identity: list[str] = []
    text: str | None = None
    price: float | None = None
    image_url: str | None = None

    # Collection status (replaces in_collection)
    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0


class CardPrinting(BaseModel):
    """Other printing of a card."""

    set_code: str
    set_name: str
    uuid: str
    image_url: str | None = None
    owns: bool = False
    total_owned: int = 0


class CardDetail(BaseModel):
    """Full card details."""

    uuid: str
    name: str
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    types: list[str] = []
    subtypes: list[str] = []
    supertypes: list[str] = []
    text: str | None = None
    flavor_text: str | None = None
    rarity: str | None = None
    set_code: str | None = None
    set_name: str | None = None
    number: str | None = None
    artist: str | None = None
    color_identity: list[str] = []
    colors: list[str] = []
    keywords: list[str] = []
    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    image_url: str | None = None
    prices: PriceBySource | None = None
    legalities: CardLegalities | None = None
    appears_in_decks: list[CardAppearance] = []
    other_printings: list[CardPrinting] = []

    # Collection status
    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0
    collection: CollectionDetail | None = None
```

---

### Task 3.3: Update Set Models

**File**: `src/mtgsim/api/models/set.py`

**Changes**:

1. Replace `in_collection` with collection stats on SetSummary/SetMeta
2. Update SetCard with `owns`/`wants` fields

```python
class SetCollectionStats(BaseModel):
    """Collection statistics for a set."""

    total_cards: int = 0
    owned_cards: int = 0
    owned_percentage: float = 0.0
    wanted_cards: int = 0


class SetSummary(BaseModel):
    """Summary set information for list views."""

    code: str
    name: str
    type: str
    release_date: str | None = None
    base_set_size: int = 0
    total_set_size: int = 0
    block: str | None = None
    keyrune_code: str | None = None
    collection_stats: SetCollectionStats | None = None


class SetCard(BaseModel):
    """Card within a set."""

    uuid: str
    name: str
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    rarity: str | None = None
    color_identity: list[str] = []
    colors: list[str] = []
    power: str | None = None
    toughness: str | None = None
    number: str | None = None
    text: str | None = None
    price: float | None = None
    image_url: str | None = None
    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0
```

---

### Task 3.4: Update Deck Models

**File**: `src/mtgsim/api/models/deck.py`

**Changes**:

1. Update DeckCard with ownership status for deck building
2. Add `source` field to DeckSummary
3. Replace `in_collection` with more specific fields

```python
class DeckCard(BaseModel):
    """Card within a deck."""

    uuid: str
    name: str
    count: int = 1
    board: str | None = None
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    types: list[str] = []
    colors: list[str] = []
    rarity: str | None = None
    text: str | None = None
    price: float | None = None
    image_url: str | None = None

    # Ownership for deck building
    owns_enough: bool = False     # User owns >= count needed
    owned_count: int = 0          # Total owned by user
    missing_count: int = 0        # count - min(count, owned_count)


class DeckSummary(BaseModel):
    """Summary deck information for list views."""

    file: str
    name: str
    code: str = ""
    deck_type: str | None = None
    card_count: int = 0
    colors: list[str] = []
    price: float | None = None
    release_date: str | None = None
    legality: DeckLegality | None = None
    source: str = "precon"        # "precon" or "user"


class DeckMeta(BaseModel):
    """Deck metadata."""

    file: str
    name: str
    code: str = ""
    deck_type: str | None = None
    release_date: str | None = None
    description: str | None = None
    format: str | None = None
    source: str = "precon"
```

---

### Task 3.5: Update Services to Map New Fields

**File**: `src/mtgsim/api/services/card_service.py`

Update the mapping from data layer dicts to response models:

```python
async def search_cards(...) -> CardListResponse:
    cards, total = cards_data.search_cards(...)

    data = []
    for c in cards:
        data.append(
            CardSummary(
                uuid=c["uuid"],
                name=c["name"],
                type=c.get("type"),
                mana_cost=c.get("mana_cost"),
                mana_value=c.get("mana_value"),
                rarity=c.get("rarity"),
                set_code=c.get("set_code"),
                color_identity=c.get("color_identity", []),
                text=c.get("oracle_text"),
                price=c.get("prices", {}).get("tcgplayer", {}).get("normal") if c.get("prices") else None,
                image_url=c.get("image_url"),
                # Collection status from data layer
                owns=c.get("owns", False),
                wants=c.get("wants", False),
                total_owned=c.get("total_owned", 0),
                total_wanted=c.get("total_wanted", 0),
            )
        )
    ...
```

Similar updates for `set_service.py` and `deck_service.py`.

---

### Task 3.6: Update Hurl Tests

**File**: `tests/hurl/cards.hurl`

Remove all `scope=` parameters and update assertions:

```hurl
# Cards Endpoint Tests

# Test cards list endpoint - default parameters
GET http://localhost:8000/api/cards
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 50


# Test cards list with search query
GET http://localhost:8000/api/cards?q=Lightning
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test cards list with owns filter
GET http://localhost:8000/api/cards?owns=true
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test cards list with wants filter
GET http://localhost:8000/api/cards?wants=true
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test cards list with set filter
GET http://localhost:8000/api/cards?set=LEA
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test cards list with pagination
GET http://localhost:8000/api/cards?page=1&limit=10
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination.page" == 1
jsonpath "$.pagination.limit" == 10


# Test get single card by UUID (capture first)
GET http://localhost:8000/api/cards?limit=1
HTTP 200
[Captures]
card_uuid: jsonpath "$.data[0].uuid"
[Asserts]
jsonpath "$.data[0].uuid" exists
jsonpath "$.data[0].name" exists
jsonpath "$.data[0].owns" exists
jsonpath "$.data[0].total_owned" exists


# Test get single card detail
GET http://localhost:8000/api/cards/{{card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.uuid" exists
jsonpath "$.name" exists
jsonpath "$.owns" exists
jsonpath "$.total_owned" exists


# Test card not found
GET http://localhost:8000/api/cards/00000000-0000-0000-0000-000000000000
HTTP 404


# Test invalid page
GET http://localhost:8000/api/cards?page=0
HTTP 422


# Test invalid limit
GET http://localhost:8000/api/cards?limit=101
HTTP 422
```

**File**: `tests/hurl/sets.hurl`

```hurl
# Sets Endpoint Tests

# Test sets list
GET http://localhost:8000/api/sets
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists
jsonpath "$.filters" exists


# Test sets list with has_owned_cards filter
GET http://localhost:8000/api/sets?has_owned_cards=true
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Test get single set
GET http://localhost:8000/api/sets?limit=1
HTTP 200
[Captures]
set_code: jsonpath "$.data[0].code"


GET http://localhost:8000/api/sets/{{set_code}}
HTTP 200
[Asserts]
jsonpath "$.meta" exists
jsonpath "$.meta.code" exists
jsonpath "$.cards" exists
jsonpath "$.cards.data" isCollection


# Test set cards with owns filter
GET http://localhost:8000/api/sets/{{set_code}}?owns=true
HTTP 200
[Asserts]
jsonpath "$.cards.data" isCollection


# Test set not found
GET http://localhost:8000/api/sets/INVALID
HTTP 404
```

**File**: `tests/hurl/decks.hurl`

```hurl
# Decks Endpoint Tests

# Test decks list
GET http://localhost:8000/api/decks
HTTP 200
[Asserts]
jsonpath "$.data" isCollection
jsonpath "$.pagination" exists


# Test decks list with source filter
GET http://localhost:8000/api/decks?source=precon
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


GET http://localhost:8000/api/decks?source=user
HTTP 200
[Asserts]
jsonpath "$.data" isCollection


# Capture a deck file
GET http://localhost:8000/api/decks?limit=1
HTTP 200
[Captures]
deck_file: jsonpath "$.data[0].file"


# Test get single deck
GET http://localhost:8000/api/decks/{{deck_file}}
HTTP 200
[Asserts]
jsonpath "$.meta" exists
jsonpath "$.main_board" isCollection
jsonpath "$.stats" exists


# Test deck cards have ownership info
GET http://localhost:8000/api/decks/{{deck_file}}
HTTP 200
[Asserts]
jsonpath "$.main_board[0].owns_enough" exists
jsonpath "$.main_board[0].owned_count" exists
jsonpath "$.main_board[0].missing_count" exists


# Test deck not found
GET http://localhost:8000/api/decks/INVALID.json
HTTP 404
```

---

### Task 3.7: Update Collection Hurl Tests

**File**: `tests/hurl/collection.hurl`

```hurl
# Collection Management Tests

# First, get a card UUID to work with
GET http://localhost:8000/api/cards?limit=1
HTTP 200
[Captures]
card_uuid: jsonpath "$.data[0].uuid"


# Add card to collection
POST http://localhost:8000/api/cards/{{card_uuid}}/collection?quantity_owned=4
HTTP 200
[Asserts]
jsonpath "$.success" == true
jsonpath "$.card.owns" == true
jsonpath "$.card.total_owned" == 4


# Verify card shows as owned
GET http://localhost:8000/api/cards/{{card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.owns" == true
jsonpath "$.total_owned" == 4


# Update quantities
POST http://localhost:8000/api/cards/{{card_uuid}}/collection?quantity_owned=2&quantity_wanted=1
HTTP 200
[Asserts]
jsonpath "$.success" == true


# Verify updates
GET http://localhost:8000/api/cards/{{card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.owns" == true
jsonpath "$.wants" == true
jsonpath "$.total_owned" == 2
jsonpath "$.total_wanted" == 1


# Remove from collection
DELETE http://localhost:8000/api/cards/{{card_uuid}}/collection
HTTP 200
[Asserts]
jsonpath "$.success" == true


# Verify removed
GET http://localhost:8000/api/cards/{{card_uuid}}
HTTP 200
[Asserts]
jsonpath "$.owns" == false
jsonpath "$.total_owned" == 0
```

---

### Task 3.8: Simplify Services Layer (Optional)

Evaluate if the services layer adds value or is just pass-through:

**Current Pattern**:
```
Router → Service → Data → Response
```

**If service is just mapping**:
```python
# card_service.py
async def search_cards(...) -> CardListResponse:
    cards, total = cards_data.search_cards(...)
    return CardListResponse(
        data=[CardSummary(**c) for c in cards],
        pagination=Pagination(...)
    )
```

**Could simplify to**:
```python
# router directly uses data layer
@router.get("", response_model=CardListResponse)
async def search_cards(...):
    cards, total = cards_data.search_cards(...)
    return CardListResponse(
        data=[CardSummary(**c) for c in cards],
        pagination=Pagination(...)
    )
```

**Decision**: Keep services for now because:
1. They handle response model construction
2. They're a good place for business logic if needed later
3. Removal is a bigger change that can be done in Phase 5

---

## File Changes Summary

### Modified Files

| File | Changes |
|------|---------|
| `src/mtgsim/api/models/common.py` | Add `CollectionStatus`, `CollectionDetail` |
| `src/mtgsim/api/models/card.py` | Replace `in_collection` with collection fields |
| `src/mtgsim/api/models/set.py` | Add `SetCollectionStats`, update fields |
| `src/mtgsim/api/models/deck.py` | Add ownership fields to `DeckCard` |
| `src/mtgsim/api/services/card_service.py` | Map new collection fields |
| `src/mtgsim/api/services/set_service.py` | Map new collection fields |
| `src/mtgsim/api/services/deck_service.py` | Map new collection fields |
| `tests/hurl/cards.hurl` | Remove scope, test new fields |
| `tests/hurl/sets.hurl` | Remove scope, test new fields |
| `tests/hurl/decks.hurl` | Remove scope, test new fields |
| `tests/hurl/collection.hurl` | Test collection endpoints |

---

## Acceptance Criteria

1. [ ] Response models include `owns`, `wants`, `total_owned`, `total_wanted` fields
2. [ ] `in_collection` boolean removed from all response models
3. [ ] CardDetail includes optional `collection` detail object
4. [ ] SetCard includes collection status fields
5. [ ] DeckCard includes `owns_enough`, `owned_count`, `missing_count`
6. [ ] All Hurl tests pass (after Phase 4 populates data)
7. [ ] No `scope` parameter in any Hurl tests
8. [ ] Services properly map data layer output to response models

---

## Dependencies

### From Phase 2 (Required)
- Data layer returns `owns`, `wants`, `total_owned`, `total_wanted` fields
- Data layer returns `collection` object when card is in user collection
- No `scope` parameter in data layer methods

### For Phase 4 (Sync)
- Hurl tests will fail until data is populated
- Run `mtgsim db sync` before testing

---

## Testing Strategy

### Unit Tests

Test response model construction:

```python
def test_card_summary_from_data():
    data = {
        "uuid": "test-uuid",
        "name": "Test Card",
        "owns": True,
        "total_owned": 4,
        ...
    }
    summary = CardSummary(**data)
    assert summary.owns is True
    assert summary.total_owned == 4
```

### Integration Tests

Test full API flow with test database:

```python
async def test_search_cards_includes_collection_status(client, test_db):
    # Add card to collection
    cards_data.add_to_collection("test-uuid", quantity_owned=2)

    # Search should return collection status
    response = client.get("/api/cards?q=Test")
    assert response.status_code == 200
    data = response.json()

    card = next(c for c in data["data"] if c["uuid"] == "test-uuid")
    assert card["owns"] is True
    assert card["total_owned"] == 2
```

### Hurl Tests

Run after Phase 4 sync:

```bash
# Start server
uv run mtgsim-api &

# Run Hurl tests
hurl --test tests/hurl/*.hurl
```

---

## Notes

### Backward Compatibility

The `in_collection` field is being replaced with `owns`. Clients using `in_collection` will need to update to use `owns`. Since this is a breaking change, consider:

1. Keep `in_collection` as deprecated alias for `owns`
2. Document the change in API changelog
3. Or just make the breaking change since this is internal tooling

### Field Naming

The data layer already returns:
- `owns: bool` - Has at least one copy owned
- `wants: bool` - Has at least one copy wanted
- `total_owned: int` - Sum of owned + owned_foil
- `total_wanted: int` - Sum of wanted + wanted_foil
- `collection: {...}` - Detailed quantities (optional)

Response models should use these exact names for consistency.

# JSON Array Normalization Plan

This document outlines the plan to normalize JSON array columns in `mj_card` and `mj_deck_card` into proper relational tables.

## Current State

### JSON Arrays in `mj_card`

| Column | Example Values | Cardinality |
|--------|---------------|-------------|
| `colors` | `["W", "U"]` | 5 values (W, U, B, R, G) |
| `color_identity` | `["W", "U", "B"]` | 5 values (W, U, B, R, G) |
| `types` | `["Creature", "Artifact"]` | ~10 values |
| `subtypes` | `["Human", "Wizard"]` | ~1000+ values |
| `supertypes` | `["Legendary", "Snow"]` | ~5 values |
| `keywords` | `["Flying", "Trample"]` | ~200+ values |

### JSON Arrays in `mj_deck_card`

| Column | Example Values | Notes |
|--------|---------------|-------|
| `colors` | `["R", "G"]` | Denormalized from card |
| `types` | `["Creature"]` | Denormalized from card |

---

## Source Data Location

**Source database:** `~/.mtgsim/reference/mtgjson/AllPrintings.sqlite`
**Source table:** `cards`

**Source query (current):**
```sql
SELECT uuid, name, setCode, ...,
       colors, colorIdentity, types, subtypes, supertypes, keywords, ...
FROM cards
```

The source columns contain JSON-encoded arrays:
- `colors` → `'["W","U"]'` or `'["W"]'` or `null`
- `colorIdentity` → `'["W","U","B"]'`
- `types` → `'["Creature","Artifact"]'`
- `subtypes` → `'["Human","Wizard"]'`
- `supertypes` → `'["Legendary"]'`
- `keywords` → `'["Flying","First strike"]'`

---

## Proposed Schema Changes

### New Reference Tables

These tables store the distinct values (lookup tables).

#### `mj_color`
```sql
CREATE TABLE mj_color (
    code TEXT PRIMARY KEY,  -- W, U, B, R, G
    name TEXT NOT NULL      -- White, Blue, Black, Red, Green
);
```

**Seed data:** Static, 5 rows
```
W -> White
U -> Blue
B -> Black
R -> Red
G -> Green
```

#### `mj_card_type`
```sql
CREATE TABLE mj_card_type (
    name TEXT PRIMARY KEY   -- Creature, Instant, Sorcery, etc.
);
```

**Source:** Extracted from `cards.types` during sync
**Expected rows:** ~15 (Artifact, Battle, Creature, Enchantment, Instant, Land, Planeswalker, Sorcery, Tribal, etc.)

#### `mj_subtype`
```sql
CREATE TABLE mj_subtype (
    name TEXT PRIMARY KEY   -- Human, Wizard, Elf, Forest, etc.
);
```

**Source:** Extracted from `cards.subtypes` during sync
**Expected rows:** ~1500+

#### `mj_supertype`
```sql
CREATE TABLE mj_supertype (
    name TEXT PRIMARY KEY   -- Basic, Legendary, Snow, World, Ongoing
);
```

**Source:** Extracted from `cards.supertypes` during sync
**Expected rows:** ~5

#### `mj_keyword`
```sql
CREATE TABLE mj_keyword (
    name TEXT PRIMARY KEY   -- Flying, Trample, Deathtouch, etc.
);
```

**Source:** Extracted from `cards.keywords` during sync
**Expected rows:** ~200+

---

### New Link Tables

These tables create many-to-many relationships between cards and their attributes.

#### `mj_card_color_link`
```sql
CREATE TABLE mj_card_color_link (
    card_uuid TEXT NOT NULL,
    color_code TEXT NOT NULL,
    PRIMARY KEY (card_uuid, color_code),
    FOREIGN KEY (card_uuid) REFERENCES mj_card(uuid),
    FOREIGN KEY (color_code) REFERENCES mj_color(code)
);
```

**Source:** `cards.colors` JSON array
**Index:** `card_uuid`, `color_code`

#### `mj_card_color_identity_link`
```sql
CREATE TABLE mj_card_color_identity_link (
    card_uuid TEXT NOT NULL,
    color_code TEXT NOT NULL,
    PRIMARY KEY (card_uuid, color_code),
    FOREIGN KEY (card_uuid) REFERENCES mj_card(uuid),
    FOREIGN KEY (color_code) REFERENCES mj_color(code)
);
```

**Source:** `cards.colorIdentity` JSON array
**Index:** `card_uuid`, `color_code`

#### `mj_card_type_link`
```sql
CREATE TABLE mj_card_type_link (
    card_uuid TEXT NOT NULL,
    type_name TEXT NOT NULL,
    PRIMARY KEY (card_uuid, type_name),
    FOREIGN KEY (card_uuid) REFERENCES mj_card(uuid),
    FOREIGN KEY (type_name) REFERENCES mj_card_type(name)
);
```

**Source:** `cards.types` JSON array
**Index:** `card_uuid`, `type_name`

#### `mj_card_subtype_link`
```sql
CREATE TABLE mj_card_subtype_link (
    card_uuid TEXT NOT NULL,
    subtype_name TEXT NOT NULL,
    PRIMARY KEY (card_uuid, subtype_name),
    FOREIGN KEY (card_uuid) REFERENCES mj_card(uuid),
    FOREIGN KEY (subtype_name) REFERENCES mj_subtype(name)
);
```

**Source:** `cards.subtypes` JSON array
**Index:** `card_uuid`, `subtype_name`

#### `mj_card_supertype_link`
```sql
CREATE TABLE mj_card_supertype_link (
    card_uuid TEXT NOT NULL,
    supertype_name TEXT NOT NULL,
    PRIMARY KEY (card_uuid, supertype_name),
    FOREIGN KEY (card_uuid) REFERENCES mj_card(uuid),
    FOREIGN KEY (supertype_name) REFERENCES mj_supertype(name)
);
```

**Source:** `cards.supertypes` JSON array
**Index:** `card_uuid`, `supertype_name`

#### `mj_card_keyword_link`
```sql
CREATE TABLE mj_card_keyword_link (
    card_uuid TEXT NOT NULL,
    keyword_name TEXT NOT NULL,
    PRIMARY KEY (card_uuid, keyword_name),
    FOREIGN KEY (card_uuid) REFERENCES mj_card(uuid),
    FOREIGN KEY (keyword_name) REFERENCES mj_keyword(name)
);
```

**Source:** `cards.keywords` JSON array
**Index:** `card_uuid`, `keyword_name`

---

## Complete Table Summary

### Reference Tables (5 new)

| Table | PK | Source | Expected Rows |
|-------|-----|--------|---------------|
| `mj_color` | `code` | Static seed | 5 |
| `mj_card_type` | `name` | `cards.types` | ~15 |
| `mj_subtype` | `name` | `cards.subtypes` | ~1500 |
| `mj_supertype` | `name` | `cards.supertypes` | ~5 |
| `mj_keyword` | `name` | `cards.keywords` | ~200 |

### Link Tables (6 new)

| Table | Composite PK | Source Column | Expected Rows |
|-------|--------------|---------------|---------------|
| `mj_card_color_link` | `(card_uuid, color_code)` | `cards.colors` | ~200k |
| `mj_card_color_identity_link` | `(card_uuid, color_code)` | `cards.colorIdentity` | ~250k |
| `mj_card_type_link` | `(card_uuid, type_name)` | `cards.types` | ~150k |
| `mj_card_subtype_link` | `(card_uuid, subtype_name)` | `cards.subtypes` | ~200k |
| `mj_card_supertype_link` | `(card_uuid, supertype_name)` | `cards.supertypes` | ~30k |
| `mj_card_keyword_link` | `(card_uuid, keyword_name)` | `cards.keywords` | ~300k |

---

## Sync Implementation Plan

### Phase 1: Add Models

**File:** `src/mtgsim/db/models.py`

Add 11 new SQLModel classes:
- `MJColor` (reference)
- `MJCardType` (reference)
- `MJSubtype` (reference)
- `MJSupertype` (reference)
- `MJKeyword` (reference)
- `MJCardColorLink` (link)
- `MJCardColorIdentityLink` (link)
- `MJCardTypeLink` (link)
- `MJCardSubtypeLink` (link)
- `MJCardSupertypeLink` (link)
- `MJCardKeywordLink` (link)

### Phase 2: Update Sync Functions

**File:** `src/mtgsim/sync/unified.py`

#### New function: `_seed_colors()`
```python
def _seed_colors(session):
    """Seed the mj_color reference table."""
    colors = [
        ("W", "White"),
        ("U", "Blue"),
        ("B", "Black"),
        ("R", "Red"),
        ("G", "Green"),
    ]
    for code, name in colors:
        session.add(MJColor(code=code, name=name))
    session.commit()
```

#### Modified function: `sync_cards()`

After inserting cards, add these steps:

1. **Collect distinct values** from JSON arrays:
   ```python
   # Collect all distinct types, subtypes, supertypes, keywords
   types_set = set()
   subtypes_set = set()
   supertypes_set = set()
   keywords_set = set()

   for row in cursor:
       types_set.update(_parse_json_or_list(row["types"]))
       subtypes_set.update(_parse_json_or_list(row["subtypes"]))
       supertypes_set.update(_parse_json_or_list(row["supertypes"]))
       keywords_set.update(_parse_json_or_list(row["keywords"]))
   ```

2. **Insert reference tables:**
   ```python
   for type_name in types_set:
       session.add(MJCardType(name=type_name))
   # ... same for subtypes, supertypes, keywords
   ```

3. **Insert link tables:**
   ```python
   for row in cursor:
       card_uuid = row["uuid"]
       for color in _parse_json_or_list(row["colors"]):
           session.add(MJCardColorLink(card_uuid=card_uuid, color_code=color))
       # ... same for other arrays
   ```

#### New function: `_sync_card_links()`
```python
def _sync_card_links(conn, engine):
    """Sync card link tables from JSON arrays."""
    # Clear existing links
    # Insert new links from JSON arrays
```

### Phase 3: Update Delete Order

The `sync_cards()` function must delete link tables BEFORE reference tables:

```python
# Delete order (respect FK constraints)
session.exec(delete(MJCardColorLink))
session.exec(delete(MJCardColorIdentityLink))
session.exec(delete(MJCardTypeLink))
session.exec(delete(MJCardSubtypeLink))
session.exec(delete(MJCardSupertypeLink))
session.exec(delete(MJCardKeywordLink))
session.exec(delete(MJCardType))
session.exec(delete(MJSubtype))
session.exec(delete(MJSupertype))
session.exec(delete(MJKeyword))
# Then delete cards
session.exec(delete(MJCard))
```

---

## Migration Strategy

### Option A: Keep JSON columns (recommended)

Keep the JSON columns in `mj_card` for backward compatibility and query convenience, but also populate the link tables for relational queries.

**Pros:**
- No breaking changes to existing queries
- Link tables available for complex queries
- Gradual migration path

**Cons:**
- Data duplication
- Slightly larger database

### Option B: Remove JSON columns

Remove JSON columns after link tables are populated.

**Pros:**
- No data duplication
- Cleaner normalized schema

**Cons:**
- Breaking change for existing code
- Requires updating all queries

### Recommendation

**Use Option A** - Keep JSON columns for now, add link tables alongside. This allows:
1. Existing API code continues to work
2. New queries can use link tables for JOINs
3. Future migration to remove JSON columns if desired

---

## Query Examples (After Implementation)

### Find all blue creatures
```sql
SELECT c.* FROM mj_card c
JOIN mj_card_color_link col ON c.uuid = col.card_uuid
JOIN mj_card_type_link typ ON c.uuid = typ.card_uuid
WHERE col.color_code = 'U' AND typ.type_name = 'Creature';
```

### Find all cards with Flying
```sql
SELECT c.* FROM mj_card c
JOIN mj_card_keyword_link kw ON c.uuid = kw.card_uuid
WHERE kw.keyword_name = 'Flying';
```

### Get color distribution for a set
```sql
SELECT col.color_code, COUNT(*) as count
FROM mj_card c
JOIN mj_card_color_link col ON c.uuid = col.card_uuid
WHERE c.set_code = 'MKM'
GROUP BY col.color_code;
```

### Find all legendary creatures
```sql
SELECT c.* FROM mj_card c
JOIN mj_card_supertype_link sup ON c.uuid = sup.card_uuid
JOIN mj_card_type_link typ ON c.uuid = typ.card_uuid
WHERE sup.supertype_name = 'Legendary' AND typ.type_name = 'Creature';
```

---

## Estimated Row Counts

| Table | Est. Rows | Size Impact |
|-------|-----------|-------------|
| `mj_color` | 5 | Negligible |
| `mj_card_type` | 15 | Negligible |
| `mj_subtype` | 1,500 | ~50KB |
| `mj_supertype` | 5 | Negligible |
| `mj_keyword` | 200 | ~10KB |
| `mj_card_color_link` | 200,000 | ~8MB |
| `mj_card_color_identity_link` | 250,000 | ~10MB |
| `mj_card_type_link` | 150,000 | ~6MB |
| `mj_card_subtype_link` | 200,000 | ~10MB |
| `mj_card_supertype_link` | 30,000 | ~1MB |
| `mj_card_keyword_link` | 300,000 | ~15MB |

**Total estimated increase:** ~50MB

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/mtgsim/db/models.py` | Add 11 new model classes |
| `src/mtgsim/sync/unified.py` | Update `sync_cards()`, add `_sync_card_links()` |
| `src/mtgsim/db/session.py` | No changes (models auto-register) |

---

## Testing Plan

1. Run `mtgsim db sync` on fresh database
2. Verify reference tables have expected row counts
3. Verify link tables have expected row counts
4. Verify JSON columns still populated (backward compat)
5. Test sample queries using link tables
6. Verify API still works (uses JSON columns)

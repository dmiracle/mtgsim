# MTG Webapp REST API Design

## Overview

This document defines a REST API to replace the client-side data handling in the MTG Deck Viewer webapp. The API will provide endpoints for browsing decks, sets, cards, and prices with server-side filtering, pagination, and calculations.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   REST API      │────▶│   Data Layer    │
│   (index.html)  │◀────│   (Python)      │◀────│   (SQLite/JSON) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │
                              ▼
                        ┌─────────────────┐
                        │   Cache Layer   │
                        │   (Redis/Mem)   │
                        └─────────────────┘
```

## Data Sources

| Source | Content | Size |
|--------|---------|------|
| `AllPrintings.sqlite` | Complete card database | ~800MB |
| `AllDeckFiles/*.json` | 2,648 deck files | ~200MB |
| `AllSetFiles/*.json` | 844 set files | ~1.5GB |
| `AllPricesToday.json` | Daily price data | ~150MB |
| `Keywords.json` | MTG keyword definitions | ~50KB |

---

## API Endpoints

### 1. Decks

#### `GET /api/decks`

List and filter decks with pagination.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search by deck name or code |
| `format` | string | Filter by format legality (standard, modern, etc.) |
| `set` | string | Filter by set code |
| `type` | string | Filter by deck type (60, 100) |
| `colors` | string | Filter by color identity (e.g., "WU", "BRG") |
| `price_min` | number | Minimum deck price |
| `price_max` | number | Maximum deck price |
| `sort` | string | Sort field (name, release_date, card_count, price, colors) |
| `order` | string | Sort order (asc, desc) |
| `page` | integer | Page number (default: 1) |
| `limit` | integer | Items per page (default: 50, max: 100) |

**Response:**
```json
{
  "data": [
    {
      "file": "AggressiveRecruitment_KLD.json",
      "name": "Aggressive Recruitment",
      "code": "KLD",
      "card_count": 60,
      "colors": ["W", "R"],
      "price": 45.67,
      "release_date": "2016-09-30",
      "legality": {
        "standard": false,
        "pioneer": true,
        "modern": true,
        "legacy": true,
        "vintage": true,
        "commander": true
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 2648,
    "pages": 53
  },
  "filters": {
    "formats": ["standard", "pioneer", "modern", ...],
    "sets": ["KLD", "AER", ...],
    "color_combinations": [["W"], ["U"], ["W", "U"], ...]
  }
}
```

**Server Logic:**
1. Parse and validate query parameters
2. Build SQL/filter query based on parameters
3. For price filtering: join with pre-calculated deck prices table
4. For color filtering: join with pre-calculated deck colors table
5. Apply sorting (price/color sorts require pre-calculated data)
6. Execute paginated query
7. Return results with pagination metadata

---

#### `GET /api/decks/{file}`

Get full deck details including cards and statistics.

**Response:**
```json
{
  "meta": {
    "file": "AggressiveRecruitment_KLD.json",
    "name": "Aggressive Recruitment",
    "code": "KLD",
    "release_date": "2016-09-30"
  },
  "legality": {
    "standard": false,
    "pioneer": true,
    "modern": true,
    "legacy": true,
    "vintage": true,
    "commander": true
  },
  "colors": ["W", "R"],
  "price": {
    "total": 45.67,
    "by_source": {
      "tcgplayer": 44.50,
      "cardkingdom": 48.00,
      "cardsphere": 44.50
    }
  },
  "commander": [],
  "main_board": [
    {
      "uuid": "abc-123",
      "name": "Lightning Bolt",
      "count": 4,
      "mana_cost": "{R}",
      "mana_value": 1,
      "type": "Instant",
      "rarity": "common",
      "price": 2.50,
      "image_url": "https://cards.scryfall.io/..."
    }
  ],
  "side_board": [...],
  "stats": {
    "total_cards": 60,
    "unique_cards": 24,
    "mana_curve": {
      "0": 0, "1": 12, "2": 16, "3": 12, "4": 8, "5": 4, "6+": 8
    },
    "type_distribution": {
      "creature": 24,
      "instant": 8,
      "sorcery": 4,
      "enchantment": 4,
      "land": 20
    },
    "rarity_distribution": {
      "common": 20,
      "uncommon": 16,
      "rare": 20,
      "mythic": 4
    },
    "color_distribution": {
      "W": 16, "R": 20, "colorless": 24
    },
    "price_histogram": [
      {"range": "0-1", "count": 20},
      {"range": "1-5", "count": 15},
      {"range": "5-10", "count": 8},
      {"range": "10+", "count": 4}
    ],
    "keywords": {
      "ability_words": {"battalion": 4, "raid": 2},
      "keyword_abilities": {"haste": 8, "first strike": 4},
      "keyword_actions": {"destroy": 6, "exile": 2}
    }
  }
}
```

**Server Logic:**
1. Load deck JSON file from disk
2. For each card, fetch current price from price cache
3. Calculate deck statistics:
   - Mana curve: group cards by mana value
   - Type distribution: count by card type
   - Rarity distribution: count by rarity
   - Color distribution: count by color identity
   - Price histogram: bin prices into ranges
4. Extract keywords by matching card text against Keywords.json
5. Calculate total price by summing (card_price × count)
6. Build response with all data

---

#### `GET /api/decks/{file}/raw`

Get raw deck JSON for developer inspection.

**Response:** Raw deck file JSON

---

### 2. Sets

#### `GET /api/sets`

List and filter sets with pagination.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search by set name or code |
| `type` | string | Filter by set type (core, expansion, masters, etc.) |
| `block` | string | Filter by block name |
| `sort` | string | Sort field (name, release_date, size) |
| `order` | string | Sort order (asc, desc) |
| `page` | integer | Page number |
| `limit` | integer | Items per page |

**Response:**
```json
{
  "data": [
    {
      "code": "KLD",
      "name": "Kaladesh",
      "type": "expansion",
      "release_date": "2016-09-30",
      "base_set_size": 264,
      "total_set_size": 302,
      "block": "Kaladesh",
      "keyrune_code": "kld"
    }
  ],
  "pagination": {...},
  "filters": {
    "types": ["core", "expansion", "masters", ...],
    "blocks": ["Kaladesh", "Amonkhet", ...]
  }
}
```

**Server Logic:**
1. Query sets index (pre-generated or from SQLite)
2. Apply filters and sorting
3. Return paginated results

---

#### `GET /api/sets/{code}`

Get full set details including cards and statistics.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `rarity` | string | Filter cards by rarity |
| `color` | string | Filter cards by color |
| `type` | string | Filter cards by type |
| `page` | integer | Page for cards |
| `limit` | integer | Cards per page |

**Response:**
```json
{
  "meta": {
    "code": "KLD",
    "name": "Kaladesh",
    "type": "expansion",
    "release_date": "2016-09-30",
    "base_set_size": 264,
    "total_set_size": 302,
    "block": "Kaladesh"
  },
  "stats": {
    "rarity_count": {
      "common": 101,
      "uncommon": 80,
      "rare": 53,
      "mythic": 15
    },
    "price": {
      "total": 1234.56,
      "by_source": {
        "tcgplayer": 1200.00,
        "cardkingdom": 1300.00,
        "cardmarket": 1100.00
      }
    },
    "price_histogram": [...],
    "keywords": {
      "ability_words": {"energy": 45, "fabricate": 12},
      "keyword_abilities": {"flying": 20, "trample": 15},
      "keyword_actions": {"create": 30, "destroy": 25}
    },
    "text_by_color": {
      "W": {"word_frequencies": {"creature": 50, "life": 30, ...}},
      "U": {"word_frequencies": {"draw": 40, "counter": 25, ...}},
      ...
    }
  },
  "cards": {
    "data": [
      {
        "uuid": "abc-123",
        "name": "Aether Hub",
        "type": "Land",
        "rarity": "uncommon",
        "color_identity": [],
        "price": 1.50,
        "image_url": "https://cards.scryfall.io/..."
      }
    ],
    "pagination": {...}
  }
}
```

**Server Logic:**
1. Load set JSON file from disk
2. Calculate statistics:
   - Rarity distribution
   - Total price by source
   - Price histogram
   - Keyword frequencies
   - Word frequencies by color (for word clouds)
3. Filter and paginate cards
4. Return combined response

---

### 3. Cards

#### `GET /api/cards`

Search cards with filters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search by card name |
| `set` | string | Filter by set code |
| `rarity` | string | Filter by rarity |
| `type` | string | Filter by card type |
| `colors` | string | Filter by color identity |
| `price_min` | number | Minimum price |
| `price_max` | number | Maximum price |
| `sort` | string | Sort field (name, price, mana_value) |
| `order` | string | Sort order |
| `page` | integer | Page number |
| `limit` | integer | Items per page |

**Response:**
```json
{
  "data": [
    {
      "uuid": "abc-123",
      "name": "Lightning Bolt",
      "type": "Instant",
      "mana_cost": "{R}",
      "mana_value": 1,
      "rarity": "common",
      "set_code": "M10",
      "color_identity": ["R"],
      "price": 2.50,
      "image_url": "https://cards.scryfall.io/..."
    }
  ],
  "pagination": {...}
}
```

**Server Logic:**
1. Query card_index (pre-loaded in memory or SQLite)
2. Apply text search on name field
3. Apply filters (set, rarity, type, colors, price range)
4. Join with price data for price filtering/sorting
5. Return paginated results

---

#### `GET /api/cards/{uuid}`

Get full card details.

**Response:**
```json
{
  "uuid": "abc-123",
  "name": "Lightning Bolt",
  "mana_cost": "{R}",
  "mana_value": 1,
  "type": "Instant",
  "types": ["Instant"],
  "text": "Lightning Bolt deals 3 damage to any target.",
  "flavor_text": "The spark mage shrieked...",
  "rarity": "common",
  "set_code": "M10",
  "set_name": "Magic 2010",
  "color_identity": ["R"],
  "colors": ["R"],
  "power": null,
  "toughness": null,
  "image_url": "https://cards.scryfall.io/...",
  "prices": {
    "tcgplayer": 2.50,
    "cardkingdom": 2.99,
    "cardsphere": 2.25,
    "cardmarket": 1.80,
    "mtgo": 0.50
  },
  "legalities": {
    "standard": "Not Legal",
    "pioneer": "Not Legal",
    "modern": "Legal",
    "legacy": "Legal",
    "vintage": "Legal",
    "commander": "Legal"
  },
  "appears_in_decks": [
    {"file": "BurnDeck_M10.json", "name": "Burn Deck", "count": 4},
    {"file": "RedAggro_RTR.json", "name": "Red Aggro", "count": 4}
  ],
  "other_printings": [
    {"set_code": "A25", "set_name": "Masters 25", "uuid": "def-456"},
    {"set_code": "2XM", "set_name": "Double Masters", "uuid": "ghi-789"}
  ]
}
```

**Server Logic:**
1. Fetch card data from SQLite/card_index
2. Fetch price data from price cache
3. Query card-to-decks mapping for deck appearances
4. Query other printings by card name
5. Build complete response

---

### 4. Prices

#### `GET /api/prices`

Search price data with filters.

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `q` | string | Search by card name |
| `set` | string | Filter by set code |
| `rarity` | string | Filter by rarity |
| `price_min` | number | Minimum price |
| `price_max` | number | Maximum price |
| `sort` | string | Sort by price source or average |
| `order` | string | Sort order |
| `page` | integer | Page number |
| `limit` | integer | Items per page |

**Response:**
```json
{
  "data": [
    {
      "uuid": "abc-123",
      "name": "Black Lotus",
      "set_code": "LEA",
      "rarity": "rare",
      "image_url": "https://cards.scryfall.io/...",
      "prices": {
        "tcgplayer": 50000.00,
        "cardkingdom": 55000.00,
        "cardsphere": 48000.00,
        "cardmarket": 45000.00,
        "mtgo": null
      },
      "average_usd": 51000.00
    }
  ],
  "pagination": {...},
  "meta": {
    "last_updated": "2024-01-05T00:00:00Z",
    "total_cards_with_prices": 105230
  }
}
```

**Server Logic:**
1. Search card_index by name
2. Join with price data
3. Apply filters
4. Calculate average USD price
5. Sort and paginate

---

#### `GET /api/prices/{uuid}`

Get detailed price data for a card.

**Response:**
```json
{
  "uuid": "abc-123",
  "name": "Lightning Bolt",
  "set_code": "M10",
  "prices": {
    "paper": {
      "tcgplayer": {
        "retail": {"normal": 2.50, "foil": 5.00},
        "buylist": {"normal": 1.50, "foil": 3.00}
      },
      "cardkingdom": {
        "retail": {"normal": 2.99, "foil": 6.00},
        "buylist": {"normal": 1.75, "foil": 3.50}
      },
      "cardsphere": {...},
      "cardmarket": {...}
    },
    "mtgo": {
      "cardhoarder": {
        "retail": {"normal": 0.50, "foil": 1.00}
      }
    }
  },
  "price_history": [
    {"date": "2024-01-01", "tcgplayer": 2.45},
    {"date": "2024-01-02", "tcgplayer": 2.48},
    ...
  ]
}
```

---

### 5. Statistics / Aggregates

#### `GET /api/stats/home`

Get aggregate statistics for home screen.

**Response:**
```json
{
  "total_decks": 2648,
  "total_sets": 844,
  "total_cards": 105230,
  "total_cards_with_prices": 95000,
  "format_distribution": {
    "standard": 150,
    "pioneer": 300,
    "modern": 800,
    "legacy": 500,
    "commander": 898
  },
  "price_histogram": [
    {"range": "0-50", "count": 500},
    {"range": "50-100", "count": 400},
    {"range": "100-500", "count": 800},
    {"range": "500+", "count": 948}
  ],
  "recent_sets": [
    {"code": "MKM", "name": "Murders at Karlov Manor", "release_date": "2024-02-09"}
  ],
  "most_expensive_cards": [
    {"name": "Black Lotus", "price": 50000.00, "set_code": "LEA"}
  ]
}
```

**Server Logic:**
1. Query pre-calculated aggregate statistics
2. Generate price histogram from deck prices
3. Fetch recent sets by release date
4. Fetch top N expensive cards
5. Cache results (update periodically)

---

#### `GET /api/stats/decks`

Get deck-specific aggregate statistics.

**Response:**
```json
{
  "by_format": {...},
  "by_set": {...},
  "by_color_combination": {...},
  "price_distribution": {...},
  "average_deck_price": 125.50,
  "average_deck_size": 68.5
}
```

---

### 6. Reference Data

#### `GET /api/keywords`

Get MTG keywords for glossary.

**Response:**
```json
{
  "ability_words": [
    {"term": "Battalion", "definition": "Whenever this creature and at least two other creatures attack..."}
  ],
  "keyword_abilities": [
    {"term": "Flying", "definition": "This creature can't be blocked except by creatures with flying or reach."}
  ],
  "keyword_actions": [
    {"term": "Destroy", "definition": "Move a permanent from the battlefield to its owner's graveyard."}
  ]
}
```

---

#### `GET /api/formats`

Get available format information.

**Response:**
```json
{
  "formats": [
    {"id": "standard", "name": "Standard", "description": "...", "deck_count": 150},
    {"id": "modern", "name": "Modern", "description": "...", "deck_count": 800}
  ]
}
```

---

## Server-Side Processing

### Startup / Initialization

```python
# Pseudo-code for server initialization

def initialize():
    # 1. Load price data into memory/Redis
    price_data = load_json("AllPricesToday.json")
    cache.set("prices", price_data)

    # 2. Build deck index with pre-calculated prices and colors
    deck_index = []
    for deck_file in glob("AllDeckFiles/*.json"):
        deck = load_json(deck_file)
        deck_meta = {
            "file": deck_file.name,
            "name": extract_deck_name(deck),
            "code": deck.get("code"),
            "card_count": count_cards(deck),
            "colors": extract_colors(deck),
            "price": calculate_deck_price(deck, price_data),
            "legality": calculate_legality(deck),
            "release_date": get_release_date(deck.code)
        }
        deck_index.append(deck_meta)
    cache.set("deck_index", deck_index)

    # 3. Build card-to-decks mapping
    card_to_decks = defaultdict(list)
    for deck in deck_index:
        for card in get_all_cards(deck):
            card_to_decks[card.uuid].append(deck.file)
    cache.set("card_to_decks", card_to_decks)

    # 4. Load set index
    set_index = load_json("sets.json")  # or build from AllSetFiles
    cache.set("set_index", set_index)

    # 5. Load card index into memory
    card_index = load_json("card_index.json")
    cache.set("card_index", card_index)

    # 6. Load keywords
    keywords = load_json("Keywords.json")
    cache.set("keywords", keywords)
```

### Price Calculation

```python
def calculate_deck_price(deck_data, price_data):
    """Calculate total deck price from all cards."""
    total = 0.0
    for card in get_all_cards(deck_data):
        price = get_average_usd_price(card.uuid, price_data)
        total += price * card.count
    return round(total, 2)

def get_average_usd_price(uuid, price_data):
    """Average price from USD paper sources."""
    card_prices = price_data.get("data", {}).get(uuid, {})
    paper = card_prices.get("paper", {})

    usd_prices = []
    for source in ["tcgplayer", "cardkingdom", "cardsphere"]:
        if source in paper:
            retail = paper[source].get("retail", {}).get("normal", {})
            if retail:
                # Get most recent price (first key)
                price = list(retail.values())[0]
                if price:
                    usd_prices.append(float(price))

    if not usd_prices:
        return 0.0
    return sum(usd_prices) / len(usd_prices)
```

### Deck Statistics Calculation

```python
def calculate_deck_stats(deck_data, price_data, keywords_data):
    """Calculate comprehensive deck statistics."""
    all_cards = get_all_cards(deck_data)

    stats = {
        "total_cards": sum(c.count for c in all_cards),
        "unique_cards": len(all_cards),
        "mana_curve": defaultdict(int),
        "type_distribution": defaultdict(int),
        "rarity_distribution": defaultdict(int),
        "color_distribution": defaultdict(int),
        "price_histogram": [],
        "keywords": {
            "ability_words": defaultdict(int),
            "keyword_abilities": defaultdict(int),
            "keyword_actions": defaultdict(int)
        }
    }

    prices = []
    for card in all_cards:
        # Mana curve
        mv = min(card.mana_value, 6)
        bucket = "6+" if mv >= 6 else str(mv)
        stats["mana_curve"][bucket] += card.count

        # Type distribution
        for card_type in card.types:
            stats["type_distribution"][card_type] += card.count

        # Rarity
        stats["rarity_distribution"][card.rarity] += card.count

        # Colors
        for color in card.color_identity or ["colorless"]:
            stats["color_distribution"][color] += card.count

        # Price
        price = get_average_usd_price(card.uuid, price_data)
        if price > 0:
            prices.append(price)

        # Keywords
        text = (card.text or "").lower()
        for kw in keywords_data["data"]["abilityWords"]:
            if kw.lower() in text:
                stats["keywords"]["ability_words"][kw] += card.count
        # ... similar for other keyword types

    # Build price histogram
    stats["price_histogram"] = build_histogram(prices)

    return stats
```

### Text Analysis for Word Clouds

```python
STOP_WORDS = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to",
              "for", "of", "with", "by", "target", "card", "creature", ...}

def extract_word_frequencies(texts):
    """Extract word frequencies for word cloud generation."""
    word_counts = defaultdict(int)

    for text in texts:
        # Remove punctuation and split
        words = re.sub(r'[^\w\s]', '', text.lower()).split()
        for word in words:
            if len(word) > 2 and word not in STOP_WORDS:
                word_counts[word] += 1

    # Return top N words
    sorted_words = sorted(word_counts.items(), key=lambda x: -x[1])
    return [{"word": w, "count": c} for w, c in sorted_words[:50]]
```

---

## Caching Strategy

| Data | Cache Type | TTL | Invalidation |
|------|------------|-----|--------------|
| Price data | Memory/Redis | 24h | Daily price update |
| Deck index | Memory | Until restart | Manual |
| Set index | Memory | Until restart | Manual |
| Card index | Memory | Until restart | Manual |
| Card-to-decks | Memory | Until restart | Manual |
| Individual deck stats | LRU cache | 1h | - |
| Individual set stats | LRU cache | 1h | - |
| Aggregate stats | Memory | 1h | Periodic refresh |

---

## Error Responses

All errors return consistent format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Deck not found: InvalidDeck.json",
    "details": {}
  }
}
```

| HTTP Code | Error Code | Description |
|-----------|------------|-------------|
| 400 | BAD_REQUEST | Invalid query parameters |
| 404 | NOT_FOUND | Resource not found |
| 500 | INTERNAL_ERROR | Server error |

---

## Performance Considerations

1. **Pre-calculate on startup**: Deck prices, colors, legalities
2. **Lazy load**: Individual deck/set details only when requested
3. **Pagination**: All list endpoints paginated (max 100 items)
4. **Caching**: Aggressive caching of computed statistics
5. **Streaming**: Consider streaming for large datasets
6. **Indexing**: SQLite indexes on name, set_code, uuid fields

---

## Implementation Stack Recommendation

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | FastAPI (Python) | Async, automatic OpenAPI docs, Pydantic validation |
| Database | SQLite | Already have AllPrintings.sqlite, embedded, fast reads |
| Cache | Redis or in-memory dict | Fast lookups, optional persistence |
| Search | SQLite FTS5 or Elasticsearch | Full-text search on card names |

---

## Migration Path

1. **Phase 1**: Implement read-only endpoints, frontend fetches from API
2. **Phase 2**: Move filtering/sorting logic to API
3. **Phase 3**: Remove client-side IndexedDB, all caching server-side
4. **Phase 4**: Add authentication for future features (user decks, etc.)

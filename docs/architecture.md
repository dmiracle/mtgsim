# MTG Webapp Architecture Documentation

This document provides a comprehensive overview of the MTG Deck Viewer webapp architecture, including the API backend and web frontend.

## System Overview

```mermaid
graph TB
    subgraph "Frontend (web/index.html)"
        UI[Single Page App]
        API_CLIENT[API Client]
        STATE[Application State]
    end

    subgraph "Backend (FastAPI)"
        FASTAPI[FastAPI App]
        ROUTERS[API Routers]
        SERVICES[Service Layer]
        DATA[Data Access Layer]
    end

    subgraph "SQLite Databases"
        SETS_DB[(AllSets.sqlite)]
        DECKS_DB[(AllDecks.sqlite)]
        PRICES_DB[(AllPricesToday.sqlite)]
        PRINTINGS_DB[(AllPrintings.sqlite)]
    end

    UI --> API_CLIENT
    API_CLIENT -->|HTTP/JSON| FASTAPI
    FASTAPI --> ROUTERS
    ROUTERS --> SERVICES
    SERVICES --> DATA
    DATA --> SETS_DB
    DATA --> DECKS_DB
    DATA --> PRICES_DB
    DATA --> PRINTINGS_DB
```

## Backend Architecture

### Layer Structure

```mermaid
graph LR
    subgraph "API Layer"
        R1[decks_router]
        R2[sets_router]
        R3[cards_router]
        R4[prices_router]
        R5[stats_router]
        R6[keywords_router]
    end

    subgraph "Service Layer"
        S1[deck_service]
        S2[set_service]
        S3[card_service]
        S4[price_service]
        S5[stats_service]
    end

    subgraph "Data Layer"
        D1[decks_data]
        D2[sets_data]
        D3[cards_data]
        D4[prices_data]
    end

    R1 --> S1 --> D1
    R2 --> S2 --> D2
    R3 --> S3 --> D3
    R4 --> S4 --> D4
    R5 --> S5
```

### File Structure

```
src/mtgsim/api/
├── main.py              # FastAPI app, lifespan, routing
├── cli.py               # CLI entry point
├── routers/
│   ├── decks.py         # /api/decks endpoints
│   ├── sets.py          # /api/sets endpoints
│   ├── cards.py         # /api/cards endpoints
│   ├── prices.py        # /api/prices endpoints
│   ├── stats.py         # /api/stats endpoints
│   └── keywords.py      # /api/keywords endpoints
├── services/
│   ├── deck_service.py  # Deck business logic
│   ├── set_service.py   # Set business logic
│   ├── card_service.py  # Card business logic
│   ├── price_service.py # Price business logic
│   └── stats_service.py # Statistics aggregation
├── data/
│   ├── database.py      # DatabaseManager singleton
│   ├── decks.py         # Deck SQL queries
│   ├── sets.py          # Set SQL queries
│   ├── cards.py         # Card SQL queries
│   ├── prices.py        # Price SQL queries
│   └── keywords.py      # Keyword data
└── models/
    ├── common.py        # Pagination, errors
    ├── deck.py          # Deck models
    ├── set.py           # Set models
    ├── card.py          # Card models
    └── price.py         # Price models
```

### Database Manager

```mermaid
classDiagram
    class DatabaseManager {
        -_sets_conn: Connection
        -_decks_conn: Connection
        -_prices_conn: Connection
        -_printings_conn: Connection
        -_initialized: bool
        +init()
        +close()
        +sets: Connection
        +decks: Connection
        +prices: Connection
        +printings: Connection
        +status(): dict
    }

    class db {
        <<singleton>>
    }

    DatabaseManager <-- db
```

**Database Files Location:** `~/.mtgsim/reference/mtgjson/`

| Database | Contents |
|----------|----------|
| AllSets.sqlite | Set metadata, card data (setdb, setcarddb tables) |
| AllDecks.sqlite | Deck metadata, deck cards (deck, deckcard tables) |
| AllPricesToday.sqlite | Daily prices (cardPrices table) |
| AllPrintings.sqlite | Complete card printings data |

## API Endpoints

### Decks API

```mermaid
sequenceDiagram
    participant Client
    participant Router as /api/decks
    participant Service as deck_service
    participant Data as decks_data
    participant DB as SQLite

    Client->>Router: GET /api/decks?q=...&colors=WU
    Router->>Service: list_decks(q, colors, ...)
    Service->>Data: list_decks(...)
    Data->>DB: SELECT FROM deck, deckcard
    DB-->>Data: rows
    Data->>DB: SELECT FROM cardPrices (prices)
    DB-->>Data: price_map
    Data-->>Service: [decks], total
    Service-->>Router: DeckListResponse
    Router-->>Client: JSON response
```

**Endpoints:**
- `GET /api/decks` - List/filter decks with pagination
- `GET /api/decks/{file}` - Get full deck details
- `GET /api/decks/{file}/raw` - Get raw deck JSON

**Query Parameters:**
| Parameter | Description |
|-----------|-------------|
| q | Search deck name/code |
| format | Filter by format (standard, modern, etc.) |
| set | Filter by set code |
| colors | Filter by color identity (e.g., "WU") |
| card_count_min/max | Filter by deck size |
| price_min/max | Filter by price range |
| sort | Sort field (name, release_date, card_count) |
| order | asc/desc |
| page, limit | Pagination |

### Sets API

```mermaid
sequenceDiagram
    participant Client
    participant Router as /api/sets
    participant Service as set_service
    participant Data as sets_data
    participant DB as SQLite

    Client->>Router: GET /api/sets/10E
    Router->>Service: get_set("10E", ...)
    Service->>Data: get_set("10E")
    Data->>DB: SELECT FROM setdb
    DB-->>Data: set metadata
    Service->>Data: get_set_cards("10E", ...)
    Data->>DB: SELECT FROM setcarddb
    Data->>DB: SELECT FROM cardPrices
    DB-->>Data: cards with prices
    Service->>Data: get_set_stats("10E")
    Data->>DB: Aggregate queries
    DB-->>Data: stats
    Service-->>Router: SetDetail
    Router-->>Client: JSON response
```

**Endpoints:**
- `GET /api/sets` - List/filter sets
- `GET /api/sets/{code}` - Get set details with cards
- `GET /api/sets/{code}/raw` - Get raw set JSON

### Cards API

**Endpoints:**
- `GET /api/cards` - Search cards with filters
- `GET /api/cards/{uuid}` - Get card details

### Prices API

**Endpoints:**
- `GET /api/prices` - Search prices
- `GET /api/prices/{uuid}` - Get card prices

### Stats API

**Endpoints:**
- `GET /api/stats/home` - Home screen statistics
- `GET /api/stats/decks` - Deck aggregate stats

## Frontend Architecture

### Application Structure

```mermaid
graph TB
    subgraph "Layout"
        SIDEBAR[Sidebar 300px]
        MAIN[Main Content Area]
    end

    subgraph "Sidebar Tabs"
        DECKS_TAB[Decks Tab]
        PRICES_TAB[Prices Tab]
        SETS_TAB[Sets Tab]
    end

    subgraph "Components"
        SEARCH[Search Box]
        FILTERS[Filter Controls]
        LIST[Item List]
        PAGINATION[Pagination]
    end

    SIDEBAR --> DECKS_TAB
    SIDEBAR --> PRICES_TAB
    SIDEBAR --> SETS_TAB
    DECKS_TAB --> SEARCH
    DECKS_TAB --> FILTERS
    DECKS_TAB --> LIST
    DECKS_TAB --> PAGINATION
```

### State Management

```mermaid
stateDiagram-v2
    [*] --> HomeScreen: Page Load

    HomeScreen --> DeckView: Click deck
    HomeScreen --> SetView: Click set
    HomeScreen --> PriceView: Switch to Prices

    DeckView --> HomeScreen: Click logo
    DeckView --> DeckView: Load another deck

    SetView --> HomeScreen: Click logo
    SetView --> SetView: Load another set

    state DeckView {
        [*] --> Loading
        Loading --> Rendered: Data received
        Rendered --> Loading: New deck selected
    }
```

### JavaScript Functions

```mermaid
flowchart TD
    subgraph "API Client"
        api["api(endpoint, params)"]
    end

    subgraph "Tab Functions"
        switchTab["switchTab(tab)"]
        loadDecks["loadDecks()"]
        loadSets["loadSets()"]
        searchPrices["searchPrices()"]
    end

    subgraph "View Functions"
        showHomeScreen["showHomeScreen()"]
        loadDeck["loadDeck(file)"]
        loadSet["loadSet(code)"]
    end

    subgraph "Render Functions"
        renderDeckList["renderDeckList(data)"]
        renderDeckView["renderDeckView(deck)"]
        renderSetList["renderSetList(sets)"]
        renderSetView["renderSetView(set)"]
        renderCard["renderCard(card)"]
        renderHomeScreen["renderHomeScreen(stats)"]
    end

    switchTab --> loadDecks
    switchTab --> loadSets
    switchTab --> showHomeScreen

    loadDecks --> api
    loadSets --> api
    showHomeScreen --> api
    loadDeck --> api
    loadSet --> api

    loadDecks --> renderDeckList
    loadSets --> renderSetList
    loadDeck --> renderDeckView
    loadSet --> renderSetView
    showHomeScreen --> renderHomeScreen

    renderDeckView --> renderCard
    renderSetView --> renderCard
```

### Filter Flow (Decks Tab)

```mermaid
flowchart LR
    subgraph "User Inputs"
        SEARCH[Search Input]
        FORMAT[Format Filter]
        SET[Set Filter]
        SIZE[Deck Size Filter]
        PRICE[Price Filter]
        COLORS[Color Checkboxes]
        SORT[Sort Dropdown]
    end

    subgraph "Processing"
        APPLY[applyFilters]
        CONVERT[Convert to API params]
        API_CALL[api /decks]
    end

    subgraph "Output"
        RENDER[renderDeckList]
        UPDATE_PAGE[Update pagination]
    end

    SEARCH --> APPLY
    FORMAT --> APPLY
    SET --> APPLY
    SIZE --> APPLY
    PRICE --> APPLY
    COLORS --> APPLY
    SORT --> APPLY

    APPLY --> CONVERT
    CONVERT --> API_CALL
    API_CALL --> RENDER
    API_CALL --> UPDATE_PAGE
```

### Card Count Filter Mapping

| Filter Value | card_count_min | card_count_max |
|--------------|----------------|----------------|
| lands5 | 5 | 5 |
| sample | 6 | 20 |
| limited | 21 | 50 |
| constructed | 51 | 75 |
| commander | 76 | 115 |
| large | 116 | 299 |
| cube | 300 | null |

## Data Flow Examples

### Loading a Deck

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend
    participant API as Backend API
    participant DB as SQLite

    User->>UI: Click deck item
    UI->>UI: loadDeck(file)
    UI->>API: GET /api/decks/{file}.json
    API->>DB: Query deck metadata
    API->>DB: Query commander cards
    API->>DB: Query main_board cards
    API->>DB: Query side_board cards
    API->>DB: Query prices for all cards
    API->>DB: Calculate deck stats
    API-->>UI: DeckDetail JSON
    UI->>UI: renderDeckView(deck)
    UI->>UI: renderCard() for each card
    UI-->>User: Display deck view
```

### Price Lookup

```mermaid
sequenceDiagram
    participant Data as Data Layer
    participant Prices as AllPricesToday.sqlite

    Data->>Data: Collect card UUIDs
    Data->>Prices: SELECT uuid, price FROM cardPrices<br/>WHERE uuid IN (?...)<br/>AND priceProvider='tcgplayer'<br/>AND providerListing='retail'<br/>AND cardFinish='normal'<br/>AND currency='USD'
    Prices-->>Data: {uuid: price, ...}
    Data->>Data: Map prices to cards
```

## UI Components

### Card Rendering

```html
<div class="card">
    <img class="card-image" src="..." alt="Card Name">
    <div class="card-header">
        <span class="card-name">Card Name</span>
        <span class="card-mana">{2}{W}{U}</span>
    </div>
    <div class="card-type">Creature - Human Wizard</div>
    <div class="card-text">Card rules text...</div>
    <div class="card-stats">
        <span class="card-pt">2/2</span>
        <div>
            <span class="card-count">x4</span>
            <i class="ss ss-set"></i> SET
            <span class="card-rarity">rare</span>
        </div>
    </div>
    <div class="card-footer">
        <div class="color-identity">W U</div>
        <div class="card-price">$1.50</div>
    </div>
</div>
```

### Image URL Generation

Card images are fetched from Scryfall using the scryfallId:
```
https://cards.scryfall.io/large/front/{id[0]}/{id[1]}/{scryfallId}.jpg
```

## External Dependencies

### CSS Libraries
- **Keyrune** - Set symbols (`ss-xxx` classes)
- **Mana** - Mana symbols (`ms-xxx` classes)

### JavaScript Libraries
- **D3.js v7** - Histograms and charts
- **d3-cloud** - Word clouds (keywords)

## Configuration

### CORS
Configured to allow all origins (development mode):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Static Files
- `/web` - Main webapp files
- `/resources` - Keyrune, Mana CSS
- `/webapp` - Legacy webapp
- `/app` - Serves web/index.html

## Error Handling

### API Errors
```json
{
    "error": {
        "code": "NOT_FOUND",
        "message": "Resource not found"
    }
}
```

### Frontend Error Handling
```javascript
try {
    const data = await api('/endpoint');
    renderData(data);
} catch (error) {
    console.error('Error:', error);
    showErrorMessage();
}
```

# MTG Deck Viewer Webapp

A single-page web application for browsing Magic: The Gathering decks, sets, and cards with price tracking.

## Architecture Overview

```mermaid
graph TB
    subgraph "Frontend (index.html)"
        UI[User Interface]
        JS[JavaScript Logic]
        CSS[Styles]
    end

    subgraph "Data Sources"
        DI[decks.json<br/>Deck Index]
        SI[sets.json<br/>Set Index]
        CI[card_index.json<br/>Card Index]
        DF[AllDeckFiles/*.json<br/>Individual Decks]
        SF[AllSetFiles/*.json<br/>Individual Sets]
        PD[AllPricesToday.json<br/>Price Data]
        KW[Keywords.json<br/>MTG Keywords]
        KR[keyrune.css<br/>Set Icons]
        MN[mana.css<br/>Mana Icons]
    end

    subgraph "Caching"
        IDB[(IndexedDB<br/>mtg_cache)]
    end

    UI --> JS
    JS --> DI
    JS --> CI
    JS --> DF
    JS --> PD
    JS --> IDB
    CSS --> KR
```

## File Structure

| File | Purpose |
|------|---------|
| `index.html` | Main single-page application |
| `decks.json` | Pre-generated deck index with metadata |
| `sets.json` | Pre-generated set index with metadata |
| `card_index.json` | Compact card data from SQLite database |
| `generate_index.py` | Script to generate `decks.json` |
| `generate_set_index.py` | Script to generate `sets.json` |
| `generate_card_index.py` | Script to generate `card_index.json` |

## Initialization Flow

```mermaid
sequenceDiagram
    participant Browser
    participant App
    participant Server
    participant IndexedDB

    Browser->>App: Page Load

    par Parallel Loading
        App->>Server: loadPriceData()
        Server-->>App: AllPricesToday.json
        App->>App: updateDeckPrices()
    and
        App->>Server: loadCardIndex()
        Server-->>App: card_index.json
    and
        App->>Server: loadDeckIndex()
        Server-->>App: decks.json
        App->>App: renderDeckList()
        App->>App: showHomeScreen()
        App->>App: buildCardIndex()
    and
        App->>Server: loadKeywords()
        Server-->>App: Keywords.json
    and
        App->>Server: loadSetIndex()
        Server-->>App: sets.json
        App->>App: renderSetList()
    end

    App->>IndexedDB: Check cache
    alt Cache Hit
        IndexedDB-->>App: Cached cardIndex
    else Cache Miss
        loop Batch Requests (20 at a time)
            App->>Server: Fetch deck files
            Server-->>App: Deck data
        end
        App->>IndexedDB: Save to cache
    end
```

## UI Components

```mermaid
graph LR
    subgraph "Sidebar (300px)"
        H1[Header/Title]
        TB[Tab Bar]
        subgraph "Decks Tab"
            DS[Search Box]
            DF1[Format Filter]
            DF2[Set Filter]
            DF3[Deck Type Filter]
            DF4[Price Filter]
            DF5[Color Filter]
            DF6[Sort Options]
            DL[Deck List]
        end
        subgraph "Prices Tab"
            PS[Price Search]
            PF[Price Filters]
            PF2[Set Filter]
            PL[Price List]
        end
        subgraph "Sets Tab"
            SS[Set Search]
            ST[Type Filter]
            SO[Sort Options]
            SL[Set List]
        end
    end

    subgraph "Main Content"
        MC[Dynamic Content Area]
        MC --> HS[Home Screen Stats]
        MC --> DV[Deck View]
        MC --> CV[Card View]
        MC --> PE[Price Explorer]
        MC --> SE[Sets Explorer]
        MC --> SV[Set View]
    end
```

## Data Flow

### Deck Filtering

```mermaid
flowchart TD
    A[User Changes Filter] --> B[applyFilters]
    B --> C{Get Filter Values}
    C --> D[Search Query]
    C --> E[Format]
    C --> F[Set]
    C --> G[Card Count]
    C --> H[Price Range]
    C --> I[Colors]
    C --> J[Sort By]

    D --> K[Filter by Name/Code]
    K --> L{Format Set?}
    L -->|Yes| M[Filter by Legality]
    L -->|No| N{Set Selected?}
    M --> N
    N -->|Yes| O[Filter by Set Code]
    N -->|No| P{Card Count?}
    O --> P
    P -->|Yes| Q[Filter by Size]
    P -->|No| R{Price Range?}
    Q --> R
    R -->|Yes| S[Calculate Prices Async]
    S --> T[Filter by Price]
    R -->|No| U{Colors Selected?}
    T --> U
    U -->|Yes| V[Load Deck Colors Async]
    V --> W[Filter by Colors]
    U -->|No| X[Sort Results]
    W --> X
    X --> Y[renderDeckList]
    Y --> Z[showHomeScreen]
```

### Sort Options

| Sort Key | Description |
|----------|-------------|
| `name` | Alphabetical A-Z |
| `name-desc` | Alphabetical Z-A |
| `release-new` | Newest release first |
| `release-old` | Oldest release first |
| `cards-high` | Most cards first |
| `cards-low` | Fewest cards first |
| `colors-few` | Mono-color decks first |
| `colors-many` | 5-color decks first |

### Price & Color Calculation

```mermaid
flowchart TD
    A[getDeckPrice] --> B{Cached price & colors?}
    B -->|Yes| C[Return cached price]
    B -->|No| D[Fetch deck file]
    D --> E[Collect all cards]
    E --> F1[Extract colorIdentity]
    F1 --> F2[Cache deckColors]
    E --> F[For each card]
    F --> G[getAverageUsdPrice]
    G --> H[getCardPrice]
    H --> I[Get USD sources]
    I --> J[TCGplayer]
    I --> K[Card Kingdom]
    I --> L[Cardsphere]
    J --> M[Average prices]
    K --> M
    L --> M
    M --> N[Multiply by count]
    N --> O[Sum total]
    O --> P[Cache deckPrices]
    P --> Q[Return total]
```

## Price Sources

```mermaid
graph TB
    subgraph "Paper Prices (USD)"
        TCG[TCGplayer]
        CK[Card Kingdom]
        CS[Cardsphere]
    end

    subgraph "Paper Prices (EUR)"
        CM[Cardmarket]
    end

    subgraph "Digital Prices"
        MTGO[MTGO/Cardhoarder]
    end

    subgraph "Calculations"
        AVG[Average USD Price]
        TCG --> AVG
        CK --> AVG
        CS --> AVG

        AVG --> DV[Deck Value]

        ALL[All Sources] --> CD[Card Display]
        TCG --> ALL
        CK --> ALL
        CS --> ALL
        CM --> ALL
        MTGO --> ALL
    end
```

## Caching System

```mermaid
flowchart TD
    subgraph "IndexedDB Cache"
        DB[(mtg_cache)]
        ST[cardData store]
        DB --> ST
        ST --> K1[cardCache_v1]
        K1 --> CI[cardIndex]
        K1 --> CTD[cardToDecks]
    end

    subgraph "Memory Cache"
        M1[deckPrices]
        M2[deckColors]
        M3[cardDataMap]
        M4[priceData]
        M5[fullCardIndex]
        M6[keywordsData]
        M7[allSets]
    end

    A[buildCardIndex] --> B{Check IndexedDB}
    B -->|Hit| C[Load from cache]
    B -->|Miss| D[Fetch all decks]
    D --> E[Build index]
    E --> F[Save to IndexedDB]

    G[getDeckPrice] --> H{In deckPrices?}
    H -->|Yes| I[Return cached]
    H -->|No| J[Calculate & cache]
```

## Key Functions

### Data Loading

| Function | Purpose |
|----------|---------|
| `loadPriceData()` | Fetches AllPricesToday.json |
| `loadCardIndex()` | Fetches card_index.json |
| `loadDeckIndex()` | Fetches decks.json, triggers UI init |
| `loadSetIndex()` | Fetches sets.json, renders set list |
| `loadKeywords()` | Fetches Keywords.json for word clouds |
| `buildCardIndex()` | Builds card-to-deck mapping with caching |

### Price Functions

| Function | Purpose |
|----------|---------|
| `getCardPrice(uuid)` | Gets all price sources for a card |
| `getAverageUsdPrice(uuid)` | Averages USD paper prices |
| `getDeckPrice(deckFile)` | Calculates deck value and caches colors |
| `formatPrice(price)` | Formats price for display |
| `updateDeckPrices()` | Updates sidebar with prices |

### Rendering Functions

| Function | Purpose |
|----------|---------|
| `renderDeckList(decks)` | Renders deck list with mana icons and prices |
| `renderDeck(deckData)` | Renders full deck view |
| `renderCard(card)` | Renders individual card |
| `renderDeckStats(stats)` | Renders deck statistics with word clouds |
| `showHomeScreen()` | Shows aggregate statistics |
| `showPriceCard(uuid)` | Shows card in price explorer |
| `renderWordCloud(selector, texts, w, h)` | D3 word cloud for rules/flavor text |
| `renderKeywordCloud(selector, counts, w, h)` | D3 word cloud for keyword frequencies |
| `renderPriceHistogram(prices)` | D3 histogram of card prices |
| `renderSetList(sets)` | Renders set list in sidebar |
| `renderSetView(setData)` | Renders full set view with cards |
| `showSetsExplorer()` | Shows sets home screen with stats |

### Filter/Search Functions

| Function | Purpose |
|----------|---------|
| `applyFilters()` | Applies all deck filters including colors |
| `applySetFilters()` | Filters and sorts set list |
| `searchPrices()` | Searches price database with set filter |
| `switchTab(tab)` | Switches between Decks/Prices/Sets tabs |
| `loadSet(setCode)` | Loads and displays a specific set |
| `populatePriceSetFilter()` | Populates set dropdown in price explorer |

## Card Data Format

### Full Format (from deck files)
```javascript
{
    uuid: "abc-123",
    name: "Lightning Bolt",
    manaCost: "{R}",
    manaValue: 1,
    type: "Instant",
    types: ["Instant"],
    rarity: "common",
    setCode: "M10",
    power: null,
    toughness: null,
    colorIdentity: ["R"],
    legalities: { standard: "Legal", ... },
    identifiers: { scryfallId: "xyz" }
}
```

### Compact Format (from card_index.json)
```javascript
{
    n: "Lightning Bolt",  // name
    t: "Instant",         // type
    m: "{R}",            // manaCost
    r: "common",         // rarity
    s: "M10",            // setCode
    p: null,             // power
    o: null,             // toughness
    c: ["R"],            // colorIdentity
    i: "xyz"             // scryfallId
}
```

## Rate Limiting

To prevent `ERR_INSUFFICIENT_RESOURCES` errors, network requests are batched:

```mermaid
flowchart LR
    A[All Requests] --> B[Split into batches<br/>BATCH_SIZE=20]
    B --> C[Process batch]
    C --> D[Wait 50ms]
    D --> E{More batches?}
    E -->|Yes| C
    E -->|No| F[Complete]
```

## Generating Data Files

### Generate Deck Index
```bash
cd webapp
python generate_index.py
```
Reads all deck files from `resources/AllDeckFiles/` and creates `decks.json` with:
- Deck name, file, code
- Card count
- Format legality
- Release date

### Generate Set Index
```bash
cd webapp
python generate_set_index.py
```
Reads all set files from `resources/AllSetFiles/` and creates `sets.json` with:
- Set code, name, type
- Base and total set size
- Release date, block
- Keyrune code for icons

### Generate Card Index
```bash
cd webapp
python generate_card_index.py
```
Reads `resources/AllPrintings.sqlite` and creates `card_index.json` with compact card data for fast lookup.

## Deck Statistics Visualizations

The deck stats view includes several D3-powered visualizations:

### Price Histogram
- Shows distribution of card prices in the deck
- Linear scale bins with D3's `bin()` generator
- Displays count of cards in each price range

### Word Clouds
Generated using d3-cloud layout:

| Cloud | Source | Size |
|-------|--------|------|
| Rules Text | Card `text` field | 420x140, 2-col |
| Flavor Text | Card `flavorText` field | 420x140, 2-col |
| Ability Words | Keywords.json `abilityWords` | 200x100 |
| Keyword Abilities | Keywords.json `keywordAbilities` | 200x100 |
| Keyword Actions | Keywords.json `keywordActions` | 200x100 |

Word frequency determines font size (8-18px for text, 8-16px for keywords).

## External Dependencies

- **Keyrune**: MTG set symbol icon font (`/resources/keyrune-master/css/keyrune.css`)
- **Mana**: Mana symbol icon font (`/resources/mana-master/css/mana.css`)
- **D3.js**: Data visualization library (CDN)
- **d3-cloud**: Word cloud layout plugin for D3 (CDN)
- **Scryfall**: Card images via `https://cards.scryfall.io/`
- **MTGJSON**: Source data for cards, decks, and prices

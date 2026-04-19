# MTGSim

A Magic: The Gathering card simulation, image extraction, and collection management toolkit.

## Features

- **Card Scanning**: Identify physical cards from photos using AI vision or local OCR
- **Card Extraction**: Extract structured card data from images
- **Collection Management**: Track owned and wanted cards, manage decks
- **ASCII Art Rendering**: Display cards as ASCII art in terminal
- **MTGJSON Sync**: Download and sync reference data from MTGJSON
- **FastAPI Backend**: RESTful API for cards, decks, sets, prices, and scanning
- **Frontend Apps**: Deck viewer, flashcard study tool (standalone React apps)

## Installation

```bash
uv sync
```

For the tesseract OCR pipeline, install tesseract separately:

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr
```

## Quick Start

```bash
# Sync reference data (required first time)
uv run mtgsim db sync

# Start the API server
just serve                    # port 8001
uv run mtgsim-api --port 8002 # custom port

# Start frontend dev servers
just dev-viewer               # port 5173
just dev-flashcards           # port 5174
```

## Configuration

All settings are loaded from environment variables or a `.env` file in the project root via pydantic-settings. Create a `.env` file to configure:

```bash
# API server
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8001

# OpenAI (required for openai scan pipeline)
OPENAI_API_KEY=sk-...

# Scan endpoint
SCAN_RATE_LIMIT=10              # max scans per window
SCAN_RATE_WINDOW=60             # rate limit window in seconds
SCAN_DEFAULT_PIPELINE=openai    # default pipeline: openai, tesseract, or mock
SCAN_FUZZY_THRESHOLD=92         # name match threshold for scan service (0-100)
```

## Card Scanning

The scan endpoint (`POST /api/cards/scan`) accepts a card photo and identifies it. Three extraction pipelines are available:

| Pipeline | Cost | Latency | Accuracy | Requirements |
|----------|------|---------|----------|--------------|
| `openai` | ~$0.01-0.03/scan | ~2-3s | High | `OPENAI_API_KEY` |
| `tesseract` | Free | <1s | Moderate | `tesseract` binary |
| `mock` | Free | Instant | N/A (testing) | None |

### Usage

```bash
# Scan with OpenAI (default)
curl -X POST "http://localhost:8001/api/cards/scan" \
  -F "image=@card.jpg"

# Scan with tesseract (free, local)
curl -X POST "http://localhost:8001/api/cards/scan?pipeline=tesseract" \
  -F "image=@card.jpg"

# Scan and add to collection
curl -X POST "http://localhost:8001/api/cards/scan?add_to_collection=true" \
  -F "image=@card.jpg"

# Scan and add to a deck
curl -X POST "http://localhost:8001/api/cards/scan?deck_id=42" \
  -F "image=@card.jpg"
```

### OCR Pipeline Configuration

The tesseract pipeline has three layers of configurable parameters. All are tunable via `.env` without code changes.

#### Image Preprocessing

Applied before OCR to improve text recognition quality.

| Env Var | Default | Description |
|---------|---------|-------------|
| `OCR_PREPROCESS_GRAYSCALE` | `true` | Convert to grayscale |
| `OCR_PREPROCESS_CONTRAST` | `1.5` | Contrast enhancement (1.0 = none, >1 = more) |
| `OCR_PREPROCESS_SHARPNESS` | `2.0` | Sharpness enhancement (1.0 = none, >1 = sharper) |
| `OCR_PREPROCESS_SCALE` | `2.0` | Upscale factor (helps tesseract with small text) |
| `OCR_PREPROCESS_BINARIZE_THRESHOLD` | `0` | Black/white cutoff (0 = disabled, 1-255) |
| `OCR_PREPROCESS_DENOISE_KERNEL` | `0` | Median filter kernel (0 = disabled, odd int) |

#### Tesseract OCR

Controls how tesseract processes the image.

| Env Var | Default | Description |
|---------|---------|-------------|
| `OCR_PSM` | `6` | Page segmentation mode (6 = uniform block, 3 = fully auto) |
| `OCR_LANG` | `eng` | Language data (must be installed in tesseract) |

#### Text Matching

After OCR extracts text, it's matched against all cards in the database using weighted multi-field fuzzy matching. Each OCR line is tried as a potential card name, and the best composite score wins.

| Env Var | Default | Description |
|---------|---------|-------------|
| `OCR_MATCH_THRESHOLD` | `60.0` | Minimum score (0-100) to accept a match |
| `OCR_MATCH_NAME_WEIGHT` | `3.0` | Weight for card name similarity |
| `OCR_MATCH_TYPE_LINE_WEIGHT` | `1.0` | Weight for type line similarity |
| `OCR_MATCH_ORACLE_TEXT_WEIGHT` | `2.0` | Weight for oracle text similarity |
| `OCR_MATCH_NAME_SCORER` | `partial_ratio` | Scorer for name matching |
| `OCR_MATCH_TEXT_SCORER` | `token_set_ratio` | Scorer for type/oracle matching |

Available scorers: `WRatio`, `ratio`, `partial_ratio`, `token_sort_ratio`, `token_set_ratio`

- `partial_ratio` — best for name matching; finds card names as substrings in noisy OCR lines
- `token_set_ratio` — best for oracle/type matching; handles word overlap regardless of order
- `WRatio` — general purpose; tries multiple strategies and picks the best

### Matching Architecture

The text matching system is pluggable. `FuzzyTextMatch` (rapidfuzz-based) is the default strategy. The `TextMatchStrategy` ABC supports adding new strategies (e.g., vector/embedding similarity) without changing the pipeline.

```
Image -> Preprocessing (Pillow) -> OCR (tesseract) -> Text Matching (pluggable) -> Card
              |                         |                      |
         configurable             configurable            configurable
         via .env                 via .env                via .env
```

## CLI Commands

```bash
mtgsim --help                 # Display help
mtgsim extract card.jpg       # Extract card from image (CLI)
mtgsim db init                # Initialize database
mtgsim db sync                # Sync MTGJSON reference data
mtgsim db sync-decks          # Sync deck data
mtgsim card "Lightning Bolt"  # Create and display ASCII card
```

## Development

```bash
just test                     # Run tests
just test-cov                 # Run tests with coverage
just lint                     # Lint source and tests
just fmt                      # Format source and tests
just check                    # Lint + format
```

## Project Structure

```
mtgsim/
├── src/mtgsim/
│   ├── api/                  # FastAPI backend
│   │   ├── routers/          # HTTP endpoints
│   │   ├── services/         # Business logic
│   │   ├── data/             # Database queries
│   │   └── models/           # Pydantic response models
│   ├── extract/              # Card image extraction
│   │   ├── pipelines.py      # Pipeline ABC + OpenAI + Mock
│   │   ├── ocr.py            # Tesseract OCR pipeline
│   │   ├── matching.py       # Text matching strategies
│   │   └── preprocess.py     # Image preprocessing (Pillow)
│   ├── domain/               # Domain models (Card, ManaCost)
│   ├── cli/                  # Typer CLI
│   ├── settings.py           # Pydantic settings (.env loader)
│   └── deck_import.py        # MTGA deck import + fuzzy matching
├── packages/
│   └── mtgdb/                # Database models and sync
├── frontend/
│   └── packages/
│       ├── ui/               # Shared component library
│       ├── viewer/           # Deck viewer app (:5173)
│       └── flashcards/       # Flashcard study app (:5174)
├── tests/
│   └── api/                  # API + pipeline tests
├── docs/                     # Architecture and requirements docs
└── justfile                  # Development commands
```

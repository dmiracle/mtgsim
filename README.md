# MTGSim

A Magic: The Gathering card simulation, image extraction, and collection management toolkit.

## Features

- **Card Scanning**: Identify physical cards from photos using AI vision or local OCR, with a scan log for review and labeling
- **Collection Management**: Track owned cards, manage decks, import MTGA collections and deck exports
- **Card Search**: Filter by set, rarity, color, mana value, type, text, format, price, ownership, user tags, and tier
- **User Data**: Personal tags, card notes, tier lists (17Lands letter grades A+ … F), pairwise card rankings, and card interactions
- **17Lands Stats**: Per-card draft stats (ALSA, ATA, GIH WR, IWD, …) from 17Lands public datasets, plus personal event history sync
- **Card Similarity**: Pluggable similarity strategies (oracle text, keywords, tags, mana curve, type)
- **Boosters & Flashcards**: Booster pack generation and SRS-scheduled flashcard study
- **ASCII Art Rendering**: Display cards as ASCII art in terminal
- **MTGJSON Sync**: Download and sync reference data from MTGJSON
- **FastAPI Backend**: REST API under `/api/*` (docs at `/docs`)
- **Frontend Apps**: Desktop card viewer and flashcard app (`frontend/`), and a mobile card-review PWA (`mobile/`)

## Installation

Requires Python 3.14+ and [uv](https://docs.astral.sh/uv/). Two dependencies are local path
packages resolved relative to the repo root, so they must be checked out two levels up:
`llmex` (`../../llmex`) and `srs` (`../../srs`).

```bash
uv sync
```

Frontend dependencies are installed separately:

```bash
just install-frontend         # frontend/ (npm install)
cd mobile && npm install      # mobile/
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
just db-sync                  # uv run mtgsim db sync

# Start the API server
just serve                    # port 8001
just serve-debug              # debug logging + auto-reload
uv run mtgsim-api --port 8002 # custom port

# Start frontend dev servers (proxy /api to :8001)
just dev                      # API + viewer together
just dev-viewer               # viewer on :5173
just dev-flashcards           # flashcards on :5174
cd mobile && npm run dev      # mobile PWA on :5175

# Component libraries
just storybook                # frontend/ui Storybook on :6006
cd mobile && npm run storybook  # mobile Storybook on :6007
```

When `mobile/dist` has been built, the API serves the mobile app at `/`; otherwise `/`
redirects to the API docs at `/docs`. Health check: `GET /health`.

Runtime data lives in `~/.mtgsim/` (override with `MTGSIM_HOME`): the user database
`mtgsim.sqlite`, the scan log `scan_log.sqlite`, and downloaded reference data under
`reference/` (MTGJSON and 17Lands).

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
SCAN_LOG_DB_PATH=               # default: ~/.mtgsim/scan_log.sqlite

# Paths
MTGSIM_HOME=~/.mtgsim           # runtime data directory
MTGSIM_APP_DIR=                 # project root override (containers)
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
| `OCR_PREPROCESS_CONTRAST` | `2.0` | Contrast enhancement (1.0 = none, >1 = more) |
| `OCR_PREPROCESS_SHARPNESS` | `2.0` | Sharpness enhancement (1.0 = none, >1 = sharper) |
| `OCR_PREPROCESS_SCALE` | `2.0` | Upscale factor (helps tesseract with small text) |
| `OCR_PREPROCESS_BINARIZE_THRESHOLD` | `0` | Black/white cutoff (0 = disabled, 1-255) |
| `OCR_PREPROCESS_DENOISE_KERNEL` | `0` | Median filter kernel (0 = disabled, odd int) |

#### Tesseract OCR

Controls how tesseract processes the image.

| Env Var | Default | Description |
|---------|---------|-------------|
| `OCR_PSM` | `3` | Page segmentation mode (3 = fully auto, 6 = uniform block) |
| `OCR_LANG` | `eng` | Language data (must be installed in tesseract) |

#### Text Matching

After OCR extracts text, it's matched against all cards in the database using weighted multi-field fuzzy matching. Each OCR line is tried as a potential card name, and the best composite score wins.

| Env Var | Default | Description |
|---------|---------|-------------|
| `OCR_MATCH_THRESHOLD` | `55.0` | Minimum score (0-100) to accept a match |
| `OCR_MATCH_NAME_WEIGHT` | `1.5` | Weight for card name similarity |
| `OCR_MATCH_TYPE_LINE_WEIGHT` | `1.5` | Weight for type line similarity |
| `OCR_MATCH_ORACLE_TEXT_WEIGHT` | `4.0` | Weight for oracle text similarity |
| `OCR_MATCH_COMBINED_WEIGHT` | `3.0` | Weight for full OCR text vs. all card fields concatenated |
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

## API Overview

All routers are mounted under `/api`; see `/docs` for the full OpenAPI reference and
`docs/architecture.md` for the layer design.

| Prefix | Purpose |
|--------|---------|
| `/api/cards` | Search/filter, detail, printings, similarity, features, collection, scan, MTGA import |
| `/api/decks` | Deck CRUD, cards, printings, pinned decks |
| `/api/sets` | Set list and detail |
| `/api/prices` | Price data |
| `/api/stats` | Home/dashboard statistics |
| `/api/keywords` | Keyword reference |
| `/api/boosters` | Booster pack generation |
| `/api/17lands` | Datasets, expansions, per-card stats, drafts, games, replays |
| `/api/flashcards` | Collections, review queue, SRS review, analytics |
| `/api/user-tags` | User tag vocabulary and card assignments |
| `/api/card-notes` | Per-card notes |
| `/api/tier-lists` | Tier lists and graded entries |
| `/api/rankings` | Pairwise card rankings (rounds of up to 4 cards) |
| `/api/interactions` | Card-to-card interactions and interaction graph |
| `/api/scan-log` | Logged scans, batches, labels, pipeline comparison |

## CLI Commands

```bash
mtgsim --help                         # Display help
mtgsim card "Lightning Bolt"          # Display a card as ASCII art
mtgsim extract card.jpg -p openai     # Extract card from image (pipelines: mock, openai, tesseract)
mtgsim db init                        # Initialize ~/.mtgsim/mtgsim.sqlite
mtgsim db sync                        # Sync MTGJSON data (--force to re-download)
mtgsim db sync-17l-personal           # Sync your personal 17Lands event history
mtgsim db import-mtga collection.csv  # Mark cards owned on MTGA from a collection CSV
mtgsim db stats                       # Database statistics
mtgsim deck import                    # Import a deck from MTGA export format
mtgsim booster open                   # Open booster pack(s) from a set
mtgsim images fetch                   # Download card PNGs from Scryfall
mtgsim mtgjson info                   # MTGJSON reference data info
mtgsim domain --help                  # Domain database operations (collection, migration, rollback)
```

## Mobile Card Review PWA

`mobile/` is a standalone mobile-first app (no shared code with `frontend/`) for swiping
through filtered cards, grading them into tier lists, and building pairwise rankings.
See [`mobile/README.md`](mobile/README.md) for details.

It runs as a macOS LaunchAgent (`deploy/launchd/com.mtgsim.api.plist`): the API on
`127.0.0.1:18001` serves the built PWA from `mobile/dist`, starts at login, and restarts on
crash. A second agent (`com.mtgsim.tailscale`) runs a separate userspace `tailscaled`
(`brew install tailscale`) that joins the tailnet as its own device, `mtgsim`, and publishes
the API over HTTPS on the tailnet only, at https://mtgsim.tail4ca9d8.ts.net/. Port 8001 stays
free for development. Logs go to `~/Library/Logs/mtgsim/`.

```bash
just services-install         # build mobile/, install + start both agents, log in the mtgsim node, enable HTTPS
just mobile-deploy            # rebuild mobile/ (served immediately)
just services-restart         # after backend changes
just services-status          # running? pid?
just services-tailscale       # mtgsim node status and serve config
just services-logs            # tail the logs
just services-uninstall       # stop + remove both agents and the serve route
```

## Development

```bash
just test                     # Run tests (pass args: just test tests/api -q)
just test-cov                 # Run tests with coverage
just lint                     # Lint source and tests
just fmt                      # Format source and tests
just fix                      # Auto-fix lint issues
just check                    # Lint + format

just typecheck                # Typecheck frontend packages
just lint-frontend            # Lint frontend code
just build-viewer             # Build the viewer
just build-flashcards         # Build the flashcards app
just build-storybook          # Build static Storybook
cd mobile && npm test         # Mobile ranking logic tests
```

API tests expect the reference SQLite DBs; run `mtgsim db sync` first.

## Project Structure

```
mtgsim/
├── src/mtgsim/
│   ├── api/                  # FastAPI backend
│   │   ├── routers/          # HTTP endpoints
│   │   ├── services/         # Business logic
│   │   ├── data/             # Database queries
│   │   ├── models/           # Pydantic request/response models
│   │   └── similarity/       # Card similarity strategies
│   ├── extract/              # Card image extraction
│   │   ├── pipelines.py      # Pipeline ABC + OpenAI + Mock
│   │   ├── ocr.py            # Tesseract OCR pipeline
│   │   ├── matching.py       # Text matching strategies
│   │   └── preprocess.py     # Image preprocessing (Pillow)
│   ├── scan_log/             # Scan log storage, batches, queries
│   ├── booster/              # Booster pack generation
│   ├── flashcards/           # Flashcard generation
│   ├── db/                   # SQLModel models and sessions
│   ├── domain/               # Domain models (Card, ManaCost)
│   ├── render/               # ASCII rendering
│   ├── cli/                  # Typer CLI
│   ├── config.py             # Project paths
│   ├── settings.py           # Pydantic settings (.env loader)
│   └── deck_import.py        # MTGA deck import + fuzzy matching
├── packages/
│   ├── mtgdb/                # Database models, MTGJSON + 17Lands sync
│   └── mtgviz/               # Computer vision / image analysis (rotation, OCR)
├── frontend/
│   └── packages/
│       ├── ui/               # Shared component library + Storybook (:6006)
│       ├── viewer/           # Card browser, decks, sets, prices, drafts (:5173)
│       └── flashcards/       # Flashcard study app (:5174)
├── mobile/                   # Mobile card-review PWA (:5175, Storybook :6007)
├── deploy/launchd/           # macOS LaunchAgent for the API service
├── tests/
│   └── api/                  # API + pipeline tests
├── docs/                     # Architecture and requirements docs
└── justfile                  # Development commands
```

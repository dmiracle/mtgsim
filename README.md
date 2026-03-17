# MTGSim

A Magic: The Gathering card simulation and image extraction toolkit.

## Features

- **Card Extraction**: Extract card data from images using AI pipelines
- **ASCII Art Rendering**: Display cards as ASCII art in terminal
- **Database Management**: Track owned and wanted cards
- **MTGJSON Sync**: Download and sync reference data from MTGJSON

## Installation

```bash
uv sync
```

## Usage

```bash
# Display help
mtgsim --help

# Initialize database
mtgsim db init

# Sync reference data
mtgsim db sync

# Sync deck data
mtgsim db sync-decks

# Extract card from image
mtgsim extract path/to/card.jpg

# Create a card
mtgsim card "Lightning Bolt" --types Instant --mana R --oracle "Deal 3 damage to any target."
```

## Project Structure

This project uses a **uv workspace** to organize code into reusable packages:

```
mtgsim/
├── pyproject.toml          # Root workspace config
├── packages/
│   └── mtgdb/              # Database models and sync
│       ├── pyproject.toml
│       └── src/mtgdb/
│           ├── models.py   # SQLModel models (MJ*, User*)
│           ├── session.py  # Database engine/session
│           ├── config.py   # Path configuration
│           └── sync/       # MTGJSON sync functions
└── src/mtgsim/             # Main application
    ├── api/                # FastAPI backend
    ├── cli/                # Typer CLI
    ├── db/                 # Re-exports from mtgdb
    └── sync/               # Re-exports from mtgdb
```

### Adding New Workspace Packages

1. Create the package directory:
   ```bash
   mkdir -p packages/mypackage/src/mypackage
   ```

2. Create `packages/mypackage/pyproject.toml`:
   ```toml
   [project]
   name = "mypackage"
   version = "0.1.0"
   requires-python = ">=3.14"
   dependencies = []

   [build-system]
   requires = ["uv_build>=0.8.19,<0.9.0"]
   build-backend = "uv_build"
   ```

3. Add to root dependencies if needed:
   ```toml
   [project]
   dependencies = ["mypackage", ...]

   [tool.uv.sources]
   mypackage = { workspace = true }
   ```

4. Lock and sync:
   ```bash
   uv lock && uv sync
   ```

### Workspace Commands

```bash
uv lock                    # Lock entire workspace
uv sync                    # Install all packages
uv sync --package mtgdb    # Install specific package
uv run pytest              # Run tests
```

## CLI Commands

- `mtgsim card` - Generate and display ASCII card
- `mtgsim extract` - Extract card data from image
- `mtgsim db init` - Initialize database
- `mtgsim db sync` - Sync MTGJSON reference data
- `mtgsim db sync-decks` - Sync deck data
- `mtgsim db add` - Add card to database
- `mtgsim db list` - List cards
- `mtgsim db search` - Search cards
- `mtgsim db own` - Mark card as owned
- `mtgsim db want` - Mark card as wanted
- `mtgsim mtgjson info` - Show MTGJSON reference info
- `mtgsim mtgjson stats` - Show reference statistics

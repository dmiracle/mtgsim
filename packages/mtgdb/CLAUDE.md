# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package Overview

`mtgdb` is a standalone Python package providing SQLModel database models and MTGJSON sync functionality for MTG card data. It's a subpackage of mtgsim, designed to be importable by other packages.

## Development Commands

```bash
# Install dependencies (from packages/mtgdb/)
uv sync

# Run tests
uv run pytest tests/ -v

# Run a single test file
uv run pytest tests/test_models.py -v

# Run sync programmatically
python -c "from mtgdb.sync import sync_all; sync_all()"

# Force re-download
python -c "from mtgdb.sync import sync_all; sync_all(force=True)"
```

## Architecture

### Data Model Naming

- **MJ prefix** (mj_* tables): MTGJSON reference data - read-only, synced from external sources
- **User prefix** (user_* tables): User-modifiable data (collection, decks)

### Core Modules

- `models.py`: All SQLModel table definitions (MJCard, MJSet, MJDeck, UserCard, UserDeck, etc.)
- `session.py`: Database engine/session management via `get_session()` context manager
- `config.py`: Paths and URLs (DB_PATH at `~/.mtgsim/mtgsim.sqlite`, MTGJSON sources)
- `sync/`: MTGJSON download and table sync pipeline

### Sync Data Flow

```
MTGJSON API -> Download .xz/.tar.xz -> Extract -> Sync to mj_* tables
```

Source files downloaded to `~/.mtgsim/reference/mtgjson/`:
- `AllPrintings.sqlite` -> mj_set, mj_card, mj_card_identifier, mj_card_legality
- `AllPricesToday.sqlite` -> mj_card_price
- `AllDeckFiles/` -> mj_deck, mj_deck_card
- `Keywords.json` -> mj_keyword

### Usage Pattern

```python
from mtgdb import get_session, MJCard
from sqlmodel import select

with get_session() as session:
    cards = session.exec(select(MJCard).where(MJCard.name == "Lightning Bolt")).all()
```

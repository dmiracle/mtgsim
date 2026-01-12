# UV Workspace Migration Plan

This document describes the steps to migrate sync and database functions to a new package `mtgdb` using uv workspaces.

## Goal

Extract the database models and sync functionality into a separate, reusable package (`mtgdb`) while keeping the CLI, API, and other mtgsim components in the main package.

## Current Structure

```
mtgsim/
├── pyproject.toml           # Single package
└── src/mtgsim/
    ├── config.py            # Path configuration (shared)
    ├── db/                   # Database models & sessions
    │   ├── models.py        # MJ* models (to move)
    │   ├── session.py       # Engine/session (to move)
    │   └── ...              # Other model files
    ├── sync/                 # MTGJSON sync (to move)
    │   ├── __init__.py
    │   ├── download.py
    │   └── tables.py
    ├── api/                  # FastAPI (stays)
    └── cli/                  # Typer CLI (stays)
```

## Target Structure

```
mtgsim/
├── pyproject.toml           # Workspace root
├── packages/
│   └── mtgdb/
│       ├── pyproject.toml   # mtgdb package
│       └── src/mtgdb/
│           ├── __init__.py
│           ├── config.py    # DB path configuration
│           ├── models.py    # All MJ* models
│           ├── session.py   # Engine & session management
│           └── sync/
│               ├── __init__.py
│               ├── download.py
│               └── tables.py
└── src/mtgsim/
    ├── config.py            # App-level config (web dirs, etc.)
    ├── api/                  # FastAPI (imports from mtgdb)
    └── cli/                  # Typer CLI (imports from mtgdb)
```

---

## Step 1: Configure Workspace Root

Modify the root `pyproject.toml` to declare the workspace:

```toml
[tool.uv.workspace]
members = ["packages/*"]

[project]
name = "mtgsim"
version = "0.3.0"
dependencies = [
    "mtgdb",              # Add workspace dependency
    "fastapi>=0.115.0",
    # ... other deps
]

[tool.uv.sources]
mtgdb = { workspace = true }
llmex = { path = "../llmex" }
```

**Key points:**
- `members = ["packages/*"]` includes all subdirectories in `packages/`
- Add `mtgdb` to dependencies
- Mark `mtgdb` as `workspace = true` in sources

---

## Step 2: Create mtgdb Package

### Directory structure

```bash
mkdir -p packages/mtgdb/src/mtgdb/sync
```

### packages/mtgdb/pyproject.toml

```toml
[project]
name = "mtgdb"
version = "0.1.0"
description = "MTG database models and MTGJSON sync"
requires-python = ">=3.14"
dependencies = [
    "sqlmodel>=0.0.27",
    "requests>=2.31.0",
]

[build-system]
requires = ["uv_build>=0.8.19,<0.9.0"]
build-backend = "uv_build"
```

**Note:** mtgdb has minimal dependencies - only what's needed for DB and sync.

---

## Step 3: Move Files

### Files to move to `packages/mtgdb/src/mtgdb/`:

| Source | Destination |
|--------|-------------|
| `src/mtgsim/db/models.py` | `packages/mtgdb/src/mtgdb/models.py` |
| `src/mtgsim/db/session.py` | `packages/mtgdb/src/mtgdb/session.py` |
| `src/mtgsim/sync/__init__.py` | `packages/mtgdb/src/mtgdb/sync/__init__.py` |
| `src/mtgsim/sync/download.py` | `packages/mtgdb/src/mtgdb/sync/download.py` |
| `src/mtgsim/sync/tables.py` | `packages/mtgdb/src/mtgdb/sync/tables.py` |

### Files to keep but modify:

| File | Change |
|------|--------|
| `src/mtgsim/config.py` | Keep app-level paths only |
| `src/mtgsim/db/__init__.py` | Re-export from mtgdb |

---

## Step 4: Create mtgdb Config

Create `packages/mtgdb/src/mtgdb/config.py`:

```python
"""Database path configuration."""
from pathlib import Path

# Base directories
MTGDB_HOME = Path.home() / ".mtgsim"
REFERENCE_DIR = MTGDB_HOME / "reference"
MTGJSON_DIR = REFERENCE_DIR / "mtgjson"

# Database path
DB_PATH = MTGDB_HOME / "mtgsim.sqlite"

# MTGJSON source directory
ALL_DECK_FILES_DIR = MTGJSON_DIR / "AllDeckFiles"

# MTGJSON API URLs
MTGJSON_BASE_URL = "https://mtgjson.com/api/v5"
ALL_PRINTINGS_URL = f"{MTGJSON_BASE_URL}/AllPrintings.sqlite.xz"
ALL_PRICES_URL = f"{MTGJSON_BASE_URL}/AllPricesToday.sqlite.xz"
ALL_DECK_FILES_URL = f"{MTGJSON_BASE_URL}/AllDeckFiles.tar.xz"
KEYWORDS_URL = f"{MTGJSON_BASE_URL}/Keywords.json.xz"

def ensure_dirs() -> None:
    """Ensure all required directories exist."""
    MTGDB_HOME.mkdir(parents=True, exist_ok=True)
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    MTGJSON_DIR.mkdir(parents=True, exist_ok=True)
```

---

## Step 5: Update Imports

### In mtgdb package

Update internal imports to use `mtgdb.*`:

```python
# packages/mtgdb/src/mtgdb/sync/tables.py
from mtgdb.models import MJCard, MJSet, ...
from mtgdb.session import get_engine

# packages/mtgdb/src/mtgdb/sync/__init__.py
from mtgdb.config import DB_PATH, MTGJSON_DIR, ...
from mtgdb.models import MJCard
from mtgdb.session import get_engine, init_db
```

### In mtgsim package

Update all imports from `mtgsim.db` and `mtgsim.sync` to use `mtgdb`:

| Old Import | New Import |
|------------|------------|
| `from mtgsim.db.models import MJCard` | `from mtgdb.models import MJCard` |
| `from mtgsim.db.session import get_engine` | `from mtgdb.session import get_engine` |
| `from mtgsim.sync import sync_all` | `from mtgdb.sync import sync_all` |
| `from mtgsim.config import DB_PATH` | `from mtgdb.config import DB_PATH` |

### Files requiring import updates:

**API layer** (19 imports):
- `src/mtgsim/api/data/cards.py`
- `src/mtgsim/api/data/decks.py`
- `src/mtgsim/api/data/prices.py`
- `src/mtgsim/api/data/sets.py`
- `src/mtgsim/api/data/__init__.py`
- `src/mtgsim/api/routers/stats.py`

**CLI layer** (30+ imports):
- `src/mtgsim/cli/db_commands.py`
- `src/mtgsim/cli/domain_commands.py`
- `src/mtgsim/cli/logging_manager.py`
- `src/mtgsim/cli/rollback.py`
- `src/mtgsim/cli/mtgjson_commands.py`

---

## Step 6: Update mtgsim db/__init__.py

Simplify to re-export from mtgdb for any remaining internal uses:

```python
"""Database models and session management.

Re-exports from mtgdb package for backwards compatibility.
"""
from mtgdb.config import DB_PATH
from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
    MJKeyword,
    MJSet,
    UserCard,
    UserDeck,
    UserDeckCard,
)
from mtgdb.session import get_engine, get_session, init_db

__all__ = [
    "DB_PATH",
    "MJCard",
    "MJCardIdentifier",
    # ... etc
]
```

---

## Step 7: Handle Legacy/Domain Models

The following files in `src/mtgsim/db/` should remain in mtgsim (not move to mtgdb):

| File | Reason |
|------|--------|
| `domain_models.py` | Legacy domain layer, not used by sync |
| `domain_session.py` | Legacy domain sessions |
| `reference_models.py` | Legacy MTGJSON models |
| `migration_models.py` | Domain migration tracking |
| `models_legacy.py` | Deprecated models |
| `deck_models.py` | Unused deck models |
| `set_models.py` | Unused set models |
| `keyword_models.py` | Unused keyword models |
| `session_legacy.py` | Legacy session |

These can be cleaned up in a separate effort.

---

## Step 8: Run Workspace Commands

```bash
# Lock the entire workspace
uv lock

# Sync workspace dependencies
uv sync

# Run mtgsim CLI
uv run mtgsim --help

# Run tests
uv run pytest

# Sync specific package
uv sync --package mtgdb
```

---

## Step 9: Update Tests

Create `packages/mtgdb/tests/` for mtgdb-specific tests:

```
packages/mtgdb/
├── pyproject.toml
├── src/mtgdb/
└── tests/
    ├── __init__.py
    ├── test_models.py
    └── test_sync.py
```

Move relevant tests from `tests/` to the mtgdb package.

---

## Migration Checklist

- [ ] Create workspace configuration in root pyproject.toml
- [ ] Create packages/mtgdb directory structure
- [ ] Create packages/mtgdb/pyproject.toml
- [ ] Move models.py to mtgdb
- [ ] Move session.py to mtgdb
- [ ] Move sync/ directory to mtgdb
- [ ] Create mtgdb config.py with DB paths
- [ ] Update internal mtgdb imports
- [ ] Update API layer imports (6 files)
- [ ] Update CLI layer imports (5 files)
- [ ] Update mtgsim db/__init__.py re-exports
- [ ] Remove moved files from src/mtgsim/
- [ ] Run uv lock
- [ ] Run uv sync
- [ ] Run pytest to verify
- [ ] Update AGENTS.md with new structure

---

## Benefits

1. **Separation of concerns**: Database and sync logic isolated from CLI/API
2. **Reusability**: mtgdb can be used by other projects
3. **Cleaner dependencies**: mtgdb has minimal deps (sqlmodel, requests)
4. **Easier testing**: Test DB/sync independently from app layer
5. **Consistent lockfile**: Single lockfile for entire workspace

---

## References

- [uv Workspaces Documentation](https://docs.astral.sh/uv/concepts/projects/workspaces/)
- [Python Workspaces (Monorepos)](https://tomasrepcik.dev/blog/2025/2025-10-26-python-workspaces/)
- [Example uv Monorepo](https://github.com/JasperHG90/uv-monorepo)

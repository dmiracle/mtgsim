"""Centralized configuration for mtgsim paths and settings.

Database paths and MTGJSON config are in mtgdb.config.
This module re-exports them and adds app-level paths.
"""

import os
from pathlib import Path

# Re-export from mtgdb for backwards compatibility
from mtgdb.config import (  # noqa: F401
    DB_PATH,
    MTGJSON_BASE_URL,
    MTGJSON_DIR,
    ensure_dirs,
)

# Legacy aliases (all point to unified DB for backwards compatibility)
USER_DB_PATH = DB_PATH
DOMAIN_DB_PATH = DB_PATH
MERGED_DB_PATH = DB_PATH

# MTGJSON URL not in mtgdb
DECK_LIST_URL = f"{MTGJSON_BASE_URL}/DeckList.json.xz"


# Project paths — override with MTGSIM_APP_DIR env var for containers
def get_project_root() -> Path:
    """Get project root directory."""
    if app_dir := os.environ.get("MTGSIM_APP_DIR"):
        return Path(app_dir)
    import mtgsim

    return Path(mtgsim.__file__).parent.parent.parent


def get_resources_dir() -> Path:
    """Get resources directory."""
    return get_project_root() / "resources"


def get_web_dir() -> Path:
    """Get web static files directory."""
    return get_project_root() / "web"


def get_webapp_dir() -> Path:
    """Get webapp static files directory."""
    return get_project_root() / "webapp"

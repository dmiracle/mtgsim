"""Centralized configuration for mtgsim paths and settings."""

from pathlib import Path

# Base directories
MTGSIM_HOME = Path.home() / ".mtgsim"
REFERENCE_DIR = MTGSIM_HOME / "reference"
MTGJSON_DIR = REFERENCE_DIR / "mtgjson"

# User database
USER_DB_PATH = MTGSIM_HOME / "mtgsim.db"

# Merged reference database (all tables in one file)
MERGED_DB_PATH = MTGJSON_DIR / "mtgjson-merged.sqlite"

# Legacy individual database paths (deprecated, use MERGED_DB_PATH)
ALLSETS_DB_PATH = MERGED_DB_PATH
ALLDECKS_DB_PATH = MERGED_DB_PATH
ALLPRICES_DB_PATH = MERGED_DB_PATH
ALLPRINTINGS_DB_PATH = MERGED_DB_PATH

# Deck files directory
ALL_DECK_FILES_DIR = MTGJSON_DIR / "AllDeckFiles"

# MTGJSON API URLs
MTGJSON_BASE_URL = "https://mtgjson.com/api/v5"
ALL_PRINTINGS_URL = f"{MTGJSON_BASE_URL}/AllPrintings.sqlite.xz"
ALL_PRICES_URL = f"{MTGJSON_BASE_URL}/AllPricesToday.sqlite.xz"
DECK_LIST_URL = f"{MTGJSON_BASE_URL}/DeckList.json.xz"
ALL_DECK_FILES_URL = f"{MTGJSON_BASE_URL}/AllDeckFiles.tar.xz"
KEYWORDS_URL = f"{MTGJSON_BASE_URL}/Keywords.json.xz"

# Project paths (relative to package location)
def get_project_root() -> Path:
    """Get project root directory."""
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


def ensure_dirs() -> None:
    """Ensure all required directories exist."""
    MTGSIM_HOME.mkdir(parents=True, exist_ok=True)
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    MTGJSON_DIR.mkdir(parents=True, exist_ok=True)

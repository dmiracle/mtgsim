"""Database path configuration."""

import os
from pathlib import Path

# Base directories — override with MTGSIM_HOME env var for containers
MTGDB_HOME = Path(os.environ.get("MTGSIM_HOME", Path.home() / ".mtgsim"))
REFERENCE_DIR = MTGDB_HOME / "reference"
MTGJSON_DIR = REFERENCE_DIR / "mtgjson"
SCRYFALL_DIR = REFERENCE_DIR / "scryfall"
SEVENTEENLANDS_DIR = REFERENCE_DIR / "17lands"

# 17Lands Prismic CMS
PRISMIC_REPO = "17lands"
PRISMIC_API_URL = f"https://{PRISMIC_REPO}.cdn.prismic.io/api/v2"

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
    SCRYFALL_DIR.mkdir(parents=True, exist_ok=True)
    SEVENTEENLANDS_DIR.mkdir(parents=True, exist_ok=True)

"""Tests for mtgdb config."""

from pathlib import Path

from mtgdb.config import (
    ALL_DECK_FILES_DIR,
    ALL_DECK_FILES_URL,
    ALL_PRICES_URL,
    ALL_PRINTINGS_URL,
    DB_PATH,
    KEYWORDS_URL,
    MTGDB_HOME,
    MTGJSON_BASE_URL,
    MTGJSON_DIR,
    REFERENCE_DIR,
    ensure_dirs,
)


class TestPaths:
    """Tests for path configuration."""

    def test_mtgdb_home_is_in_home_directory(self):
        """Test MTGDB_HOME is under user home."""
        assert MTGDB_HOME == Path.home() / ".mtgsim"

    def test_reference_dir_under_home(self):
        """Test REFERENCE_DIR is under MTGDB_HOME."""
        assert REFERENCE_DIR == MTGDB_HOME / "reference"

    def test_mtgjson_dir_under_reference(self):
        """Test MTGJSON_DIR is under REFERENCE_DIR."""
        assert MTGJSON_DIR == REFERENCE_DIR / "mtgjson"

    def test_db_path_under_home(self):
        """Test DB_PATH is under MTGDB_HOME."""
        assert DB_PATH == MTGDB_HOME / "mtgsim.sqlite"

    def test_all_deck_files_dir(self):
        """Test ALL_DECK_FILES_DIR path."""
        assert ALL_DECK_FILES_DIR == MTGJSON_DIR / "AllDeckFiles"


class TestUrls:
    """Tests for URL configuration."""

    def test_base_url(self):
        """Test MTGJSON base URL."""
        assert MTGJSON_BASE_URL == "https://mtgjson.com/api/v5"

    def test_all_printings_url(self):
        """Test AllPrintings URL."""
        assert ALL_PRINTINGS_URL == f"{MTGJSON_BASE_URL}/AllPrintings.sqlite.xz"

    def test_all_prices_url(self):
        """Test AllPrices URL."""
        assert ALL_PRICES_URL == f"{MTGJSON_BASE_URL}/AllPricesToday.sqlite.xz"

    def test_all_deck_files_url(self):
        """Test AllDeckFiles URL."""
        assert ALL_DECK_FILES_URL == f"{MTGJSON_BASE_URL}/AllDeckFiles.tar.xz"

    def test_keywords_url(self):
        """Test Keywords URL."""
        assert KEYWORDS_URL == f"{MTGJSON_BASE_URL}/Keywords.json.xz"


class TestEnsureDirs:
    """Tests for ensure_dirs function."""

    def test_ensure_dirs_creates_directories(self):
        """Test that ensure_dirs creates required directories."""
        ensure_dirs()
        assert MTGDB_HOME.exists()
        assert REFERENCE_DIR.exists()
        assert MTGJSON_DIR.exists()

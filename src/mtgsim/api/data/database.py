"""Database connection management for API data layer."""

import sqlite3

from mtgsim.config import config


class DatabaseManager:
    """Manages connections to all reference databases."""

    def __init__(self):
        self._sets_conn: sqlite3.Connection | None = None
        self._decks_conn: sqlite3.Connection | None = None
        self._prices_conn: sqlite3.Connection | None = None
        self._printings_conn: sqlite3.Connection | None = None
        self._initialized = False

    def init(self):
        """Initialize database connections."""
        if self._initialized:
            return

        sets_path = config.mtgjson_dir / "AllSets.sqlite"
        decks_path = config.mtgjson_dir / "AllDecks.sqlite"
        prices_path = config.mtgjson_dir / "AllPricesToday.sqlite"
        printings_path = config.mtgjson_dir / "AllPrintings.sqlite"

        if sets_path.exists():
            self._sets_conn = sqlite3.connect(sets_path, check_same_thread=False)
            self._sets_conn.row_factory = sqlite3.Row

        if decks_path.exists():
            self._decks_conn = sqlite3.connect(decks_path, check_same_thread=False)
            self._decks_conn.row_factory = sqlite3.Row

        if prices_path.exists():
            self._prices_conn = sqlite3.connect(prices_path, check_same_thread=False)
            self._prices_conn.row_factory = sqlite3.Row

        if printings_path.exists():
            self._printings_conn = sqlite3.connect(printings_path, check_same_thread=False)
            self._printings_conn.row_factory = sqlite3.Row

        self._initialized = True

    def close(self):
        """Close all database connections."""
        if self._sets_conn:
            self._sets_conn.close()
            self._sets_conn = None
        if self._decks_conn:
            self._decks_conn.close()
            self._decks_conn = None
        if self._prices_conn:
            self._prices_conn.close()
            self._prices_conn = None
        if self._printings_conn:
            self._printings_conn.close()
            self._printings_conn = None
        self._initialized = False

    @property
    def sets(self) -> sqlite3.Connection:
        """Get sets database connection."""
        if not self._sets_conn:
            raise RuntimeError("Sets database not initialized. Run 'mtgsim db sync-sets' first.")
        return self._sets_conn

    @property
    def decks(self) -> sqlite3.Connection:
        """Get decks database connection."""
        if not self._decks_conn:
            raise RuntimeError("Decks database not initialized. Run 'mtgsim db sync-decks' first.")
        return self._decks_conn

    @property
    def prices(self) -> sqlite3.Connection:
        """Get prices database connection."""
        if not self._prices_conn:
            raise RuntimeError("Prices database not initialized. Run 'mtgsim db sync' first.")
        return self._prices_conn

    @property
    def printings(self) -> sqlite3.Connection:
        """Get AllPrintings database connection."""
        if not self._printings_conn:
            raise RuntimeError("AllPrintings database not initialized. Run 'mtgsim db sync' first.")
        return self._printings_conn

    def status(self) -> dict[str, bool]:
        """Return status of each database connection."""
        return {
            "sets": self._sets_conn is not None,
            "decks": self._decks_conn is not None,
            "prices": self._prices_conn is not None,
            "printings": self._printings_conn is not None,
        }


# Singleton instance
db = DatabaseManager()


def init_databases():
    """Initialize all database connections."""
    db.init()


def close_databases():
    """Close all database connections."""
    db.close()

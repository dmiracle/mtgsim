"""Reference database wrapper with read-only connections and helper utilities."""

import json
import sqlite3

from mtgsim.config import MERGED_DB_PATH


def parse_json(value: str | None, default=None):
    """Parse JSON string, returning default if None or invalid."""
    if not value:
        return default if default is not None else []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def parse_json_dict(value: str | None) -> dict:
    """Parse JSON string into dict, returning empty dict if None or invalid."""
    if not value:
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}


def get_scryfall_image_url(identifiers_json: str | None, size: str = "normal") -> str | None:
    """Build Scryfall image URL from identifiers JSON."""
    identifiers = parse_json_dict(identifiers_json)
    scryfall_id = identifiers.get("scryfallId")
    if scryfall_id and len(scryfall_id) >= 2:
        return f"https://cards.scryfall.io/{size}/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg?v=1"
    return None


def paginate(page: int, limit: int, total: int) -> tuple[int, int]:
    """Calculate offset and total pages from pagination params."""
    offset = (page - 1) * limit
    pages = (total + limit - 1) // limit if limit > 0 else 0
    return offset, pages


def build_in_clause(items: list) -> tuple[str, list]:
    """Build SQL IN clause with placeholders."""
    if not items:
        return "1=0", []
    placeholders = ",".join(["?"] * len(items))
    return f"IN ({placeholders})", list(items)


class ReferenceDb:
    """Manages read-only connection to the merged reference database."""

    def __init__(self):
        self._conn: sqlite3.Connection | None = None
        self._initialized = False

    def init(self):
        """Initialize database connection."""
        if self._initialized:
            return

        if MERGED_DB_PATH.exists():
            self._conn = sqlite3.connect(str(MERGED_DB_PATH), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row

        self._initialized = True

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
        self._conn = None
        self._initialized = False

    @property
    def conn(self) -> sqlite3.Connection:
        """Get the database connection."""
        if not self._conn:
            raise RuntimeError("Database not initialized. Run 'mtgsim db sync' first.")
        return self._conn

    # Legacy properties for backwards compatibility - all return same connection
    @property
    def sets(self) -> sqlite3.Connection:
        """Get database connection (legacy alias)."""
        return self.conn

    @property
    def decks(self) -> sqlite3.Connection:
        """Get database connection (legacy alias)."""
        return self.conn

    @property
    def prices(self) -> sqlite3.Connection:
        """Get database connection (legacy alias)."""
        return self.conn

    @property
    def printings(self) -> sqlite3.Connection:
        """Get database connection (legacy alias)."""
        return self.conn

    def is_initialized(self) -> bool:
        return self._conn is not None

    # Legacy methods for backwards compatibility
    def has_sets(self) -> bool:
        return self.is_initialized()

    def has_decks(self) -> bool:
        return self.is_initialized()

    def has_prices(self) -> bool:
        return self.is_initialized()

    def has_printings(self) -> bool:
        return self.is_initialized()

    def status(self) -> dict[str, bool]:
        """Return status of database connection."""
        initialized = self.is_initialized()
        return {
            "connected": initialized,
            "sets": initialized,
            "decks": initialized,
            "prices": initialized,
            "printings": initialized,
        }

    def get_tcgplayer_prices(self, uuids: list[str]) -> dict[str, float]:
        """
        Batch lookup TCGPlayer retail prices for card UUIDs.
        Returns dict mapping uuid -> price.
        """
        if not uuids or not self.is_initialized():
            return {}

        in_clause, params = build_in_clause(uuids)
        cursor = self._conn.execute(
            f"""
            SELECT uuid, price FROM cardPrices
            WHERE uuid {in_clause}
              AND priceProvider = 'tcgplayer'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
              AND currency = 'USD'
            """,
            params,
        )
        return {row["uuid"]: row["price"] for row in cursor.fetchall()}

    def get_card_price(self, uuid: str, provider: str = "tcgplayer") -> float | None:
        """Get single card price."""
        if not self.is_initialized():
            return None
        cursor = self._conn.execute(
            """
            SELECT price FROM cardPrices
            WHERE uuid = ?
              AND priceProvider = ?
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
              AND currency = 'USD'
            """,
            [uuid, provider],
        )
        row = cursor.fetchone()
        return row["price"] if row else None

    def get_set_name(self, set_code: str) -> str | None:
        """Get set name by code."""
        if not self.is_initialized():
            return None
        cursor = self._conn.execute("SELECT name FROM setdb WHERE code = ?", [set_code])
        row = cursor.fetchone()
        return row["name"] if row else None

    def count_cards(self, where: str = "1=1", params: list | None = None) -> int:
        """Count cards matching condition."""
        cursor = self.conn.execute(f"SELECT COUNT(*) FROM setcarddb WHERE {where}", params or [])
        return cursor.fetchone()[0]

    def count_sets(self) -> int:
        """Count total sets."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM setdb")
        return cursor.fetchone()[0]

    def count_decks(self) -> int:
        """Count total decks."""
        if not self.is_initialized():
            return 0
        cursor = self.conn.execute("SELECT COUNT(*) FROM deck")
        return cursor.fetchone()[0]


# Singleton instance
ref_db = ReferenceDb()

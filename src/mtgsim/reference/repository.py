"""Unified reference database repository.

This module provides a centralized interface for accessing all MTGJSON reference
databases with common operations, helper methods, and consistent error handling.
"""

import json
import sqlite3
from typing import Any

from ..config import MTGSimConfig


class ReferenceRepository:
    """Unified access to reference databases with common operations.

    This class provides a single interface for accessing AllPrintings, AllPrices,
    AllDecks, and AllSets databases with helper methods for common operations
    like JSON decoding, pagination, and price joins.
    """

    def __init__(self, config: MTGSimConfig):
        """Initialize repository with configuration.

        Args:
            config: MTGSim configuration instance
        """
        self.config = config
        self._connections: dict[str, sqlite3.Connection] = {}
        self._initialized = False

    def init(self) -> None:
        """Initialize database connections.

        Opens connections to all available reference databases and sets
        row factory for dict-like access.
        """
        if self._initialized:
            return

        db_files = {
            "sets": "AllSets.sqlite",
            "decks": "AllDecks.sqlite",
            "prices": "AllPricesToday.sqlite",
            "printings": "AllPrintings.sqlite",
        }

        for db_name, filename in db_files.items():
            db_path = self.config.mtgjson_dir / filename
            if db_path.exists():
                conn = sqlite3.connect(db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self._connections[db_name] = conn

        self._initialized = True

    def close(self) -> None:
        """Close all database connections."""
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()
        self._initialized = False

    def get_connection(self, db_name: str) -> sqlite3.Connection:
        """Get connection to specified reference database.

        Args:
            db_name: Database name ('sets', 'decks', 'prices', 'printings')

        Returns:
            SQLite connection with row factory

        Raises:
            RuntimeError: If database is not available
        """
        if not self._initialized:
            self.init()

        if db_name not in self._connections:
            db_map = {
                "sets": "AllSets.sqlite",
                "decks": "AllDecks.sqlite",
                "prices": "AllPricesToday.sqlite",
                "printings": "AllPrintings.sqlite",
            }
            filename = db_map.get(db_name, f"{db_name}.sqlite")
            raise RuntimeError(f"{filename} database not available. Run 'mtgsim db sync' first.")

        return self._connections[db_name]

    def execute_paginated_query(
        self, db_name: str, query: str, params: list[Any], page: int, limit: int
    ) -> tuple[list[sqlite3.Row], int]:
        """Execute paginated query with total count.

        Args:
            db_name: Database name to query
            query: SQL query without LIMIT/OFFSET
            params: Query parameters
            page: Page number (1-based)
            limit: Items per page

        Returns:
            Tuple of (rows, total_count)
        """
        conn = self.get_connection(db_name)

        # Get total count by wrapping query
        count_query = f"SELECT COUNT(*) FROM ({query})"
        cursor = conn.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        offset = (page - 1) * limit
        paginated_query = f"{query} LIMIT ? OFFSET ?"
        cursor = conn.execute(paginated_query, params + [limit, offset])
        rows = cursor.fetchall()

        return rows, total

    def get_price_map(self, uuids: list[str]) -> dict[str, float]:
        """Get price mapping for card UUIDs.

        Args:
            uuids: List of card UUIDs

        Returns:
            Dictionary mapping UUID to TCGPlayer price
        """
        if not uuids:
            return {}

        try:
            conn = self.get_connection("prices")
        except RuntimeError:
            return {}

        placeholders = ",".join(["?"] * len(uuids))
        cursor = conn.execute(
            f"""
            SELECT uuid, price FROM cardPrices
            WHERE uuid IN ({placeholders})
              AND priceProvider = 'tcgplayer'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
              AND currency = 'USD'
            """,
            uuids,
        )

        return {row["uuid"]: row["price"] for row in cursor.fetchall() if row["price"]}

    def decode_json_field(self, value: str | None) -> Any:
        """Safely decode JSON field from database.

        Args:
            value: JSON string from database field

        Returns:
            Decoded JSON value or empty list/dict on error
        """
        if not value:
            return []

        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []

    def execute_query(self, db_name: str, query: str, params: list[Any] | None = None) -> list[sqlite3.Row]:
        """Execute a query and return all results.

        Args:
            db_name: Database name to query
            query: SQL query
            params: Query parameters

        Returns:
            List of result rows
        """
        conn = self.get_connection(db_name)
        cursor = conn.execute(query, params or [])
        return cursor.fetchall()

    def execute_single_query(self, db_name: str, query: str, params: list[Any] | None = None) -> sqlite3.Row | None:
        """Execute a query and return single result.

        Args:
            db_name: Database name to query
            query: SQL query
            params: Query parameters

        Returns:
            Single result row or None
        """
        conn = self.get_connection(db_name)
        cursor = conn.execute(query, params or [])
        return cursor.fetchone()

    def get_bulk_prices(self, uuids: list[str]) -> dict[str, float]:
        """Get prices for multiple cards efficiently.

        This is an alias for get_price_map for consistency with the design.

        Args:
            uuids: List of card UUIDs

        Returns:
            Dictionary mapping UUID to price
        """
        return self.get_price_map(uuids)

    def status(self) -> dict[str, bool]:
        """Return status of each database connection.

        Returns:
            Dictionary mapping database name to availability status
        """
        if not self._initialized:
            self.init()

        return {
            "sets": "sets" in self._connections,
            "decks": "decks" in self._connections,
            "prices": "prices" in self._connections,
            "printings": "printings" in self._connections,
        }

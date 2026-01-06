"""Sets data access layer."""

import json

from mtgsim.config import config
from mtgsim.reference.repository import ReferenceRepository

from .cards import get_scryfall_image_url


class SetsData:
    """Data access for sets."""

    def __init__(self):
        """Initialize with reference repository."""
        self.repo = ReferenceRepository(config)

    def list_sets(
        self,
        q: str | None = None,
        set_type: str | None = None,
        block: str | None = None,
        sort: str = "release_date",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        List sets with filtering and pagination.

        Returns: (list of sets, total count)
        """
        # Build WHERE clause
        conditions = []
        params = []

        if q:
            conditions.append("(name LIKE ? OR code LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%"])

        if set_type:
            conditions.append("type = ?")
            params.append(set_type)

        if block:
            conditions.append("block = ?")
            params.append(block)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Map sort fields
        sort_map = {
            "name": "name",
            "release_date": "release_date",
            "code": "code",
            "size": "total_set_size",
        }
        sort_field = sort_map.get(sort, "release_date")
        order_dir = "DESC" if order == "desc" else "ASC"

        # Build query
        query = f"""
            SELECT code, name, type, release_date, base_set_size, total_set_size,
                   block, keyrune_code, is_foil_only, is_online_only
            FROM setdb
            WHERE {where_clause}
            ORDER BY {sort_field} {order_dir}
        """

        # Execute paginated query
        rows, total = self.repo.execute_paginated_query("sets", query, params, page, limit)

        sets = []
        for row in rows:
            sets.append(
                {
                    "code": row["code"],
                    "name": row["name"],
                    "type": row["type"],
                    "release_date": row["release_date"],
                    "base_set_size": row["base_set_size"],
                    "total_set_size": row["total_set_size"],
                    "block": row["block"],
                    "keyrune_code": row["keyrune_code"],
                }
            )

        return sets, total

    def get_set(self, code: str) -> dict | None:
        """Get set metadata by code."""
        row = self.repo.execute_single_query(
            "sets",
            """
            SELECT code, name, type, release_date, base_set_size, total_set_size,
                   block, keyrune_code, is_foil_only, is_online_only, mtgo_code,
                   tcgplayer_group_id, cardmarket_id, languages, translations
            FROM setdb
            WHERE code = ?
            """,
            [code],
        )

        if not row:
            return None

        return {
            "code": row["code"],
            "name": row["name"],
            "type": row["type"],
            "release_date": row["release_date"],
            "base_set_size": row["base_set_size"],
            "total_set_size": row["total_set_size"],
            "block": row["block"],
            "keyrune_code": row["keyrune_code"],
            "is_foil_only": bool(row["is_foil_only"]),
            "is_online_only": bool(row["is_online_only"]),
            "mtgo_code": row["mtgo_code"],
            "tcgplayer_group_id": row["tcgplayer_group_id"],
            "cardmarket_id": row["cardmarket_id"],
            "languages": self.repo.decode_json_field(row["languages"]),
            "translations": self.repo.decode_json_field(row["translations"]),
        }

    def get_set_cards(
        self,
        code: str,
        rarity: str | None = None,
        color: str | None = None,
        card_type: str | None = None,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        Get cards in a set with filtering and pagination.

        Returns: (list of cards, total count)
        """
        conditions = ["set_code = ?"]
        params = [code]

        if rarity:
            conditions.append("rarity = ?")
            params.append(rarity)

        if color:
            conditions.append("color_identity LIKE ?")
            params.append(f'%"{color}"%')

        if card_type:
            conditions.append("type LIKE ?")
            params.append(f"%{card_type}%")

        where_clause = " AND ".join(conditions)

        # Build query
        query = f"""
            SELECT uuid, name, mana_cost, mana_value, type, rarity,
                   color_identity, colors, power, toughness, number, identifiers, text
            FROM setcarddb
            WHERE {where_clause}
            ORDER BY CAST(number AS INTEGER), number
        """

        # Execute paginated query
        rows, total = self.repo.execute_paginated_query("sets", query, params, page, limit)

        # Get prices for all cards in batch
        uuids = [row["uuid"] for row in rows]
        price_map = self.repo.get_price_map(uuids)

        cards = []
        for row in rows:
            cards.append(
                {
                    "uuid": row["uuid"],
                    "name": row["name"],
                    "mana_cost": row["mana_cost"],
                    "mana_value": row["mana_value"],
                    "type": row["type"],
                    "rarity": row["rarity"],
                    "color_identity": self.repo.decode_json_field(row["color_identity"]),
                    "colors": self.repo.decode_json_field(row["colors"]),
                    "power": row["power"],
                    "toughness": row["toughness"],
                    "number": row["number"],
                    "text": row["text"],
                    "image_url": get_scryfall_image_url(row["identifiers"], "large"),
                    "price": price_map.get(row["uuid"]),
                }
            )

        return cards, total

    def get_set_stats(self, code: str) -> dict:
        """Calculate statistics for a set."""
        # Rarity distribution
        rows = self.repo.execute_query(
            "sets",
            """
            SELECT rarity, COUNT(*) as count
            FROM setcarddb
            WHERE set_code = ?
            GROUP BY rarity
            """,
            [code],
        )
        rarity_count = {row["rarity"]: row["count"] for row in rows}

        # Color distribution
        rows = self.repo.execute_query("sets", "SELECT color_identity FROM setcarddb WHERE set_code = ?", [code])
        color_count = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for row in rows:
            colors = self.repo.decode_json_field(row["color_identity"])
            if not colors:
                color_count["C"] += 1
            else:
                for c in colors:
                    if c in color_count:
                        color_count[c] += 1

        # Type distribution
        rows = self.repo.execute_query("sets", "SELECT types FROM setcarddb WHERE set_code = ?", [code])
        type_count = {}
        for row in rows:
            types = self.repo.decode_json_field(row["types"])
            for t in types:
                type_count[t] = type_count.get(t, 0) + 1

        # Keywords
        rows = self.repo.execute_query("sets", "SELECT keywords FROM setcarddb WHERE set_code = ?", [code])
        keyword_count = {}
        for row in rows:
            keywords = self.repo.decode_json_field(row["keywords"])
            for k in keywords:
                keyword_count[k] = keyword_count.get(k, 0) + 1

        # Calculate total set price
        total_price = self._get_set_price(code)

        return {
            "rarity_count": rarity_count,
            "color_distribution": color_count,
            "type_distribution": type_count,
            "keywords": keyword_count,
            "total_price": total_price,
        }

    def _get_set_price(self, code: str) -> float | None:
        """Calculate total set price from tcgplayer prices."""
        # Get all card UUIDs in the set
        rows = self.repo.execute_query("sets", "SELECT uuid FROM setcarddb WHERE set_code = ?", [code])
        uuids = [row["uuid"] for row in rows]
        if not uuids:
            return None

        # Get prices for these cards
        price_map = self.repo.get_price_map(uuids)
        total = sum(price_map.values())
        return round(total, 2) if total > 0 else None

    def get_available_types(self) -> list[str]:
        """Get list of unique set types."""
        rows = self.repo.execute_query("sets", "SELECT DISTINCT type FROM setdb ORDER BY type")
        return [row["type"] for row in rows]

    def get_available_blocks(self) -> list[str]:
        """Get list of unique blocks."""
        rows = self.repo.execute_query(
            "sets",
            """
            SELECT DISTINCT block FROM setdb
            WHERE block IS NOT NULL
            ORDER BY block
            """,
        )
        return [row["block"] for row in rows]


# Singleton instance
sets_data = SetsData()

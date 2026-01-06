"""Sets data access layer."""

import json

from .cards import get_scryfall_image_url
from .database import db


class SetsData:
    """Data access for sets."""

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
        conn = db.sets

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

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM setdb WHERE {where_clause}"
        cursor = conn.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        offset = (page - 1) * limit
        query_sql = f"""
            SELECT code, name, type, release_date, base_set_size, total_set_size,
                   block, keyrune_code, is_foil_only, is_online_only
            FROM setdb
            WHERE {where_clause}
            ORDER BY {sort_field} {order_dir}
            LIMIT ? OFFSET ?
        """
        cursor = conn.execute(query_sql, params + [limit, offset])

        sets = []
        for row in cursor.fetchall():
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
        conn = db.sets

        cursor = conn.execute(
            """
            SELECT code, name, type, release_date, base_set_size, total_set_size,
                   block, keyrune_code, is_foil_only, is_online_only, mtgo_code,
                   tcgplayer_group_id, cardmarket_id, languages, translations
            FROM setdb
            WHERE code = ?
        """,
            [code],
        )

        row = cursor.fetchone()
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
            "languages": json.loads(row["languages"]) if row["languages"] else [],
            "translations": json.loads(row["translations"]) if row["translations"] else {},
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
        conn = db.sets

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

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM setcarddb WHERE {where_clause}"
        cursor = conn.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        offset = (page - 1) * limit
        query_sql = f"""
            SELECT uuid, name, mana_cost, mana_value, type, rarity,
                   color_identity, colors, power, toughness, number, identifiers, text
            FROM setcarddb
            WHERE {where_clause}
            ORDER BY CAST(number AS INTEGER), number
            LIMIT ? OFFSET ?
        """
        cursor = conn.execute(query_sql, params + [limit, offset])
        rows = cursor.fetchall()

        # Get prices for all cards in batch
        price_map = {}
        try:
            prices_conn = db.prices
            uuids = [row["uuid"] for row in rows]
            if uuids:
                placeholders = ",".join(["?"] * len(uuids))
                price_cursor = prices_conn.execute(
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
                price_map = {r["uuid"]: r["price"] for r in price_cursor.fetchall()}
        except RuntimeError:
            pass

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
                    "color_identity": json.loads(row["color_identity"]) if row["color_identity"] else [],
                    "colors": json.loads(row["colors"]) if row["colors"] else [],
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
        conn = db.sets

        # Rarity distribution
        cursor = conn.execute(
            """
            SELECT rarity, COUNT(*) as count
            FROM setcarddb
            WHERE set_code = ?
            GROUP BY rarity
        """,
            [code],
        )
        rarity_count = {row["rarity"]: row["count"] for row in cursor.fetchall()}

        # Color distribution
        cursor = conn.execute(
            """
            SELECT color_identity FROM setcarddb WHERE set_code = ?
        """,
            [code],
        )
        color_count = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for row in cursor.fetchall():
            colors = json.loads(row["color_identity"]) if row["color_identity"] else []
            if not colors:
                color_count["C"] += 1
            else:
                for c in colors:
                    if c in color_count:
                        color_count[c] += 1

        # Type distribution
        cursor = conn.execute(
            """
            SELECT types FROM setcarddb WHERE set_code = ?
        """,
            [code],
        )
        type_count = {}
        for row in cursor.fetchall():
            types = json.loads(row["types"]) if row["types"] else []
            for t in types:
                type_count[t] = type_count.get(t, 0) + 1

        # Keywords
        cursor = conn.execute(
            """
            SELECT keywords FROM setcarddb WHERE set_code = ?
        """,
            [code],
        )
        keyword_count = {}
        for row in cursor.fetchall():
            keywords = json.loads(row["keywords"]) if row["keywords"] else []
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
        try:
            sets_conn = db.sets
            prices_conn = db.prices
        except RuntimeError:
            return None

        # Get all card UUIDs in the set
        cursor = sets_conn.execute(
            """
            SELECT uuid FROM setcarddb WHERE set_code = ?
        """,
            [code],
        )
        uuids = [row["uuid"] for row in cursor.fetchall()]
        if not uuids:
            return None

        # Get prices for these cards
        placeholders = ",".join(["?"] * len(uuids))
        cursor = prices_conn.execute(
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

        total = sum(row["price"] for row in cursor.fetchall() if row["price"])
        return round(total, 2) if total > 0 else None

    def get_available_types(self) -> list[str]:
        """Get list of unique set types."""
        conn = db.sets
        cursor = conn.execute("SELECT DISTINCT type FROM setdb ORDER BY type")
        return [row["type"] for row in cursor.fetchall()]

    def get_available_blocks(self) -> list[str]:
        """Get list of unique blocks."""
        conn = db.sets
        cursor = conn.execute("""
            SELECT DISTINCT block FROM setdb
            WHERE block IS NOT NULL
            ORDER BY block
        """)
        return [row["block"] for row in cursor.fetchall()]


# Singleton instance
sets_data = SetsData()

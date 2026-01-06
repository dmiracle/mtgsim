"""Cards data access layer."""

from mtgsim.reference.db import get_scryfall_image_url, parse_json, parse_json_dict

from .database import db


class CardsData:
    """Data access for cards."""

    def search_cards(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        Search cards with filtering and pagination.

        Returns: (list of cards, total count)
        """
        conn = db.sets

        conditions = []
        params = []

        if q:
            conditions.append("(name LIKE ? OR type LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%"])

        if set_code:
            conditions.append("set_code = ?")
            params.append(set_code)

        if rarity:
            conditions.append("rarity = ?")
            params.append(rarity)

        if card_type:
            conditions.append("type LIKE ?")
            params.append(f"%{card_type}%")

        if colors:
            for color in colors:
                conditions.append("color_identity LIKE ?")
                params.append(f'%"{color}"%')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Map sort fields
        sort_map = {
            "name": "name",
            "mana_value": "mana_value",
            "rarity": "rarity",
            "set_code": "set_code",
        }
        sort_field = sort_map.get(sort, "name")
        order_dir = "DESC" if order == "desc" else "ASC"

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM setcarddb WHERE {where_clause}"
        cursor = conn.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        offset = (page - 1) * limit
        query_sql = f"""
            SELECT uuid, name, mana_cost, mana_value, type, rarity,
                   set_code, color_identity, colors, power, toughness, number,
                   identifiers, text
            FROM setcarddb
            WHERE {where_clause}
            ORDER BY {sort_field} {order_dir}
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
                    "set_code": row["set_code"],
                    "color_identity": parse_json(row["color_identity"]),
                    "colors": parse_json(row["colors"]),
                    "power": row["power"],
                    "toughness": row["toughness"],
                    "number": row["number"],
                    "text": row["text"],
                    "image_url": get_scryfall_image_url(row["identifiers"], "large"),
                    "price": price_map.get(row["uuid"]),
                }
            )

        return cards, total

    def get_card(self, uuid: str) -> dict | None:
        """Get card details by UUID."""
        conn = db.sets

        cursor = conn.execute(
            """
            SELECT uuid, name, mana_cost, mana_value, type, types, subtypes,
                   supertypes, rarity, set_code, color_identity, colors,
                   power, toughness, text, flavor_text, number, artist,
                   keywords, legalities, identifiers
            FROM setcarddb
            WHERE uuid = ?
        """,
            [uuid],
        )

        row = cursor.fetchone()
        if not row:
            return None

        # Get set name
        set_cursor = conn.execute("SELECT name FROM setdb WHERE code = ?", [row["set_code"]])
        set_row = set_cursor.fetchone()
        set_name = set_row["name"] if set_row else None

        return {
            "uuid": row["uuid"],
            "name": row["name"],
            "mana_cost": row["mana_cost"],
            "mana_value": row["mana_value"],
            "type": row["type"],
            "types": parse_json(row["types"]),
            "subtypes": parse_json(row["subtypes"]),
            "supertypes": parse_json(row["supertypes"]),
            "rarity": row["rarity"],
            "set_code": row["set_code"],
            "set_name": set_name,
            "color_identity": parse_json(row["color_identity"]),
            "colors": parse_json(row["colors"]),
            "power": row["power"],
            "toughness": row["toughness"],
            "text": row["text"],
            "flavor_text": row["flavor_text"],
            "number": row["number"],
            "artist": row["artist"],
            "keywords": parse_json(row["keywords"]),
            "legalities": parse_json_dict(row["legalities"]),
            "image_url": get_scryfall_image_url(row["identifiers"], "large"),
        }

    def get_cards_by_name(self, name: str) -> list[dict]:
        """Get all printings of a card by exact name."""
        conn = db.sets

        cursor = conn.execute(
            """
            SELECT uuid, name, set_code, rarity, number
            FROM setcarddb
            WHERE name = ?
            ORDER BY set_code
        """,
            [name],
        )

        cards = []
        for row in cursor.fetchall():
            # Get set name
            set_cursor = conn.execute("SELECT name FROM setdb WHERE code = ?", [row["set_code"]])
            set_row = set_cursor.fetchone()
            set_name = set_row["name"] if set_row else None

            cards.append(
                {
                    "uuid": row["uuid"],
                    "name": row["name"],
                    "set_code": row["set_code"],
                    "set_name": set_name,
                    "rarity": row["rarity"],
                    "number": row["number"],
                }
            )

        return cards

    def get_card_appearances(self, uuid: str) -> list[dict]:
        """Get decks that contain this card."""
        try:
            conn = db.decks
        except RuntimeError:
            return []

        # First get the card name
        sets_conn = db.sets
        cursor = sets_conn.execute("SELECT name FROM setcarddb WHERE uuid = ?", [uuid])
        row = cursor.fetchone()
        if not row:
            return []
        card_name = row["name"]

        # Find decks containing this card
        cursor = conn.execute(
            """
            SELECT d.file_name, d.name, dc.count
            FROM deckcard dc
            JOIN deck d ON dc.deck_uuid = d.uuid
            WHERE dc.name = ?
            ORDER BY d.name
            LIMIT 20
        """,
            [card_name],
        )

        appearances = []
        for row in cursor.fetchall():
            appearances.append(
                {
                    "file": row["file_name"] + ".json",
                    "name": row["name"],
                    "count": row["count"],
                }
            )

        return appearances

    def get_other_printings(self, uuid: str) -> list[dict]:
        """Get other printings of the same card."""
        conn = db.sets

        # Get card name
        cursor = conn.execute("SELECT name FROM setcarddb WHERE uuid = ?", [uuid])
        row = cursor.fetchone()
        if not row:
            return []
        card_name = row["name"]

        # Get other printings
        cursor = conn.execute(
            """
            SELECT uuid, set_code, rarity
            FROM setcarddb
            WHERE name = ? AND uuid != ?
            ORDER BY set_code
        """,
            [card_name, uuid],
        )

        printings = []
        for row in cursor.fetchall():
            set_cursor = conn.execute("SELECT name FROM setdb WHERE code = ?", [row["set_code"]])
            set_row = set_cursor.fetchone()
            set_name = set_row["name"] if set_row else None

            printings.append(
                {
                    "uuid": row["uuid"],
                    "set_code": row["set_code"],
                    "set_name": set_name,
                }
            )

        return printings


# Singleton instance
cards_data = CardsData()

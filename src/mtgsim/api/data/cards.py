"""Cards data access layer."""

import json

from mtgsim.config import config
from mtgsim.reference.repository import ReferenceRepository


def get_scryfall_image_url(identifiers_json: str | None, size: str = "normal") -> str | None:
    """Build Scryfall image URL from identifiers JSON."""
    if not identifiers_json:
        return None
    try:
        identifiers = json.loads(identifiers_json)
        scryfall_id = identifiers.get("scryfallId")
        if scryfall_id:
            return f"https://cards.scryfall.io/{size}/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    return None


class CardsData:
    """Data access for cards."""

    def __init__(self):
        """Initialize with reference repository."""
        self.repo = ReferenceRepository(config)

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

        # Build query
        query = f"""
            SELECT uuid, name, mana_cost, mana_value, type, rarity,
                   set_code, color_identity, colors, power, toughness, number,
                   identifiers, text
            FROM setcarddb
            WHERE {where_clause}
            ORDER BY {sort_field} {order_dir}
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
                    "set_code": row["set_code"],
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

    def get_card(self, uuid: str) -> dict | None:
        """Get card details by UUID."""
        row = self.repo.execute_single_query(
            "sets",
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

        if not row:
            return None

        # Get set name
        set_row = self.repo.execute_single_query("sets", "SELECT name FROM setdb WHERE code = ?", [row["set_code"]])
        set_name = set_row["name"] if set_row else None

        return {
            "uuid": row["uuid"],
            "name": row["name"],
            "mana_cost": row["mana_cost"],
            "mana_value": row["mana_value"],
            "type": row["type"],
            "types": self.repo.decode_json_field(row["types"]),
            "subtypes": self.repo.decode_json_field(row["subtypes"]),
            "supertypes": self.repo.decode_json_field(row["supertypes"]),
            "rarity": row["rarity"],
            "set_code": row["set_code"],
            "set_name": set_name,
            "color_identity": self.repo.decode_json_field(row["color_identity"]),
            "colors": self.repo.decode_json_field(row["colors"]),
            "power": row["power"],
            "toughness": row["toughness"],
            "text": row["text"],
            "flavor_text": row["flavor_text"],
            "number": row["number"],
            "artist": row["artist"],
            "keywords": self.repo.decode_json_field(row["keywords"]),
            "legalities": self.repo.decode_json_field(row["legalities"]),
            "image_url": get_scryfall_image_url(row["identifiers"], "large"),
        }

    def get_cards_by_name(self, name: str) -> list[dict]:
        """Get all printings of a card by exact name."""
        rows = self.repo.execute_query(
            "sets",
            """
            SELECT uuid, name, set_code, rarity, number
            FROM setcarddb
            WHERE name = ?
            ORDER BY set_code
            """,
            [name],
        )

        cards = []
        for row in rows:
            # Get set name
            set_row = self.repo.execute_single_query("sets", "SELECT name FROM setdb WHERE code = ?", [row["set_code"]])
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
        # First get the card name
        row = self.repo.execute_single_query("sets", "SELECT name FROM setcarddb WHERE uuid = ?", [uuid])
        if not row:
            return []
        card_name = row["name"]

        # Find decks containing this card
        try:
            rows = self.repo.execute_query(
                "decks",
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
        except RuntimeError:
            return []

        appearances = []
        for row in rows:
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
        # Get card name
        row = self.repo.execute_single_query("sets", "SELECT name FROM setcarddb WHERE uuid = ?", [uuid])
        if not row:
            return []
        card_name = row["name"]

        # Get other printings
        rows = self.repo.execute_query(
            "sets",
            """
            SELECT uuid, set_code, rarity
            FROM setcarddb
            WHERE name = ? AND uuid != ?
            ORDER BY set_code
            """,
            [card_name, uuid],
        )

        printings = []
        for row in rows:
            set_row = self.repo.execute_single_query("sets", "SELECT name FROM setdb WHERE code = ?", [row["set_code"]])
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

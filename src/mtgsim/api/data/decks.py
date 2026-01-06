"""Decks data access layer."""

import json

from mtgsim.config import config
from mtgsim.reference.repository import ReferenceRepository

from .cards import get_scryfall_image_url


def _get_deck_price(deck_uuid: str, repo: ReferenceRepository) -> float | None:
    """Calculate total deck price from tcgplayer prices."""
    # Get card UUIDs and counts from deck
    try:
        rows = repo.execute_query(
            "decks",
            """
            SELECT card_uuid, count FROM deckcard
            WHERE deck_uuid = ? AND board IN ('mainBoard', 'sideBoard')
            """,
            [deck_uuid],
        )
    except RuntimeError:
        return None

    cards = [(row["card_uuid"], row["count"]) for row in rows]
    if not cards:
        return None

    # Get prices for these cards
    uuids = [c[0] for c in cards if c[0]]
    if not uuids:
        return None

    price_map = repo.get_price_map(uuids)

    # Calculate total
    total = 0.0
    for uuid, count in cards:
        if uuid and uuid in price_map:
            total += price_map[uuid] * count

    return round(total, 2) if total > 0 else None


class DecksData:
    """Data access for decks."""

    def __init__(self):
        """Initialize with reference repository."""
        self.repo = ReferenceRepository(config)

    def list_decks(
        self,
        q: str | None = None,
        format_filter: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: str | None = None,
        card_count_min: int | None = None,
        card_count_max: int | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        List decks with filtering and pagination.

        Returns: (list of decks, total count)
        """
        conditions = []
        params = []

        if q:
            conditions.append("(d.name LIKE ? OR d.file_name LIKE ?)")
            params.extend([f"%{q}%", f"%{q}%"])

        if set_code:
            conditions.append("d.code = ?")
            params.append(set_code)

        if deck_type:
            conditions.append("d.type = ?")
            params.append(deck_type)

        if card_count_min is not None:
            conditions.append("""
                (SELECT COALESCE(SUM(dc.count), 0) FROM deckcard dc
                 WHERE dc.deck_uuid = d.uuid AND dc.board IN ('mainBoard', 'sideBoard')) >= ?
            """)
            params.append(card_count_min)

        if card_count_max is not None:
            conditions.append("""
                (SELECT COALESCE(SUM(dc.count), 0) FROM deckcard dc
                 WHERE dc.deck_uuid = d.uuid AND dc.board IN ('mainBoard', 'sideBoard')) <= ?
            """)
            params.append(card_count_max)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Map sort fields
        sort_map = {
            "name": "d.name",
            "release_date": "d.release_date",
            "code": "d.code",
            "card_count": "(d.main_board_count + d.side_board_count)",
        }
        sort_field = sort_map.get(sort, "d.name")
        order_dir = "DESC" if order == "desc" else "ASC"

        # Build query
        query = f"""
            SELECT d.uuid, d.file_name, d.name, d.code, d.type, d.release_date,
                   (SELECT COALESCE(SUM(dc.count), 0) FROM deckcard dc
                    WHERE dc.deck_uuid = d.uuid AND dc.board IN ('mainBoard', 'sideBoard')) as card_count
            FROM deck d
            WHERE {where_clause}
            ORDER BY {sort_field} {order_dir}
        """

        # Execute paginated query
        try:
            rows, total = self.repo.execute_paginated_query("decks", query, params, page, limit)
        except RuntimeError:
            return [], 0

        decks = []
        for row in rows:
            # Get color identity for deck
            colors = self._get_deck_colors(row["uuid"])
            # Get price for deck
            price = _get_deck_price(row["uuid"], self.repo)

            decks.append(
                {
                    "file": row["file_name"] + ".json",
                    "name": row["name"],
                    "code": row["code"],
                    "type": row["type"],
                    "release_date": row["release_date"],
                    "card_count": row["card_count"] or 0,
                    "colors": colors,
                    "price": price,
                }
            )

        return decks, total

    def _get_deck_colors(self, deck_uuid: str) -> list[str]:
        """Get combined color identity for a deck."""
        try:
            rows = self.repo.execute_query(
                "decks",
                """
                SELECT DISTINCT color_identity FROM deckcard
                WHERE deck_uuid = ?
                """,
                [deck_uuid],
            )
        except RuntimeError:
            return []

        colors = set()
        for row in rows:
            ci = self.repo.decode_json_field(row["color_identity"])
            colors.update(ci)

        # Sort in WUBRG order
        order = ["W", "U", "B", "R", "G"]
        return sorted(colors, key=lambda c: order.index(c) if c in order else 99)

    def get_deck(self, file_name: str) -> dict | None:
        """Get full deck details by file name."""
        # Remove .json extension if present
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        try:
            row = self.repo.execute_single_query(
                "decks",
                """
                SELECT uuid, file_name, name, code, type, release_date,
                       main_board_count, side_board_count, commander_count,
                       commander, meta_json
                FROM deck
                WHERE file_name = ?
                """,
                [file_name],
            )
        except RuntimeError:
            return None

        if not row:
            return None

        deck_uuid = row["uuid"]

        # Get cards by board
        main_board = self._get_deck_cards(deck_uuid, "mainBoard")
        side_board = self._get_deck_cards(deck_uuid, "sideBoard")
        commander = self._get_deck_cards(deck_uuid, "commander")

        # Calculate stats
        stats = self._calculate_deck_stats(deck_uuid)

        # Get colors
        colors = self._get_deck_colors(deck_uuid)

        # Calculate legality
        legality = self._calculate_deck_legality(deck_uuid)

        # Calculate total price
        price = _get_deck_price(deck_uuid, self.repo)

        return {
            "meta": {
                "file": row["file_name"] + ".json",
                "name": row["name"],
                "code": row["code"],
                "type": row["type"],
                "release_date": row["release_date"],
            },
            "colors": colors,
            "legality": legality,
            "commander": commander,
            "main_board": main_board,
            "side_board": side_board,
            "stats": stats,
            "price": price,
        }

    def _get_deck_cards(self, deck_uuid: str, board: str) -> list[dict]:
        """Get cards from a specific board."""
        try:
            rows = self.repo.execute_query(
                "decks",
                """
                SELECT card_uuid, name, count, mana_cost, mana_value, types,
                       rarity, color_identity, colors, power, toughness, identifiers_json, text
                FROM deckcard
                WHERE deck_uuid = ? AND board = ?
                ORDER BY mana_value, name
                """,
                [deck_uuid, board],
            )
        except RuntimeError:
            return []

        if not rows:
            return []

        # Get prices for all cards in batch
        uuids = [row["card_uuid"] for row in rows if row["card_uuid"]]
        price_map = self.repo.get_price_map(uuids)

        cards = []
        for row in rows:
            cards.append(
                {
                    "uuid": row["card_uuid"],
                    "name": row["name"],
                    "count": row["count"],
                    "mana_cost": row["mana_cost"],
                    "mana_value": row["mana_value"],
                    "type": ", ".join(self.repo.decode_json_field(row["types"])) if row["types"] else None,
                    "rarity": row["rarity"],
                    "color_identity": self.repo.decode_json_field(row["color_identity"]),
                    "text": row["text"],
                    "image_url": get_scryfall_image_url(row["identifiers_json"], "large"),
                    "price": price_map.get(row["card_uuid"]),
                }
            )

        return cards

    def _calculate_deck_stats(self, deck_uuid: str) -> dict:
        """Calculate deck statistics."""
        try:
            # Total cards
            row = self.repo.execute_single_query(
                "decks",
                """
                SELECT SUM(count) as total, COUNT(*) as unique_count
                FROM deckcard
                WHERE deck_uuid = ? AND board IN ('mainBoard', 'sideBoard')
                """,
                [deck_uuid],
            )
            total_cards = row["total"] or 0 if row else 0
            unique_cards = row["unique_count"] or 0 if row else 0

            # Mana curve (mainBoard only)
            rows = self.repo.execute_query(
                "decks",
                """
                SELECT
                    CASE
                        WHEN mana_value IS NULL THEN 'X'
                        WHEN mana_value >= 7 THEN '7+'
                        ELSE CAST(CAST(mana_value AS INTEGER) AS TEXT)
                    END as mv,
                    SUM(count) as count
                FROM deckcard
                WHERE deck_uuid = ? AND board = 'mainBoard'
                GROUP BY mv
                ORDER BY mv
                """,
                [deck_uuid],
            )
            mana_curve = {row["mv"]: row["count"] for row in rows}

            # Type distribution
            rows = self.repo.execute_query(
                "decks",
                """
                SELECT types, SUM(count) as count
                FROM deckcard
                WHERE deck_uuid = ? AND board = 'mainBoard'
                GROUP BY types
                """,
                [deck_uuid],
            )
            type_dist = {}
            for row in rows:
                types = self.repo.decode_json_field(row["types"])
                for t in types:
                    type_dist[t] = type_dist.get(t, 0) + row["count"]

            # Rarity distribution
            rows = self.repo.execute_query(
                "decks",
                """
                SELECT rarity, SUM(count) as count
                FROM deckcard
                WHERE deck_uuid = ? AND board = 'mainBoard'
                GROUP BY rarity
                """,
                [deck_uuid],
            )
            rarity_dist = {row["rarity"]: row["count"] for row in rows if row["rarity"]}

            # Color distribution
            rows = self.repo.execute_query(
                "decks",
                """
                SELECT color_identity, SUM(count) as count
                FROM deckcard
                WHERE deck_uuid = ? AND board = 'mainBoard'
                GROUP BY color_identity
                """,
                [deck_uuid],
            )
            color_dist = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
            for row in rows:
                colors = self.repo.decode_json_field(row["color_identity"])
                if not colors:
                    color_dist["C"] += row["count"]
                else:
                    for c in colors:
                        if c in color_dist:
                            color_dist[c] += row["count"]

        except RuntimeError:
            # Return empty stats if database not available
            return {
                "total_cards": 0,
                "unique_cards": 0,
                "mana_curve": {},
                "type_distribution": {},
                "rarity_distribution": {},
                "color_distribution": {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0},
            }

        return {
            "total_cards": total_cards,
            "unique_cards": unique_cards,
            "mana_curve": mana_curve,
            "type_distribution": type_dist,
            "rarity_distribution": rarity_dist,
            "color_distribution": color_dist,
        }

    def _calculate_deck_legality(self, deck_uuid: str) -> dict:
        """Calculate deck legality across formats."""
        try:
            # Get all card legalities
            rows = self.repo.execute_query(
                "decks", "SELECT legalities_json FROM deckcard WHERE deck_uuid = ?", [deck_uuid]
            )
        except RuntimeError:
            return dict.fromkeys(["standard", "pioneer", "modern", "legacy", "vintage", "commander"], False)

        formats = ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]
        legality = dict.fromkeys(formats, True)

        for row in rows:
            card_legalities = self.repo.decode_json_field(row["legalities_json"])
            for fmt in formats:
                if card_legalities.get(fmt) != "Legal":
                    legality[fmt] = False

        return legality

    def get_available_sets(self) -> list[str]:
        """Get list of set codes that have decks."""
        try:
            rows = self.repo.execute_query("decks", "SELECT DISTINCT code FROM deck ORDER BY code")
            return [row["code"] for row in rows]
        except RuntimeError:
            return []

    def get_available_formats(self) -> list[str]:
        """Get list of formats decks are legal in."""
        return ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]


# Singleton instance
decks_data = DecksData()

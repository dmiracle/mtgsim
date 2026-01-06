"""Decks data access layer."""

import json

from .cards import get_scryfall_image_url
from .database import db


def _get_deck_price(deck_uuid: str) -> float | None:
    """Calculate total deck price from tcgplayer prices."""
    try:
        decks_conn = db.decks
        prices_conn = db.prices
    except RuntimeError:
        return None

    # Get card UUIDs and counts from deck
    cursor = decks_conn.execute(
        """
        SELECT card_uuid, count FROM deckcard
        WHERE deck_uuid = ? AND board IN ('mainBoard', 'sideBoard')
    """,
        [deck_uuid],
    )

    cards = [(row["card_uuid"], row["count"]) for row in cursor.fetchall()]
    if not cards:
        return None

    # Get prices for these cards
    uuids = [c[0] for c in cards if c[0]]
    if not uuids:
        return None

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

    price_map = {row["uuid"]: row["price"] for row in cursor.fetchall()}

    # Calculate total
    total = 0.0
    for uuid, count in cards:
        if uuid and uuid in price_map:
            total += price_map[uuid] * count

    return round(total, 2) if total > 0 else None


class DecksData:
    """Data access for decks."""

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
        conn = db.decks

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

        # Get total count
        count_sql = f"SELECT COUNT(*) FROM deck d WHERE {where_clause}"
        cursor = conn.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # Get paginated results
        offset = (page - 1) * limit
        query_sql = f"""
            SELECT d.uuid, d.file_name, d.name, d.code, d.type, d.release_date,
                   (SELECT COALESCE(SUM(dc.count), 0) FROM deckcard dc
                    WHERE dc.deck_uuid = d.uuid AND dc.board IN ('mainBoard', 'sideBoard')) as card_count
            FROM deck d
            WHERE {where_clause}
            ORDER BY {sort_field} {order_dir}
            LIMIT ? OFFSET ?
        """
        cursor = conn.execute(query_sql, params + [limit, offset])

        decks = []
        for row in cursor.fetchall():
            # Get color identity for deck
            colors = self._get_deck_colors(row["uuid"])
            # Get price for deck
            price = _get_deck_price(row["uuid"])

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
        conn = db.decks
        cursor = conn.execute(
            """
            SELECT DISTINCT color_identity FROM deckcard
            WHERE deck_uuid = ?
        """,
            [deck_uuid],
        )

        colors = set()
        for row in cursor.fetchall():
            ci = json.loads(row["color_identity"]) if row["color_identity"] else []
            colors.update(ci)

        # Sort in WUBRG order
        order = ["W", "U", "B", "R", "G"]
        return sorted(colors, key=lambda c: order.index(c) if c in order else 99)

    def get_deck(self, file_name: str) -> dict | None:
        """Get full deck details by file name."""
        conn = db.decks

        # Remove .json extension if present
        if file_name.endswith(".json"):
            file_name = file_name[:-5]

        cursor = conn.execute(
            """
            SELECT uuid, file_name, name, code, type, release_date,
                   main_board_count, side_board_count, commander_count,
                   commander, meta_json
            FROM deck
            WHERE file_name = ?
        """,
            [file_name],
        )

        row = cursor.fetchone()
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
        price = _get_deck_price(deck_uuid)

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
        conn = db.decks
        cursor = conn.execute(
            """
            SELECT card_uuid, name, count, mana_cost, mana_value, types,
                   rarity, color_identity, colors, power, toughness, identifiers_json, text
            FROM deckcard
            WHERE deck_uuid = ? AND board = ?
            ORDER BY mana_value, name
        """,
            [deck_uuid, board],
        )

        rows = cursor.fetchall()
        if not rows:
            return []

        # Get prices for all cards in batch
        price_map = {}
        try:
            prices_conn = db.prices
            uuids = [row["card_uuid"] for row in rows if row["card_uuid"]]
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
                    "uuid": row["card_uuid"],
                    "name": row["name"],
                    "count": row["count"],
                    "mana_cost": row["mana_cost"],
                    "mana_value": row["mana_value"],
                    "type": ", ".join(json.loads(row["types"])) if row["types"] else None,
                    "rarity": row["rarity"],
                    "color_identity": json.loads(row["color_identity"]) if row["color_identity"] else [],
                    "text": row["text"],
                    "image_url": get_scryfall_image_url(row["identifiers_json"], "large"),
                    "price": price_map.get(row["card_uuid"]),
                }
            )

        return cards

    def _calculate_deck_stats(self, deck_uuid: str) -> dict:
        """Calculate deck statistics."""
        conn = db.decks

        # Total cards
        cursor = conn.execute(
            """
            SELECT SUM(count) as total, COUNT(*) as unique_count
            FROM deckcard
            WHERE deck_uuid = ? AND board IN ('mainBoard', 'sideBoard')
        """,
            [deck_uuid],
        )
        row = cursor.fetchone()
        total_cards = row["total"] or 0
        unique_cards = row["unique_count"] or 0

        # Mana curve (mainBoard only)
        cursor = conn.execute(
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
        mana_curve = {row["mv"]: row["count"] for row in cursor.fetchall()}

        # Type distribution
        cursor = conn.execute(
            """
            SELECT types, SUM(count) as count
            FROM deckcard
            WHERE deck_uuid = ? AND board = 'mainBoard'
            GROUP BY types
        """,
            [deck_uuid],
        )
        type_dist = {}
        for row in cursor.fetchall():
            types = json.loads(row["types"]) if row["types"] else []
            for t in types:
                type_dist[t] = type_dist.get(t, 0) + row["count"]

        # Rarity distribution
        cursor = conn.execute(
            """
            SELECT rarity, SUM(count) as count
            FROM deckcard
            WHERE deck_uuid = ? AND board = 'mainBoard'
            GROUP BY rarity
        """,
            [deck_uuid],
        )
        rarity_dist = {row["rarity"]: row["count"] for row in cursor.fetchall() if row["rarity"]}

        # Color distribution
        cursor = conn.execute(
            """
            SELECT color_identity, SUM(count) as count
            FROM deckcard
            WHERE deck_uuid = ? AND board = 'mainBoard'
            GROUP BY color_identity
        """,
            [deck_uuid],
        )
        color_dist = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for row in cursor.fetchall():
            colors = json.loads(row["color_identity"]) if row["color_identity"] else []
            if not colors:
                color_dist["C"] += row["count"]
            else:
                for c in colors:
                    if c in color_dist:
                        color_dist[c] += row["count"]

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
        conn = db.decks

        # Get all card legalities
        cursor = conn.execute(
            """
            SELECT legalities_json FROM deckcard WHERE deck_uuid = ?
        """,
            [deck_uuid],
        )

        formats = ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]
        legality = dict.fromkeys(formats, True)

        for row in cursor.fetchall():
            card_legalities = json.loads(row["legalities_json"]) if row["legalities_json"] else {}
            for fmt in formats:
                if card_legalities.get(fmt) != "Legal":
                    legality[fmt] = False

        return legality

    def get_available_sets(self) -> list[str]:
        """Get list of set codes that have decks."""
        conn = db.decks
        cursor = conn.execute("SELECT DISTINCT code FROM deck ORDER BY code")
        return [row["code"] for row in cursor.fetchall()]

    def get_available_formats(self) -> list[str]:
        """Get list of formats decks are legal in."""
        return ["standard", "pioneer", "modern", "legacy", "vintage", "commander"]


# Singleton instance
decks_data = DecksData()

"""Prices data access layer."""

from .database import db


class PricesData:
    """Data access for card prices."""

    # Providers for USD paper prices
    PAPER_PROVIDERS = ["tcgplayer", "cardkingdom", "cardsphere", "cardmarket"]
    MTGO_PROVIDERS = ["cardhoarder"]

    def get_card_prices(self, uuid: str) -> dict | None:
        """
        Get all prices for a card by UUID.

        Returns structured price data by provider and finish.
        """
        conn = db.prices

        cursor = conn.execute(
            """
            SELECT priceProvider, providerListing, cardFinish, currency,
                   gameAvailability, price
            FROM cardPrices
            WHERE uuid = ?
        """,
            [uuid],
        )

        rows = cursor.fetchall()
        if not rows:
            return None

        # Structure: paper/mtgo -> provider -> listing -> finish -> price
        paper = {}
        mtgo = {}

        for row in rows:
            provider = row["priceProvider"]
            listing = row["providerListing"]  # retail or buylist
            finish = row["cardFinish"]  # normal or foil
            price = row["price"]
            game = row["gameAvailability"]

            if game == "paper":
                if provider not in paper:
                    paper[provider] = {"retail": {}, "buylist": {}}
                if listing in paper[provider]:
                    paper[provider][listing][finish] = price
            elif game == "mtgo":
                if provider not in mtgo:
                    mtgo[provider] = {"retail": {}, "buylist": {}}
                if listing in mtgo[provider]:
                    mtgo[provider][listing][finish] = price

        return {
            "paper": paper,
            "mtgo": mtgo,
        }

    def get_average_price(self, uuid: str) -> float | None:
        """
        Calculate average USD paper price for a card.

        Uses tcgplayer, cardkingdom, cardsphere retail normal prices.
        """
        conn = db.prices

        cursor = conn.execute(
            """
            SELECT AVG(price) as avg_price
            FROM cardPrices
            WHERE uuid = ?
              AND currency = 'USD'
              AND gameAvailability = 'paper'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
              AND priceProvider IN ('tcgplayer', 'cardkingdom', 'cardsphere')
        """,
            [uuid],
        )

        row = cursor.fetchone()
        return row["avg_price"] if row and row["avg_price"] else None

    def get_tcgplayer_price(self, uuid: str) -> float | None:
        """Get TCGplayer retail normal price."""
        conn = db.prices

        cursor = conn.execute(
            """
            SELECT price FROM cardPrices
            WHERE uuid = ?
              AND priceProvider = 'tcgplayer'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
        """,
            [uuid],
        )

        row = cursor.fetchone()
        return row["price"] if row else None

    def search_prices(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "average_usd",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        Search cards with prices.

        Joins setcarddb with cardPrices for filtering and sorting.
        Returns: (list of price summaries, total count)
        """
        sets_conn = db.sets
        prices_conn = db.prices

        # First, get card UUIDs with prices that match filters

        # Build base query on setcarddb
        base_conditions = []
        base_params = []

        if q:
            base_conditions.append("name LIKE ?")
            base_params.append(f"%{q}%")

        if set_code:
            base_conditions.append("set_code = ?")
            base_params.append(set_code)

        if rarity:
            base_conditions.append("rarity = ?")
            base_params.append(rarity)

        where_clause = " AND ".join(base_conditions) if base_conditions else "1=1"

        # Get matching cards from sets database
        cards_sql = f"""
            SELECT uuid, name, set_code, rarity, mana_cost, color_identity
            FROM setcarddb
            WHERE {where_clause}
        """
        cursor = sets_conn.execute(cards_sql, base_params)
        cards_map = {row["uuid"]: dict(row) for row in cursor.fetchall()}

        if not cards_map:
            return [], 0

        # Get prices for these cards
        uuids = list(cards_map.keys())
        placeholders = ",".join(["?"] * len(uuids))

        prices_sql = f"""
            SELECT uuid, priceProvider, price
            FROM cardPrices
            WHERE uuid IN ({placeholders})
              AND currency = 'USD'
              AND gameAvailability = 'paper'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
        """
        cursor = prices_conn.execute(prices_sql, uuids)

        # Build price map: uuid -> {provider: price}
        price_map = {}
        for row in cursor.fetchall():
            uuid = row["uuid"]
            if uuid not in price_map:
                price_map[uuid] = {}
            price_map[uuid][row["priceProvider"]] = row["price"]

        # Combine and calculate average prices
        results = []
        for uuid, card in cards_map.items():
            prices = price_map.get(uuid, {})
            if not prices:
                continue  # Skip cards without prices

            # Calculate average from available sources
            avg_sources = [prices.get(p) for p in ["tcgplayer", "cardkingdom", "cardsphere"] if prices.get(p)]
            avg_price = sum(avg_sources) / len(avg_sources) if avg_sources else None

            if avg_price is None:
                continue

            # Apply price filters
            if price_min is not None and avg_price < price_min:
                continue
            if price_max is not None and avg_price > price_max:
                continue

            results.append(
                {
                    "uuid": uuid,
                    "name": card["name"],
                    "set_code": card["set_code"],
                    "rarity": card["rarity"],
                    "mana_cost": card["mana_cost"],
                    "prices": {
                        "tcgplayer": prices.get("tcgplayer"),
                        "cardkingdom": prices.get("cardkingdom"),
                        "cardsphere": prices.get("cardsphere"),
                        "cardmarket": prices.get("cardmarket"),
                    },
                    "average_usd": round(avg_price, 2) if avg_price else None,
                }
            )

        # Sort
        if sort == "average_usd":
            results.sort(key=lambda x: x["average_usd"] or 0, reverse=(order == "desc"))
        elif sort == "name":
            results.sort(key=lambda x: x["name"], reverse=(order == "desc"))
        elif sort in ["tcgplayer", "cardkingdom", "cardsphere"]:
            results.sort(key=lambda x: x["prices"].get(sort) or 0, reverse=(order == "desc"))

        total = len(results)

        # Paginate
        offset = (page - 1) * limit
        results = results[offset : offset + limit]

        return results, total

    def calculate_deck_price(self, deck_cards: list[dict]) -> dict:
        """
        Calculate total deck price from list of cards with counts.

        Args:
            deck_cards: List of dicts with 'uuid' and 'count' keys

        Returns:
            Dict with total and by_source breakdowns
        """
        if not deck_cards:
            return {"total": 0, "by_source": {}}

        prices_conn = db.prices

        uuids = [c["uuid"] for c in deck_cards if c.get("uuid")]
        if not uuids:
            return {"total": 0, "by_source": {}}

        placeholders = ",".join(["?"] * len(uuids))
        cursor = prices_conn.execute(
            f"""
            SELECT uuid, priceProvider, price
            FROM cardPrices
            WHERE uuid IN ({placeholders})
              AND currency = 'USD'
              AND gameAvailability = 'paper'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
        """,
            uuids,
        )

        # Build price map
        price_map = {}
        for row in cursor.fetchall():
            uuid = row["uuid"]
            if uuid not in price_map:
                price_map[uuid] = {}
            price_map[uuid][row["priceProvider"]] = row["price"]

        # Calculate totals by source
        by_source = {"tcgplayer": 0, "cardkingdom": 0, "cardsphere": 0}

        for card in deck_cards:
            uuid = card.get("uuid")
            count = card.get("count", 1)
            if uuid and uuid in price_map:
                for source in by_source:
                    if price_map[uuid].get(source):
                        by_source[source] += price_map[uuid][source] * count

        # Calculate average total
        valid_totals = [v for v in by_source.values() if v > 0]
        total = sum(valid_totals) / len(valid_totals) if valid_totals else 0

        return {
            "total": round(total, 2),
            "by_source": {k: round(v, 2) for k, v in by_source.items()},
        }

    def get_price_stats(self) -> dict:
        """Get overall price statistics."""
        conn = db.prices

        cursor = conn.execute("""
            SELECT COUNT(DISTINCT uuid) as cards_with_prices
            FROM cardPrices
        """)
        row = cursor.fetchone()

        cursor = conn.execute("""
            SELECT date FROM cardPrices LIMIT 1
        """)
        date_row = cursor.fetchone()

        return {
            "total_cards_with_prices": row["cards_with_prices"] if row else 0,
            "last_updated": date_row["date"] if date_row else None,
        }


# Singleton instance
prices_data = PricesData()

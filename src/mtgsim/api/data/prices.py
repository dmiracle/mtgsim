"""Prices data access layer using unified database schema."""

from sqlmodel import func, select

from mtgdb.models import MJCard, MJCardPrice
from mtgdb.session import get_session


class PricesData:
    """Data access for card prices using unified schema."""

    PAPER_PROVIDERS = ["tcgplayer", "cardkingdom", "cardsphere", "cardmarket"]
    MTGO_PROVIDERS = ["cardhoarder"]

    def get_card_prices(self, uuid: str) -> dict | None:
        """
        Get all prices for a card by UUID.

        Returns structured price data by provider and finish.
        """
        with get_session() as session:
            query = select(MJCardPrice).where(MJCardPrice.card_uuid == uuid)
            results = session.exec(query).all()

            if not results:
                return None

            # Structure: provider -> listing_type -> finish -> price
            prices = {}
            for price in results:
                provider = price.provider
                listing = price.listing_type
                finish = price.finish

                if provider not in prices:
                    prices[provider] = {"retail": {}, "buylist": {}}

                if listing in prices[provider]:
                    prices[provider][listing][finish] = price.price

            return prices

    def get_price(
        self,
        uuid: str,
        provider: str = "tcgplayer",
        listing_type: str = "retail",
        finish: str = "normal",
    ) -> float | None:
        """Get specific price for a card."""
        with get_session() as session:
            query = select(MJCardPrice.price).where(
                (MJCardPrice.card_uuid == uuid)
                & (MJCardPrice.provider == provider)
                & (MJCardPrice.listing_type == listing_type)
                & (MJCardPrice.finish == finish)
            )
            return session.exec(query).first()

    def get_tcgplayer_price(self, uuid: str) -> float | None:
        """Get TCGplayer retail normal price."""
        return self.get_price(uuid, "tcgplayer", "retail", "normal")

    def get_average_price(self, uuid: str) -> float | None:
        """
        Calculate average USD paper price for a card.

        Uses tcgplayer, cardkingdom, cardsphere retail normal prices.
        """
        with get_session() as session:
            query = select(func.avg(MJCardPrice.price)).where(
                (MJCardPrice.card_uuid == uuid)
                & (MJCardPrice.currency == "USD")
                & (MJCardPrice.listing_type == "retail")
                & (MJCardPrice.finish == "normal")
                & (MJCardPrice.provider.in_(["tcgplayer", "cardkingdom", "cardsphere"]))
            )
            result = session.exec(query).first()
            return round(result, 2) if result else None

    def search_by_price(
        self,
        price_min: float | None = None,
        price_max: float | None = None,
        provider: str = "tcgplayer",
        listing_type: str = "retail",
        finish: str = "normal",
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        sort: str = "price",
        order: str = "desc",
        page: int = 1,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        """
        Search cards by price range.

        Returns: (list of price summaries, total count)
        """
        with get_session() as session:
            # Join cards with prices
            query = (
                select(MJCard, MJCardPrice)
                .join(MJCardPrice, MJCard.uuid == MJCardPrice.card_uuid)
                .where(
                    (MJCardPrice.provider == provider)
                    & (MJCardPrice.listing_type == listing_type)
                    & (MJCardPrice.finish == finish)
                    & (MJCardPrice.price.is_not(None))
                )
            )

            # Text search
            if q:
                query = query.where(MJCard.name.contains(q))

            # Set filter
            if set_code:
                query = query.where(MJCard.set_code == set_code)

            # Rarity filter
            if rarity:
                query = query.where(MJCard.rarity == rarity)

            # Price range filters
            if price_min is not None:
                query = query.where(MJCardPrice.price >= price_min)
            if price_max is not None:
                query = query.where(MJCardPrice.price <= price_max)

            # Count
            count_query = select(func.count()).select_from(query.subquery())
            total = session.exec(count_query).one()

            # Sorting
            if sort == "price":
                sort_field = MJCardPrice.price
            elif sort == "name":
                sort_field = MJCard.name
            else:
                sort_field = MJCardPrice.price

            if order == "desc":
                query = query.order_by(sort_field.desc())
            else:
                query = query.order_by(sort_field.asc())

            # Pagination
            offset = (page - 1) * limit
            query = query.offset(offset).limit(limit)

            # Execute
            results = session.exec(query).all()

            cards = []
            for card, price in results:
                cards.append(
                    {
                        "uuid": card.uuid,
                        "name": card.name,
                        "set_code": card.set_code,
                        "rarity": card.rarity,
                        "mana_cost": card.mana_cost,
                        "price": price.price,
                        "provider": price.provider,
                        "finish": price.finish,
                    }
                )

            return cards, total

    def get_price_history(self, uuid: str) -> list[dict]:
        """Get price history for a card (if available)."""
        # Note: This would require a price history table
        # For now, return current prices only
        prices = self.get_card_prices(uuid)
        if not prices:
            return []

        history = []
        for provider, listings in prices.items():
            for listing_type, finishes in listings.items():
                for finish, price in finishes.items():
                    if price is not None:
                        history.append(
                            {
                                "provider": provider,
                                "listing_type": listing_type,
                                "finish": finish,
                                "price": price,
                            }
                        )

        return history

    def calculate_deck_price(self, deck_cards: list[dict]) -> dict:
        """
        Calculate total deck price from list of cards with counts.

        Args:
            deck_cards: List of dicts with 'uuid' and 'count' keys

        Returns:
            Dict with total and by_provider breakdowns
        """
        if not deck_cards:
            return {"total": 0, "by_provider": {}}

        uuids = [c["uuid"] for c in deck_cards if c.get("uuid")]
        if not uuids:
            return {"total": 0, "by_provider": {}}

        # Create uuid -> count map
        count_map = {c["uuid"]: c.get("count", 1) for c in deck_cards}

        with get_session() as session:
            # Get prices for all providers
            query = select(MJCardPrice).where(
                (MJCardPrice.card_uuid.in_(uuids))
                & (MJCardPrice.listing_type == "retail")
                & (MJCardPrice.finish == "normal")
            )
            results = session.exec(query).all()

            # Build price map: uuid -> {provider: price}
            price_map = {}
            for price in results:
                if price.card_uuid not in price_map:
                    price_map[price.card_uuid] = {}
                price_map[price.card_uuid][price.provider] = price.price

            # Calculate totals by provider
            by_provider = {}
            for provider in self.PAPER_PROVIDERS:
                total = 0.0
                for uuid, count in count_map.items():
                    if uuid in price_map and price_map[uuid].get(provider):
                        total += price_map[uuid][provider] * count
                if total > 0:
                    by_provider[provider] = round(total, 2)

            # Calculate average total
            valid_totals = [v for v in by_provider.values() if v > 0]
            total = round(sum(valid_totals) / len(valid_totals), 2) if valid_totals else 0

            return {
                "total": total,
                "by_provider": by_provider,
            }

    def get_price_stats(self) -> dict:
        """Get overall price statistics."""
        with get_session() as session:
            # Total cards with prices
            count_query = select(func.count(func.distinct(MJCardPrice.card_uuid)))
            cards_with_prices = session.exec(count_query).first() or 0

            # Get latest update time
            latest_query = select(func.max(MJCardPrice.updated_at))
            latest_update = session.exec(latest_query).first()

            # Price distribution
            price_ranges = {
                "under_1": 0,
                "1_to_5": 0,
                "5_to_20": 0,
                "20_to_100": 0,
                "over_100": 0,
            }

            # Count cards in each price range (tcgplayer retail normal)
            range_query = select(MJCardPrice.price).where(
                (MJCardPrice.provider == "tcgplayer")
                & (MJCardPrice.listing_type == "retail")
                & (MJCardPrice.finish == "normal")
                & (MJCardPrice.price.is_not(None))
            )
            prices = session.exec(range_query).all()

            for price in prices:
                if price < 1:
                    price_ranges["under_1"] += 1
                elif price < 5:
                    price_ranges["1_to_5"] += 1
                elif price < 20:
                    price_ranges["5_to_20"] += 1
                elif price < 100:
                    price_ranges["20_to_100"] += 1
                else:
                    price_ranges["over_100"] += 1

            return {
                "total_cards_with_prices": cards_with_prices,
                "last_updated": latest_update.isoformat() if latest_update else None,
                "price_distribution": price_ranges,
            }


# Singleton instance
prices_data = PricesData()

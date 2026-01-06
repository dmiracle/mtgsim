"""Price utilities for centralized price calculations and lookups."""

from typing import Any

from mtgsim.reference.repository import ReferenceRepository


class PriceUtility:
    """Centralized price calculation and lookup functionality.

    This class consolidates all price-related operations that were previously
    scattered across different modules, providing a unified interface for
    TCGPlayer lookups, multi-provider averaging, and deck calculations.
    """

    def __init__(self, reference_repo: ReferenceRepository):
        """Initialize PriceUtility with reference repository.

        Args:
            reference_repo: Repository for accessing reference databases
        """
        self.reference_repo = reference_repo

    def get_tcgplayer_price(self, uuid: str) -> float | None:
        """Get TCGPlayer retail normal price for card UUID.

        Args:
            uuid: Card UUID to lookup price for

        Returns:
            TCGPlayer price if found, None otherwise
        """
        if not uuid:
            return None

        try:
            conn = self.reference_repo.get_connection("prices")
        except RuntimeError:
            return None

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
        return row["price"] if row and row["price"] else None

    def get_average_price(self, uuid: str) -> float | None:
        """Get average price across multiple providers.

        Calculates average from tcgplayer, cardkingdom, and cardsphere
        retail normal prices for USD paper cards.

        Args:
            uuid: Card UUID to lookup price for

        Returns:
            Average price if providers found, None otherwise
        """
        if not uuid:
            return None

        try:
            conn = self.reference_repo.get_connection("prices")
        except RuntimeError:
            return None

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
              AND price IS NOT NULL
            """,
            [uuid],
        )

        row = cursor.fetchone()
        return row["avg_price"] if row and row["avg_price"] else None

    def calculate_deck_total(self, deck_cards: list[dict]) -> float:
        """Calculate total price for deck cards using average pricing.

        Args:
            deck_cards: List of dicts with 'uuid' and 'count' keys

        Returns:
            Total deck price using average pricing across providers
        """
        if not deck_cards:
            return 0.0

        # Extract UUIDs and get bulk prices
        uuids = [card.get("uuid") for card in deck_cards if card.get("uuid")]
        if not uuids:
            return 0.0

        price_map = self.get_bulk_average_prices(uuids)

        total = 0.0
        for card in deck_cards:
            uuid = card.get("uuid")
            count = card.get("count", 1)

            # Handle string counts by converting to int
            if isinstance(count, str):
                try:
                    count = int(count)
                except (ValueError, TypeError):
                    continue  # Skip invalid counts

            if uuid and uuid in price_map and isinstance(count, (int, float)) and count > 0:
                total += price_map[uuid] * count

        return round(total, 2)

    def get_bulk_prices(self, uuids: list[str]) -> dict[str, float]:
        """Get TCGPlayer prices for multiple cards efficiently.

        This method uses the reference repository's bulk price functionality
        which specifically returns TCGPlayer prices.

        Args:
            uuids: List of card UUIDs to lookup prices for

        Returns:
            Dictionary mapping UUID to TCGPlayer price
        """
        return self.reference_repo.get_price_map(uuids)

    def get_bulk_average_prices(self, uuids: list[str]) -> dict[str, float]:
        """Get average prices for multiple cards efficiently.

        Calculates average prices across tcgplayer, cardkingdom, and cardsphere
        for each UUID in the list.

        Args:
            uuids: List of card UUIDs to lookup prices for

        Returns:
            Dictionary mapping UUID to average price
        """
        if not uuids:
            return {}

        try:
            conn = self.reference_repo.get_connection("prices")
        except RuntimeError:
            return {}

        placeholders = ",".join(["?"] * len(uuids))
        cursor = conn.execute(
            f"""
            SELECT uuid, priceProvider, price
            FROM cardPrices
            WHERE uuid IN ({placeholders})
              AND currency = 'USD'
              AND gameAvailability = 'paper'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
              AND priceProvider IN ('tcgplayer', 'cardkingdom', 'cardsphere')
              AND price IS NOT NULL
            """,
            uuids,
        )

        # Build price map: uuid -> {provider: price}
        price_data = {}
        for row in cursor.fetchall():
            uuid = row["uuid"]
            provider = row["priceProvider"]
            price = row["price"]

            if uuid not in price_data:
                price_data[uuid] = {}
            price_data[uuid][provider] = price

        # Calculate averages
        result = {}
        for uuid, providers in price_data.items():
            prices = list(providers.values())
            if prices:
                result[uuid] = sum(prices) / len(prices)

        return result

    def get_price_breakdown(self, uuid: str) -> dict[str, Any]:
        """Get detailed price breakdown for a card across all providers.

        Args:
            uuid: Card UUID to lookup prices for

        Returns:
            Dictionary with provider prices and calculated average
        """
        if not uuid:
            return {}

        try:
            conn = self.reference_repo.get_connection("prices")
        except RuntimeError:
            return {}

        cursor = conn.execute(
            """
            SELECT priceProvider, price
            FROM cardPrices
            WHERE uuid = ?
              AND currency = 'USD'
              AND gameAvailability = 'paper'
              AND providerListing = 'retail'
              AND cardFinish = 'normal'
              AND price IS NOT NULL
            """,
            [uuid],
        )

        providers = {}
        for row in cursor.fetchall():
            providers[row["priceProvider"]] = row["price"]

        # Calculate average from main providers
        main_providers = ["tcgplayer", "cardkingdom", "cardsphere"]
        main_prices = [providers.get(p) for p in main_providers if providers.get(p)]
        average = sum(main_prices) / len(main_prices) if main_prices else None

        return {
            "providers": providers,
            "average": average,
            "tcgplayer": providers.get("tcgplayer"),
            "cardkingdom": providers.get("cardkingdom"),
            "cardsphere": providers.get("cardsphere"),
            "cardmarket": providers.get("cardmarket"),
        }

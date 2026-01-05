"""Price service - handles price data access and calculations."""

from datetime import datetime, timezone

from mtgsim.api.models.common import Pagination
from mtgsim.api.models.price import (
    PriceSummary,
    PriceDetail,
    PriceListResponse,
    PriceListMeta,
    PricesBySource,
    PaperPrices,
    MtgoPrices,
    SourcePrices,
    RetailBuylistPrices,
    PriceHistoryPoint,
)


class PriceService:
    """Service for price-related operations."""

    async def search_prices(
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
    ) -> PriceListResponse:
        """
        Search price data with filters.

        TODO: Implement actual database queries:
        1. Search card_index by name (q parameter)
        2. Join with price data
        3. Apply filters (set_code, rarity, price range)
        4. Calculate average USD price for each card
        5. Sort and paginate
        """
        return PriceListResponse(
            data=[
                PriceSummary(
                    uuid="stub-price-001",
                    name="Expensive Card",
                    set_code="TST",
                    rarity="mythic",
                    image_url="https://cards.scryfall.io/small/front/a/b/stub.jpg",
                    prices=PricesBySource(
                        tcgplayer=50.00,
                        cardkingdom=55.00,
                        cardsphere=48.00,
                        cardmarket=45.00,
                        mtgo=10.00,
                    ),
                    average_usd=51.00,
                )
            ],
            pagination=Pagination(page=page, limit=limit, total=1, pages=1),
            meta=PriceListMeta(
                last_updated=datetime.now(timezone.utc),
                total_cards_with_prices=105230,
            ),
        )

    async def get_price(self, uuid: str) -> PriceDetail | None:
        """
        Get detailed price data for a card.

        TODO: Implement actual data loading:
        1. Fetch price data from AllPricesToday.json by uuid
        2. Parse all price sources (paper and MTGO)
        3. Include retail and buylist prices
        4. Optionally load price history if available
        """
        return PriceDetail(
            uuid=uuid,
            name="Expensive Card",
            set_code="TST",
            paper=PaperPrices(
                tcgplayer=SourcePrices(
                    retail=RetailBuylistPrices(normal=50.00, foil=100.00),
                    buylist=RetailBuylistPrices(normal=35.00, foil=70.00),
                ),
                cardkingdom=SourcePrices(
                    retail=RetailBuylistPrices(normal=55.00, foil=110.00),
                    buylist=RetailBuylistPrices(normal=40.00, foil=80.00),
                ),
                cardsphere=SourcePrices(
                    retail=RetailBuylistPrices(normal=48.00, foil=95.00),
                ),
                cardmarket=SourcePrices(
                    retail=RetailBuylistPrices(normal=45.00, foil=90.00),
                ),
            ),
            mtgo=MtgoPrices(
                cardhoarder=SourcePrices(
                    retail=RetailBuylistPrices(normal=10.00, foil=20.00),
                ),
            ),
            price_history=[
                PriceHistoryPoint(date="2024-01-01", tcgplayer=48.00),
                PriceHistoryPoint(date="2024-01-02", tcgplayer=49.50),
                PriceHistoryPoint(date="2024-01-03", tcgplayer=50.00),
            ],
        )

    async def get_average_usd_price(self, uuid: str) -> float:
        """
        Calculate average USD price for a card.

        TODO: Implement actual calculation:
        1. Get prices from tcgplayer, cardkingdom, cardsphere
        2. Average the available values
        """
        return 51.00

    async def calculate_deck_price(self, deck_file: str) -> float:
        """
        Calculate total deck price.

        TODO: Implement actual calculation:
        1. Load deck file
        2. For each card, get average USD price
        3. Multiply by count and sum
        """
        return 99.99

    async def get_price_data_info(self) -> PriceListMeta:
        """
        Get metadata about price data.

        TODO: Return actual metadata from loaded price data
        """
        return PriceListMeta(
            last_updated=datetime.now(timezone.utc),
            total_cards_with_prices=105230,
        )


# Singleton instance
price_service = PriceService()

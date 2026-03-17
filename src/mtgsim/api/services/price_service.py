"""Price service - handles price data access and calculations."""

import logging
from datetime import UTC, datetime

from mtgsim.api.data import prices_data
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.price import (
    MtgoPrices,
    PaperPrices,
    PriceDetail,
    PriceListMeta,
    PriceListResponse,
    PricesBySource,
    PriceSummary,
    RetailBuylistPrices,
    SourcePrices,
)

logger = logging.getLogger("mtgsim.api.services.price")


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
        """Search price data with filters."""
        logger.debug(f"search_prices: q={q} set={set_code} rarity={rarity} range=[{price_min},{price_max}]")

        # Map sort field: frontend uses "average_usd" but data layer uses "price"
        data_sort = "price" if sort == "average_usd" else sort

        results, total = prices_data.search_by_price(
            q=q,
            set_code=set_code,
            rarity=rarity,
            price_min=price_min,
            price_max=price_max,
            sort=data_sort,
            order=order,
            page=page,
            limit=limit,
        )
        logger.debug(f"search_prices: got {len(results)} results, total={total}")

        data = [
            PriceSummary(
                uuid=r["uuid"],
                name=r["name"],
                set_code=r["set_code"],
                rarity=r["rarity"],
                image_url=None,
                prices=PricesBySource(
                    tcgplayer=r.get("price"),
                    cardkingdom=None,
                    cardsphere=None,
                    cardmarket=None,
                    mtgo=None,
                ),
                average_usd=r.get("price"),
            )
            for r in results
        ]

        pages = (total + limit - 1) // limit if limit > 0 else 1
        logger.debug("search_prices: fetching price stats")
        stats = prices_data.get_price_stats()

        return PriceListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
            meta=PriceListMeta(
                last_updated=datetime.fromisoformat(stats["last_updated"])
                if stats.get("last_updated")
                else datetime.now(UTC),
                total_cards_with_prices=stats.get("total_cards_with_prices", 0),
            ),
        )

    async def get_price(self, uuid: str) -> PriceDetail | None:
        """Get detailed price data for a card."""
        price_data = prices_data.get_card_prices(uuid)
        if not price_data:
            return None

        paper = price_data.get("paper", {})
        mtgo = price_data.get("mtgo", {})

        def build_source_prices(provider_data: dict) -> SourcePrices:
            retail = provider_data.get("retail", {})
            buylist = provider_data.get("buylist", {})
            return SourcePrices(
                retail=RetailBuylistPrices(
                    normal=retail.get("normal"),
                    foil=retail.get("foil"),
                ),
                buylist=RetailBuylistPrices(
                    normal=buylist.get("normal"),
                    foil=buylist.get("foil"),
                )
                if buylist
                else None,
            )

        return PriceDetail(
            uuid=uuid,
            name="",  # Would need to join with cards DB
            set_code="",
            paper=PaperPrices(
                tcgplayer=build_source_prices(paper.get("tcgplayer", {})) if paper.get("tcgplayer") else None,
                cardkingdom=build_source_prices(paper.get("cardkingdom", {})) if paper.get("cardkingdom") else None,
                cardsphere=build_source_prices(paper.get("cardsphere", {})) if paper.get("cardsphere") else None,
                cardmarket=build_source_prices(paper.get("cardmarket", {})) if paper.get("cardmarket") else None,
            ),
            mtgo=MtgoPrices(
                cardhoarder=build_source_prices(mtgo.get("cardhoarder", {})) if mtgo.get("cardhoarder") else None,
            ),
            price_history=[],
        )

    async def get_average_usd_price(self, uuid: str) -> float:
        """Calculate average USD price for a card."""
        avg = prices_data.get_average_price(uuid)
        return avg if avg else 0.0

    async def calculate_deck_price(self, deck_file: str) -> float:
        """Calculate total deck price."""
        # Would need to load deck and calculate
        return 0.0

    async def get_price_data_info(self) -> PriceListMeta:
        """Get metadata about price data."""
        stats = prices_data.get_price_stats()
        return PriceListMeta(
            last_updated=datetime.fromisoformat(stats["last_updated"])
            if stats.get("last_updated")
            else datetime.now(UTC),
            total_cards_with_prices=stats.get("total_cards_with_prices", 0),
        )


# Singleton instance
price_service = PriceService()

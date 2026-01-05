"""Price-related Pydantic models."""

from datetime import datetime

from pydantic import BaseModel

from mtgsim.api.models.common import Pagination


class PricesBySource(BaseModel):
    """Prices organized by source."""

    tcgplayer: float | None = None
    cardkingdom: float | None = None
    cardsphere: float | None = None
    cardmarket: float | None = None
    mtgo: float | None = None


class PriceSummary(BaseModel):
    """Summary price information for list views."""

    uuid: str
    name: str
    set_code: str | None = None
    rarity: str | None = None
    image_url: str | None = None
    prices: PricesBySource
    average_usd: float | None = None


class PriceListMeta(BaseModel):
    """Metadata for price list response."""

    last_updated: datetime | None = None
    total_cards_with_prices: int


class PriceListResponse(BaseModel):
    """Response for price list endpoint."""

    data: list[PriceSummary]
    pagination: Pagination
    meta: PriceListMeta


class RetailBuylistPrices(BaseModel):
    """Retail and buylist prices for a condition."""

    normal: float | None = None
    foil: float | None = None


class SourcePrices(BaseModel):
    """Prices from a single source."""

    retail: RetailBuylistPrices | None = None
    buylist: RetailBuylistPrices | None = None


class PaperPrices(BaseModel):
    """All paper price sources."""

    tcgplayer: SourcePrices | None = None
    cardkingdom: SourcePrices | None = None
    cardsphere: SourcePrices | None = None
    cardmarket: SourcePrices | None = None


class MtgoPrices(BaseModel):
    """MTGO price sources."""

    cardhoarder: SourcePrices | None = None


class PriceHistoryPoint(BaseModel):
    """Single point in price history."""

    date: str
    tcgplayer: float | None = None
    cardkingdom: float | None = None
    cardsphere: float | None = None


class PriceDetail(BaseModel):
    """Full price details for a card."""

    uuid: str
    name: str
    set_code: str | None = None
    paper: PaperPrices | None = None
    mtgo: MtgoPrices | None = None
    price_history: list[PriceHistoryPoint] = []

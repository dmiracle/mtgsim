"""Pydantic models for API request/response."""

from mtgsim.api.models.common import Pagination, PaginatedResponse, ErrorResponse
from mtgsim.api.models.deck import (
    DeckSummary,
    DeckDetail,
    DeckStats,
    DeckCard,
    DeckListResponse,
    DeckFilters,
)
from mtgsim.api.models.set import (
    SetSummary,
    SetDetail,
    SetStats,
    SetListResponse,
    SetFilters,
)
from mtgsim.api.models.card import (
    CardSummary,
    CardDetail,
    CardListResponse,
    CardAppearance,
    CardPrinting,
)
from mtgsim.api.models.price import (
    PriceSummary,
    PriceDetail,
    PriceListResponse,
    PricesBySource,
)

__all__ = [
    "Pagination",
    "PaginatedResponse",
    "ErrorResponse",
    "DeckSummary",
    "DeckDetail",
    "DeckStats",
    "DeckCard",
    "DeckListResponse",
    "DeckFilters",
    "SetSummary",
    "SetDetail",
    "SetStats",
    "SetListResponse",
    "SetFilters",
    "CardSummary",
    "CardDetail",
    "CardListResponse",
    "CardAppearance",
    "CardPrinting",
    "PriceSummary",
    "PriceDetail",
    "PriceListResponse",
    "PricesBySource",
]

"""Pydantic models for API request/response."""

from mtgsim.api.models.card import (
    CardAppearance,
    CardDetail,
    CardListResponse,
    CardPrinting,
    CardSummary,
)
from mtgsim.api.models.common import ErrorResponse, PaginatedResponse, Pagination
from mtgsim.api.models.deck import (
    DeckCard,
    DeckDetail,
    DeckFilters,
    DeckListResponse,
    DeckStats,
    DeckSummary,
)
from mtgsim.api.models.price import (
    PriceDetail,
    PriceListResponse,
    PricesBySource,
    PriceSummary,
)
from mtgsim.api.models.set import (
    SetDetail,
    SetFilters,
    SetListResponse,
    SetStats,
    SetSummary,
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

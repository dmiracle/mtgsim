"""Set-related Pydantic models."""

from pydantic import BaseModel

from mtgsim.api.models.common import (
    HistogramBucket,
    KeywordCounts,
    Pagination,
    WordFrequency,
)
from mtgsim.api.models.deck import PriceBySource


class SetSummary(BaseModel):
    """Summary set information for list views."""

    code: str
    name: str
    type: str
    release_date: str | None = None
    base_set_size: int
    total_set_size: int
    block: str | None = None
    keyrune_code: str
    in_collection: bool = False


class SetFilters(BaseModel):
    """Available filter options for set list."""

    types: list[str]
    blocks: list[str]


class SetListResponse(BaseModel):
    """Response for set list endpoint."""

    data: list[SetSummary]
    pagination: Pagination
    filters: SetFilters


class SetCard(BaseModel):
    """Card within a set."""

    uuid: str
    name: str
    type: str | None = None
    rarity: str | None = None
    color_identity: list[str]
    text: str | None = None
    price: float | None = None
    image_url: str | None = None
    in_collection: bool = False


class SetCardsResponse(BaseModel):
    """Paginated cards within a set."""

    data: list[SetCard]
    pagination: Pagination


class ColorWordFrequencies(BaseModel):
    """Word frequencies organized by color."""

    W: list[WordFrequency] = []
    U: list[WordFrequency] = []
    B: list[WordFrequency] = []
    R: list[WordFrequency] = []
    G: list[WordFrequency] = []
    C: list[WordFrequency] = []  # Colorless


class SetPrice(BaseModel):
    """Set price information."""

    total: float
    by_source: PriceBySource


class SetStats(BaseModel):
    """Comprehensive set statistics."""

    rarity_count: dict[str, int]
    price: SetPrice
    price_histogram: list[HistogramBucket]
    keywords: KeywordCounts
    text_by_color: ColorWordFrequencies


class SetMeta(BaseModel):
    """Set metadata."""

    code: str
    name: str
    type: str
    release_date: str | None = None
    base_set_size: int
    total_set_size: int
    block: str | None = None
    keyrune_code: str
    in_collection: bool = False


class SetDetail(BaseModel):
    """Full set details."""

    meta: SetMeta
    stats: SetStats
    cards: SetCardsResponse

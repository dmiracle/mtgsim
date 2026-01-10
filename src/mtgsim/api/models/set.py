"""Set-related Pydantic models."""

from pydantic import BaseModel

from mtgsim.api.models.common import (
    HistogramBucket,
    KeywordCounts,
    Pagination,
    WordFrequency,
)
from mtgsim.api.models.deck import PriceBySource


class SetCollectionStats(BaseModel):
    """Collection statistics for a set."""

    total_cards: int = 0
    owned_cards: int = 0
    owned_percentage: float = 0.0
    wanted_cards: int = 0


class SetSummary(BaseModel):
    """Summary set information for list views."""

    code: str
    name: str
    type: str
    release_date: str | None = None
    base_set_size: int = 0
    total_set_size: int = 0
    block: str | None = None
    keyrune_code: str | None = None
    collection_stats: SetCollectionStats | None = None


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
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    rarity: str | None = None
    color_identity: list[str] = []
    colors: list[str] = []
    power: str | None = None
    toughness: str | None = None
    number: str | None = None
    text: str | None = None
    price: float | None = None
    image_url: str | None = None
    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0


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
    base_set_size: int = 0
    total_set_size: int = 0
    block: str | None = None
    keyrune_code: str | None = None
    collection_stats: SetCollectionStats | None = None


class SetDetail(BaseModel):
    """Full set details."""

    meta: SetMeta
    stats: SetStats
    cards: SetCardsResponse

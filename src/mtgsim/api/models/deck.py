"""Deck-related Pydantic models."""

from pydantic import BaseModel, Field

from mtgsim.api.models.common import (
    HistogramBucket,
    KeywordCounts,
    Pagination,
)


class DeckLegality(BaseModel):
    """Format legality for a deck."""

    standard: bool = False
    pioneer: bool = False
    modern: bool = False
    legacy: bool = False
    vintage: bool = False
    commander: bool = False
    brawl: bool = False
    historic: bool = False
    pauper: bool = False


class DeckSummary(BaseModel):
    """Summary deck information for list views."""

    file: str
    name: str
    code: str
    card_count: int
    colors: list[str]
    price: float | None = None
    release_date: str | None = None
    legality: DeckLegality


class DeckFilters(BaseModel):
    """Available filter options for deck list."""

    formats: list[str]
    sets: list[str]
    color_combinations: list[list[str]]


class DeckListResponse(BaseModel):
    """Response for deck list endpoint."""

    data: list[DeckSummary]
    pagination: Pagination
    filters: DeckFilters


class DeckCard(BaseModel):
    """Card within a deck."""

    uuid: str
    name: str
    count: int = 1
    mana_cost: str | None = None
    mana_value: int = 0
    type: str | None = None
    rarity: str | None = None
    text: str | None = None
    price: float | None = None
    image_url: str | None = None


class PriceBySource(BaseModel):
    """Price breakdown by source."""

    tcgplayer: float | None = None
    cardkingdom: float | None = None
    cardsphere: float | None = None
    cardmarket: float | None = None
    mtgo: float | None = None


class DeckPrice(BaseModel):
    """Deck price information."""

    total: float
    by_source: PriceBySource


class ManaCurve(BaseModel):
    """Mana curve distribution."""

    zero: int = Field(0, alias="0")
    one: int = Field(0, alias="1")
    two: int = Field(0, alias="2")
    three: int = Field(0, alias="3")
    four: int = Field(0, alias="4")
    five: int = Field(0, alias="5")
    six_plus: int = Field(0, alias="6+")

    model_config = {"populate_by_name": True}


class DeckStats(BaseModel):
    """Comprehensive deck statistics."""

    total_cards: int
    unique_cards: int
    mana_curve: dict[str, int]
    type_distribution: dict[str, int]
    rarity_distribution: dict[str, int]
    color_distribution: dict[str, int]
    price_histogram: list[HistogramBucket]
    keywords: KeywordCounts


class DeckMeta(BaseModel):
    """Deck metadata."""

    file: str
    name: str
    code: str
    release_date: str | None = None


class DeckDetail(BaseModel):
    """Full deck details."""

    meta: DeckMeta
    legality: DeckLegality
    colors: list[str]
    price: DeckPrice
    commander: list[DeckCard]
    main_board: list[DeckCard]
    side_board: list[DeckCard]
    stats: DeckStats

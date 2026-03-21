"""Card-related Pydantic models."""

from pydantic import BaseModel

from mtgsim.api.models.common import CollectionDetail, Pagination


class CardSummary(BaseModel):
    """Summary card information for list views."""

    uuid: str
    name: str
    type: str | None = None
    mana_cost: str | None = None
    mana_value: float | None = None
    rarity: str | None = None
    set_code: str | None = None
    color_identity: list[str] = []
    tags: list[str] = []
    text: str | None = None
    price: float | None = None
    image_url: str | None = None
    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0


class CardListResponse(BaseModel):
    """Response for card list endpoint."""

    data: list[CardSummary]
    pagination: Pagination


class CardPriceEntry(BaseModel):
    """Single price entry from a provider."""

    provider: str
    finish: str
    listing_type: str
    price: float


class CardAppearance(BaseModel):
    """Deck appearance for a card."""

    file: str
    name: str
    count: int


class CardPrinting(BaseModel):
    """Other printing of a card."""

    set_code: str
    set_name: str
    uuid: str
    rarity: str | None = None
    number: str | None = None
    image_url: str | None = None
    price: float | None = None
    owns: bool = False
    total_owned: int = 0


class QuadrantRating(BaseModel):
    """Quadrant theory rating for a card."""

    developing: float | None = None
    ahead: float | None = None
    behind: float | None = None
    parity: float | None = None
    notes: str | None = None


class CardDetail(BaseModel):
    """Full card details."""

    uuid: str
    name: str
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    types: list[str] = []
    subtypes: list[str] = []
    supertypes: list[str] = []
    text: str | None = None
    flavor_text: str | None = None
    rarity: str | None = None
    set_code: str | None = None
    set_name: str | None = None
    color_identity: list[str] = []
    colors: list[str] = []
    keywords: list[str] = []
    tags: list[str] = []
    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None
    artist: str | None = None
    number: str | None = None
    layout: str | None = None
    finishes: list[str] = []
    border_color: str | None = None
    frame_version: str | None = None
    is_reprint: bool = False
    is_reserved: bool = False
    is_promo: bool = False
    image_url: str | None = None
    legalities: dict[str, str] = {}
    all_prices: list[CardPriceEntry] = []
    appears_in_decks: list[CardAppearance] = []
    other_printings: list[CardPrinting] = []
    owns: bool = False
    wants: bool = False
    total_owned: int = 0
    total_wanted: int = 0
    collection: CollectionDetail | None = None
    quadrant_rating: QuadrantRating | None = None

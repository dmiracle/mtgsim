"""Card-related Pydantic models."""

from pydantic import BaseModel

from mtgsim.api.models.common import Pagination
from mtgsim.api.models.deck import PriceBySource


class CardSummary(BaseModel):
    """Summary card information for list views."""

    uuid: str
    name: str
    type: str | None = None
    mana_cost: str | None = None
    mana_value: int = 0
    rarity: str | None = None
    set_code: str | None = None
    color_identity: list[str] = []
    text: str | None = None
    price: float | None = None
    image_url: str | None = None


class CardListResponse(BaseModel):
    """Response for card list endpoint."""

    data: list[CardSummary]
    pagination: Pagination


class CardLegalities(BaseModel):
    """Card format legalities."""

    standard: str = "Not Legal"
    pioneer: str = "Not Legal"
    modern: str = "Not Legal"
    legacy: str = "Not Legal"
    vintage: str = "Not Legal"
    commander: str = "Not Legal"
    brawl: str = "Not Legal"
    historic: str = "Not Legal"
    pauper: str = "Not Legal"


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


class CardDetail(BaseModel):
    """Full card details."""

    uuid: str
    name: str
    mana_cost: str | None = None
    mana_value: int = 0
    type: str | None = None
    types: list[str] = []
    subtypes: list[str] = []
    text: str | None = None
    flavor_text: str | None = None
    rarity: str | None = None
    set_code: str | None = None
    set_name: str | None = None
    color_identity: list[str] = []
    colors: list[str] = []
    power: str | None = None
    toughness: str | None = None
    image_url: str | None = None
    prices: PriceBySource
    legalities: CardLegalities
    appears_in_decks: list[CardAppearance] = []
    other_printings: list[CardPrinting] = []

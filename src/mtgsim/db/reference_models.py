"""SQLModel classes for reference tables (mtgjson_*) in the domain database."""

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class MTGJsonCard(SQLModel, table=True):
    """Reference table copy of MTGJSON card data."""

    __tablename__ = "mtgjson_card"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(index=True, unique=True)
    name: str = Field(index=True)
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    text: str | None = None
    oracle_text: str | None = None
    flavor_text: str | None = None
    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None
    rarity: str | None = Field(default=None, index=True)
    number: str | None = None
    artist: str | None = None
    layout: str | None = None
    border_color: str | None = None
    frame_version: str | None = None
    language: str | None = None

    # Set information
    set_code: str | None = Field(default=None, index=True)

    # JSON fields for complex data
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    subtypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    supertypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    legalities: dict = Field(default_factory=dict, sa_column=Column(JSON))
    identifiers: dict = Field(default_factory=dict, sa_column=Column(JSON))
    purchase_urls: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Boolean flags
    has_foil: bool = False
    has_non_foil: bool = False
    is_reprint: bool = False
    is_foil_only: bool = False
    is_online_only: bool = False

    # External IDs (from identifiers)
    scryfall_id: str | None = Field(default=None, index=True)
    mtgo_id: int | None = None
    arena_id: int | None = None
    tcgplayer_id: int | None = None
    cardmarket_id: int | None = None

    # EDHREC data
    edhrec_rank: int | None = None
    edhrec_saltiness: float | None = None


class MTGJsonSet(SQLModel, table=True):
    """Reference table copy of MTGJSON set data."""

    __tablename__ = "mtgjson_set"

    code: str = Field(primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)
    release_date: str | None = Field(default=None, index=True)
    base_set_size: int = 0
    total_set_size: int = 0
    block: str | None = Field(default=None, index=True)
    keyrune_code: str | None = None
    parent_code: str | None = None

    # Boolean flags
    is_foil_only: bool = False
    is_online_only: bool = False
    is_partial_preview: bool = False

    # External IDs
    mtgo_code: str | None = None
    tcgplayer_group_id: int | None = None
    cardmarket_id: int | None = None
    cardsphere_set_id: int | None = None

    # JSON fields
    languages: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    translations: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Token set reference
    token_set_code: str | None = None


class MTGJsonDeck(SQLModel, table=True):
    """Reference table copy of MTGJSON deck data."""

    __tablename__ = "mtgjson_deck"

    uuid: str = Field(primary_key=True)
    file_name: str = Field(index=True, unique=True)
    code: str = Field(index=True)
    name: str = Field(index=True)
    type: str | None = None
    release_date: str | None = None

    # Deck composition counts
    main_board_count: int = 0
    side_board_count: int = 0
    commander_count: int = 0

    # JSON fields for complex data
    commander: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))


class MTGJsonDeckCard(SQLModel, table=True):
    """Reference table copy of MTGJSON deck card data."""

    __tablename__ = "mtgjson_deck_card"

    id: int | None = Field(default=None, primary_key=True)
    deck_uuid: str = Field(foreign_key="mtgjson_deck.uuid", index=True)
    card_uuid: str | None = Field(default=None, index=True)

    # Card identification
    name: str = Field(index=True)
    board: str = Field(index=True)  # "mainBoard", "sideBoard", "commander"
    count: int

    # Card properties
    mana_cost: str | None = None
    mana_value: float | None = None

    # JSON fields for complex data
    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    subtypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    supertypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    printings: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Boolean flags
    is_foil: bool = False
    is_etched: bool = False
    is_starter: bool = False
    is_reprint: bool = False
    has_foil: bool = False
    has_non_foil: bool = False


class MTGJsonPrice(SQLModel, table=True):
    """Reference table copy of MTGJSON price data."""

    __tablename__ = "mtgjson_price"

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(index=True)
    date: str = Field(index=True)

    # Price data from different providers
    tcgplayer_retail: float | None = None
    tcgplayer_buylist: float | None = None
    tcgplayer_market: float | None = None
    tcgplayer_direct_low: float | None = None
    tcgplayer_foil: float | None = None

    cardmarket_retail: float | None = None
    cardmarket_low: float | None = None
    cardmarket_trend: float | None = None
    cardmarket_foil: float | None = None

    mtgo_retail: float | None = None
    mtgo_buylist: float | None = None

    cardsphere_retail: float | None = None
    cardsphere_buylist: float | None = None

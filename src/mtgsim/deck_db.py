from pathlib import Path

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class DeckList(SQLModel, table=True):
    """Index of available decks from DeckList.json."""

    file_name: str = Field(primary_key=True)
    code: str
    name: str = Field(index=True)
    release_date: str | None = None
    type: str | None = None


class Deck(SQLModel, table=True):
    """Deck metadata from individual deck JSON files."""

    uuid: str = Field(primary_key=True)
    file_name: str = Field(index=True, unique=True)
    code: str
    name: str
    type: str | None = None
    release_date: str | None = None
    commander: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    meta_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    main_board_count: int = 0
    side_board_count: int = 0
    commander_count: int = 0

    cards: list["DeckCard"] = Relationship(back_populates="deck")


class DeckCard(SQLModel, table=True):
    """Card entry in a deck."""

    id: int | None = Field(default=None, primary_key=True)
    deck_uuid: str = Field(foreign_key="deck.uuid", index=True)
    card_uuid: str | None = Field(default=None, index=True)

    board: str = Field(index=True)
    count: int
    name: str = Field(index=True)
    mana_cost: str | None = None
    mana_value: float | None = None

    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    indicators: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    printings: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    subtypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    supertypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    identifiers_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    legalities_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    artist_ids_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    availability_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    finishes_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    foreign_data_json: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    keywords_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    purchase_urls_json: dict = Field(default_factory=dict, sa_column=Column(JSON))
    original_printings_json: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    is_foil: bool = False
    is_etched: bool = False
    is_starter: bool = False
    is_reprint: bool = False
    has_foil: bool = False
    has_non_foil: bool = False

    layout: str | None = None
    number: str | None = None
    original_text: str | None = None
    text: str | None = None
    original_release_date: str | None = None

    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None
    rarity: str | None = None
    watermark: str | None = None

    artist: str | None = None
    border_color: str | None = None
    frame_version: str | None = None
    language: str | None = None
    signature: str | None = None

    edhrec_rank: int | None = None
    edhrec_saltiness: float | None = None

    deck: Deck = Relationship(back_populates="cards")


REFERENCE_DB_DIR = Path.home() / ".mtgsim" / "reference" / "mtgjson"
ALL_DECKS_DB_PATH = REFERENCE_DB_DIR / "AllDecks.sqlite"


def get_deck_engine():
    REFERENCE_DB_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{ALL_DECKS_DB_PATH}")


def init_deck_db():
    engine = get_deck_engine()
    SQLModel.metadata.create_all(engine)
    return engine

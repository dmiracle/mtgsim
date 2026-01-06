"""SQLModel models for AllSetFiles reference database."""

from pathlib import Path

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel, create_engine


class SetDB(SQLModel, table=True):
    """Set metadata from AllSetFiles JSON."""

    code: str = Field(primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)
    release_date: str | None = Field(default=None, index=True)
    base_set_size: int = 0
    total_set_size: int = 0
    block: str | None = Field(default=None, index=True)
    keyrune_code: str | None = None
    is_foil_only: bool = False
    is_online_only: bool = False
    mtgo_code: str | None = None
    tcgplayer_group_id: int | None = None
    cardmarket_id: int | None = None
    cardsphere_set_id: int | None = None
    token_set_code: str | None = None
    parent_code: str | None = None
    languages: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    translations: dict = Field(default_factory=dict, sa_column=Column(JSON))

    cards: list["SetCardDB"] = Relationship(back_populates="set_ref")


class SetCardDB(SQLModel, table=True):
    """Card entry from a set file."""

    id: int | None = Field(default=None, primary_key=True)
    uuid: str = Field(index=True)
    set_code: str = Field(foreign_key="setdb.code", index=True)

    name: str = Field(index=True)
    mana_cost: str | None = None
    mana_value: float | None = None
    type: str | None = None
    text: str | None = None
    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None
    rarity: str | None = Field(default=None, index=True)
    number: str | None = None
    artist: str | None = None
    flavor_text: str | None = None
    layout: str | None = None
    border_color: str | None = None
    frame_version: str | None = None
    language: str | None = None

    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    subtypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    supertypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    finishes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    printings: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    legalities: dict = Field(default_factory=dict, sa_column=Column(JSON))
    identifiers: dict = Field(default_factory=dict, sa_column=Column(JSON))
    purchase_urls: dict = Field(default_factory=dict, sa_column=Column(JSON))

    has_foil: bool = False
    has_non_foil: bool = False
    is_reprint: bool = False

    edhrec_rank: int | None = None
    edhrec_saltiness: float | None = None

    set_ref: SetDB = Relationship(back_populates="cards")


REFERENCE_DB_DIR = Path.home() / ".mtgsim" / "reference" / "mtgjson"
ALL_SETS_DB_PATH = REFERENCE_DB_DIR / "AllSets.sqlite"


def get_sets_engine():
    """Get SQLite engine for sets database."""
    REFERENCE_DB_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{ALL_SETS_DB_PATH}")


def init_sets_db():
    """Initialize the sets database tables."""
    engine = get_sets_engine()
    SQLModel.metadata.create_all(
        engine,
        tables=[
            SetDB.__table__,
            SetCardDB.__table__,
        ],
    )
    return engine

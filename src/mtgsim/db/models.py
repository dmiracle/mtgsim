from datetime import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from ..domain.card import CardType, Supertype


class Format(str, Enum):
    STANDARD = "standard"
    PIONEER = "pioneer"
    MODERN = "modern"
    LEGACY = "legacy"
    VINTAGE = "vintage"
    COMMANDER = "commander"
    PAUPER = "pauper"
    HISTORIC = "historic"
    ALCHEMY = "alchemy"
    BRAWL = "brawl"


class CardColorLink(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="carddb.id", primary_key=True)
    color: str = Field(primary_key=True)


class CardTypeLink(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="carddb.id", primary_key=True)
    card_type: str = Field(primary_key=True)


class CardSupertypeLink(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="carddb.id", primary_key=True)
    supertype: str = Field(primary_key=True)


class CardSubtypeLink(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="carddb.id", primary_key=True)
    subtype: str = Field(primary_key=True)


class CardLegalityLink(SQLModel, table=True):
    card_id: int | None = Field(default=None, foreign_key="carddb.id", primary_key=True)
    format: str = Field(primary_key=True)
    legality: str = Field(default="legal")


class CardDB(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    mana_cost_white: int = 0
    mana_cost_blue: int = 0
    mana_cost_black: int = 0
    mana_cost_red: int = 0
    mana_cost_green: int = 0
    mana_cost_colorless: int = 0
    mana_cost_generic: int = 0

    oracle_text: str = ""
    flavor_text: str = ""
    text_box: str = ""
    raw_text: str = ""
    image_url: str | None = None

    power: int | None = None
    toughness: int | None = None
    loyalty: int | None = None
    defense: int | None = None

    rarity: str = "common"

    is_owned: bool = Field(default=False, index=True)
    quantity_owned: int = Field(default=0)
    is_wanted: bool = Field(default=False, index=True)
    is_foil: bool = Field(default=False)

    set_code: str | None = Field(default=None, index=True)
    set_name: str | None = None
    collector_number: str | None = None
    expansion_symbol: str | None = None

    uuid: str | None = Field(default=None, unique=True, index=True)
    scryfall_id: str | None = Field(default=None, unique=True, index=True)
    mtgo_id: int | None = None
    arena_id: int | None = None
    tcgplayer_id: int | None = None
    cardmarket_id: int | None = None

    price_usd_cents: int | None = None
    price_usd_foil_cents: int | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    colors: list["CardColorLink"] = Relationship(cascade_delete=True)
    card_types: list["CardTypeLink"] = Relationship(cascade_delete=True)
    supertypes: list["CardSupertypeLink"] = Relationship(cascade_delete=True)
    subtypes: list["CardSubtypeLink"] = Relationship(cascade_delete=True)
    legalities: list["CardLegalityLink"] = Relationship(cascade_delete=True)

    @property
    def cmc(self) -> int:
        return (
            self.mana_cost_white
            + self.mana_cost_blue
            + self.mana_cost_black
            + self.mana_cost_red
            + self.mana_cost_green
            + self.mana_cost_colorless
            + self.mana_cost_generic
        )

    @property
    def is_creature(self) -> bool:
        return any(link.card_type == CardType.CREATURE.value for link in self.card_types)

    @property
    def is_land(self) -> bool:
        return any(link.card_type == CardType.LAND.value for link in self.card_types)

    @property
    def is_legendary(self) -> bool:
        return any(link.supertype == Supertype.LEGENDARY.value for link in self.supertypes)


class AllPrintingsMetadata(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    last_synced_at: datetime = Field(default_factory=datetime.utcnow)
    version: str | None = None
    fingerprint: str | None = None
    record_count: int | None = None

"""Enhanced domain models for the unified domain database."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class DomainCard(SQLModel, table=True):
    """Enhanced domain card model with all API-required fields."""

    __tablename__ = "domain_card"

    # Primary identification
    id: int | None = Field(default=None, primary_key=True)
    uuid: str | None = Field(default=None, unique=True, index=True)
    name: str = Field(index=True)

    # Mana cost information
    mana_cost: str | None = None  # Original mana cost string like "{2}{U}{R}"
    mana_value: float | None = None  # Converted mana cost
    mana_cost_white: int = 0
    mana_cost_blue: int = 0
    mana_cost_black: int = 0
    mana_cost_red: int = 0
    mana_cost_green: int = 0
    mana_cost_colorless: int = 0
    mana_cost_generic: int = 0

    # Card text
    type_line: str | None = None  # Full type line
    oracle_text: str = ""
    flavor_text: str = ""
    text_box: str = ""
    raw_text: str = ""

    # Stats
    power: str | None = None  # Can be "*" or "1+*"
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None

    # Set information
    set_code: str | None = Field(default=None, foreign_key="domain_set.code", index=True)
    set_name: str | None = None
    collector_number: str | None = None
    rarity: str = "common"

    # Visual properties
    layout: str | None = None
    border_color: str | None = None
    frame_version: str | None = None
    artist: str | None = None
    image_url: str | None = None

    # Pricing data (embedded from reference)
    tcgplayer_price_usd: float | None = None
    tcgplayer_price_usd_foil: float | None = None
    cardmarket_price_eur: float | None = None
    mtgo_price_tix: float | None = None
    price_usd_cents: int | None = None
    price_usd_foil_cents: int | None = None

    # Legality data (JSON field)
    legalities: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Identifiers for external services
    scryfall_id: str | None = Field(default=None, unique=True, index=True)
    mtgo_id: int | None = None
    arena_id: int | None = None
    tcgplayer_id: int | None = None
    cardmarket_id: int | None = None

    # User collection data
    is_owned: bool = Field(default=False, index=True)
    quantity_owned: int = Field(default=0)
    is_wanted: bool = Field(default=False, index=True)
    is_foil: bool = Field(default=False)

    # Boolean flags
    has_foil: bool = False
    has_non_foil: bool = False
    is_reprint: bool = False
    is_foil_only: bool = False
    is_online_only: bool = False

    # Metadata
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "mtgjson"  # Track where this card was added from

    # Relationships
    color_links: list["DomainCardColorLink"] = Relationship(cascade_delete=True)
    card_types: list["DomainCardTypeLink"] = Relationship(cascade_delete=True)
    supertypes: list["DomainCardSupertypeLink"] = Relationship(cascade_delete=True)
    subtype_links: list["DomainCardSubtypeLink"] = Relationship(cascade_delete=True)
    set_ref: Optional["DomainSet"] = Relationship(back_populates="cards")

    # Computed properties for API compatibility
    @property
    def color_identity(self) -> list[str]:
        """Get color identity from relationships."""
        return [link.color for link in self.color_links]

    @property
    def type_list(self) -> list[str]:
        """Get card types from relationships."""
        return [link.card_type for link in self.card_types]

    @property
    def colors(self) -> list[str]:
        """Get colors from color identity (simplified for API compatibility)."""
        return self.color_identity

    @property
    def subtypes(self) -> list[str]:
        """Get subtypes from relationships."""
        return [link.subtype for link in self.subtype_links]

    @property
    def cmc(self) -> int:
        """Converted mana cost (legacy compatibility)."""
        return (
            self.mana_cost_white
            + self.mana_cost_blue
            + self.mana_cost_black
            + self.mana_cost_red
            + self.mana_cost_green
            + self.mana_cost_colorless
            + self.mana_cost_generic
        )


class DomainSet(SQLModel, table=True):
    """Enhanced domain set model with all API-required fields."""

    __tablename__ = "domain_set"

    # Primary identification
    code: str = Field(primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)

    # Release information
    release_date: str | None = Field(default=None, index=True)
    base_set_size: int = 0
    total_set_size: int = 0
    block: str | None = Field(default=None, index=True)
    parent_code: str | None = None

    # Visual identifiers
    keyrune_code: str | None = None

    # Boolean flags
    is_foil_only: bool = False
    is_online_only: bool = False
    is_partial_preview: bool = False

    # External IDs
    mtgo_code: str | None = None
    tcgplayer_group_id: int | None = None
    cardmarket_id: int | None = None
    cardsphere_set_id: int | None = None

    # Aggregated statistics (computed during migration)
    total_price_usd: float | None = None
    average_price_usd: float | None = None
    card_count_by_rarity: dict = Field(default_factory=dict, sa_column=Column(JSON))
    color_distribution: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Localization
    languages: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    translations: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Token set reference
    token_set_code: str | None = None

    # Metadata
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "mtgjson"

    # Relationships
    cards: list["DomainCard"] = Relationship(back_populates="set_ref")


class DomainDeck(SQLModel, table=True):
    """Enhanced domain deck model with all API-required fields."""

    __tablename__ = "domain_deck"

    # Primary identification
    uuid: str = Field(primary_key=True)
    file_name: str = Field(index=True, unique=True)
    code: str = Field(index=True)
    name: str = Field(index=True)

    # Deck metadata
    type: str | None = None
    release_date: str | None = None

    # Aggregated data (computed during migration)
    total_price_usd: float | None = None
    main_board_count: int = 0
    side_board_count: int = 0
    commander_count: int = 0

    # Color identity (computed from cards)
    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Format legalities (computed from cards)
    format_legalities: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Mana curve data
    mana_curve: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Commander information
    commander: list[dict] = Field(default_factory=list, sa_column=Column(JSON))

    # Additional metadata
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Metadata
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = "mtgjson"

    # Relationships
    cards: list["DomainDeckCard"] = Relationship(back_populates="deck")


class DomainDeckCard(SQLModel, table=True):
    """Enhanced domain deck card model."""

    __tablename__ = "domain_deck_card"

    id: int | None = Field(default=None, primary_key=True)
    deck_uuid: str = Field(foreign_key="domain_deck.uuid", index=True)
    card_uuid: str | None = Field(default=None, index=True)

    # Card identification
    name: str = Field(index=True)
    board: str = Field(index=True)  # "mainBoard", "sideBoard", "commander"
    count: int

    # Card properties (denormalized for performance)
    mana_cost: str | None = None
    mana_value: float | None = None
    type_line: str | None = None
    rarity: str | None = None

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

    # Relationships
    deck: DomainDeck = Relationship(back_populates="cards")


# Relationship link tables for the enhanced Card model
class DomainCardColorLink(SQLModel, table=True):
    """Link table for card colors."""

    __tablename__ = "domain_card_color_link"

    card_id: int | None = Field(default=None, foreign_key="domain_card.id", primary_key=True)
    color: str = Field(primary_key=True)


class DomainCardTypeLink(SQLModel, table=True):
    """Link table for card types."""

    __tablename__ = "domain_card_type_link"

    card_id: int | None = Field(default=None, foreign_key="domain_card.id", primary_key=True)
    card_type: str = Field(primary_key=True)


class DomainCardSupertypeLink(SQLModel, table=True):
    """Link table for card supertypes."""

    __tablename__ = "domain_card_supertype_link"

    card_id: int | None = Field(default=None, foreign_key="domain_card.id", primary_key=True)
    supertype: str = Field(primary_key=True)


class DomainCardSubtypeLink(SQLModel, table=True):
    """Link table for card subtypes."""

    __tablename__ = "domain_card_subtype_link"

    card_id: int | None = Field(default=None, foreign_key="domain_card.id", primary_key=True)
    subtype: str = Field(primary_key=True)

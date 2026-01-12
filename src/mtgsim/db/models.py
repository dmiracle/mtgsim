"""Unified database models for mtgsim.

This module defines all database models in a single file:
- MJ* models: Reference data from MTGJSON (read-only, synced)
- User models: User-modifiable data (Card, Deck, DeckCard)

Naming conventions:
- MJ prefix: MTGJSON reference data (mj_* tables)
- No prefix: User data (card, deck, deck_card tables)
"""

from datetime import datetime

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

# =============================================================================
# Reference Models (MJ prefix) - Read-only, synced from MTGJSON
# =============================================================================


class MJCard(SQLModel, table=True):
    """Card data from MTGJSON AllPrintings."""

    __tablename__ = "mj_card"

    uuid: str = Field(primary_key=True)
    name: str = Field(index=True)
    set_code: str = Field(index=True)

    # Card text
    mana_cost: str | None = None
    mana_value: float | None = None
    type_line: str | None = None
    oracle_text: str | None = None
    flavor_text: str | None = None

    # Stats
    power: str | None = None
    toughness: str | None = None
    loyalty: str | None = None
    defense: str | None = None

    # Metadata
    rarity: str | None = Field(default=None, index=True)
    number: str | None = None
    artist: str | None = None
    layout: str | None = None
    border_color: str | None = None
    frame_version: str | None = None

    # JSON arrays (replaces link tables)
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    color_identity: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    subtypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    supertypes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Flags
    has_foil: bool = False
    has_non_foil: bool = False
    is_reprint: bool = False
    is_reserved: bool = False
    is_promo: bool = False


class MJCardIdentifier(SQLModel, table=True):
    """External identifiers for cards (Scryfall, TCGPlayer, etc.)."""

    __tablename__ = "mj_card_identifier"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    scryfall_id: str | None = Field(default=None, index=True)
    scryfall_oracle_id: str | None = None
    scryfall_illustration_id: str | None = None

    tcgplayer_product_id: str | None = None
    tcgplayer_etched_product_id: str | None = None

    cardmarket_id: str | None = None

    mtgo_id: str | None = None
    mtgo_foil_id: str | None = None

    mtgjson_v4_id: str | None = None
    multiverse_id: str | None = None


class MJCardLegality(SQLModel, table=True):
    """Format legality for cards."""

    __tablename__ = "mj_card_legality"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)
    format: str = Field(index=True)  # standard, modern, legacy, etc.
    status: str  # Legal, Banned, Restricted, Not Legal


class MJCardPrice(SQLModel, table=True):
    """Price data from multiple providers."""

    __tablename__ = "mj_card_price"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    provider: str = Field(index=True)  # tcgplayer, cardmarket, cardsphere, cardkingdom
    listing_type: str  # retail, buylist
    finish: str  # normal, foil, etched
    currency: str = "USD"
    price: float | None = None

    updated_at: datetime | None = None


class MJSet(SQLModel, table=True):
    """Set data from MTGJSON."""

    __tablename__ = "mj_set"

    code: str = Field(primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)

    release_date: str | None = Field(default=None, index=True)
    base_set_size: int = 0
    total_set_size: int = 0

    block: str | None = Field(default=None, index=True)
    parent_code: str | None = None
    keyrune_code: str | None = None

    is_foil_only: bool = False
    is_online_only: bool = False
    is_partial_preview: bool = False


class MJDeck(SQLModel, table=True):
    """Preconstructed deck data from MTGJSON."""

    __tablename__ = "mj_deck"

    uuid: str = Field(primary_key=True)
    file_name: str = Field(index=True, unique=True)
    name: str = Field(index=True)
    code: str = Field(index=True)

    type: str | None = None
    release_date: str | None = None

    main_board_count: int = 0
    side_board_count: int = 0
    commander_count: int = 0


class MJDeckCard(SQLModel, table=True):
    """Cards in preconstructed decks."""

    __tablename__ = "mj_deck_card"

    id: int | None = Field(default=None, primary_key=True)
    deck_uuid: str = Field(foreign_key="mj_deck.uuid", index=True)
    card_uuid: str | None = Field(default=None, index=True)

    name: str = Field(index=True)
    board: str = Field(index=True)  # mainBoard, sideBoard, commander
    count: int = 1

    # Denormalized for query performance
    mana_cost: str | None = None
    mana_value: float | None = None
    colors: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    types: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class MJKeyword(SQLModel, table=True):
    """MTG keyword from MTGJSON Keywords.json."""

    __tablename__ = "mj_keyword"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str = Field(index=True)  # abilityWords, keywordAbilities, keywordActions


# =============================================================================
# User Models - User-modifiable data
# =============================================================================


class UserCard(SQLModel, table=True):
    """User's card collection entry.

    Tracks both owned cards and wishlist in a single table.
    A card can be owned, wanted, or both.
    """

    __tablename__ = "user_card"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    # Ownership
    quantity_owned: int = 0
    quantity_owned_foil: int = 0

    # Wishlist
    quantity_wanted: int = 0
    quantity_wanted_foil: int = 0

    # Purchase tracking
    purchase_price: float | None = None
    purchase_date: datetime | None = None

    # Condition (for owned cards)
    condition: str = "NM"  # NM, LP, MP, HP, DMG

    # Notes
    notes: str | None = None

    # Timestamps
    added_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def owns(self) -> bool:
        """True if user owns any copies."""
        return (self.quantity_owned + self.quantity_owned_foil) > 0

    @property
    def wants(self) -> bool:
        """True if user wants any copies."""
        return (self.quantity_wanted + self.quantity_wanted_foil) > 0

    @property
    def total_owned(self) -> int:
        """Total owned copies (regular + foil)."""
        return self.quantity_owned + self.quantity_owned_foil

    @property
    def total_wanted(self) -> int:
        """Total wanted copies (regular + foil)."""
        return self.quantity_wanted + self.quantity_wanted_foil


class UserDeck(SQLModel, table=True):
    """User-created deck."""

    __tablename__ = "user_deck"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None

    format: str | None = None  # standard, modern, commander, etc.

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserDeckCard(SQLModel, table=True):
    """Card entry in a user deck."""

    __tablename__ = "user_deck_card"

    id: int | None = Field(default=None, primary_key=True)
    deck_id: int = Field(foreign_key="user_deck.id", index=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    board: str = "main"  # main, side, commander, maybe
    count: int = 1
    is_foil: bool = False

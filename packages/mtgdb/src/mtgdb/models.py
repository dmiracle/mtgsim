"""Unified database models for mtgdb.

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
    finishes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
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


class MJKeywordDefinition(SQLModel, table=True):
    """Definition/rules text for an MTG keyword."""

    __tablename__ = "mj_keyword_definition"

    id: int | None = Field(default=None, primary_key=True)
    keyword: str = Field(index=True, unique=True)
    definition: str
    source: str = "generated"  # comprehensive_rules, manual, generated
    last_verified_at: datetime | None = None


class MJCardTag(SQLModel, table=True):
    """Card tag from Scryfall oracle tags (e.g. mana-dork, ramp, removal)."""

    __tablename__ = "mj_card_tag"

    id: int | None = Field(default=None, primary_key=True)
    card_name: str = Field(index=True)
    tag: str = Field(index=True)


# =============================================================================
# 17Lands Models (MJ17L prefix) - Read-only, synced from 17Lands
# =============================================================================


class MJ17LDataset(SQLModel, table=True):
    """17Lands public dataset metadata."""

    __tablename__ = "mj_17l_dataset"

    id: int | None = Field(default=None, primary_key=True)
    expansion: str = Field(index=True)
    format: str = Field(index=True)
    last_updated: str | None = None

    draft_data_url: str | None = None
    game_data_url: str | None = None
    replay_data_url: str | None = None

    draft_data_downloaded: bool = False
    game_data_downloaded: bool = False
    replay_data_downloaded: bool = False

    synced_at: str | None = None


class MJ17LDraftPick(SQLModel, table=True):
    """One row per draft pick from 17Lands draft data."""

    __tablename__ = "mj_17l_draft_pick"

    id: int | None = Field(default=None, primary_key=True)
    expansion: str = Field(index=True)
    event_type: str = Field(index=True)
    draft_id: str = Field(index=True)
    draft_time: str | None = None
    user_win_rate_bucket: float | None = None
    user_n_matches_bucket: int | None = None
    event_match_wins: int | None = None
    event_match_losses: int | None = None
    pack_number: int | None = None
    pick_number: int | None = None
    pick: str | None = Field(default=None, index=True)
    pick_maindeck_rate: float | None = None
    pick_sideboard_in_rate: float | None = None


class MJ17LDraftCard(SQLModel, table=True):
    """One row per card available in a draft pack."""

    __tablename__ = "mj_17l_draft_card"

    id: int | None = Field(default=None, primary_key=True)
    draft_id: str = Field(index=True)
    pack_number: int | None = None
    pick_number: int | None = None
    card_name: str = Field(index=True)
    in_pack: bool = False
    pool_count: int = 0


class MJ17LGame(SQLModel, table=True):
    """One row per game from 17Lands game data."""

    __tablename__ = "mj_17l_game"

    id: int | None = Field(default=None, primary_key=True)
    expansion: str = Field(index=True)
    event_type: str = Field(index=True)
    draft_id: str = Field(index=True)
    build_index: int | None = None
    draft_time: str | None = None
    game_number: int | None = None
    rank: str | None = None
    user_win_rate_bucket: float | None = None
    user_n_games_bucket: int | None = None
    on_play: bool | None = None
    num_mulligans: int | None = None
    opp_num_mulligans: int | None = None
    opp_colors: str | None = None
    num_turns: int | None = None
    won: bool | None = None


class MJ17LGameCard(SQLModel, table=True):
    """One row per card in a game's deck composition."""

    __tablename__ = "mj_17l_game_card"

    id: int | None = Field(default=None, primary_key=True)
    draft_id: str = Field(index=True)
    build_index: int | None = None
    game_number: int | None = None
    card_name: str = Field(index=True)
    in_opening_hand: int = 0
    in_deck: int = 0
    drawn: int = 0
    sideboarded: int = 0


class MJ17LReplay(SQLModel, table=True):
    """One row per game replay from 17Lands replay data."""

    __tablename__ = "mj_17l_replay"

    id: int | None = Field(default=None, primary_key=True)
    expansion: str = Field(index=True)
    format: str = Field(index=True)
    draft_id: str = Field(index=True)
    history_id: str | None = None
    time: str | None = None
    game_index: int | None = None
    user_rank: str | None = None
    oppo_rank: str | None = None
    user_deck_colors: str | None = None
    oppo_deck_colors: str | None = None
    user_mulligans: int | None = None
    oppo_mulligans: int | None = None
    on_play: bool | None = None
    turns: int | None = None
    won: bool | None = None
    missing_diffs: str | None = None
    user_total_cards_drawn: int | None = None
    user_total_cards_discarded: int | None = None
    user_total_lands_played: int | None = None
    user_total_cards_foretold: int | None = None
    user_total_creatures_cast: int | None = None
    user_total_non_creatures_cast: int | None = None
    user_total_instants_sorceries_cast: int | None = None
    user_total_cards_learned: int | None = None
    user_total_mana_spent: int | None = None
    oppo_total_cards_drawn: int | None = None
    oppo_total_cards_discarded: int | None = None
    oppo_total_lands_played: int | None = None
    oppo_total_cards_foretold: int | None = None
    oppo_total_creatures_cast: int | None = None
    oppo_total_non_creatures_cast: int | None = None
    oppo_total_instants_sorceries_cast: int | None = None
    oppo_total_cards_learned: int | None = None
    oppo_total_mana_spent: int | None = None


class MJ17LReplayTurn(SQLModel, table=True):
    """One row per turn per player in a game replay."""

    __tablename__ = "mj_17l_replay_turn"

    id: int | None = Field(default=None, primary_key=True)
    draft_id: str = Field(index=True)
    game_index: int | None = None
    turn_number: int | None = None
    player: str | None = None  # "user" or "oppo"
    cards_drawn: str | None = None
    cards_discarded: str | None = None
    lands_played: str | None = None
    cards_foretold: str | None = None
    creatures_cast: str | None = None
    non_creatures_cast: str | None = None
    user_instants_sorceries_cast: str | None = None
    oppo_instants_sorceries_cast: str | None = None
    user_abilities: str | None = None
    oppo_abilities: str | None = None
    user_cards_learned: str | None = None
    oppo_cards_learned: str | None = None
    creatures_attacked: str | None = None
    creatures_blocked: str | None = None
    creatures_unblocked: str | None = None
    creatures_blocking: str | None = None
    player_combat_damage_dealt: int | None = None
    user_creatures_killed_combat: str | None = None
    oppo_creatures_killed_combat: str | None = None
    user_creatures_killed_non_combat: str | None = None
    oppo_creatures_killed_non_combat: str | None = None
    user_mana_spent: int | None = None
    oppo_mana_spent: int | None = None
    eot_user_cards_in_hand: str | None = None
    eot_oppo_cards_in_hand: str | None = None
    eot_user_lands_in_play: str | None = None
    eot_oppo_lands_in_play: str | None = None
    eot_user_creatures_in_play: str | None = None
    eot_oppo_creatures_in_play: str | None = None
    eot_user_non_creatures_in_play: str | None = None
    eot_oppo_non_creatures_in_play: str | None = None
    eot_user_life: int | None = None
    eot_oppo_life: int | None = None


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


class UserCardRating(SQLModel, table=True):
    """User's quadrant theory rating for a card.

    Rates cards on a 1-5 scale across four game states:
    - Developing: building your board (early game, playing on curve)
    - Ahead: you have board advantage
    - Behind: opponent has board advantage
    - Parity: board is stalled, neither player is ahead
    """

    __tablename__ = "user_card_rating"

    id: int | None = Field(default=None, primary_key=True)
    card_uuid: str = Field(foreign_key="mj_card.uuid", index=True, unique=True)

    developing: float | None = None  # 1.0 - 5.0
    ahead: float | None = None
    behind: float | None = None
    parity: float | None = None

    notes: str | None = None

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserDeck(SQLModel, table=True):
    """User-created deck."""

    __tablename__ = "user_deck"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None

    format: str | None = None  # standard, modern, commander, etc.
    source: str = Field(default="user", index=True)  # user, import, test, ...

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


class User17LEvent(SQLModel, table=True):
    """A personal 17Lands event (draft/sealed) with game results."""

    __tablename__ = "user_17l_event"

    id: int | None = Field(default=None, primary_key=True)
    draft_id: str = Field(unique=True, index=True)
    expansion: str | None = Field(default=None, index=True)
    event_type: str | None = Field(default=None, index=True)
    start_time: str | None = None
    end_time: str | None = None
    entry_fee: int | None = None
    wins: int | None = None
    losses: int | None = None
    rank: str | None = None
    deck_colors: str | None = None
    deck_index: int | None = None

    # Raw JSON from 17Lands API for detailed data
    event_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    draft_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    game_data: dict = Field(default_factory=dict, sa_column=Column(JSON))
    deck_data: dict = Field(default_factory=dict, sa_column=Column(JSON))

    synced_at: datetime = Field(default_factory=datetime.utcnow)


class PinnedDeck(SQLModel, table=True):
    """A pinned deck reference. Stores the deck file identifier and pin order."""

    __tablename__ = "pinned_deck"

    id: int | None = Field(default=None, primary_key=True)
    deck_file: str = Field(unique=True, index=True)
    pinned_at: datetime = Field(default_factory=datetime.utcnow)


class UserCardInteraction(SQLModel, table=True):
    """Interaction between two cards (combo, synergy, counter, etc.)."""

    __tablename__ = "user_card_interaction"

    id: int | None = Field(default=None, primary_key=True)
    source_card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)
    target_card_uuid: str = Field(foreign_key="mj_card.uuid", index=True)

    interaction_type: str = Field(index=True)
    is_bidirectional: bool = True
    description: str | None = None
    strength: int | None = None
    extra: dict = Field(default_factory=dict, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

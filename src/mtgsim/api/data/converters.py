"""Conversion utilities between reference and domain models.

This module provides functions to transform data between reference models (MTGJson*)
and domain models (Domain*), as well as converting both to API response formats.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from mtgsim.db.reference_models import MTGJsonCard, MTGJsonSet, MTGJsonDeck, MTGJsonDeckCard
from mtgsim.db.domain_models import DomainCard, DomainSet, DomainDeck, DomainDeckCard


def reference_card_to_domain(ref_card: MTGJsonCard, **overrides) -> DomainCard:
    """
    Convert a reference MTGJsonCard to a DomainCard.
    
    Args:
        ref_card: The reference card to convert
        **overrides: Additional fields to override in the domain card
        
    Returns:
        DomainCard instance with data from reference card
    """
    # Extract identifiers
    scryfall_id = None
    mtgo_id = None
    arena_id = None
    tcgplayer_id = None
    cardmarket_id = None
    
    if ref_card.identifiers:
        scryfall_id = ref_card.identifiers.get("scryfallId")
        mtgo_id = ref_card.identifiers.get("mtgoId")
        arena_id = ref_card.identifiers.get("arenaId")
        tcgplayer_id = ref_card.identifiers.get("tcgplayerId")
        cardmarket_id = ref_card.identifiers.get("cardmarketId")

    # Create domain card with enhanced fields
    domain_card = DomainCard(
        uuid=ref_card.uuid,
        name=ref_card.name,
        mana_cost=ref_card.mana_cost,
        mana_value=ref_card.mana_value,
        type_line=ref_card.type,
        oracle_text=ref_card.oracle_text or ref_card.text or "",
        flavor_text=ref_card.flavor_text or "",
        power=ref_card.power,
        toughness=ref_card.toughness,
        loyalty=ref_card.loyalty,
        defense=ref_card.defense,
        set_code=ref_card.set_code,
        collector_number=ref_card.number,
        rarity=ref_card.rarity or "common",
        layout=ref_card.layout,
        border_color=ref_card.border_color,
        frame_version=ref_card.frame_version,
        artist=ref_card.artist,
        legalities=ref_card.legalities or {},
        scryfall_id=scryfall_id,
        mtgo_id=mtgo_id,
        arena_id=arena_id,
        tcgplayer_id=tcgplayer_id,
        cardmarket_id=cardmarket_id,
        has_foil=ref_card.has_foil,
        has_non_foil=ref_card.has_non_foil,
        is_reprint=ref_card.is_reprint,
        is_foil_only=ref_card.is_foil_only,
        is_online_only=ref_card.is_online_only,
        added_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        source="mtgjson",
        **overrides
    )
    
    return domain_card


def reference_set_to_domain(ref_set: MTGJsonSet, **overrides) -> DomainSet:
    """
    Convert a reference MTGJsonSet to a DomainSet.
    
    Args:
        ref_set: The reference set to convert
        **overrides: Additional fields to override in the domain set
        
    Returns:
        DomainSet instance with data from reference set
    """
    domain_set = DomainSet(
        code=ref_set.code,
        name=ref_set.name,
        type=ref_set.type,
        release_date=ref_set.release_date,
        base_set_size=ref_set.base_set_size,
        total_set_size=ref_set.total_set_size,
        block=ref_set.block,
        parent_code=ref_set.parent_code,
        keyrune_code=ref_set.keyrune_code,
        is_foil_only=ref_set.is_foil_only,
        is_online_only=ref_set.is_online_only,
        is_partial_preview=ref_set.is_partial_preview,
        mtgo_code=ref_set.mtgo_code,
        tcgplayer_group_id=ref_set.tcgplayer_group_id,
        cardmarket_id=ref_set.cardmarket_id,
        cardsphere_set_id=ref_set.cardsphere_set_id,
        languages=ref_set.languages or [],
        translations=ref_set.translations or {},
        token_set_code=ref_set.token_set_code,
        added_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        source="mtgjson",
        **overrides
    )
    
    return domain_set


def reference_deck_to_domain(ref_deck: MTGJsonDeck, **overrides) -> DomainDeck:
    """
    Convert a reference MTGJsonDeck to a DomainDeck.
    
    Args:
        ref_deck: The reference deck to convert
        **overrides: Additional fields to override in the domain deck
        
    Returns:
        DomainDeck instance with data from reference deck
    """
    domain_deck = DomainDeck(
        uuid=ref_deck.uuid,
        file_name=ref_deck.file_name,
        code=ref_deck.code,
        name=ref_deck.name,
        type=ref_deck.type,
        release_date=ref_deck.release_date,
        main_board_count=ref_deck.main_board_count,
        side_board_count=ref_deck.side_board_count,
        commander_count=ref_deck.commander_count,
        commander=ref_deck.commander or [],
        added_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        source="mtgjson",
        **overrides
    )
    
    return domain_deck


def reference_deck_card_to_domain(ref_deck_card: MTGJsonDeckCard, **overrides) -> DomainDeckCard:
    """
    Convert a reference MTGJsonDeckCard to a DomainDeckCard.
    
    Args:
        ref_deck_card: The reference deck card to convert
        **overrides: Additional fields to override in the domain deck card
        
    Returns:
        DomainDeckCard instance with data from reference deck card
    """
    domain_deck_card = DomainDeckCard(
        deck_uuid=ref_deck_card.deck_uuid,
        card_uuid=ref_deck_card.card_uuid,
        name=ref_deck_card.name,
        board=ref_deck_card.board,
        count=ref_deck_card.count,
        mana_cost=ref_deck_card.mana_cost,
        mana_value=ref_deck_card.mana_value,
        color_identity=ref_deck_card.color_identity or [],
        colors=ref_deck_card.colors or [],
        types=ref_deck_card.types or [],
        subtypes=ref_deck_card.subtypes or [],
        supertypes=ref_deck_card.supertypes or [],
        printings=ref_deck_card.printings or [],
        is_foil=ref_deck_card.is_foil,
        is_etched=ref_deck_card.is_etched,
        is_starter=ref_deck_card.is_starter,
        is_reprint=ref_deck_card.is_reprint,
        has_foil=ref_deck_card.has_foil,
        has_non_foil=ref_deck_card.has_non_foil,
        **overrides
    )
    
    return domain_deck_card


def domain_card_to_api_dict(domain_card: DomainCard) -> Dict[str, Any]:
    """
    Convert a DomainCard to API response dictionary format.
    
    Args:
        domain_card: The domain card to convert
        
    Returns:
        Dictionary suitable for API responses
    """
    return {
        "uuid": domain_card.uuid,
        "name": domain_card.name,
        "mana_cost": domain_card.mana_cost,
        "mana_value": domain_card.mana_value,
        "type": domain_card.type_line,
        "types": domain_card.type_list,
        "subtypes": domain_card.subtypes,
        "supertypes": [link.supertype for link in domain_card.supertypes],
        "rarity": domain_card.rarity,
        "set_code": domain_card.set_code,
        "set_name": domain_card.set_name,
        "color_identity": domain_card.color_identity,
        "colors": domain_card.colors,
        "power": domain_card.power,
        "toughness": domain_card.toughness,
        "loyalty": domain_card.loyalty,
        "defense": domain_card.defense,
        "text": domain_card.oracle_text,
        "flavor_text": domain_card.flavor_text,
        "number": domain_card.collector_number,
        "artist": domain_card.artist,
        "keywords": [],  # TODO: Add keywords support
        "legalities": domain_card.legalities,
        "image_url": domain_card.image_url or _build_image_url(domain_card.scryfall_id),
        "price": domain_card.tcgplayer_price_usd,
        "in_collection": True,
        # Additional domain-specific fields
        "is_owned": domain_card.is_owned,
        "quantity_owned": domain_card.quantity_owned,
        "is_wanted": domain_card.is_wanted,
        "added_at": domain_card.added_at.isoformat() if domain_card.added_at else None,
    }


def reference_card_to_api_dict(ref_card: MTGJsonCard) -> Dict[str, Any]:
    """
    Convert a reference MTGJsonCard to API response dictionary format.
    
    Args:
        ref_card: The reference card to convert
        
    Returns:
        Dictionary suitable for API responses
    """
    return {
        "uuid": ref_card.uuid,
        "name": ref_card.name,
        "mana_cost": ref_card.mana_cost,
        "mana_value": ref_card.mana_value,
        "type": ref_card.type,
        "types": ref_card.types or [],
        "subtypes": ref_card.subtypes or [],
        "supertypes": ref_card.supertypes or [],
        "rarity": ref_card.rarity,
        "set_code": ref_card.set_code,
        "set_name": None,  # Would need to be looked up separately
        "color_identity": ref_card.color_identity or [],
        "colors": ref_card.colors or [],
        "power": ref_card.power,
        "toughness": ref_card.toughness,
        "loyalty": ref_card.loyalty,
        "defense": ref_card.defense,
        "text": ref_card.oracle_text or ref_card.text,
        "flavor_text": ref_card.flavor_text,
        "number": ref_card.number,
        "artist": ref_card.artist,
        "keywords": ref_card.keywords or [],
        "legalities": ref_card.legalities or {},
        "image_url": _build_image_url(ref_card.scryfall_id),
        "price": None,  # Reference cards don't have pricing
        "in_collection": False,
        # Reference-specific fields
        "edhrec_rank": ref_card.edhrec_rank,
        "edhrec_saltiness": ref_card.edhrec_saltiness,
    }


def domain_set_to_api_dict(domain_set: DomainSet) -> Dict[str, Any]:
    """
    Convert a DomainSet to API response dictionary format.
    
    Args:
        domain_set: The domain set to convert
        
    Returns:
        Dictionary suitable for API responses
    """
    return {
        "code": domain_set.code,
        "name": domain_set.name,
        "type": domain_set.type,
        "release_date": domain_set.release_date,
        "base_set_size": domain_set.base_set_size,
        "total_set_size": domain_set.total_set_size,
        "block": domain_set.block,
        "keyrune_code": domain_set.keyrune_code,
        "is_foil_only": domain_set.is_foil_only,
        "is_online_only": domain_set.is_online_only,
        "mtgo_code": domain_set.mtgo_code,
        "tcgplayer_group_id": domain_set.tcgplayer_group_id,
        "cardmarket_id": domain_set.cardmarket_id,
        "languages": domain_set.languages,
        "translations": domain_set.translations,
        "in_collection": True,
        # Domain-specific aggregated data
        "total_price": domain_set.total_price_usd,
        "average_price": domain_set.average_price_usd,
        "card_count_by_rarity": domain_set.card_count_by_rarity,
        "color_distribution": domain_set.color_distribution,
        "added_at": domain_set.added_at.isoformat() if domain_set.added_at else None,
    }


def reference_set_to_api_dict(ref_set: MTGJsonSet) -> Dict[str, Any]:
    """
    Convert a reference MTGJsonSet to API response dictionary format.
    
    Args:
        ref_set: The reference set to convert
        
    Returns:
        Dictionary suitable for API responses
    """
    return {
        "code": ref_set.code,
        "name": ref_set.name,
        "type": ref_set.type,
        "release_date": ref_set.release_date,
        "base_set_size": ref_set.base_set_size,
        "total_set_size": ref_set.total_set_size,
        "block": ref_set.block,
        "keyrune_code": ref_set.keyrune_code,
        "is_foil_only": ref_set.is_foil_only,
        "is_online_only": ref_set.is_online_only,
        "mtgo_code": ref_set.mtgo_code,
        "tcgplayer_group_id": ref_set.tcgplayer_group_id,
        "cardmarket_id": ref_set.cardmarket_id,
        "languages": ref_set.languages,
        "translations": ref_set.translations,
        "in_collection": False,
        # Reference sets don't have aggregated pricing data
        "total_price": None,
        "average_price": None,
        "card_count_by_rarity": {},
        "color_distribution": {},
    }


def domain_deck_to_api_dict(domain_deck: DomainDeck) -> Dict[str, Any]:
    """
    Convert a DomainDeck to API response dictionary format.
    
    Args:
        domain_deck: The domain deck to convert
        
    Returns:
        Dictionary suitable for API responses
    """
    return {
        "file": domain_deck.file_name + ".json",
        "name": domain_deck.name,
        "code": domain_deck.code,
        "type": domain_deck.type,
        "release_date": domain_deck.release_date,
        "card_count": domain_deck.main_board_count + domain_deck.side_board_count,
        "colors": domain_deck.color_identity,
        "price": domain_deck.total_price_usd,
        "in_collection": True,
        # Domain-specific aggregated data
        "format_legalities": domain_deck.format_legalities,
        "mana_curve": domain_deck.mana_curve,
        "commander": domain_deck.commander,
        "added_at": domain_deck.added_at.isoformat() if domain_deck.added_at else None,
    }


def reference_deck_to_api_dict(ref_deck: MTGJsonDeck) -> Dict[str, Any]:
    """
    Convert a reference MTGJsonDeck to API response dictionary format.
    
    Args:
        ref_deck: The reference deck to convert
        
    Returns:
        Dictionary suitable for API responses
    """
    return {
        "file": ref_deck.file_name + ".json",
        "name": ref_deck.name,
        "code": ref_deck.code,
        "type": ref_deck.type,
        "release_date": ref_deck.release_date,
        "card_count": ref_deck.main_board_count + ref_deck.side_board_count,
        "colors": [],  # Would need to be computed from deck cards
        "price": None,  # Reference decks don't have pricing
        "in_collection": False,
        # Reference decks don't have aggregated data
        "format_legalities": {},
        "mana_curve": {},
        "commander": ref_deck.commander,
    }


def _build_image_url(scryfall_id: Optional[str]) -> Optional[str]:
    """
    Build Scryfall image URL from scryfall_id.
    
    Args:
        scryfall_id: The Scryfall UUID for the card
        
    Returns:
        Image URL or None if no scryfall_id provided
    """
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"


def create_readonly_domain_card(ref_card: MTGJsonCard) -> Dict[str, Any]:
    """
    Create a read-only domain card representation from a reference card.
    
    This is used when displaying reference cards in a domain-like format
    without actually adding them to the domain database.
    
    Args:
        ref_card: The reference card to convert
        
    Returns:
        Dictionary with domain-like structure but marked as read-only
    """
    api_dict = reference_card_to_api_dict(ref_card)
    
    # Add domain-like fields with default values
    api_dict.update({
        "is_owned": False,
        "quantity_owned": 0,
        "is_wanted": False,
        "added_at": None,
    })
    
    return api_dict


def create_readonly_domain_set(ref_set: MTGJsonSet) -> Dict[str, Any]:
    """
    Create a read-only domain set representation from a reference set.
    
    Args:
        ref_set: The reference set to convert
        
    Returns:
        Dictionary with domain-like structure but marked as read-only
    """
    api_dict = reference_set_to_api_dict(ref_set)
    
    # Add domain-like fields with default values
    api_dict.update({
        "added_at": None,
    })
    
    return api_dict


def create_readonly_domain_deck(ref_deck: MTGJsonDeck) -> Dict[str, Any]:
    """
    Create a read-only domain deck representation from a reference deck.
    
    Args:
        ref_deck: The reference deck to convert
        
    Returns:
        Dictionary with domain-like structure but marked as read-only
    """
    api_dict = reference_deck_to_api_dict(ref_deck)
    
    # Add domain-like fields with default values
    api_dict.update({
        "added_at": None,
    })
    
    return api_dict
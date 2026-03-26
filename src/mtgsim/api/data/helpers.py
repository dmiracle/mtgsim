"""Shared utilities for data access layer."""

import json


def build_image_url(scryfall_id: str | None) -> str | None:
    """Build Scryfall image URL from identifier."""
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg"


def parse_json_column(value: str | list | None, default=None) -> list:
    """Parse JSON column value (handles both string and list)."""
    if value is None:
        return default if default is not None else []
    if isinstance(value, list):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else []


def apply_card_filters(
    query,
    rarity: str | None = None,
    card_type: str | None = None,
    text: str | None = None,
    colors: list[str] | None = None,
    mana_values: list[int] | None = None,
    keywords: list[str] | None = None,
    tags: list[str] | None = None,
    owns: bool | None = None,
    wants: bool | None = None,
):
    """Apply common card filters to a query that joins MJCard and optionally UserCard."""
    from mtgdb.models import MJCard, MJCardTag, UserCard
    from sqlalchemy import exists
    from sqlalchemy import select as sa_select
    from sqlmodel import func

    if rarity:
        query = query.where(MJCard.rarity == rarity)
    if card_type:
        query = query.where(MJCard.type_line.contains(card_type))
    if text:
        query = query.where(MJCard.oracle_text.contains(text))
    if colors:
        from sqlalchemy import or_

        query = query.where(or_(*[func.json_extract(MJCard.color_identity, "$").contains(f'"{c}"') for c in colors]))
    if mana_values:
        from sqlalchemy import or_

        mv_conditions = []
        for mv in mana_values:
            if mv >= 7:
                mv_conditions.append(MJCard.mana_value >= 7)
            else:
                mv_conditions.append(MJCard.mana_value == mv)
        query = query.where(or_(*mv_conditions))
    if keywords:
        for kw in keywords:
            query = query.where(func.json_extract(MJCard.keywords, "$").contains(f'"{kw}"'))
    if tags:
        query = query.where(
            exists(sa_select(MJCardTag.id).where((MJCardTag.card_name == MJCard.name) & (MJCardTag.tag.in_(tags))))
        )
    if owns is True:
        query = query.where((UserCard.quantity_owned > 0) | (UserCard.quantity_owned_foil > 0))
    elif owns is False:
        query = query.where(
            (UserCard.id.is_(None)) | ((UserCard.quantity_owned == 0) & (UserCard.quantity_owned_foil == 0))
        )
    if wants is True:
        query = query.where((UserCard.quantity_wanted > 0) | (UserCard.quantity_wanted_foil > 0))
    elif wants is False:
        query = query.where(
            (UserCard.id.is_(None)) | ((UserCard.quantity_wanted == 0) & (UserCard.quantity_wanted_foil == 0))
        )
    return query


def apply_pagination(query, page: int, limit: int):
    """Apply pagination to query."""
    offset = (page - 1) * limit
    return query.offset(offset).limit(limit)


def add_price_join(query):
    """Add LEFT JOIN to MJCardPrice for TCGPlayer normal retail price.

    Returns (modified_query, price_column).
    """
    from mtgdb.models import MJCardPrice
    from sqlalchemy import case

    query = query.outerjoin(
        MJCardPrice,
        (MJCardPrice.card_uuid == MJCard_uuid_col())
        & (MJCardPrice.provider == "tcgplayer")
        & (MJCardPrice.finish == "normal")
        & (MJCardPrice.listing_type == "retail"),
    )
    price_col = case(
        (MJCardPrice.price.is_not(None), MJCardPrice.price),
        else_=None,
    ).label("best_price")
    return query, price_col


def MJCard_uuid_col():
    """Get MJCard.uuid column reference (avoids circular import)."""
    from mtgdb.models import MJCard

    return MJCard.uuid


def card_to_api_dict(
    mj_card,
    identifier=None,
    user_card=None,
    set_name: str | None = None,
    price: float | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Convert MJCard + optional joins to API response dict."""
    scryfall_id = identifier.scryfall_id if identifier else None

    # Collection status
    owns = False
    wants = False
    total_owned = 0
    total_wanted = 0
    collection = None

    if user_card:
        total_owned = (user_card.quantity_owned or 0) + (user_card.quantity_owned_foil or 0)
        total_wanted = (user_card.quantity_wanted or 0) + (user_card.quantity_wanted_foil or 0)
        owns = total_owned > 0
        wants = total_wanted > 0

        if owns or wants:
            collection = {
                "quantity_owned": user_card.quantity_owned,
                "quantity_owned_foil": user_card.quantity_owned_foil,
                "quantity_wanted": user_card.quantity_wanted,
                "quantity_wanted_foil": user_card.quantity_wanted_foil,
                "condition": user_card.condition,
                "notes": user_card.notes,
            }

    return {
        "uuid": mj_card.uuid,
        "name": mj_card.name,
        "mana_cost": mj_card.mana_cost,
        "mana_value": mj_card.mana_value,
        "type": mj_card.type_line,
        "types": mj_card.types or [],
        "subtypes": mj_card.subtypes or [],
        "supertypes": mj_card.supertypes or [],
        "oracle_text": mj_card.oracle_text,
        "flavor_text": mj_card.flavor_text,
        "power": mj_card.power,
        "toughness": mj_card.toughness,
        "loyalty": mj_card.loyalty,
        "defense": mj_card.defense,
        "colors": mj_card.colors or [],
        "color_identity": mj_card.color_identity or [],
        "keywords": mj_card.keywords or [],
        "rarity": mj_card.rarity,
        "set_code": mj_card.set_code,
        "set_name": set_name,
        "number": mj_card.number,
        "artist": mj_card.artist,
        "layout": mj_card.layout,
        "border_color": mj_card.border_color,
        "frame_version": mj_card.frame_version,
        "finishes": mj_card.finishes or [],
        "is_reprint": mj_card.is_reprint,
        "is_reserved": mj_card.is_reserved,
        "is_promo": mj_card.is_promo,
        "image_url": build_image_url(scryfall_id),
        "price": price,
        "owns": owns,
        "wants": wants,
        "total_owned": total_owned,
        "total_wanted": total_wanted,
        "tags": tags or [],
        "collection": collection,
    }


def set_to_api_dict(mj_set, collection_stats: dict | None = None) -> dict:
    """Convert MJSet to API response dict."""
    return {
        "code": mj_set.code,
        "name": mj_set.name,
        "type": mj_set.type,
        "release_date": mj_set.release_date,
        "base_set_size": mj_set.base_set_size,
        "total_set_size": mj_set.total_set_size,
        "block": mj_set.block,
        "parent_code": mj_set.parent_code,
        "keyrune_code": mj_set.keyrune_code,
        "is_foil_only": mj_set.is_foil_only,
        "is_online_only": mj_set.is_online_only,
        "is_partial_preview": mj_set.is_partial_preview,
        "collection_stats": collection_stats,
    }


def deck_to_api_dict(mj_deck, colors: list[str] | None = None, price: float | None = None) -> dict:
    """Convert MJDeck to API response dict."""
    return {
        "uuid": mj_deck.uuid,
        "file": mj_deck.file_name + ".json",
        "name": mj_deck.name,
        "code": mj_deck.code,
        "type": mj_deck.type,
        "release_date": mj_deck.release_date,
        "main_board_count": mj_deck.main_board_count,
        "side_board_count": mj_deck.side_board_count,
        "commander_count": mj_deck.commander_count,
        "card_count": mj_deck.main_board_count + mj_deck.side_board_count,
        "colors": colors or [],
        "price": price,
    }


def deck_card_to_api_dict(
    deck_card,
    owned_count: int = 0,
    image_url: str | None = None,
    price: float | None = None,
) -> dict:
    """Convert MJDeckCard to API response dict."""
    count = deck_card.count or 1
    owns_enough = owned_count >= count
    missing_count = max(0, count - owned_count)

    return {
        "card_uuid": deck_card.card_uuid,
        "name": deck_card.name,
        "count": count,
        "board": deck_card.board,
        "mana_cost": deck_card.mana_cost,
        "mana_value": deck_card.mana_value,
        "colors": deck_card.colors or [],
        "types": deck_card.types or [],
        "image_url": image_url,
        "price": price,
        "owns_enough": owns_enough,
        "owned_count": owned_count,
        "missing_count": missing_count,
    }

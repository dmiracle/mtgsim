"""Shared utilities for data access layer."""

import json
import logging
import re

from sqlalchemy import text

logger = logging.getLogger("mtgsim.api.data.helpers")


def build_image_url(scryfall_id: str | None) -> str | None:
    """Build Scryfall image URL from identifier."""
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg?v=1"


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


_FTS_OPERATORS = {"AND", "OR", "NOT"}
# Tokenize: quoted phrase | open-paren | close-paren | bare word (no parens / quotes / spaces).
# Greedy \S+ would glue `reach)` into a single token; the explicit class avoids that.
_FTS_TOKEN_RE = re.compile(r'"[^"]*"|\(|\)|[^\s()"]+')


def _escape_fts_query(q: str) -> str:
    """Translate a user query into a safe FTS5 MATCH expression.

    Passes through FTS5 boolean operators (AND / OR / NOT, case-insensitive),
    parentheses, quoted phrases, and a trailing ``*`` prefix operator. Every
    other bare token is wrapped in double quotes so punctuation (``-`` ``:``
    ``+`` ``^`` etc.) is treated as literal text instead of FTS5 syntax.
    Stray double quotes inside bare tokens are stripped.

    Examples (left = user input, right = emitted FTS5 expression)::

        flying lifelink              → "flying" "lifelink"
        flying OR lifelink           → "flying" OR "lifelink"
        flying NOT vigilance         → "flying" NOT "vigilance"
        "trigger an ability"         → "trigger an ability"
        (flying OR reach) AND lifelink → ( "flying" OR "reach" ) AND "lifelink"
        enchant*                     → "enchant"*
    """
    q = q.strip()
    if not q:
        return q
    out: list[str] = []
    for raw in _FTS_TOKEN_RE.findall(q):
        if raw in ("(", ")"):
            out.append(raw)
            continue
        if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
            out.append(raw)
            continue
        upper = raw.upper()
        if upper in _FTS_OPERATORS:
            out.append(upper)
            continue
        prefix = raw.endswith("*")
        word = raw[:-1] if prefix else raw
        word = word.replace('"', "")
        if not word:
            continue
        out.append(f'"{word}"*' if prefix else f'"{word}"')
    return " ".join(out)


def fts_search_uuids(session, column: str, query: str) -> list[str]:
    """Search the FTS5 index and return matching card UUIDs.

    Args:
        session: SQLAlchemy session (used to get the connection)
        column: FTS column to search ('name', 'printed_name', 'oracle_text', 'type_line')
        query: search text (will be escaped for FTS5 safety)

    Returns:
        List of matching card UUIDs.
    """
    escaped = _escape_fts_query(query)
    if not escaped:
        return []
    # Wrap in parens so the column filter binds to the whole boolean expression,
    # not just the first phrase/group inside it.
    fts_query = f"{column} : ({escaped})"
    result = session.exec(
        text("SELECT uuid FROM mj_card_fts WHERE mj_card_fts MATCH :q"),
        params={"q": fts_query},
    )
    return [row[0] for row in result]


def fts_name_search_uuids(session, query: str) -> list[str]:
    """Search FTS5 for card names (both name and printed_name columns)."""
    escaped = _escape_fts_query(query)
    if not escaped:
        return []
    fts_query = f"{{name printed_name}} : ({escaped})"
    result = session.exec(
        text("SELECT uuid FROM mj_card_fts WHERE mj_card_fts MATCH :q"),
        params={"q": fts_query},
    )
    return [row[0] for row in result]


def apply_card_filters(
    query,
    rarity: str | None = None,
    card_type: str | None = None,
    text: str | None = None,
    colors: list[str] | None = None,
    mana_values: list[int] | None = None,
    keywords: list[str] | None = None,
    tags: list[str] | None = None,
    user_tags: list[str] | None = None,
    tier_list_id: int | None = None,
    tiers: list[str] | None = None,
    owns: bool | None = None,
    wants: bool | None = None,
    owns_platform: str | None = None,
    session=None,
    *,
    mjcard=None,
    user_card=None,
):
    """Apply common card filters to a query that joins MJCard and optionally UserCard.

    Pass `mjcard` / `user_card` to bind filters to alias tables when reusing this
    helper inside a window/ranking subquery (so the canonical printing picked by
    `unique=true` respects every active filter, not just set/format).
    """
    from mtgdb.models import MJCard, MJCardTag, UserCard
    from sqlalchemy import exists
    from sqlalchemy import select as sa_select
    from sqlmodel import func

    M = mjcard if mjcard is not None else MJCard
    U = user_card if user_card is not None else UserCard

    if rarity:
        rarities = [r.strip() for r in rarity.split(",") if r.strip()]
        if len(rarities) == 1:
            query = query.where(M.rarity == rarities[0])
        elif rarities:
            query = query.where(M.rarity.in_(rarities))
    if card_type:
        from sqlalchemy import or_

        types = [t.strip() for t in card_type.split(",") if t.strip()]
        if len(types) == 1:
            query = query.where(M.type_line.contains(types[0]))
        elif types:
            query = query.where(or_(*[M.type_line.contains(t) for t in types]))
    if text:
        if session:
            uuids = fts_search_uuids(session, "oracle_text", text)
            query = query.where(M.uuid.in_(uuids))
        else:
            query = query.where(M.oracle_text.contains(text))
    if colors:
        from sqlalchemy import and_, or_

        has_multicolor = "M" in colors
        has_colorless = "C" in colors
        wubrg = [c for c in colors if c in "WUBRG"]

        clauses = []
        if has_multicolor:
            # Gold: multicolor cards (2+ colors) that include every selected color.
            conditions = [func.json_array_length(M.color_identity) >= 2]
            for c in wubrg:
                conditions.append(func.json_extract(M.color_identity, "$").contains(f'"{c}"'))
            clauses.append(and_(*conditions))
        elif wubrg:
            # Plain colors (no gold): only mono-colored cards of a selected color.
            clauses.append(
                and_(
                    func.json_array_length(M.color_identity) == 1,
                    or_(*[func.json_extract(M.color_identity, "$").contains(f'"{c}"') for c in wubrg]),
                )
            )
        if has_colorless:
            clauses.append(func.json_array_length(M.color_identity) == 0)
        if clauses:
            query = query.where(or_(*clauses))
    if mana_values:
        from sqlalchemy import or_

        mv_conditions = []
        for mv in mana_values:
            if mv >= 7:
                mv_conditions.append(M.mana_value >= 7)
            else:
                mv_conditions.append(M.mana_value == mv)
        query = query.where(or_(*mv_conditions))
    if keywords:
        for kw in keywords:
            query = query.where(func.json_extract(M.keywords, "$").contains(f'"{kw}"'))
    if tags:
        query = query.where(
            exists(sa_select(MJCardTag.id).where((MJCardTag.card_name == M.name) & (MJCardTag.tag.in_(tags))))
        )
    if user_tags:
        from mtgdb.models import UserCardTag

        normalized = [normalize_user_tag(t) for t in user_tags]
        query = query.where(
            exists(
                sa_select(UserCardTag.id).where((UserCardTag.card_name == M.name) & (UserCardTag.tag.in_(normalized)))
            )
        )
    if tier_list_id is not None:
        from mtgdb.models import UserTierListEntry

        conditions = [UserTierListEntry.card_name == M.name, UserTierListEntry.tier_list_id == tier_list_id]
        if tiers:
            conditions.append(UserTierListEntry.tier.in_(tiers))
        # correlate only the card table: the outer query may join the entries
        # table itself for tier sorting, which would otherwise auto-correlate
        # this subquery into having no FROM clause
        query = query.where(exists(sa_select(UserTierListEntry.id).where(*conditions).correlate(M)))
    if owns is True:
        query = query.where(
            (U.quantity_owned > 0)
            | (U.quantity_owned_foil > 0)
            | (U.quantity_owned_mtga > 0)
            | (U.quantity_owned_mtga_foil > 0)
        )
    elif owns is False:
        query = query.where(
            (U.id.is_(None))
            | (
                (U.quantity_owned == 0)
                & (U.quantity_owned_foil == 0)
                & (U.quantity_owned_mtga == 0)
                & (U.quantity_owned_mtga_foil == 0)
            )
        )
    if owns_platform == "paper":
        query = query.where((U.quantity_owned > 0) | (U.quantity_owned_foil > 0))
    elif owns_platform == "mtga":
        query = query.where((U.quantity_owned_mtga > 0) | (U.quantity_owned_mtga_foil > 0))
    if wants is True:
        query = query.where((U.quantity_wanted > 0) | (U.quantity_wanted_foil > 0))
    elif wants is False:
        query = query.where((U.id.is_(None)) | ((U.quantity_wanted == 0) & (U.quantity_wanted_foil == 0)))
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
        total_owned = (
            (user_card.quantity_owned or 0)
            + (user_card.quantity_owned_foil or 0)
            + (user_card.quantity_owned_mtga or 0)
            + (user_card.quantity_owned_mtga_foil or 0)
        )
        total_wanted = (user_card.quantity_wanted or 0) + (user_card.quantity_wanted_foil or 0)
        owns = total_owned > 0
        wants = total_wanted > 0

        if owns or wants:
            collection = {
                "quantity_owned": user_card.quantity_owned,
                "quantity_owned_foil": user_card.quantity_owned_foil,
                "quantity_owned_mtga": user_card.quantity_owned_mtga,
                "quantity_owned_mtga_foil": user_card.quantity_owned_mtga_foil,
                "quantity_wanted": user_card.quantity_wanted,
                "quantity_wanted_foil": user_card.quantity_wanted_foil,
                "condition": user_card.condition,
                "notes": user_card.notes,
            }

    return {
        "uuid": mj_card.uuid,
        "name": mj_card.printed_name or mj_card.name,
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


RARITY_RANK = {"common": 0, "uncommon": 1, "rare": 2, "mythic": 3}


def rarity_order():
    """CASE expression ranking rarity common < uncommon < rare < mythic < other."""
    from mtgdb.models import MJCard
    from sqlalchemy import case

    return case(RARITY_RANK, value=MJCard.rarity, else_=len(RARITY_RANK))


def canonical_card_name(session, name: str) -> str | None:
    """Resolve user input to the exact MJCard.name, or None if no such card.

    Accepts the full name, a case-insensitive match, or a single face of an
    "A // B" multi-face card (no face_name column exists; match by pattern).
    """
    from mtgdb.models import MJCard
    from sqlmodel import select

    exact = session.exec(select(MJCard.name).where(MJCard.name == name).limit(1)).first()
    if exact:
        return exact
    from sqlalchemy import func as safunc

    lowered = name.strip().lower()
    if not lowered:
        return None
    fuzzy = session.exec(
        select(MJCard.name)
        .where(
            (safunc.lower(MJCard.name) == lowered)
            | safunc.lower(MJCard.name).like(f"{lowered} //%")
            | safunc.lower(MJCard.name).like(f"%// {lowered}")
        )
        .limit(1)
    ).first()
    return fuzzy


def resolve_default_printing(session, card_name: str) -> dict | None:
    """Card summary for a name, preferring the generic (default-booster) printing."""
    from mtgdb.models import MJCard, MJCardIdentifier
    from sqlalchemy import case
    from sqlmodel import select

    row = session.exec(
        select(MJCard, MJCardIdentifier)
        .outerjoin(MJCardIdentifier, MJCardIdentifier.card_uuid == MJCard.uuid)
        .where(MJCard.name == card_name)
        .order_by(
            MJCard.is_default_printing.desc(),
            case({"English": 0}, value=MJCard.language, else_=1),
            MJCard.uuid.asc(),
        )
        .limit(1)
    ).first()
    if not row:
        return None
    card, ident = row
    return {
        "uuid": card.uuid,
        "name": card.name,
        "type_line": card.type_line,
        "mana_cost": card.mana_cost,
        "set_code": card.set_code,
        "image_url": build_image_url(ident.scryfall_id if ident else None),
    }


def normalize_user_tag(tag: str) -> str:
    """Normalize a user tag: strip, collapse inner whitespace, lowercase."""
    return " ".join(tag.split()).lower()

"""MTGA deck format parser and importer.

Parses MTG Arena deck export format:
    Deck
    <count> <card name> (<set code>) <collector number>
    ...

    Sideboard
    <count> <card name> (<set code>) <collector number>
    ...
"""

import re
import uuid as uuid_lib

from mtgdb.models import MJCard, MJCardLegality
from mtgdb.session import get_session
from pydantic import BaseModel
from rapidfuzz import fuzz, process
from sqlmodel import select


class ParsedCard(BaseModel):
    count: int
    name: str
    set_code: str
    number: str
    board: str  # "main" or "side"


class ResolvedCard(BaseModel):
    count: int
    name: str
    set_code: str
    number: str
    board: str
    card_uuid: str
    match_type: str = "exact"  # "exact", "fuzzy", "created"
    matched_name: str | None = None  # name it fuzzy-matched to
    match_score: float | None = None


class DeckLegalityResult(BaseModel):
    """Per-format legality with reasons for illegality."""

    format: str
    legal: bool
    reason: str | None = None


class ImportResult(BaseModel):
    deck_id: int
    deck_name: str
    resolved: list[ResolvedCard] = []
    total_cards: int = 0
    legality: list[DeckLegalityResult] = []


# Full MTGA format: "4 Lightning Bolt (2ED) 162"
LINE_PATTERN_FULL = re.compile(r"^(\d+)\s+(.+?)\s+\((\w+)\)\s+(\S+)$")
# Simple format: "4 Lightning Bolt"
LINE_PATTERN_SIMPLE = re.compile(r"^(\d+)\s+(.+)$")

# Formats we care about checking
CHECKED_FORMATS = [
    "standard",
    "pioneer",
    "modern",
    "legacy",
    "vintage",
    "commander",
    "pauper",
    "historic",
    "brawl",
]

# Min deck sizes by format
MIN_DECK_SIZE = {
    "commander": 100,
    "brawl": 60,
}
DEFAULT_MIN_DECK_SIZE = 60

# Max copies per card (basic lands exempt)
MAX_COPIES = {
    "commander": 1,
}
DEFAULT_MAX_COPIES = 4

BASIC_LAND_NAMES = {"Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"}

FUZZY_THRESHOLD = 92


class MatchResult(BaseModel):
    """Result of matching a card name against the database."""

    uuid: str | None = None
    match_type: str = "none"  # "exact", "fuzzy", "none"
    matched_name: str | None = None
    score: float | None = None


def match_card_by_name(
    name: str,
    name_index: dict[str, str],
    name_list: list[str] | None = None,
    threshold: int = FUZZY_THRESHOLD,
) -> MatchResult:
    """Match a card name against a name index with exact then fuzzy matching.

    Args:
        name: The card name to look up.
        name_index: Mapping of card name -> uuid.
        name_list: Pre-computed list of name_index keys (for fuzzy search performance).
            Built from name_index.keys() if not provided.
        threshold: Minimum fuzzy match score (0-100). Default 92.

    Returns:
        MatchResult with uuid, match_type, matched_name, and score.
    """
    # Exact match
    if name in name_index:
        return MatchResult(uuid=name_index[name], match_type="exact", matched_name=name, score=100.0)

    # Fuzzy match
    if name_list is None:
        name_list = list(name_index.keys())

    result = process.extractOne(
        name,
        name_list,
        scorer=fuzz.WRatio,
        score_cutoff=threshold,
    )
    if result:
        best_name, score, _ = result
        return MatchResult(uuid=name_index[best_name], match_type="fuzzy", matched_name=best_name, score=score)

    return MatchResult()


def parse_mtga_deck(text: str) -> list[ParsedCard]:
    """Parse MTGA deck text into a list of ParsedCard entries."""
    cards = []
    board = "main"

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower() in ("deck", "companion", "commander", "about"):
            board = "main"
            continue
        if line.lower() == "sideboard":
            board = "side"
            continue
        if line.lower().startswith("name "):
            continue

        match = LINE_PATTERN_FULL.match(line)
        if match:
            count, name, set_code, number = match.groups()
            cards.append(
                ParsedCard(
                    count=int(count),
                    name=name,
                    set_code=set_code.lower(),
                    number=number,
                    board=board,
                )
            )
            continue

        match = LINE_PATTERN_SIMPLE.match(line)
        if match:
            count, name = match.groups()
            cards.append(
                ParsedCard(
                    count=int(count),
                    name=name.strip(),
                    set_code="",
                    number="",
                    board=board,
                )
            )

    return cards


def _load_card_name_index(session) -> dict[str, str]:
    """Load a name->uuid index for all cards. One entry per unique name.

    Indexes both the Oracle name and printed_name so imports using either
    version (e.g. Marvel IP name or real card name) resolve correctly.
    """
    rows = session.exec(select(MJCard.name, MJCard.printed_name, MJCard.uuid)).all()
    index = {}
    for name, printed_name, card_uuid in rows:
        if name not in index:
            index[name] = card_uuid
        if printed_name and printed_name not in index:
            index[printed_name] = card_uuid
    return index


def _create_placeholder_card(session, name: str, set_code: str, number: str) -> str:
    """Create a minimal placeholder MJCard and return its uuid."""
    card_uuid = str(uuid_lib.uuid5(uuid_lib.NAMESPACE_URL, f"placeholder:{name}"))
    existing = session.exec(select(MJCard.uuid).where(MJCard.uuid == card_uuid)).first()
    if existing:
        return existing
    card = MJCard(
        uuid=card_uuid,
        name=name,
        set_code=set_code or "unknown",
        number=number or "",
    )
    session.add(card)
    session.flush()
    return card_uuid


def resolve_cards(parsed: list[ParsedCard]) -> list[ResolvedCard]:
    """Resolve parsed cards to UUIDs: exact -> fuzzy -> create placeholder."""
    resolved = []

    with get_session() as session:
        name_index = _load_card_name_index(session)
        name_list = list(name_index.keys())

        for card in parsed:
            uuid = None
            match_type = "exact"
            matched_name = None
            match_score = None

            # 1. Exact match by set_code + number
            if card.set_code and card.number:
                query = select(MJCard.uuid).where(
                    MJCard.set_code == card.set_code,
                    MJCard.number == card.number,
                )
                uuid = session.exec(query).first()

            # 2. Exact match by name + set_code
            if not uuid and card.set_code:
                query = select(MJCard.uuid).where(
                    MJCard.name == card.name,
                    MJCard.set_code == card.set_code,
                )
                uuid = session.exec(query).first()

            # 3 & 4. Exact or fuzzy match by name
            if not uuid:
                mr = match_card_by_name(card.name, name_index, name_list)
                if mr.uuid:
                    uuid = mr.uuid
                    match_type = mr.match_type
                    matched_name = mr.matched_name
                    match_score = mr.score

            # 5. Create placeholder card
            if not uuid:
                uuid = _create_placeholder_card(session, card.name, card.set_code, card.number)
                match_type = "created"

            resolved.append(
                ResolvedCard(
                    count=card.count,
                    name=card.name,
                    set_code=card.set_code,
                    number=card.number,
                    board=card.board,
                    card_uuid=uuid,
                    match_type=match_type,
                    matched_name=matched_name,
                    match_score=match_score,
                )
            )

        session.commit()

    return resolved


def check_deck_legality(resolved: list[ResolvedCard]) -> list[DeckLegalityResult]:
    """Check which formats this deck is legal in."""
    if not resolved:
        return []

    card_uuids = list({c.card_uuid for c in resolved})
    main_cards = [c for c in resolved if c.board == "main"]
    main_total = sum(c.count for c in main_cards)

    # Fetch legalities for all cards in one query
    with get_session() as session:
        query = select(MJCardLegality).where(MJCardLegality.card_uuid.in_(card_uuids))
        rows = session.exec(query).all()

    # Build map: card_uuid -> {format: status}
    card_legalities: dict[str, dict[str, str]] = {}
    for row in rows:
        card_legalities.setdefault(row.card_uuid, {})[row.format] = row.status

    results = []
    for fmt in CHECKED_FORMATS:
        reason = _check_format(fmt, resolved, main_total, card_legalities)
        results.append(
            DeckLegalityResult(
                format=fmt,
                legal=reason is None,
                reason=reason,
            )
        )

    return results


def _check_format(
    fmt: str,
    resolved: list[ResolvedCard],
    main_total: int,
    card_legalities: dict[str, dict[str, str]],
) -> str | None:
    """Return None if legal, or a reason string if not."""
    min_size = MIN_DECK_SIZE.get(fmt, DEFAULT_MIN_DECK_SIZE)
    if main_total < min_size:
        return f"Main deck has {main_total} cards, minimum {min_size}"

    max_copies = MAX_COPIES.get(fmt, DEFAULT_MAX_COPIES)

    banned = []
    not_legal = []
    too_many = []

    name_counts: dict[str, int] = {}
    for card in resolved:
        if card.board == "main":
            name_counts[card.name] = name_counts.get(card.name, 0) + card.count

    for card in resolved:
        statuses = card_legalities.get(card.card_uuid, {})
        status = statuses.get(fmt)

        if status == "Banned":
            banned.append(card.name)
        elif status != "Legal" and status != "Restricted":
            not_legal.append(card.name)

    for name, count in name_counts.items():
        if name not in BASIC_LAND_NAMES and count > max_copies:
            too_many.append(f"{name} x{count}")

    parts = []
    if banned:
        parts.append(f"Banned: {', '.join(sorted(set(banned)))}")
    if not_legal:
        parts.append(f"Not legal: {', '.join(sorted(set(not_legal)))}")
    if too_many:
        parts.append(f"Too many copies: {', '.join(sorted(set(too_many)))}")

    return "; ".join(parts) if parts else None


def import_mtga_deck(text: str, name: str) -> ImportResult:
    """Parse MTGA deck text, resolve cards, create deck, and check legality."""
    from mtgsim.api.data import decks_data

    parsed = parse_mtga_deck(text)
    resolved = resolve_cards(parsed)
    legality = check_deck_legality(resolved)

    # Auto-detect format: first legal format in priority order
    detected_format = None
    for lr in legality:
        if lr.legal:
            detected_format = lr.format
            break

    deck = decks_data.create_user_deck(name=name, format=detected_format, source="import")
    deck_id = deck["id"]

    for card in resolved:
        decks_data.add_card_to_deck(
            deck_id=deck_id,
            card_uuid=card.card_uuid,
            count=card.count,
            board=card.board,
        )

    return ImportResult(
        deck_id=deck_id,
        deck_name=name,
        resolved=resolved,
        total_cards=sum(c.count for c in parsed),
        legality=legality,
    )

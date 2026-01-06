"""Centralized row-to-model mappers for API responses."""

from sqlite3 import Row

from mtgsim.api.models.card import (
    CardAppearance,
    CardDetail,
    CardLegalities,
    CardPrinting,
    CardSummary,
)
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.deck import (
    DeckCard,
    DeckLegality,
    DeckSummary,
    PriceBySource,
)
from mtgsim.reference.db import get_scryfall_image_url, parse_json, parse_json_dict


def map_card_summary(row: dict | Row, price: float | None = None) -> CardSummary:
    """Map a database row to CardSummary model."""
    return CardSummary(
        uuid=row["uuid"],
        name=row["name"],
        type=row.get("type"),
        mana_cost=row.get("mana_cost"),
        mana_value=row.get("mana_value") or 0,
        rarity=row.get("rarity"),
        set_code=row.get("set_code"),
        color_identity=parse_json(row.get("color_identity")),
        text=row.get("text"),
        price=price or row.get("price"),
        image_url=get_scryfall_image_url(row.get("identifiers"), "large"),
    )


def map_card_detail(
    row: dict | Row,
    set_name: str | None = None,
    prices: PriceBySource | None = None,
    appearances: list[dict] | None = None,
    printings: list[dict] | None = None,
) -> CardDetail:
    """Map a database row to CardDetail model."""
    legalities = parse_json_dict(row.get("legalities"))

    return CardDetail(
        uuid=row["uuid"],
        name=row["name"],
        mana_cost=row.get("mana_cost"),
        mana_value=row.get("mana_value") or 0,
        type=row.get("type"),
        types=parse_json(row.get("types")),
        subtypes=parse_json(row.get("subtypes")),
        text=row.get("text"),
        flavor_text=row.get("flavor_text"),
        rarity=row.get("rarity"),
        set_code=row.get("set_code"),
        set_name=set_name,
        color_identity=parse_json(row.get("color_identity")),
        colors=parse_json(row.get("colors")),
        power=row.get("power"),
        toughness=row.get("toughness"),
        image_url=get_scryfall_image_url(row.get("identifiers"), "large"),
        prices=prices or PriceBySource(),
        legalities=CardLegalities(
            standard=legalities.get("standard", "Not Legal"),
            pioneer=legalities.get("pioneer", "Not Legal"),
            modern=legalities.get("modern", "Not Legal"),
            legacy=legalities.get("legacy", "Not Legal"),
            vintage=legalities.get("vintage", "Not Legal"),
            commander=legalities.get("commander", "Not Legal"),
            brawl=legalities.get("brawl", "Not Legal"),
            historic=legalities.get("historic", "Not Legal"),
            pauper=legalities.get("pauper", "Not Legal"),
        ),
        appears_in_decks=[
            CardAppearance(file=a["file"], name=a["name"], count=a["count"]) for a in (appearances or [])
        ],
        other_printings=[
            CardPrinting(set_code=p["set_code"], set_name=p["set_name"] or "", uuid=p["uuid"])
            for p in (printings or [])
        ],
    )


def map_card_printing(row: dict | Row, set_name: str | None = None) -> CardPrinting:
    """Map a database row to CardPrinting model."""
    return CardPrinting(
        uuid=row["uuid"],
        set_code=row["set_code"],
        set_name=set_name or "",
    )


def map_deck_summary(
    row: dict | Row,
    card_count: int = 0,
    colors: list[str] | None = None,
    price: float | None = None,
    legality: DeckLegality | None = None,
) -> DeckSummary:
    """Map a database row to DeckSummary model."""
    return DeckSummary(
        file=row["file_name"] + ".json",
        name=row["name"],
        code=row["code"],
        card_count=card_count,
        colors=colors or [],
        price=price,
        release_date=row.get("release_date"),
        legality=legality or DeckLegality(),
    )


def map_deck_card(row: dict | Row, price: float | None = None, image_url: str | None = None) -> DeckCard:
    """Map a database row to DeckCard model."""
    return DeckCard(
        uuid=row.get("card_uuid") or row.get("uuid") or "",
        name=row.get("name") or "",
        count=row.get("count") or 1,
        mana_cost=row.get("mana_cost"),
        mana_value=row.get("mana_value") or 0,
        type=row.get("type"),
        rarity=row.get("rarity"),
        text=row.get("text"),
        price=price,
        image_url=image_url,
    )


def map_deck_legality(legalities: dict) -> DeckLegality:
    """Map legalities dict to DeckLegality model."""
    return DeckLegality(
        standard=legalities.get("standard") == "Legal",
        pioneer=legalities.get("pioneer") == "Legal",
        modern=legalities.get("modern") == "Legal",
        legacy=legalities.get("legacy") == "Legal",
        vintage=legalities.get("vintage") == "Legal",
        commander=legalities.get("commander") == "Legal",
        brawl=legalities.get("brawl") == "Legal",
        historic=legalities.get("historic") == "Legal",
        pauper=legalities.get("pauper") == "Legal",
    )


def map_pagination(page: int, limit: int, total: int) -> Pagination:
    """Create Pagination model from parameters."""
    pages = (total + limit - 1) // limit if limit > 0 else 0
    return Pagination(page=page, limit=limit, total=total, pages=pages)

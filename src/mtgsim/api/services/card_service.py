"""Card service - handles card data access and processing."""

import logging

from mtgsim.api.data import cards_data
from mtgsim.api.models.card import (
    CardAppearance,
    CardDetail,
    CardListResponse,
    CardPriceEntry,
    CardPrinting,
    CardSummary,
    QuadrantRating,
)
from mtgsim.api.models.common import CollectionDetail, Pagination

logger = logging.getLogger("mtgsim.api.services.card")


class CardService:
    """Service for card-related operations."""

    async def search_cards(
        self,
        q: str | None = None,
        text: str | None = None,
        set_code: str | None = None,
        set_codes: list[str] | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        mana_values: list[int] | None = None,
        format_legal: str | None = None,
        keywords: list[str] | None = None,
        tags: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
        owns: bool | None = None,
        wants: bool | None = None,
        unique: bool = False,
        price_mode: str = "min",
    ) -> CardListResponse:
        """Search cards with filters."""
        logger.debug(
            f"search_cards: q={q} text={text} set_code={set_code} format={format_legal} sort={sort} page={page}"
        )
        cards, total = cards_data.search_cards(
            q=q,
            text=text,
            set_code=set_code,
            set_codes=set_codes,
            rarity=rarity,
            card_type=card_type,
            colors=colors,
            mana_values=mana_values,
            format_legal=format_legal,
            keywords=keywords,
            tags=tags,
            price_min=price_min,
            price_max=price_max,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
            owns=owns,
            wants=wants,
            unique=unique,
            price_mode=price_mode,
        )

        logger.debug(f"search_cards: got {len(cards)} cards, total={total}")
        data = []
        for c in cards:
            data.append(
                CardSummary(
                    uuid=c["uuid"],
                    name=c["name"],
                    type=c.get("type", ""),
                    mana_cost=c.get("mana_cost"),
                    mana_value=c.get("mana_value"),
                    rarity=c.get("rarity", ""),
                    set_code=c.get("set_code", ""),
                    color_identity=c.get("color_identity", []),
                    tags=c.get("tags", []),
                    text=c.get("oracle_text"),
                    price=c.get("price"),
                    image_url=c.get("image_url"),
                    owns=c.get("owns", False),
                    wants=c.get("wants", False),
                    total_owned=c.get("total_owned", 0),
                    total_wanted=c.get("total_wanted", 0),
                )
            )

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return CardListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def get_card(self, uuid: str) -> CardDetail | None:
        """Get full card details."""
        logger.debug(f"get_card: uuid={uuid}")
        card = cards_data.get_card(uuid)
        if not card:
            return None

        # Get appearances in decks
        appearances = cards_data.get_card_appearances(uuid)

        # Get other printings
        other_printings = cards_data.get_other_printings(uuid)

        # Build collection detail if card is in collection
        collection_detail = None
        collection_data = card.get("collection")
        if collection_data:
            collection_detail = CollectionDetail(
                quantity_owned=collection_data.get("quantity_owned", 0),
                quantity_owned_foil=collection_data.get("quantity_owned_foil", 0),
                quantity_wanted=collection_data.get("quantity_wanted", 0),
                quantity_wanted_foil=collection_data.get("quantity_wanted_foil", 0),
                condition=collection_data.get("condition"),
                notes=collection_data.get("notes"),
            )

        return CardDetail(
            uuid=card["uuid"],
            name=card["name"],
            mana_cost=card.get("mana_cost"),
            mana_value=card.get("mana_value"),
            type=card.get("type", ""),
            types=card.get("types", []),
            subtypes=card.get("subtypes", []),
            supertypes=card.get("supertypes", []),
            text=card.get("oracle_text", ""),
            flavor_text=card.get("flavor_text", ""),
            rarity=card.get("rarity", ""),
            set_code=card.get("set_code", ""),
            set_name=card.get("set_name") or "",
            color_identity=card.get("color_identity", []),
            colors=card.get("colors", []),
            keywords=card.get("keywords", []),
            tags=card.get("tags", []),
            power=card.get("power"),
            toughness=card.get("toughness"),
            loyalty=card.get("loyalty"),
            defense=card.get("defense"),
            artist=card.get("artist"),
            number=card.get("number"),
            layout=card.get("layout"),
            finishes=card.get("finishes", []),
            border_color=card.get("border_color"),
            frame_version=card.get("frame_version"),
            is_reprint=card.get("is_reprint", False),
            is_reserved=card.get("is_reserved", False),
            is_promo=card.get("is_promo", False),
            image_url=card.get("image_url"),
            legalities=card.get("legalities", {}),
            all_prices=[CardPriceEntry(**p) for p in card.get("all_prices", [])],
            appears_in_decks=[CardAppearance(file=a["file"], name=a["name"], count=a["count"]) for a in appearances],
            other_printings=[
                CardPrinting(
                    set_code=p["set_code"],
                    set_name=p.get("set_name") or "",
                    uuid=p["uuid"],
                    rarity=p.get("rarity"),
                    number=p.get("number"),
                    image_url=p.get("image_url"),
                    price=p.get("price"),
                    owns=p.get("owns", False),
                    total_owned=p.get("total_owned", 0),
                )
                for p in other_printings
            ],
            owns=card.get("owns", False),
            wants=card.get("wants", False),
            total_owned=card.get("total_owned", 0),
            total_wanted=card.get("total_wanted", 0),
            collection=collection_detail,
            quadrant_rating=QuadrantRating(**card["quadrant_rating"]) if card.get("quadrant_rating") else None,
        )

    async def get_card_by_name(self, name: str) -> list[CardSummary]:
        """Get all printings of a card by name."""
        cards = cards_data.get_cards_by_name(name)
        return [
            CardSummary(
                uuid=c["uuid"],
                name=c["name"],
                type=c.get("type", ""),
                mana_cost=c.get("mana_cost"),
                mana_value=c.get("mana_value"),
                rarity=c.get("rarity", ""),
                set_code=c.get("set_code", ""),
                color_identity=c.get("color_identity", []),
                image_url=c.get("image_url"),
                owns=c.get("owns", False),
                wants=c.get("wants", False),
                total_owned=c.get("total_owned", 0),
                total_wanted=c.get("total_wanted", 0),
            )
            for c in cards
        ]

    async def add_card_to_collection(
        self,
        card_uuid: str,
        quantity_owned: int = 1,
        quantity_owned_foil: int = 0,
        quantity_wanted: int = 0,
        quantity_wanted_foil: int = 0,
    ) -> dict:
        """Add a card to user's collection."""
        result = cards_data.add_to_collection(
            card_uuid=card_uuid,
            quantity_owned=quantity_owned,
            quantity_owned_foil=quantity_owned_foil,
            quantity_wanted=quantity_wanted,
            quantity_wanted_foil=quantity_wanted_foil,
        )

        if result:
            return {"success": True, "message": f"Card {card_uuid} added to collection", "card": result}
        else:
            return {"success": False, "message": f"Card {card_uuid} not found", "card": None}

    async def remove_card_from_collection(self, card_uuid: str) -> dict:
        """Remove a card from user's collection."""
        success = cards_data.remove_from_collection(card_uuid)

        if success:
            return {"success": True, "message": f"Card {card_uuid} removed from collection"}
        else:
            return {"success": False, "message": f"Card {card_uuid} not found in collection"}

    async def get_collection_stats(self) -> dict:
        """Get collection statistics."""
        return cards_data.get_collection_stats()


# Singleton instance
card_service = CardService()

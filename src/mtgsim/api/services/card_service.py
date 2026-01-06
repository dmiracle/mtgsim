"""Card service - handles card data access and processing."""

from mtgsim.api.data import cards_data, prices_data
from mtgsim.api.models.card import (
    CardAppearance,
    CardDetail,
    CardLegalities,
    CardListResponse,
    CardPrinting,
    CardSummary,
)
from mtgsim.api.models.common import Pagination
from mtgsim.api.models.deck import PriceBySource


class CardService:
    """Service for card-related operations."""

    async def search_cards(
        self,
        q: str | None = None,
        set_code: str | None = None,
        rarity: str | None = None,
        card_type: str | None = None,
        colors: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> CardListResponse:
        """Search cards with filters."""
        cards, total = cards_data.search_cards(
            q=q,
            set_code=set_code,
            rarity=rarity,
            card_type=card_type,
            colors=colors,
            sort=sort,
            order=order,
            page=page,
            limit=limit,
        )

        data = [
            CardSummary(
                uuid=c["uuid"],
                name=c["name"],
                type=c["type"],
                mana_cost=c["mana_cost"],
                mana_value=c["mana_value"],
                rarity=c["rarity"],
                set_code=c["set_code"],
                color_identity=c["color_identity"],
                text=c.get("text"),
                price=c.get("price"),
                image_url=c.get("image_url"),
            )
            for c in cards
        ]

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return CardListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def get_card(self, uuid: str) -> CardDetail | None:
        """Get full card details."""
        card = cards_data.get_card(uuid)
        if not card:
            return None

        # Get legalities
        legalities = card.get("legalities", {})

        # Get prices
        prices_data.get_average_price(uuid)
        tcg_price = prices_data.get_tcgplayer_price(uuid)

        # Get appearances in decks
        appearances = cards_data.get_card_appearances(uuid)

        # Get other printings
        other_printings = cards_data.get_other_printings(uuid)

        return CardDetail(
            uuid=card["uuid"],
            name=card["name"],
            mana_cost=card["mana_cost"],
            mana_value=card["mana_value"],
            type=card["type"],
            types=card["types"],
            subtypes=card["subtypes"],
            text=card["text"],
            flavor_text=card["flavor_text"],
            rarity=card["rarity"],
            set_code=card["set_code"],
            set_name=card["set_name"],
            color_identity=card["color_identity"],
            colors=card["colors"],
            power=card["power"],
            toughness=card["toughness"],
            image_url=card.get("image_url"),
            prices=PriceBySource(
                tcgplayer=tcg_price,
            ),
            legalities=CardLegalities(
                standard=legalities.get("standard", "Not Legal"),
                pioneer=legalities.get("pioneer", "Not Legal"),
                modern=legalities.get("modern", "Not Legal"),
                legacy=legalities.get("legacy", "Not Legal"),
                vintage=legalities.get("vintage", "Not Legal"),
                commander=legalities.get("commander", "Not Legal"),
            ),
            appears_in_decks=[
                CardAppearance(
                    file=a["file"],
                    name=a["name"],
                    count=a["count"],
                )
                for a in appearances
            ],
            other_printings=[
                CardPrinting(
                    set_code=p["set_code"],
                    set_name=p["set_name"],
                    uuid=p["uuid"],
                )
                for p in other_printings
            ],
        )

    async def get_card_by_name(self, name: str) -> list[CardSummary]:
        """Get all printings of a card by name."""
        cards = cards_data.get_cards_by_name(name)
        return [
            CardSummary(
                uuid=c["uuid"],
                name=c["name"],
                type="",
                mana_cost=None,
                mana_value=None,
                rarity=c["rarity"],
                set_code=c["set_code"],
                color_identity=[],
                price=None,
                image_url=None,
            )
            for c in cards
        ]

    async def get_cards_in_deck(self, deck_file: str) -> list[str]:
        """Get all card UUIDs in a deck."""
        return []


# Singleton instance
card_service = CardService()

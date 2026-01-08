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
        scope: str = "combined",  # "user", "reference", "combined"
    ) -> CardListResponse:
        """Search cards with filters and scope control."""
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
            scope=scope,
        )

        data = []
        for c in cards:
            # Handle both domain and reference card formats
            data.append(
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
                    in_collection=c.get("in_collection", scope == "user"),
                )
            )

        pages = (total + limit - 1) // limit if limit > 0 else 1

        return CardListResponse(
            data=data,
            pagination=Pagination(page=page, limit=limit, total=total, pages=pages),
        )

    async def get_card(self, uuid: str, scope: str = "combined") -> CardDetail | None:
        """Get full card details with scope control."""
        card = cards_data.get_card(uuid, scope=scope)
        if not card:
            return None

        # Get legalities
        legalities = card.get("legalities", {})

        # Get prices (only available for domain cards)
        tcg_price = None
        if card.get("in_collection", scope == "user"):
            prices_data.get_average_price(uuid)
            tcg_price = prices_data.get_tcgplayer_price(uuid)

        # Get appearances in decks
        appearances = cards_data.get_card_appearances(uuid)

        # Get other printings
        other_printings = cards_data.get_other_printings(uuid, scope="combined")

        return CardDetail(
            uuid=card["uuid"],
            name=card["name"],
            mana_cost=card["mana_cost"],
            mana_value=card["mana_value"],
            type=card["type"],
            types=card.get("types", []),
            subtypes=card.get("subtypes", []),
            text=card.get("text", ""),
            flavor_text=card.get("flavor_text", ""),
            rarity=card["rarity"],
            set_code=card["set_code"],
            set_name=card.get("set_name", ""),
            color_identity=card["color_identity"],
            colors=card.get("colors", []),
            power=card.get("power"),
            toughness=card.get("toughness"),
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
                    in_collection=p.get("in_collection", False),
                )
                for p in other_printings
            ],
            in_collection=card.get("in_collection", scope == "user"),
        )

    async def get_card_by_name(self, name: str, scope: str = "combined") -> list[CardSummary]:
        """Get all printings of a card by name with scope control."""
        cards = cards_data.get_cards_by_name(name, scope=scope)
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
                in_collection=c.get("in_collection", scope == "user"),
            )
            for c in cards
        ]

    async def add_card_to_collection(self, card_uuid: str) -> dict:
        """Add a card from reference tables to user's domain tables."""
        from mtgsim.cli.domain_commands import add_card_to_domain

        try:
            result = add_card_to_domain(card_uuid)
            return {"success": True, "message": f"Card {card_uuid} added to collection", "card": result}
        except Exception as e:
            return {"success": False, "message": f"Failed to add card: {str(e)}", "card": None}

    async def remove_card_from_collection(self, card_uuid: str) -> dict:
        """Remove a card from user's domain tables."""
        try:
            success = cards_data.remove_card_from_collection(card_uuid)

            if not success:
                return {
                    "success": False,
                    "message": f"Card {card_uuid} not found in collection",
                }

            return {
                "success": True,
                "message": f"Card {card_uuid} removed from collection",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to remove card: {str(e)}",
            }

    async def get_cards_in_deck(self, deck_file: str) -> list[str]:
        """Get all card UUIDs in a deck."""
        return []


# Singleton instance
card_service = CardService()

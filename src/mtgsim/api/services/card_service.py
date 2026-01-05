"""Card service - handles card data access and processing."""

from mtgsim.api.models.common import Pagination
from mtgsim.api.models.deck import PriceBySource
from mtgsim.api.models.card import (
    CardSummary,
    CardDetail,
    CardListResponse,
    CardLegalities,
    CardAppearance,
    CardPrinting,
)


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
        """
        Search cards with filters.

        TODO: Implement actual database queries:
        1. Query card_index (pre-loaded in memory or SQLite)
        2. Apply text search on name field
        3. Apply filters (set_code, rarity, card_type, colors, price range)
        4. Join with price data for price filtering/sorting
        5. Return paginated results
        """
        return CardListResponse(
            data=[
                CardSummary(
                    uuid="stub-card-001",
                    name="Stub Card",
                    type="Creature - Human",
                    mana_cost="{1}{W}",
                    mana_value=2,
                    rarity="common",
                    set_code="TST",
                    color_identity=["W"],
                    price=1.50,
                    image_url="https://cards.scryfall.io/small/front/a/b/stub.jpg",
                )
            ],
            pagination=Pagination(page=page, limit=limit, total=1, pages=1),
        )

    async def get_card(self, uuid: str) -> CardDetail | None:
        """
        Get full card details.

        TODO: Implement actual data loading:
        1. Fetch card data from SQLite/card_index by uuid
        2. Fetch price data from price cache
        3. Query card-to-decks mapping for deck appearances
        4. Query other printings by card name
        5. Build complete response
        """
        return CardDetail(
            uuid=uuid,
            name="Stub Card",
            mana_cost="{1}{W}",
            mana_value=2,
            type="Creature - Human Soldier",
            types=["Creature"],
            subtypes=["Human", "Soldier"],
            text="When Stub Card enters the battlefield, gain 2 life.",
            flavor_text="A test card for testing purposes.",
            rarity="common",
            set_code="TST",
            set_name="Test Set",
            color_identity=["W"],
            colors=["W"],
            power="2",
            toughness="2",
            image_url="https://cards.scryfall.io/normal/front/a/b/stub.jpg",
            prices=PriceBySource(
                tcgplayer=1.50,
                cardkingdom=1.75,
                cardsphere=1.25,
                cardmarket=1.00,
                mtgo=0.10,
            ),
            legalities=CardLegalities(
                standard="Not Legal",
                pioneer="Not Legal",
                modern="Legal",
                legacy="Legal",
                vintage="Legal",
                commander="Legal",
            ),
            appears_in_decks=[
                CardAppearance(file="TestDeck_TST.json", name="Test Deck", count=4),
            ],
            other_printings=[
                CardPrinting(set_code="XYZ", set_name="Another Set", uuid="other-print-001"),
            ],
        )

    async def get_card_by_name(self, name: str) -> list[CardSummary]:
        """
        Get all printings of a card by name.

        TODO: Query all cards with matching name
        """
        return []

    async def get_cards_in_deck(self, deck_file: str) -> list[str]:
        """
        Get all card UUIDs in a deck.

        TODO: Load deck and extract card UUIDs
        """
        return []


# Singleton instance
card_service = CardService()

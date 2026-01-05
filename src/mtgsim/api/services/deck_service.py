"""Deck service - handles deck data access and processing."""

from mtgsim.api.models.common import Pagination, HistogramBucket, KeywordCounts
from mtgsim.api.models.deck import (
    DeckSummary,
    DeckDetail,
    DeckStats,
    DeckCard,
    DeckListResponse,
    DeckFilters,
    DeckLegality,
    DeckMeta,
    DeckPrice,
    PriceBySource,
)


class DeckService:
    """Service for deck-related operations."""

    async def list_decks(
        self,
        q: str | None = None,
        format: str | None = None,
        set_code: str | None = None,
        deck_type: str | None = None,
        colors: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 50,
    ) -> DeckListResponse:
        """
        List and filter decks with pagination.

        TODO: Implement actual database queries:
        1. Load deck index from cache/database
        2. Apply filters (q, format, set_code, deck_type, colors, price range)
        3. Sort by specified field
        4. Apply pagination
        5. Return results with filter options
        """
        # Stub: return empty response with structure
        return DeckListResponse(
            data=[
                DeckSummary(
                    file="StubDeck_TST.json",
                    name="Stub Deck",
                    code="TST",
                    card_count=60,
                    colors=["W", "U"],
                    price=99.99,
                    release_date="2024-01-01",
                    legality=DeckLegality(modern=True, legacy=True, vintage=True),
                )
            ],
            pagination=Pagination(page=page, limit=limit, total=1, pages=1),
            filters=DeckFilters(
                formats=["standard", "pioneer", "modern", "legacy", "vintage", "commander"],
                sets=["TST"],
                color_combinations=[["W"], ["U"], ["W", "U"]],
            ),
        )

    async def get_deck(self, file: str) -> DeckDetail | None:
        """
        Get full deck details including cards and statistics.

        TODO: Implement actual data loading:
        1. Load deck JSON file from AllDeckFiles/{file}
        2. For each card, fetch price from price cache
        3. Calculate deck statistics (mana curve, type distribution, etc.)
        4. Extract keywords by matching card text against Keywords.json
        5. Calculate total price by summing (card_price * count)
        6. Return complete deck detail
        """
        # Stub: return mock deck
        return DeckDetail(
            meta=DeckMeta(
                file=file,
                name="Stub Deck",
                code="TST",
                release_date="2024-01-01",
            ),
            legality=DeckLegality(modern=True, legacy=True, vintage=True),
            colors=["W", "U"],
            price=DeckPrice(
                total=99.99,
                by_source=PriceBySource(tcgplayer=95.00, cardkingdom=105.00),
            ),
            commander=[],
            main_board=[
                DeckCard(
                    uuid="stub-uuid-001",
                    name="Stub Card",
                    count=4,
                    mana_cost="{1}{W}",
                    mana_value=2,
                    type="Creature - Human",
                    rarity="common",
                    price=1.50,
                    image_url="https://cards.scryfall.io/small/front/a/b/stub.jpg",
                )
            ],
            side_board=[],
            stats=DeckStats(
                total_cards=60,
                unique_cards=24,
                mana_curve={"0": 0, "1": 8, "2": 12, "3": 16, "4": 12, "5": 8, "6+": 4},
                type_distribution={"Creature": 24, "Instant": 8, "Sorcery": 4, "Land": 24},
                rarity_distribution={"common": 20, "uncommon": 16, "rare": 20, "mythic": 4},
                color_distribution={"W": 20, "U": 16, "colorless": 24},
                price_histogram=[
                    HistogramBucket(range="0-1", count=20),
                    HistogramBucket(range="1-5", count=15),
                    HistogramBucket(range="5-10", count=8),
                    HistogramBucket(range="10+", count=4),
                ],
                keywords=KeywordCounts(
                    ability_words={"landfall": 4},
                    keyword_abilities={"flying": 8, "vigilance": 4},
                    keyword_actions={"destroy": 4},
                ),
            ),
        )

    async def get_deck_raw(self, file: str) -> dict | None:
        """
        Get raw deck JSON.

        TODO: Load and return raw JSON from AllDeckFiles/{file}
        """
        return {"stub": True, "file": file}

    async def get_available_sets(self) -> list[str]:
        """
        Get list of set codes that have decks.

        TODO: Query distinct set codes from deck index
        """
        return ["TST", "XYZ"]


# Singleton instance
deck_service = DeckService()

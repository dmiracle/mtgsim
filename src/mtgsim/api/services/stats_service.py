"""Stats service - handles aggregate statistics."""

from pydantic import BaseModel

from mtgsim.api.models.common import HistogramBucket


class RecentSet(BaseModel):
    """Recent set information."""

    code: str
    name: str
    release_date: str


class ExpensiveCard(BaseModel):
    """Expensive card information."""

    name: str
    price: float
    set_code: str


class HomeStats(BaseModel):
    """Aggregate statistics for home screen."""

    total_decks: int
    total_sets: int
    total_cards: int
    total_cards_with_prices: int
    format_distribution: dict[str, int]
    price_histogram: list[HistogramBucket]
    recent_sets: list[RecentSet]
    most_expensive_cards: list[ExpensiveCard]


class DeckAggregateStats(BaseModel):
    """Aggregate deck statistics."""

    by_format: dict[str, int]
    by_set: dict[str, int]
    by_color_combination: dict[str, int]
    price_distribution: list[HistogramBucket]
    average_deck_price: float
    average_deck_size: float


class StatsService:
    """Service for aggregate statistics."""

    async def get_home_stats(self) -> HomeStats:
        """
        Get aggregate statistics for home screen.

        TODO: Implement actual aggregation:
        1. Count total decks from deck index
        2. Count total sets from set index
        3. Count total cards from card index
        4. Count cards with prices from price data
        5. Calculate format distribution from deck legalities
        6. Build price histogram from deck prices
        7. Get recent sets sorted by release date
        8. Get most expensive cards from price data
        """
        return HomeStats(
            total_decks=2648,
            total_sets=844,
            total_cards=105230,
            total_cards_with_prices=95000,
            format_distribution={
                "standard": 150,
                "pioneer": 300,
                "modern": 800,
                "legacy": 500,
                "vintage": 400,
                "commander": 898,
            },
            price_histogram=[
                HistogramBucket(range="0-50", count=500),
                HistogramBucket(range="50-100", count=400),
                HistogramBucket(range="100-500", count=800),
                HistogramBucket(range="500+", count=948),
            ],
            recent_sets=[
                RecentSet(code="MKM", name="Murders at Karlov Manor", release_date="2024-02-09"),
                RecentSet(code="LCI", name="Lost Caverns of Ixalan", release_date="2023-11-17"),
            ],
            most_expensive_cards=[
                ExpensiveCard(name="Black Lotus", price=50000.00, set_code="LEA"),
                ExpensiveCard(name="Ancestral Recall", price=15000.00, set_code="LEA"),
                ExpensiveCard(name="Time Walk", price=12000.00, set_code="LEA"),
            ],
        )

    async def get_deck_stats(self) -> DeckAggregateStats:
        """
        Get aggregate deck statistics.

        TODO: Implement actual aggregation:
        1. Group decks by format legality
        2. Group decks by set code
        3. Group decks by color combination
        4. Build deck price distribution histogram
        5. Calculate average deck price
        6. Calculate average deck size
        """
        return DeckAggregateStats(
            by_format={
                "standard": 150,
                "pioneer": 300,
                "modern": 800,
                "legacy": 500,
                "commander": 898,
            },
            by_set={"TST": 50, "XYZ": 30},
            by_color_combination={"W": 200, "U": 180, "WU": 150, "WUB": 100},
            price_distribution=[
                HistogramBucket(range="0-50", count=500),
                HistogramBucket(range="50-100", count=400),
                HistogramBucket(range="100-500", count=800),
                HistogramBucket(range="500+", count=948),
            ],
            average_deck_price=125.50,
            average_deck_size=68.5,
        )


# Singleton instance
stats_service = StatsService()

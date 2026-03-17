"""Stats service - handles aggregate statistics using real reference data."""

import logging

from pydantic import BaseModel

from mtgsim.api.models.common import HistogramBucket
from mtgsim.reference import ref_db

logger = logging.getLogger("mtgsim.api.services.stats")


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
        """Get aggregate statistics for home screen from real data."""
        logger.debug("get_home_stats: computing aggregate stats")
        total_decks = self._get_total_decks()
        total_sets = self._get_total_sets()
        total_cards = self._get_total_cards()
        total_cards_with_prices = self._get_cards_with_prices()
        format_distribution = self._get_format_distribution()
        price_histogram = self._get_price_histogram()
        recent_sets = self._get_recent_sets()
        most_expensive_cards = self._get_most_expensive_cards()

        return HomeStats(
            total_decks=total_decks,
            total_sets=total_sets,
            total_cards=total_cards,
            total_cards_with_prices=total_cards_with_prices,
            format_distribution=format_distribution,
            price_histogram=price_histogram,
            recent_sets=recent_sets,
            most_expensive_cards=most_expensive_cards,
        )

    async def get_deck_stats(self) -> DeckAggregateStats:
        """Get aggregate deck statistics from real data."""
        by_format = self._get_format_distribution()
        by_set = self._get_decks_by_set()
        by_color = self._get_decks_by_color()
        price_dist = self._get_deck_price_distribution()
        avg_price, avg_size = self._get_deck_averages()

        return DeckAggregateStats(
            by_format=by_format,
            by_set=by_set,
            by_color_combination=by_color,
            price_distribution=price_dist,
            average_deck_price=avg_price,
            average_deck_size=avg_size,
        )

    def _get_total_decks(self) -> int:
        """Count total decks in database."""
        return ref_db.count_decks()

    def _get_total_sets(self) -> int:
        """Count total sets in database."""
        if not ref_db.has_sets():
            return 0
        return ref_db.count_sets()

    def _get_total_cards(self) -> int:
        """Count total unique cards in database."""
        if not ref_db.has_sets():
            return 0
        return ref_db.count_cards()

    def _get_cards_with_prices(self) -> int:
        """Count cards that have price data."""
        if not ref_db.has_prices():
            return 0
        cursor = ref_db.prices.execute("SELECT COUNT(DISTINCT uuid) FROM prices")
        row = cursor.fetchone()
        return row[0] if row else 0

    def _get_format_distribution(self) -> dict[str, int]:
        """Get distribution of decks by format type."""
        if not ref_db.has_decks():
            return {}
        cursor = ref_db.decks.execute("""
            SELECT type, COUNT(*) as count
            FROM deck
            WHERE type IS NOT NULL
            GROUP BY type
            ORDER BY count DESC
            LIMIT 10
        """)
        return {row["type"]: row["count"] for row in cursor.fetchall()}

    def _get_price_histogram(self) -> list[HistogramBucket]:
        """Build price histogram for cards."""
        if not ref_db.has_prices():
            return []

        cursor = ref_db.prices.execute("""
            SELECT
                CASE
                    WHEN price < 1 THEN '$0-1'
                    WHEN price < 5 THEN '$1-5'
                    WHEN price < 20 THEN '$5-20'
                    WHEN price < 50 THEN '$20-50'
                    WHEN price < 100 THEN '$50-100'
                    ELSE '$100+'
                END as price_range,
                COUNT(DISTINCT uuid) as count
            FROM prices
            WHERE provider = 'tcgplayer'
              AND priceType = 'retail'
              AND finish = 'normal'
              AND currency = 'USD'
            GROUP BY price_range
            ORDER BY MIN(price)
        """)

        return [HistogramBucket(range=row["price_range"], count=row["count"]) for row in cursor.fetchall()]

    def _get_recent_sets(self) -> list[RecentSet]:
        """Get most recently released sets."""
        if not ref_db.has_sets():
            return []

        cursor = ref_db.sets.execute("""
            SELECT code, name, release_date
            FROM setdb
            WHERE release_date IS NOT NULL
            ORDER BY release_date DESC
            LIMIT 10
        """)

        return [
            RecentSet(code=row["code"], name=row["name"], release_date=row["release_date"]) for row in cursor.fetchall()
        ]

    def _get_most_expensive_cards(self) -> list[ExpensiveCard]:
        """Get most expensive cards by TCGPlayer price."""
        if not ref_db.has_prices() or not ref_db.has_sets():
            return []

        # Get top prices
        cursor = ref_db.prices.execute("""
            SELECT uuid, price
            FROM prices
            WHERE provider = 'tcgplayer'
              AND priceType = 'retail'
              AND finish = 'normal'
              AND currency = 'USD'
            ORDER BY price DESC
            LIMIT 20
        """)
        price_rows = cursor.fetchall()

        if not price_rows:
            return []

        # Get card names for these UUIDs
        uuids = [row["uuid"] for row in price_rows]
        placeholders = ",".join(["?"] * len(uuids))
        cursor = ref_db.sets.execute(
            f"SELECT uuid, name, set_code FROM setcarddb WHERE uuid IN ({placeholders})",
            uuids,
        )
        card_map = {row["uuid"]: row for row in cursor.fetchall()}

        results = []
        for row in price_rows:
            card = card_map.get(row["uuid"])
            if card:
                results.append(ExpensiveCard(name=card["name"], price=row["price"], set_code=card["set_code"]))
            if len(results) >= 10:
                break

        return results

    def _get_decks_by_set(self) -> dict[str, int]:
        """Get distribution of decks by set code."""
        if not ref_db.has_decks():
            return {}
        cursor = ref_db.decks.execute("""
            SELECT code, COUNT(*) as count
            FROM deck
            WHERE code IS NOT NULL AND code != ''
            GROUP BY code
            ORDER BY count DESC
            LIMIT 20
        """)
        return {row["code"]: row["count"] for row in cursor.fetchall()}

    def _get_decks_by_color(self) -> dict[str, int]:
        """Get distribution of decks by color combination."""
        if not ref_db.has_decks():
            return {}

        # Query deck cards and aggregate color identities
        cursor = ref_db.decks.execute("""
            SELECT d.uuid, dc.color_identity
            FROM deck d
            JOIN deckcard dc ON d.uuid = dc.deck_uuid
            WHERE dc.board = 'mainBoard'
        """)

        deck_colors = {}
        for row in cursor.fetchall():
            deck_uuid = row["uuid"]
            colors = row["color_identity"]
            if colors:
                import json

                try:
                    color_list = json.loads(colors) if isinstance(colors, str) else colors
                    if deck_uuid not in deck_colors:
                        deck_colors[deck_uuid] = set()
                    deck_colors[deck_uuid].update(color_list)
                except (json.JSONDecodeError, TypeError):
                    pass

        # Count by color combination
        color_counts = {}
        for colors in deck_colors.values():
            key = "".join(sorted(colors)) or "C"
            color_counts[key] = color_counts.get(key, 0) + 1

        # Sort by count and return top 20
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        return dict(sorted_colors)

    def _get_deck_price_distribution(self) -> list[HistogramBucket]:
        """Build price histogram for decks."""
        # Would need to calculate deck prices which is expensive
        # Return placeholder for now
        return [
            HistogramBucket(range="$0-50", count=0),
            HistogramBucket(range="$50-100", count=0),
            HistogramBucket(range="$100-500", count=0),
            HistogramBucket(range="$500+", count=0),
        ]

    def _get_deck_averages(self) -> tuple[float, float]:
        """Get average deck price and size."""
        if not ref_db.has_decks():
            return 0.0, 0.0

        cursor = ref_db.decks.execute("""
            SELECT AVG(card_count) as avg_size
            FROM (
                SELECT deck_uuid, SUM(count) as card_count
                FROM deckcard
                WHERE board IN ('mainBoard', 'sideBoard')
                GROUP BY deck_uuid
            )
        """)
        row = cursor.fetchone()
        avg_size = row["avg_size"] if row and row["avg_size"] else 0.0

        # Average price would require joining with prices - skip for now
        return 0.0, avg_size


# Singleton instance
stats_service = StatsService()

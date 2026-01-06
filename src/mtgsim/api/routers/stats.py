"""Statistics API endpoints."""

from fastapi import APIRouter

from mtgsim.api.services.stats_service import DeckAggregateStats, HomeStats, stats_service

router = APIRouter(prefix="/stats", tags=["statistics"])


@router.get("/home", response_model=HomeStats)
async def get_home_stats() -> HomeStats:
    """
    Get aggregate statistics for home screen.

    Returns:
    - Total counts (decks, sets, cards, cards with prices)
    - Format distribution (number of decks legal in each format)
    - Deck price histogram
    - Recent sets
    - Most expensive cards
    """
    return await stats_service.get_home_stats()


@router.get("/decks", response_model=DeckAggregateStats)
async def get_deck_stats() -> DeckAggregateStats:
    """
    Get aggregate deck statistics.

    Returns:
    - Decks by format
    - Decks by set
    - Decks by color combination
    - Deck price distribution
    - Average deck price
    - Average deck size
    """
    return await stats_service.get_deck_stats()

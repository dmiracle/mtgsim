"""Statistics API endpoints."""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from mtgsim.api.services.stats_service import DeckAggregateStats, HomeStats, stats_service
from mtgsim.config import MTGSIM_HOME

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


@router.get("/corpus-wordfreq")
async def get_corpus_wordfreq():
    """
    Get corpus word frequencies for rules text baseline.

    Returns word frequencies computed from all card oracle text.
    Used as baseline for deck wordcloud residue calculation.

    Returns:
    - total_words: Total word count across corpus
    - unique_words: Number of unique words
    - frequencies: Dict mapping word -> frequency (count/total)
    """
    wordfreq_path = MTGSIM_HOME / "corpus_wordfreq.json"
    if not wordfreq_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Corpus word frequencies not found. Run 'mtgsim db sync' first.",
        )

    with open(wordfreq_path) as f:
        return json.load(f)

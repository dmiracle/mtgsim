"""MTGJSON data synchronization.

Downloads MTGJSON data files and syncs them to the local mtgsim.sqlite database.

Usage:
    from mtgsim.sync import sync_all
    sync_all()  # Full sync
    sync_all(force=True)  # Force re-download

Data flow:
    MTGJSON API -> Download -> Extract -> Sync to mj_* tables

Source files (downloaded to ~/.mtgsim/reference/mtgjson/):
    - AllPrintings.sqlite   -> mj_set, mj_card, mj_card_identifier, mj_card_legality
    - AllPricesToday.sqlite -> mj_card_price
    - AllDeckFiles/         -> mj_deck, mj_deck_card
    - Keywords.json         -> mj_keyword
"""

import json
import logging
import re
from collections import Counter

from sqlmodel import Session, select

from mtgsim.config import (
    ALL_DECK_FILES_DIR,
    ALL_DECK_FILES_URL,
    ALL_PRICES_URL,
    ALL_PRINTINGS_URL,
    DB_PATH,
    KEYWORDS_URL,
    MTGJSON_DIR,
    MTGSIM_HOME,
    ensure_dirs,
)
from mtgsim.db.models import MJCard
from mtgsim.db.session import get_engine, init_db

from .download import download_and_extract_tar_xz, download_and_extract_xz
from .tables import sync_cards, sync_decks, sync_keywords, sync_prices, sync_sets

logger = logging.getLogger(__name__)

__all__ = [
    "sync_all",
    "sync_sets",
    "sync_cards",
    "sync_prices",
    "sync_decks",
    "sync_keywords",
]


def sync_all(force: bool = False) -> bool:
    """Run full sync: download MTGJSON files and populate database.

    Args:
        force: Re-download files even if they exist

    Returns:
        True if sync completed successfully
    """
    ensure_dirs()
    init_db()

    # Download source files
    printings_db = MTGJSON_DIR / "AllPrintings.sqlite"
    prices_db = MTGJSON_DIR / "AllPricesToday.sqlite"
    keywords_file = MTGJSON_DIR / "Keywords.json"

    if not download_and_extract_xz(ALL_PRINTINGS_URL, printings_db, force):
        logger.error("Failed to download AllPrintings.sqlite")
        return False

    if not download_and_extract_xz(ALL_PRICES_URL, prices_db, force):
        logger.warning("Failed to download prices, continuing without")

    if not download_and_extract_tar_xz(ALL_DECK_FILES_URL, ALL_DECK_FILES_DIR, force):
        logger.warning("Failed to download decks, continuing without")

    if not download_and_extract_xz(KEYWORDS_URL, keywords_file, force):
        logger.warning("Failed to download keywords, continuing without")

    # Sync tables
    sync_sets(printings_db)
    sync_cards(printings_db)

    if prices_db.exists():
        sync_prices(prices_db)

    if ALL_DECK_FILES_DIR.exists():
        sync_decks(ALL_DECK_FILES_DIR)

    if keywords_file.exists():
        sync_keywords(keywords_file)

    # Post-processing
    _compute_word_frequencies()

    logger.info(f"Sync complete. Database: {DB_PATH}")
    return True


def _compute_word_frequencies():
    """Compute word frequencies from card oracle text for wordcloud baseline."""
    logger.info("Computing word frequencies...")

    stop_words = {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "if",
        "then",
        "of",
        "to",
        "in",
        "on",
        "at",
        "for",
        "is",
        "it",
        "its",
        "this",
        "that",
        "with",
        "as",
        "be",
        "by",
        "from",
        "are",
        "was",
        "were",
        "you",
        "your",
        "may",
        "can",
        "has",
        "have",
        "do",
        "does",
        "each",
        "all",
        "any",
        "one",
        "two",
        "three",
        "four",
        "five",
        "up",
        "into",
        "when",
        "where",
        "until",
        "end",
        "turn",
        "would",
        "could",
        "they",
        "their",
        "them",
        "he",
        "she",
        "his",
        "her",
        "who",
        "which",
    }

    engine = get_engine()
    word_counts: Counter = Counter()
    total_words = 0

    with Session(engine) as session:
        for oracle_text in session.exec(select(MJCard.oracle_text)):
            if not oracle_text:
                continue

            text = oracle_text.lower()
            text = re.sub(r"[{}\(\)•—\-:;,.\"\\'!?]", " ", text)
            words = [w for w in text.split() if len(w) > 2 and w not in stop_words and not w.isdigit()]
            word_counts.update(words)
            total_words += len(words)

    # Save frequencies
    output_path = MTGSIM_HOME / "corpus_wordfreq.json"
    with open(output_path, "w") as f:
        json.dump(
            {
                "total_words": total_words,
                "unique_words": len(word_counts),
                "frequencies": {word: count / total_words for word, count in word_counts.items()},
            },
            f,
        )

    logger.info(f"Saved {len(word_counts)} word frequencies")

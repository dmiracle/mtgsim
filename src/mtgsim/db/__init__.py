"""Database models and session management."""

from mtgsim.config import MERGED_DB_PATH as ALL_SETS_DB_PATH  # Legacy alias
from mtgsim.config import MERGED_DB_PATH as REFERENCE_DB_PATH
from mtgsim.config import USER_DB_PATH as DATABASE_PATH

from .deck_models import Deck, DeckCard, DeckList
from .keyword_models import Keyword
from .models import (
    AllPrintingsMetadata,
    CardColorLink,
    CardDB,
    CardLegalityLink,
    CardSubtypeLink,
    CardSupertypeLink,
    CardTypeLink,
    Format,
)
from .session import get_engine, get_session, init_db, init_deck_db
from .set_models import SetCardDB, SetDB, get_sets_engine, init_sets_db

__all__ = [
    "ALL_SETS_DB_PATH",
    "AllPrintingsMetadata",
    "CardColorLink",
    "CardDB",
    "CardLegalityLink",
    "CardSubtypeLink",
    "CardSupertypeLink",
    "CardTypeLink",
    "DATABASE_PATH",
    "Deck",
    "DeckCard",
    "DeckList",
    "Format",
    "Keyword",
    "REFERENCE_DB_PATH",
    "SetCardDB",
    "SetDB",
    "get_engine",
    "get_session",
    "get_sets_engine",
    "init_db",
    "init_deck_db",
    "init_sets_db",
]

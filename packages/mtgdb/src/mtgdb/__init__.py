"""MTG database models and MTGJSON sync.

This package provides:
- SQLModel database models for MTG data (MJ* tables)
- Session management for the unified database
- MTGJSON sync functionality
"""

from mtgdb.config import DB_PATH, MTGJSON_DIR
from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
    MJKeyword,
    MJSet,
    UserCard,
    UserDeck,
    UserDeckCard,
)
from mtgdb.session import get_engine, get_session, init_db

__all__ = [
    "DB_PATH",
    "MTGJSON_DIR",
    "MJCard",
    "MJCardIdentifier",
    "MJCardLegality",
    "MJCardPrice",
    "MJDeck",
    "MJDeckCard",
    "MJKeyword",
    "MJSet",
    "UserCard",
    "UserDeck",
    "UserDeckCard",
    "get_engine",
    "get_session",
    "init_db",
]

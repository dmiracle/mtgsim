"""MTG database models and MTGJSON sync.

This package provides:
- SQLModel database models for MTG data (MJ* tables)
- Session management for the unified database
- MTGJSON sync functionality
"""

from mtgdb.config import DB_PATH, MTGJSON_DIR
from mtgdb.embeddings.models import MJCardEmbedding
from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJCardTag,
    MJDeck,
    MJDeckCard,
    MJKeyword,
    MJSet,
    PinnedDeck,
    User17LEvent,
    UserCard,
    UserCardEvaluation,
    UserCardInteraction,
    UserCardNote,
    UserCardRating,
    UserCardTag,
    UserDeck,
    UserDeckCard,
    UserEvaluationSet,
    UserRanking,
    UserRankingComparison,
    UserRankingExclusion,
    UserTagDefinition,
    UserTierList,
    UserTierListEntry,
)
from mtgdb.session import get_engine, get_session, init_db, rebuild_fts

__all__ = [
    "DB_PATH",
    "MTGJSON_DIR",
    "MJCard",
    "MJCardEmbedding",
    "MJCardIdentifier",
    "MJCardLegality",
    "MJCardPrice",
    "MJCardTag",
    "MJDeck",
    "MJDeckCard",
    "MJKeyword",
    "MJSet",
    "PinnedDeck",
    "User17LEvent",
    "UserCard",
    "UserCardInteraction",
    "UserCardNote",
    "UserCardRating",
    "UserCardTag",
    "UserDeck",
    "UserDeckCard",
    "UserCardEvaluation",
    "UserEvaluationSet",
    "UserRanking",
    "UserRankingComparison",
    "UserRankingExclusion",
    "UserTagDefinition",
    "UserTierList",
    "UserTierListEntry",
    "get_engine",
    "get_session",
    "init_db",
    "rebuild_fts",
]

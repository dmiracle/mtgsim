"""Database models and session management.

Primary models and session are in the mtgdb package.
This module re-exports them and provides legacy compatibility.
"""

# Re-export from mtgdb package (primary API)
from mtgdb.config import DB_PATH
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
from mtgdb.session import close_db, get_engine, get_session, init_db

# Legacy path aliases (all point to unified DB)
from mtgsim.config import DOMAIN_DB_PATH
from mtgsim.config import MERGED_DB_PATH as ALL_SETS_DB_PATH  # Legacy alias
from mtgsim.config import MERGED_DB_PATH as REFERENCE_DB_PATH
from mtgsim.config import USER_DB_PATH as DATABASE_PATH

# Legacy models (kept for backwards compatibility)
from .deck_models import Deck, DeckCard, DeckList

# New domain database models and session management
from .domain_models import (
    DomainCard,
    DomainCardColorLink,
    DomainCardSubtypeLink,
    DomainCardSupertypeLink,
    DomainCardTypeLink,
    DomainDeck,
    DomainDeckCard,
    DomainSet,
)
from .domain_session import (
    create_domain_tables_only,
    create_reference_tables_only,
    get_domain_engine,
    get_domain_session,
    init_domain_db,
    validate_domain_schema,
)
from .keyword_models import Keyword
from .migration_models import (
    DataIntegrityCheck,
    MigrationLog,
    MigrationStatus,
    MigrationType,
    SchemaVersion,
)
from .models_legacy import (
    AllPrintingsMetadata,
    CardColorLink,
    CardDB,
    CardLegalityLink,
    CardSubtypeLink,
    CardSupertypeLink,
    CardTypeLink,
    Format,
)
from .reference_models import (
    MTGJsonCard,
    MTGJsonDeck,
    MTGJsonDeckCard,
    MTGJsonPrice,
    MTGJsonSet,
)
from .session_legacy import get_engine, get_session, init_db, init_deck_db
from .set_models import SetCardDB, SetDB, get_sets_engine, init_sets_db

__all__ = [
    # mtgdb re-exports (primary API)
    "DB_PATH",
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
    "close_db",
    # Legacy path aliases
    "ALL_SETS_DB_PATH",
    "DATABASE_PATH",
    "DOMAIN_DB_PATH",
    "REFERENCE_DB_PATH",
    # Legacy models
    "AllPrintingsMetadata",
    "CardColorLink",
    "CardDB",
    "CardLegalityLink",
    "CardSubtypeLink",
    "CardSupertypeLink",
    "CardTypeLink",
    "Deck",
    "DeckCard",
    "DeckList",
    "Format",
    "Keyword",
    "SetCardDB",
    "SetDB",
    "get_sets_engine",
    "init_deck_db",
    "init_sets_db",
    # Domain database exports
    "DomainCard",
    "DomainSet",
    "DomainDeck",
    "DomainDeckCard",
    "DomainCardColorLink",
    "DomainCardTypeLink",
    "DomainCardSupertypeLink",
    "DomainCardSubtypeLink",
    "MTGJsonCard",
    "MTGJsonSet",
    "MTGJsonDeck",
    "MTGJsonDeckCard",
    "MTGJsonPrice",
    "MigrationLog",
    "MigrationStatus",
    "MigrationType",
    "SchemaVersion",
    "DataIntegrityCheck",
    "get_domain_engine",
    "get_domain_session",
    "init_domain_db",
    "create_domain_tables_only",
    "create_reference_tables_only",
    "validate_domain_schema",
]

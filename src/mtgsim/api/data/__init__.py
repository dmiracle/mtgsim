"""Data access layer for mtgsim API.

All data access uses the unified database schema.
Collection status is automatically included in responses.
"""

from mtgdb.session import close_db, init_db

from .cards import cards_data
from .decks import decks_data
from .helpers import build_image_url, parse_json_column
from .keywords import keywords_data
from .prices import prices_data
from .sets import sets_data

# Re-export session management with old names for backwards compatibility
init_databases = init_db
close_databases = close_db

__all__ = [
    # Data access singletons
    "cards_data",
    "sets_data",
    "decks_data",
    "prices_data",
    "keywords_data",
    # Session management
    "init_databases",
    "close_databases",
    # Utilities
    "build_image_url",
    "parse_json_column",
]

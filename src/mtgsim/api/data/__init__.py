"""Data access layer for the API."""

from .cards import cards_data
from .database import close_databases, db, init_databases
from .decks import decks_data
from .keywords import keywords_data
from .prices import prices_data
from .sets import sets_data

__all__ = [
    "db",
    "init_databases",
    "close_databases",
    "sets_data",
    "decks_data",
    "prices_data",
    "cards_data",
    "keywords_data",
]

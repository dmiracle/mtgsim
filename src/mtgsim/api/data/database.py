"""Database connection management for API data layer.

This module re-exports from the centralized reference module for backwards compatibility.
New code should import directly from mtgsim.reference.
"""

from mtgsim.reference import ref_db
from mtgsim.reference.db import ReferenceDb

# Re-export with old names for backwards compatibility
db = ref_db
DatabaseManager = ReferenceDb


def init_databases():
    """Initialize all database connections."""
    ref_db.init()


def close_databases():
    """Close all database connections."""
    ref_db.close()

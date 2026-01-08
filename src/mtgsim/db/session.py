"""Unified database session management for mtgsim.

This module provides a single session factory for the unified database.
All models (MJ* reference and user models) are in the same database.
"""

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from mtgsim.config import DB_PATH

_engine: Engine | None = None


def get_engine(db_path: Path | None = None) -> Engine:
    """Get or create the database engine."""
    global _engine

    if _engine is None or db_path is not None:
        path = db_path or DB_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(
            f"sqlite:///{path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        if db_path is None:
            _engine = engine
        return engine

    return _engine


def init_db(db_path: Path | None = None) -> Engine:
    """Initialize database with all tables."""
    # Import models to ensure they're registered with SQLModel

    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    return engine


@contextmanager
def get_session(db_path: Path | None = None):
    """Get a database session as a context manager."""
    engine = get_engine(db_path)
    with Session(engine) as session:
        yield session


def close_db() -> None:
    """Close database connection."""
    global _engine
    if _engine:
        _engine.dispose()
        _engine = None

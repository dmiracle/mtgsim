"""Unified database session management for mtgdb.

This module provides a single session factory for the unified database.
All models (MJ* reference and user models) are in the same database.
"""

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from mtgdb.config import DB_PATH

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
    import mtgdb.embeddings.models  # noqa: F401
    import mtgdb.models  # noqa: F401

    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    _ensure_columns(engine)
    _ensure_fts_table(engine)
    return engine


def _ensure_columns(engine: Engine) -> None:
    """Add columns introduced after initial table creation."""
    from sqlalchemy import text

    added_columns = {
        "mj_card": {"side": "VARCHAR"},
        "mj_17l_card_stat": {"mtga_id": "INTEGER"},
        "mj_17l_dataset": {
            "draft_data_downloaded_version": "VARCHAR",
            "game_data_downloaded_version": "VARCHAR",
            "replay_data_downloaded_version": "VARCHAR",
            "draft_data_ingested_at": "VARCHAR",
            "game_data_ingested_at": "VARCHAR",
            "replay_data_ingested_at": "VARCHAR",
        },
    }
    with engine.connect() as conn:
        for table, columns in added_columns.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
            for column, col_type in columns.items():
                if existing and column not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
        conn.commit()


def _ensure_fts_table(engine: Engine) -> None:
    """Create FTS5 virtual table for card text search if it doesn't exist."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(
            text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS mj_card_fts USING fts5(
                uuid UNINDEXED,
                name,
                printed_name,
                type_line,
                oracle_text,
                tokenize='unicode61'
            )
        """)
        )
        # Populate if empty
        count = conn.execute(text("SELECT count(*) FROM mj_card_fts")).scalar()
        if count == 0:
            conn.execute(
                text("""
                INSERT INTO mj_card_fts(uuid, name, printed_name, type_line, oracle_text)
                SELECT uuid, name, COALESCE(printed_name, ''), COALESCE(type_line, ''), COALESCE(oracle_text, '')
                FROM mj_card
            """)
            )
        conn.commit()


def rebuild_fts(engine: Engine | None = None) -> int:
    """Rebuild the FTS index from mj_card. Returns row count."""
    from sqlalchemy import text

    eng = engine or get_engine()
    with eng.connect() as conn:
        conn.execute(text("DELETE FROM mj_card_fts"))
        conn.execute(
            text("""
            INSERT INTO mj_card_fts(uuid, name, printed_name, type_line, oracle_text)
            SELECT uuid, name, COALESCE(printed_name, ''), COALESCE(type_line, ''), COALESCE(oracle_text, '')
            FROM mj_card
        """)
        )
        count = conn.execute(text("SELECT count(*) FROM mj_card_fts")).scalar()
        conn.commit()
    return count


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

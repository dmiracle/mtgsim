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
    _rename_17l_tables(engine)
    SQLModel.metadata.create_all(engine)
    _ensure_columns(engine)
    _ensure_indexes(engine)
    _backfill_interaction_names(engine)
    _ensure_fts_table(engine)
    return engine


def _rename_17l_tables(engine: Engine) -> None:
    """Rename legacy mj_17l_* tables to sl_* (17Lands data is not from MTGJSON)."""
    from sqlalchemy import text

    renames = {
        "mj_17l_dataset": "sl_dataset",
        "mj_17l_draft_pick": "sl_draft_pick",
        "mj_17l_draft_card": "sl_draft_card",
        "mj_17l_game": "sl_game",
        "mj_17l_game_card": "sl_game_card",
        "mj_17l_replay": "sl_replay",
        "mj_17l_replay_turn": "sl_replay_turn",
        "mj_17l_card_stat": "sl_card_stat",
    }
    with engine.connect() as conn:
        existing = {
            row[0] for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        }
        for old, new in renames.items():
            if old in existing and new not in existing:
                conn.execute(text(f"ALTER TABLE {old} RENAME TO {new}"))
        conn.commit()


def _ensure_columns(engine: Engine) -> None:
    """Add columns introduced after initial table creation."""
    from sqlalchemy import text

    added_columns = {
        "mj_card": {"side": "VARCHAR"},
        "sl_card_stat": {"mtga_id": "INTEGER"},
        "sl_dataset": {
            "draft_data_downloaded_version": "VARCHAR",
            "game_data_downloaded_version": "VARCHAR",
            "replay_data_downloaded_version": "VARCHAR",
            "draft_data_ingested_at": "VARCHAR",
            "game_data_ingested_at": "VARCHAR",
            "replay_data_ingested_at": "VARCHAR",
        },
        "user_card_interaction": {
            "source_card_name": "VARCHAR",
            "target_card_name": "VARCHAR",
            "interaction_subtype": "VARCHAR",
            "detected_by": "VARCHAR DEFAULT 'manual'",
            "confidence": "FLOAT DEFAULT 1.0",
            "win_rate_correlation": "FLOAT",
            "co_occurrence_count": "INTEGER",
        },
    }
    with engine.connect() as conn:
        for table, columns in added_columns.items():
            existing = {row[1] for row in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
            for column, col_type in columns.items():
                if existing and column not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
        conn.commit()


def _ensure_indexes(engine: Engine) -> None:
    """Create indexes for columns added to existing tables (create_all skips them)."""
    from sqlalchemy import text

    indexes = {
        "ix_user_card_interaction_source_card_name": ("user_card_interaction", "source_card_name"),
        "ix_user_card_interaction_target_card_name": ("user_card_interaction", "target_card_name"),
        "ix_user_card_interaction_interaction_subtype": ("user_card_interaction", "interaction_subtype"),
    }
    with engine.connect() as conn:
        for name, (table, column) in indexes.items():
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS {name} ON {table} ({column})"))
        conn.commit()


def _backfill_interaction_names(engine: Engine) -> None:
    """Populate name columns on pre-existing interaction rows from their uuid FKs. Idempotent."""
    from sqlalchemy import text

    with engine.connect() as conn:
        conn.execute(
            text("""
            UPDATE user_card_interaction
            SET source_card_name = (SELECT name FROM mj_card WHERE mj_card.uuid = source_card_uuid)
            WHERE source_card_name IS NULL
        """)
        )
        conn.execute(
            text("""
            UPDATE user_card_interaction
            SET target_card_name = (SELECT name FROM mj_card WHERE mj_card.uuid = target_card_uuid)
            WHERE target_card_name IS NULL
        """)
        )
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

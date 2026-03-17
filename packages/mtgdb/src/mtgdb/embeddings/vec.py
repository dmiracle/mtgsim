"""sqlite-vec integration for vector storage."""

import sqlite_vec
from sqlalchemy import event
from sqlalchemy.engine import Engine

from .generate import EMBEDDING_DIMENSIONS


def load_sqlite_vec(dbapi_conn, connection_record=None):
    """Load sqlite-vec extension on a connection."""
    dbapi_conn.enable_load_extension(True)
    sqlite_vec.load(dbapi_conn)
    dbapi_conn.enable_load_extension(False)


def register_sqlite_vec(engine: Engine) -> None:
    """Register sqlite-vec extension loading for an engine.

    This should be called once after creating the engine to ensure
    sqlite-vec is loaded for all connections from that engine's pool.
    """
    event.listen(engine, "connect", load_sqlite_vec)


def init_vec_tables(engine: Engine) -> None:
    """Create the sqlite-vec virtual tables if they don't exist.

    Creates:
        vec_card_embeddings: Stores card embedding vectors with metadata
    """
    conn = engine.raw_connection()
    try:
        # Load sqlite-vec on this raw connection
        load_sqlite_vec(conn)

        cursor = conn.cursor()

        # Check if table exists
        existing = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='vec_card_embeddings'"
        ).fetchone()

        if not existing:
            cursor.execute(f"""
                CREATE VIRTUAL TABLE vec_card_embeddings USING vec0(
                    card_uuid TEXT NOT NULL,
                    field_source TEXT NOT NULL,
                    embedding float[{EMBEDDING_DIMENSIONS}]
                )
            """)
            conn.commit()
    finally:
        conn.close()

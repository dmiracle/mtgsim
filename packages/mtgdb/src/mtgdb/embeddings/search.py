"""Similarity search functions for card embeddings."""

import struct

from sqlalchemy import text
from sqlmodel import Session, select

from mtgdb.models import MJCard

from .generate import DEFAULT_MODEL, embed_text


def _serialize_vector(vector: list[float]) -> bytes:
    """Serialize a vector to bytes for sqlite-vec."""
    return struct.pack(f"{len(vector)}f", *vector)


def search_similar_cards(
    session: Session,
    query: str | None = None,
    embedding: list[float] | None = None,
    field_source: str = "oracle",
    limit: int = 10,
    model_name: str = DEFAULT_MODEL,
) -> list[tuple[MJCard, float]]:
    """Search for cards similar to a query or embedding.

    Args:
        session: SQLModel session (must have sqlite-vec loaded)
        query: Text query to search for (will be embedded)
        embedding: Pre-computed embedding vector (alternative to query)
        field_source: Which embedding type to search
        limit: Maximum results to return
        model_name: Model to use for query embedding

    Returns:
        List of (card, distance) tuples, sorted by distance ascending
    """
    if query is None and embedding is None:
        raise ValueError("Must provide either query or embedding")

    if embedding is None:
        embedding = embed_text(query, model_name)

    # Query sqlite-vec
    vector_bytes = _serialize_vector(embedding)

    results = session.execute(
        text("""
            SELECT card_uuid, distance
            FROM vec_card_embeddings
            WHERE field_source = :field_source
              AND embedding MATCH :embedding
            ORDER BY distance
            LIMIT :limit
        """),
        {"field_source": field_source, "embedding": vector_bytes, "limit": limit},
    ).fetchall()

    if not results:
        return []

    # Fetch card objects
    uuids = [r[0] for r in results]
    distances = {r[0]: r[1] for r in results}

    cards = session.exec(select(MJCard).where(MJCard.uuid.in_(uuids))).all()

    # Build result list preserving order
    card_map = {c.uuid: c for c in cards}
    return [(card_map[uuid], distances[uuid]) for uuid in uuids if uuid in card_map]


def search_by_name(
    session: Session,
    name: str,
    limit: int = 5,
    model_name: str = DEFAULT_MODEL,
) -> list[tuple[MJCard, float]]:
    """Search for cards by name similarity.

    Useful for OCR results where the name may have errors.
    """
    return search_similar_cards(
        session=session,
        query=name,
        field_source="name_only",
        limit=limit,
        model_name=model_name,
    )


def search_by_oracle_text(
    session: Session,
    text: str,
    limit: int = 10,
    model_name: str = DEFAULT_MODEL,
) -> list[tuple[MJCard, float]]:
    """Search for cards with similar oracle text/mechanics."""
    return search_similar_cards(
        session=session,
        query=text,
        field_source="oracle",
        limit=limit,
        model_name=model_name,
    )

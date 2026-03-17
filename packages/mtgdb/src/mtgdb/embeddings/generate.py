"""Embedding generation for card text."""

import hashlib
from collections.abc import Iterator
from datetime import UTC, datetime

import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
from sqlmodel import Session, select

from mtgdb.models import MJCard

from .models import MJCardEmbedding

DEFAULT_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

_model_cache: dict[str, SentenceTransformer] = {}


def get_embedding_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """Get or create the embedding model."""
    if model_name not in _model_cache:
        _model_cache[model_name] = SentenceTransformer(model_name)
    return _model_cache[model_name]


def hash_text(text: str) -> str:
    """Compute hash of text for change detection."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def prepare_card_text(
    card: MJCard,
    field_source: str = "oracle",
) -> str | None:
    """Prepare card text for embedding generation.

    Args:
        card: The card to prepare text for
        field_source: Which fields to include:
            - "oracle": name + type_line + oracle_text
            - "flavor": name + flavor_text
            - "combined": all text fields
            - "name_only": just the card name

    Returns:
        Prepared text string, or None if no relevant text
    """
    if field_source == "name_only":
        return card.name

    if field_source == "flavor":
        if not card.flavor_text:
            return None
        parts = [f"Card: {card.name}"]
        parts.append(card.flavor_text)
        return "\n".join(parts)

    if field_source == "oracle":
        if not card.oracle_text:
            return None
        parts = [f"Card: {card.name}"]
        if card.type_line:
            parts.append(f"Type: {card.type_line}")
        parts.append(card.oracle_text)
        return "\n".join(parts)

    if field_source == "combined":
        parts = [f"Card: {card.name}"]
        if card.type_line:
            parts.append(f"Type: {card.type_line}")
        if card.oracle_text:
            parts.append(card.oracle_text)
        if card.flavor_text:
            parts.append(f"Flavor: {card.flavor_text}")
        # Need at least some content beyond just the name
        if len(parts) == 1:
            return None
        return "\n".join(parts)

    raise ValueError(f"Unknown field_source: {field_source}")


def iter_cards_for_embedding(
    session: Session,
    field_source: str = "oracle",
    batch_size: int = 1000,
) -> Iterator[tuple[MJCard, str]]:
    """Iterate over cards that have embeddable text.

    Yields:
        Tuples of (card, prepared_text)
    """
    offset = 0
    while True:
        cards = session.exec(select(MJCard).offset(offset).limit(batch_size)).all()

        if not cards:
            break

        for card in cards:
            text = prepare_card_text(card, field_source)
            if text:
                yield card, text

        offset += batch_size


def generate_embeddings(
    session: Session,
    field_source: str = "oracle",
    model_name: str = DEFAULT_MODEL,
    batch_size: int = 256,
    force: bool = False,
) -> int:
    """Generate embeddings for all cards.

    Args:
        session: SQLModel session for card data (must have sqlite-vec loaded)
        field_source: Which text fields to embed
        model_name: Embedding model to use
        batch_size: Batch size for embedding generation
        force: If True, regenerate all embeddings even if unchanged

    Returns:
        Number of embeddings generated
    """
    model = get_embedding_model(model_name)

    # Get existing embeddings for this field_source/model combo
    existing = {}
    if not force:
        results = session.exec(
            select(MJCardEmbedding)
            .where(MJCardEmbedding.field_source == field_source)
            .where(MJCardEmbedding.model_name == model_name)
        ).all()
        existing = {e.card_uuid: e.source_hash for e in results}

    # Collect cards that need embedding
    to_embed: list[tuple[str, str, str]] = []  # (uuid, text, hash)

    for card, card_text in iter_cards_for_embedding(session, field_source):
        text_hash = hash_text(card_text)

        # Skip if unchanged
        if card.uuid in existing and existing[card.uuid] == text_hash:
            continue

        to_embed.append((card.uuid, card_text, text_hash))

    if not to_embed:
        return 0

    # Generate embeddings in batches
    count = 0
    for i in range(0, len(to_embed), batch_size):
        batch = to_embed[i : i + batch_size]
        texts = [t[1] for t in batch]

        # Generate embeddings using sentence-transformers
        embeddings = model.encode(texts, convert_to_numpy=True)

        # Insert into sqlite-vec and metadata table
        for (uuid, card_text, text_hash), embedding in zip(batch, embeddings):
            # Convert to float32 bytes for sqlite-vec
            embedding_bytes = np.asarray(embedding, dtype=np.float32).tobytes()

            # Check if vector already exists
            result = session.execute(
                text("SELECT rowid FROM vec_card_embeddings WHERE card_uuid = :uuid AND field_source = :fs"),
                {"uuid": uuid, "fs": field_source},
            ).fetchone()

            if result:
                # Update existing
                session.execute(
                    text("UPDATE vec_card_embeddings SET embedding = :emb WHERE rowid = :rowid"),
                    {"emb": embedding_bytes, "rowid": result[0]},
                )
            else:
                # Insert new
                session.execute(
                    text(
                        "INSERT INTO vec_card_embeddings (card_uuid, field_source, embedding) VALUES (:uuid, :fs, :emb)"
                    ),
                    {"uuid": uuid, "fs": field_source, "emb": embedding_bytes},
                )

            # Insert/update metadata
            existing_meta = session.exec(
                select(MJCardEmbedding)
                .where(MJCardEmbedding.card_uuid == uuid)
                .where(MJCardEmbedding.field_source == field_source)
                .where(MJCardEmbedding.model_name == model_name)
            ).first()

            if existing_meta:
                existing_meta.source_hash = text_hash
                existing_meta.generated_at = datetime.now(UTC)
                session.add(existing_meta)
            else:
                meta = MJCardEmbedding(
                    card_uuid=uuid,
                    field_source=field_source,
                    source_hash=text_hash,
                    model_name=model_name,
                    dimensions=EMBEDDING_DIMENSIONS,
                )
                session.add(meta)

            count += 1

        # Commit batch
        session.commit()

    return count


def embed_text(
    text: str,
    model_name: str = DEFAULT_MODEL,
) -> list[float]:
    """Generate embedding for a single text string.

    Useful for query embedding before search.
    """
    model = get_embedding_model(model_name)
    embedding = model.encode([text], convert_to_numpy=True)[0]
    return embedding.tolist()

"""Vector embeddings for MTG card text.

This module provides semantic search capabilities over card text using
sqlite-vec for vector storage and sentence-transformers for embedding generation.

Heavy imports (sentence-transformers, torch) are deferred until actually needed.
Only the lightweight MJCardEmbedding model is available at import time.
"""

from .models import MJCardEmbedding

__all__ = [
    "MJCardEmbedding",
    "generate_embeddings",
    "embed_text",
    "prepare_card_text",
    "DEFAULT_MODEL",
    "EMBEDDING_DIMENSIONS",
    "search_similar_cards",
    "search_by_name",
    "search_by_oracle_text",
    "init_vec_tables",
    "register_sqlite_vec",
]

_GENERATE_ATTRS = {"generate_embeddings", "embed_text", "prepare_card_text", "DEFAULT_MODEL", "EMBEDDING_DIMENSIONS"}
_SEARCH_ATTRS = {"search_similar_cards", "search_by_name", "search_by_oracle_text"}
_VEC_ATTRS = {"init_vec_tables", "register_sqlite_vec"}


def __getattr__(name: str):  # noqa: C901
    """Lazy-load heavy embedding functions on first access."""
    if name in _GENERATE_ATTRS:
        from . import generate  # noqa: F811

        return getattr(generate, name)
    if name in _SEARCH_ATTRS:
        from . import search  # noqa: F811

        return getattr(search, name)
    if name in _VEC_ATTRS:
        from . import vec  # noqa: F811

        return getattr(vec, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

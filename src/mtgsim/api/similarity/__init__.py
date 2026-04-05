"""Card similarity search strategies.

Import this package to register all built-in strategies.
"""

# Import strategy modules to trigger registration
from . import (
    keywords,  # noqa: F401
    mana_curve,  # noqa: F401
    oracle_vector,  # noqa: F401
    tags,  # noqa: F401
    type_match,  # noqa: F401
)
from .base import (
    MergedScore,
    ScoredCard,
    SimilarityStrategy,
    get_strategy,
    list_strategies,
    register_strategy,
)

__all__ = [
    "MergedScore",
    "ScoredCard",
    "SimilarityStrategy",
    "get_strategy",
    "list_strategies",
    "register_strategy",
]

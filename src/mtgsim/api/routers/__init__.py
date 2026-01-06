"""API routers."""

from mtgsim.api.routers.cards import router as cards_router
from mtgsim.api.routers.decks import router as decks_router
from mtgsim.api.routers.keywords import router as keywords_router
from mtgsim.api.routers.prices import router as prices_router
from mtgsim.api.routers.sets import router as sets_router
from mtgsim.api.routers.stats import router as stats_router

__all__ = [
    "decks_router",
    "sets_router",
    "cards_router",
    "prices_router",
    "stats_router",
    "keywords_router",
]

"""API routers."""

from mtgsim.api.routers.boosters import router as boosters_router
from mtgsim.api.routers.card_notes import router as card_notes_router
from mtgsim.api.routers.cards import router as cards_router
from mtgsim.api.routers.decks import router as decks_router
from mtgsim.api.routers.flashcards import router as flashcards_router
from mtgsim.api.routers.interactions import router as interactions_router
from mtgsim.api.routers.keywords import router as keywords_router
from mtgsim.api.routers.prices import router as prices_router
from mtgsim.api.routers.scan_log import router as scan_log_router
from mtgsim.api.routers.sets import router as sets_router
from mtgsim.api.routers.seventeenlands import router as seventeenlands_router
from mtgsim.api.routers.stats import router as stats_router
from mtgsim.api.routers.user_tags import router as user_tags_router

__all__ = [
    "boosters_router",
    "card_notes_router",
    "decks_router",
    "sets_router",
    "cards_router",
    "prices_router",
    "stats_router",
    "keywords_router",
    "seventeenlands_router",
    "flashcards_router",
    "interactions_router",
    "user_tags_router",
    "scan_log_router",
]

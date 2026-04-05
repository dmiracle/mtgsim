"""FastAPI application for MTG Webapp REST API."""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from mtgsim.api.data import close_databases, init_databases
from mtgsim.api.models.common import ErrorDetail, ErrorResponse
from mtgsim.api.profiler import (
    RequestProfile,
    get_history,
    record_profile,
    start_profiling,
    stop_profiling,
)
from mtgsim.api.routers import (
    boosters_router,
    cards_router,
    decks_router,
    flashcards_router,
    interactions_router,
    keywords_router,
    prices_router,
    sets_router,
    seventeenlands_router,
    stats_router,
)
from mtgsim.config import get_resources_dir

# Configure logging based on settings (reads .env automatically)
from mtgsim.settings import settings as app_settings

DEBUG = app_settings.debug or os.environ.get("MTGSIM_DEBUG", "0") == "1"
log_level = logging.DEBUG if DEBUG else logging.INFO

logging.basicConfig(
    level=log_level,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("mtgsim.api")

# Threshold in seconds for warning about slow responses
SLOW_RESPONSE_THRESHOLD = 1.0


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request timing, identify slow responses, and profile queries."""

    async def dispatch(self, request: Request, call_next):
        # Skip logging for static files and health checks
        path = request.url.path
        if path.startswith("/resources") or path == "/health":
            return await call_next(request)

        start_time = time.perf_counter()
        method = request.method
        query_string = f"?{request.url.query}" if request.url.query else ""

        logger.debug(f"-> {method} {path}{query_string}")

        start_profiling()
        response = await call_next(request)
        queries = stop_profiling()

        duration = time.perf_counter() - start_time
        duration_ms = duration * 1000
        total_query_ms = sum(q.duration_ms for q in queries)
        status = response.status_code

        # Add profiling headers
        response.headers["X-Query-Count"] = str(len(queries))
        response.headers["X-Query-Time-Ms"] = f"{total_query_ms:.1f}"
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.1f}"

        # Record profile
        profile = RequestProfile(
            method=method,
            path=path,
            query_string=query_string,
            query_count=len(queries),
            total_query_ms=total_query_ms,
            request_ms=duration_ms,
            queries=queries,
        )
        record_profile(profile)

        if duration >= SLOW_RESPONSE_THRESHOLD:
            logger.warning(
                f"SLOW {method} {path}{query_string} -> {status} ({duration_ms:.0f}ms) "
                f"[{len(queries)} queries, {total_query_ms:.0f}ms db]"
            )
        else:
            logger.info(f"{method} {path}{query_string} -> {status} ({duration_ms:.0f}ms)")

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    import time as _time

    t0 = _time.perf_counter()
    logger.info("Starting MTG API server..." + (" [DEBUG MODE]" if DEBUG else ""))
    logger.debug(f"Resources dir: {get_resources_dir()}")
    t1 = _time.perf_counter()
    init_databases()
    logger.info(f"Database initialized ({(_time.perf_counter() - t1) * 1000:.0f}ms)")

    from mtgdb.session import get_engine

    from mtgsim.api.profiler import attach_profiler

    engine = get_engine()
    attach_profiler(engine)

    from mtgdb.embeddings.vec import register_sqlite_vec

    register_sqlite_vec(engine)
    logger.info(f"Server ready ({(_time.perf_counter() - t0) * 1000:.0f}ms startup)")

    yield

    # Shutdown
    logger.info("Shutting down MTG API server...")
    close_databases()


app = FastAPI(
    title="MTG Webapp API",
    description="""
REST API for the MTG Deck Viewer webapp.

## Features

- **Decks**: Browse and filter Magic: The Gathering decks
- **Sets**: Explore MTG sets with statistics and cards
- **Cards**: Search cards with detailed information
- **Prices**: Access price data from multiple sources
- **Statistics**: Aggregate data and analytics

## Data Sources

- Card data from MTGJSON AllPrintings database
- Deck files from MTGJSON AllDeckFiles
- Set files from MTGJSON AllSetFiles
- Daily price updates from MTGJSON AllPricesToday
    """,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Query-Count", "X-Query-Time-Ms", "X-Response-Time-Ms"],
)

# Request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error=ErrorDetail(
                code="NOT_FOUND",
                message=str(exc.detail) if hasattr(exc, "detail") else "Resource not found",
            )
        ).model_dump(),
    )


@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 400 errors."""
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=ErrorDetail(
                code="BAD_REQUEST",
                message=str(exc.detail) if hasattr(exc, "detail") else "Bad request",
            )
        ).model_dump(),
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An internal error occurred",
            )
        ).model_dump(),
    )


# Include routers
app.include_router(boosters_router, prefix="/api")
app.include_router(decks_router, prefix="/api")
app.include_router(sets_router, prefix="/api")
app.include_router(cards_router, prefix="/api")
app.include_router(prices_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(keywords_router, prefix="/api")
app.include_router(seventeenlands_router, prefix="/api")
app.include_router(flashcards_router, prefix="/api")
app.include_router(interactions_router, prefix="/api")


@app.get("/")
async def root():
    """Redirect root to the API docs."""
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/docs")


@app.get("/api")
async def api_root():
    """API information endpoint."""
    return {
        "name": "MTG Webapp API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "decks": "/api/decks",
            "sets": "/api/sets",
            "cards": "/api/cards",
            "prices": "/api/prices",
            "stats": "/api/stats/home",
            "keywords": "/api/keywords",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/debug/queries")
async def debug_queries(
    min_queries: int = 0,
    min_db_ms: float = 0,
    path: str = "",
    limit: int = 50,
):
    """Return recent query profiles for debugging slow endpoints."""
    profiles = get_history(
        min_queries=min_queries,
        min_db_ms=min_db_ms,
        path_contains=path,
        limit=limit,
    )
    return [
        {
            "method": p.method,
            "path": p.path,
            "query_string": p.query_string,
            "query_count": p.query_count,
            "total_query_ms": round(p.total_query_ms, 1),
            "request_ms": round(p.request_ms, 1),
            "timestamp": p.timestamp,
            "queries": [
                {
                    "sql": q.sql[:500],
                    "params": q.params_repr,
                    "duration_ms": round(q.duration_ms, 2),
                }
                for q in p.queries
            ],
        }
        for p in profiles
    ]


# Mount static files for resources
resources_dir = get_resources_dir()

if resources_dir.exists():
    app.mount("/resources", StaticFiles(directory=str(resources_dir)), name="resources")

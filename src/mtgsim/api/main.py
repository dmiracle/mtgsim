"""FastAPI application for MTG Webapp REST API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from mtgsim.api.data import close_databases, init_databases
from mtgsim.api.models.common import ErrorDetail, ErrorResponse
from mtgsim.api.routers import (
    cards_router,
    decks_router,
    keywords_router,
    prices_router,
    sets_router,
    stats_router,
)
from mtgsim.config import get_resources_dir, get_web_dir, get_webapp_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    print("Starting MTG API server...")
    init_databases()
    print("Database connections initialized")

    yield

    # Shutdown
    print("Shutting down MTG API server...")
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
)


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
app.include_router(decks_router, prefix="/api")
app.include_router(sets_router, prefix="/api")
app.include_router(cards_router, prefix="/api")
app.include_router(prices_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(keywords_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API information."""
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


# Mount static files for the webapp
web_dir = get_web_dir()
resources_dir = get_resources_dir()
webapp_dir = get_webapp_dir()

if web_dir.exists():
    app.mount("/web", StaticFiles(directory=str(web_dir)), name="web")

if resources_dir.exists():
    app.mount("/resources", StaticFiles(directory=str(resources_dir)), name="resources")

if webapp_dir.exists():
    app.mount("/webapp", StaticFiles(directory=str(webapp_dir)), name="webapp")


@app.get("/app")
async def serve_webapp():
    """Serve the main webapp."""
    index_path = web_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"error": "Webapp not found"}

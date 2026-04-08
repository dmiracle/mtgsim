"""Card API endpoints."""

import logging
import time
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Query, Request, UploadFile
from pydantic import BaseModel

from mtgsim.api.models.card import CardDetail, CardListResponse, CardStatsResponse
from mtgsim.api.models.scan import ScanResponse
from mtgsim.api.services.card_service import card_service
from mtgsim.api.services.scan_service import scan_service
from mtgsim.settings import settings

logger = logging.getLogger("mtgsim.api.routers.cards")

router = APIRouter(prefix="/cards", tags=["cards"])

# Simple in-memory rate limiter for scan endpoint.
# Configured via SCAN_RATE_LIMIT and SCAN_RATE_WINDOW in .env or environment.
SCAN_RATE_LIMIT = settings.scan_rate_limit
SCAN_RATE_WINDOW = settings.scan_rate_window
_scan_timestamps: dict[str, list[float]] = defaultdict(list)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 MB


class CollectionResponse(BaseModel):
    """Response for collection management operations."""

    success: bool
    message: str
    card: dict | None = None


class QuadrantRatingRequest(BaseModel):
    developing: float | None = None
    ahead: float | None = None
    behind: float | None = None
    parity: float | None = None
    notes: str | None = None


class QuadrantRatingResponse(BaseModel):
    developing: float | None = None
    ahead: float | None = None
    behind: float | None = None
    parity: float | None = None
    notes: str | None = None


@router.get("", response_model=CardListResponse)
async def search_cards(
    q: str | None = Query(None, description="Search by card name"),
    text: str | None = Query(None, description="Filter by oracle text"),
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by multiple set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    format: str | None = Query(None, description="Filter by format legality (standard, modern, etc.)"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated, e.g. mana-dork,ramp)"),
    mana_value: str | None = Query(None, description="Filter by mana values (comma-separated, e.g. 0,1,2). 7 means 7+"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    owns: bool | None = Query(None, description="Filter by ownership"),
    owns_platform: str | None = Query(None, pattern="^(paper|mtga)$", description="Filter by ownership platform"),
    wants: bool | None = Query(None, description="Filter by want status"),
    unique: bool = Query(False, description="Show only one printing per card name"),
    price_mode: str = Query("min", pattern="^(min|max)$", description="Price mode: min (cheapest) or max"),
    sort: str = Query("name", description="Sort field"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
) -> CardListResponse:
    """Search cards with filters."""
    color_list = list(colors.upper()) if colors else None
    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    mv_list = [int(v) for v in mana_value.split(",") if v.strip().isdigit()] if mana_value else None

    logger.debug(f"search_cards: q={q} set={set} format={format} rarity={rarity}")
    return await card_service.search_cards(
        q=q,
        text=text,
        set_code=set,
        set_codes=set_code_list,
        rarity=rarity,
        card_type=type,
        colors=color_list,
        mana_values=mv_list,
        format_legal=format,
        keywords=keyword_list,
        tags=tag_list,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        owns_platform=owns_platform,
        wants=wants,
        unique=unique,
        price_mode=price_mode,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )


@router.get("/download")
async def download_cards(
    q: str | None = Query(None, description="Search by card name"),
    text: str | None = Query(None, description="Filter by oracle text"),
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    format: str | None = Query(None, description="Filter by format legality"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated)"),
    mana_value: str | None = Query(None, description="Filter by mana values (comma-separated)"),
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    owns: bool | None = Query(None),
    owns_platform: str | None = Query(None, pattern="^(paper|mtga)$"),
    wants: bool | None = Query(None),
    unique: bool = Query(True, description="One printing per card name (default true for downloads)"),
    price_mode: str = Query("min", pattern="^(min|max)$"),
    sort: str = Query("name"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    limit: int = Query(10000, ge=1, le=50000, description="Max cards to export"),
):
    """Download filtered cards as a JSON file."""
    import json

    from fastapi.responses import Response

    color_list = list(colors.upper()) if colors else None
    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    mv_list = [int(v) for v in mana_value.split(",") if v.strip().isdigit()] if mana_value else None

    result = await card_service.search_cards(
        q=q,
        text=text,
        set_code=set,
        set_codes=set_code_list,
        rarity=rarity,
        card_type=type,
        colors=color_list,
        mana_values=mv_list,
        format_legal=format,
        keywords=keyword_list,
        tags=tag_list,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        owns_platform=owns_platform,
        wants=wants,
        unique=unique,
        price_mode=price_mode,
        sort=sort,
        order=order,
        page=1,
        limit=limit,
    )

    content = json.dumps(
        {"cards": [card.model_dump() for card in result.data], "total": result.pagination.total},
        indent=2,
    )
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=cards.json"},
    )


@router.get("/stats", response_model=CardStatsResponse)
async def get_card_stats(
    q: str | None = Query(None, description="Search by name, type, or oracle text"),
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by colors (e.g. WUB)"),
    format: str | None = Query(None, description="Filter by format legality"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated)"),
    mana_value: str | None = Query(None, description="Filter by mana values (comma-separated, 7 means 7+)"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    owns: bool | None = Query(None, description="Filter by ownership"),
    wants: bool | None = Query(None, description="Filter by want status"),
    unique: bool = Query(False, description="One printing per card name"),
) -> CardStatsResponse:
    """Get aggregated statistics for filtered cards.

    Accepts the same filter parameters as GET /api/cards but returns
    mana curve, type/rarity/color distributions, and price stats.
    """
    from mtgsim.api.data.cards import cards_data

    color_list = list(colors.upper()) if colors else None
    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    mv_list = [int(v) for v in mana_value.split(",") if v.strip().isdigit()] if mana_value else None

    stats = cards_data.get_card_stats(
        q=q,
        set_code=set,
        set_codes=set_code_list,
        rarity=rarity,
        card_type=type,
        colors=color_list,
        mana_values=mv_list,
        format_legal=format,
        keywords=keyword_list,
        tags=tag_list,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        wants=wants,
        unique=unique,
    )
    return CardStatsResponse(**stats)


@router.get("/tags")
async def get_tags(
    set: str | None = Query(None, description="Filter by set code"),
    format: str | None = Query(None, description="Filter by format legality"),
    colors: str | None = Query(None, description="Filter by colors (e.g. WUB)"),
    type: str | None = Query(None, description="Filter by card type"),
    rarity: str | None = Query(None, description="Filter by rarity"),
) -> list[dict]:
    """Get available oracle tags with card counts, optionally filtered."""
    from mtgsim.api.data import cards_data

    color_list = list(colors.upper()) if colors else None
    return cards_data.get_available_tags(
        set_code=set,
        format_legal=format,
        colors=color_list,
        card_type=type,
        rarity=rarity,
    )


@router.get("/keyword-frequencies")
async def get_keyword_frequencies(
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by multiple set codes (comma-separated)"),
    format: str | None = Query(None, description="Filter by format legality"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    colors: str | None = Query(None, description="Filter by colors (e.g. WUB)"),
    type: str | None = Query(None, description="Filter by card type"),
) -> dict:
    """Get keyword frequencies for filtered cards, categorized by type."""
    from mtgsim.api.data import cards_data
    from mtgsim.api.data.keywords import keywords_data

    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    color_list = list(colors.upper()) if colors else None
    freq = cards_data.get_keyword_frequencies(
        set_code=set,
        set_codes=set_code_list,
        format_legal=format,
        rarity=rarity,
        colors=color_list,
        card_type=type,
    )
    return keywords_data.categorize_keyword_freq(freq)


@router.get("/features/grid-layout")
async def get_feature_grid_layout() -> dict:
    """Get the optimal 8x8 grid layout for the 64 compact feature dimensions.

    Uses PCA on feature co-occurrence + Hungarian algorithm to assign
    each feature to a grid cell preserving spatial relationships.
    The layout is deterministic for a given card database.
    """
    from mtgsim.api.services.feature_service import feature_service

    return feature_service.compute_grid_layout()


@router.get("/features/compact")
async def batch_compact_vectors(
    q: str | None = Query(None, description="Search by card name"),
    text: str | None = Query(None, description="Filter by oracle text"),
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    format: str | None = Query(None, description="Filter by format legality"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated)"),
    mana_value: str | None = Query(None, description="Filter by mana values (comma-separated)"),
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    owns: bool | None = Query(None),
    wants: bool | None = Query(None),
    limit: int = Query(200, ge=1, le=4096, description="Max cards to return"),
) -> dict:
    """Get compact 64-dim feature vectors for cards matching filters."""
    from mtgsim.api.services.feature_service import feature_service

    return feature_service.batch_compact_vectors(
        q=q,
        text=text,
        set_code=set,
        set_codes=[s.strip() for s in sets.split(",") if s.strip()] if sets else None,
        rarity=rarity,
        card_type=type,
        colors=list(colors.upper()) if colors else None,
        mana_values=[int(v) for v in mana_value.split(",") if v.strip().isdigit()] if mana_value else None,
        format_legal=format,
        keywords=[k.strip() for k in keywords.split(",") if k.strip()] if keywords else None,
        tags=[t.strip() for t in tags.split(",") if t.strip()] if tags else None,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        wants=wants,
        limit=limit,
    )


@router.get("/features/aggregate")
async def aggregate_vectors(
    q: str | None = Query(None, description="Search by card name"),
    text: str | None = Query(None, description="Filter by oracle text"),
    set: str | None = Query(None, description="Filter by set code"),
    sets: str | None = Query(None, description="Filter by set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    format: str | None = Query(None, description="Filter by format legality"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated)"),
    mana_value: str | None = Query(None, description="Filter by mana values (comma-separated)"),
    price_min: float | None = Query(None, ge=0),
    price_max: float | None = Query(None, ge=0),
    owns: bool | None = Query(None),
    wants: bool | None = Query(None),
) -> dict:
    """Get L2-normalized aggregate of compact vectors for matching cards."""
    from mtgsim.api.services.feature_service import feature_service

    return feature_service.aggregate_vectors(
        q=q,
        text=text,
        set_code=set,
        set_codes=[s.strip() for s in sets.split(",") if s.strip()] if sets else None,
        rarity=rarity,
        card_type=type,
        colors=list(colors.upper()) if colors else None,
        mana_values=[int(v) for v in mana_value.split(",") if v.strip().isdigit()] if mana_value else None,
        format_legal=format,
        keywords=[k.strip() for k in keywords.split(",") if k.strip()] if keywords else None,
        tags=[t.strip() for t in tags.split(",") if t.strip()] if tags else None,
        price_min=price_min,
        price_max=price_max,
        owns=owns,
        wants=wants,
    )


@router.post("/collection/import-mtga")
async def import_mtga_collection(file: UploadFile) -> dict:
    """Import an MTGA collection CSV to mark cards as owned on MTGA."""
    import tempfile

    from mtgsim.mtga_import import import_mtga_collection

    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a .csv")

    contents = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="wb") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    from pathlib import Path

    result = import_mtga_collection(Path(tmp_path))
    Path(tmp_path).unlink(missing_ok=True)

    return result.model_dump()


@router.post("/scan", response_model=ScanResponse)
async def scan_card(
    request: Request,
    image: UploadFile,
    pipeline: str = Query("openai", description="Extraction pipeline: 'openai' or 'mock'"),
    add_to_collection: bool = Query(False, description="Add matched card to collection"),
    deck_id: int | None = Query(None, description="Add matched card to this deck"),
) -> ScanResponse:
    """Scan a card image and identify it.

    Accepts a JPEG or PNG photo, extracts card data via the chosen pipeline,
    and fuzzy-matches against the database. Returns extraction details and
    match info even when no database match is found (matched=false).
    """
    # Rate limiting
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    timestamps = _scan_timestamps[client_ip]
    _scan_timestamps[client_ip] = [t for t in timestamps if now - t < SCAN_RATE_WINDOW]
    if len(_scan_timestamps[client_ip]) >= SCAN_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {SCAN_RATE_LIMIT} scans per {SCAN_RATE_WINDOW}s.",
        )
    _scan_timestamps[client_ip].append(now)

    # Validate file type
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {image.content_type}")

    # Read and validate size
    data = await image.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty image file")
    if len(data) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"Image too large. Max {MAX_IMAGE_SIZE // (1024 * 1024)}MB.")

    try:
        return await scan_service.scan_card(
            image_data=data,
            mime_type=image.content_type,
            pipeline_name=pipeline,
            add_to_collection=add_to_collection,
            deck_id=deck_id,
        )
    except Exception:
        logger.exception("Card scan failed")
        raise HTTPException(status_code=502, detail="Card extraction service unavailable")


@router.get("/similar/strategies")
async def get_similarity_strategies() -> list[dict]:
    """List available similarity search strategies."""
    from mtgsim.api.services.similarity_service import similarity_service

    return similarity_service.get_strategies()


@router.get("/{uuid}/similar")
async def get_similar_cards(
    uuid: str,
    strategies: str = Query("keywords,tags", description="Comma-separated strategy names"),
    weights: str | None = Query(None, description="Comma-separated weights (must match strategies count)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    # Card filters (same as search endpoint)
    text: str | None = Query(None, description="Filter by oracle text"),
    sets: str | None = Query(None, description="Filter by set codes (comma-separated)"),
    rarity: str | None = Query(None, description="Filter by rarity"),
    type: str | None = Query(None, description="Filter by card type"),
    colors: str | None = Query(None, description="Filter by color identity"),
    format: str | None = Query(None, description="Filter by format legality"),
    keywords: str | None = Query(None, description="Filter by keywords (comma-separated)"),
    tags: str | None = Query(None, description="Filter by oracle tags (comma-separated)"),
    mana_value: str | None = Query(None, description="Filter by mana values (comma-separated)"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    owns: bool | None = Query(None, description="Filter by ownership"),
    wants: bool | None = Query(None, description="Filter by want status"),
) -> dict:
    """Find cards similar to the given card using composable strategies.

    Each strategy scores candidates differently. Results are merged by weighted
    average and include per-strategy score breakdowns. All standard card filters
    can be applied to narrow results.
    """
    from mtgsim.api.services.similarity_service import similarity_service

    strategy_list = [s.strip() for s in strategies.split(",") if s.strip()]
    weight_list = None
    if weights:
        weight_list = [float(w) for w in weights.split(",") if w.strip()]

    color_list = list(colors.upper()) if colors else None
    set_code_list = [s.strip() for s in sets.split(",") if s.strip()] if sets else None
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else None
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    mv_list = [int(v) for v in mana_value.split(",") if v.strip().isdigit()] if mana_value else None

    try:
        result = similarity_service.search_similar(
            card_uuid=uuid,
            strategy_names=strategy_list,
            weights=weight_list,
            limit=limit,
            rarity=rarity,
            card_type=type,
            text=text,
            colors=color_list,
            mana_values=mv_list,
            format_legal=format,
            keywords=keyword_list,
            tags=tag_list,
            set_codes=set_code_list,
            price_min=price_min,
            price_max=price_max,
            owns=owns,
            wants=wants,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if result is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    return result


@router.get("/{uuid}/features/compact")
async def get_card_features_compact(uuid: str) -> dict:
    """Get the compact (~60-dim) feature vector for a card.

    Keywords are grouped into functional categories (evasion, graveyard, etc.),
    subtypes collapsed to a boolean, and numeric values normalized 0-1.
    """
    from mtgdb.models import MJCard as MJCardModel
    from mtgdb.models import MJCardTag
    from mtgdb.session import get_session
    from sqlmodel import select

    from mtgsim.api.similarity.compact_vector import compact_dimension_names, compact_size, encode_compact

    with get_session() as session:
        card = session.exec(select(MJCardModel).where(MJCardModel.uuid == uuid)).first()
        if not card:
            raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")

        card_tags = list(session.exec(select(MJCardTag.tag).where(MJCardTag.card_name == card.name)).all())
        vec = encode_compact(card, tags=card_tags)
        dim_names = compact_dimension_names()

        features = {dim_names[i]: v for i, v in enumerate(vec) if v != 0.0}
        return {
            "uuid": uuid,
            "name": card.printed_name or card.name,
            "dimensions": compact_size(),
            "nonzero": len(features),
            "features": features,
            "vector": vec,
        }


@router.get("/{uuid}/features")
async def get_card_features(uuid: str) -> dict:
    """Get the feature vector for a card.

    Returns a sparse representation (only non-zero dimensions) and metadata.
    """
    from mtgdb.models import MJCard, MJCardTag
    from mtgdb.session import get_session
    from sqlmodel import select

    from mtgsim.api.similarity.feature_vector import encode_card, get_vocabulary

    with get_session() as session:
        card = session.exec(select(MJCard).where(MJCard.uuid == uuid)).first()
        if not card:
            raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")

        card_tags = list(session.exec(select(MJCardTag.tag).where(MJCardTag.card_name == card.name)).all())
        vec = encode_card(card, session, tags=card_tags)
        vocab = get_vocabulary()

        # Return sparse representation
        features = {vocab.dimension_names[i]: v for i, v in enumerate(vec) if v != 0.0}
        return {
            "uuid": uuid,
            "name": card.printed_name or card.name,
            "dimensions": vocab.size,
            "nonzero": len(features),
            "features": features,
        }


@router.get("/{uuid}/printings")
async def get_card_printings(uuid: str) -> list[dict]:
    """List all printings of a card with image URLs for a printing picker."""
    from mtgsim.api.data import decks_data

    result = decks_data.get_card_printings(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    return result


@router.get("/{uuid}", response_model=CardDetail)
async def get_card(uuid: str) -> CardDetail:
    """
    Get full card details.

    Returns complete card information with:
    - Card data (name, type, text, stats)
    - Prices from all sources
    - Format legalities
    - Deck appearances
    - Other printings
    - Collection status (owns, wants, quantities)
    """
    logger.debug(f"get_card: uuid={uuid}")
    card = await card_service.get_card(uuid)
    if card is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    logger.debug(f"get_card: found '{card.name}' ({card.set_code})")
    return card


@router.post("/{uuid}/collection", response_model=CollectionResponse)
async def add_card_to_collection(
    uuid: str,
    quantity_owned: int = Query(1, ge=0, description="Quantity owned (non-foil)"),
    quantity_owned_foil: int = Query(0, ge=0, description="Quantity owned (foil)"),
    quantity_wanted: int = Query(0, ge=0, description="Quantity wanted (non-foil)"),
    quantity_wanted_foil: int = Query(0, ge=0, description="Quantity wanted (foil)"),
) -> CollectionResponse:
    """
    Add a card to user's collection.

    - **uuid**: The UUID of the card to add to collection
    - **quantity_owned**: Number of non-foil copies owned
    - **quantity_owned_foil**: Number of foil copies owned
    - **quantity_wanted**: Number of non-foil copies wanted
    - **quantity_wanted_foil**: Number of foil copies wanted

    Returns success/failure status and details about the operation.
    """
    result = await card_service.add_card_to_collection(
        card_uuid=uuid,
        quantity_owned=quantity_owned,
        quantity_owned_foil=quantity_owned_foil,
        quantity_wanted=quantity_wanted,
        quantity_wanted_foil=quantity_wanted_foil,
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return CollectionResponse(**result)


@router.delete("/{uuid}/collection", response_model=CollectionResponse)
async def remove_card_from_collection(uuid: str) -> CollectionResponse:
    """Remove a card from user's collection."""
    result = await card_service.remove_card_from_collection(uuid)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return CollectionResponse(**result)


@router.put("/{uuid}/rating", response_model=QuadrantRatingResponse)
async def set_quadrant_rating(uuid: str, req: QuadrantRatingRequest) -> QuadrantRatingResponse:
    """Set quadrant theory rating for a card (developing, ahead, behind, parity)."""
    from mtgsim.api.data import cards_data

    result = cards_data.set_quadrant_rating(
        card_uuid=uuid,
        developing=req.developing,
        ahead=req.ahead,
        behind=req.behind,
        parity=req.parity,
        notes=req.notes,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"Card not found: {uuid}")
    return QuadrantRatingResponse(**result)


@router.get("/{uuid}/rating", response_model=QuadrantRatingResponse)
async def get_quadrant_rating(uuid: str) -> QuadrantRatingResponse:
    """Get quadrant theory rating for a card."""
    from mtgsim.api.data import cards_data

    result = cards_data.get_quadrant_rating(uuid)
    if result is None:
        return QuadrantRatingResponse()
    return QuadrantRatingResponse(**result)

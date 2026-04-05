"""Scan service — orchestrates card image extraction, matching, and optional collection/deck adds."""

import logging
import time

from mtgdb.models import MJCard
from mtgdb.session import get_session
from sqlmodel import select

from mtgsim.api.data import cards_data
from mtgsim.api.models.card import CardSummary
from mtgsim.api.models.scan import ExtractionDetail, ScanResponse
from mtgsim.deck_import import MatchResult, _load_card_name_index, match_card_by_name
from mtgsim.extract.pipelines import ExtractionPipeline, get_pipeline
from mtgsim.extract.preprocess import preprocess_card_image
from mtgsim.scan_log.db import log_llm_call, log_scan
from mtgsim.settings import settings

logger = logging.getLogger("mtgsim.api.services.scan")


def _ms_since(start: float) -> float:
    return (time.perf_counter() - start) * 1000


class ScanService:
    """Orchestrates scan: preprocess -> extract -> match -> optional add."""

    def __init__(self, default_pipeline: str = "openai"):
        self.default_pipeline = default_pipeline
        self._name_index: dict[str, str] | None = None
        self._name_list: list[str] | None = None

    def _ensure_name_index(self) -> None:
        """Lazily load and cache the card name index."""
        if self._name_index is None:
            with get_session() as session:
                self._name_index = _load_card_name_index(session)
                self._name_list = list(self._name_index.keys())

    def _resolve_printing(self, name: str, set_code: str, collector_number: str) -> str | None:
        """Try to find the exact printing UUID by set code and/or collector number."""
        # DB stores set codes in uppercase
        sc = set_code.upper() if set_code else ""

        with get_session() as session:
            # Best: set_code + collector_number
            if sc and collector_number:
                uuid = session.exec(
                    select(MJCard.uuid).where(MJCard.set_code == sc, MJCard.number == collector_number)
                ).first()
                if uuid:
                    return uuid

            # Next: name + set_code
            if sc:
                uuid = session.exec(
                    select(MJCard.uuid).where(MJCard.name == name, MJCard.set_code == sc)
                ).first()
                if uuid:
                    return uuid

        return None

    async def scan_card(
        self,
        image_data: bytes,
        mime_type: str,
        pipeline_name: str | None = None,
        add_to_collection: bool = False,
        deck_id: int | None = None,
    ) -> ScanResponse:
        t_total = time.perf_counter()

        pipeline_name = pipeline_name or self.default_pipeline
        pipeline: ExtractionPipeline = get_pipeline(pipeline_name)

        # Preprocess image
        t0 = time.perf_counter()
        processed_data, processed_mime = preprocess_card_image(image_data, mime_type)
        preprocess_ms = _ms_since(t0)

        # Extract card data from image
        t0 = time.perf_counter()
        result = pipeline.extract_bytes_with_usage(processed_data, processed_mime)
        extracted = result.card
        llm_usage = result.llm_usage
        extract_ms = _ms_since(t0)
        logger.info(f"Extracted card: {extracted.name} via {pipeline_name}")

        extraction_detail = ExtractionDetail(
            name=extracted.name,
            mana_cost=extracted.mana_cost,
            card_types=[t.value for t in extracted.card_types],
            subtypes=extracted.subtypes,
            oracle_text=extracted.oracle_text,
            rarity=extracted.rarity.value,
            power=extracted.power,
            toughness=extracted.toughness,
            set_code=extracted.set_code,
            set_name=extracted.set_name,
            collector_number=extracted.collector_number,
            finish=extracted.finish.value,
            language=extracted.language,
            border_color=extracted.border_color,
            frame_version=extracted.frame_version,
            is_promo=extracted.is_promo,
            is_reprint=extracted.is_reprint,
        )

        # Match against database — try specific printing first, fall back to name
        t0 = time.perf_counter()
        self._ensure_name_index()
        match = match_card_by_name(
            extracted.name, self._name_index, self._name_list, threshold=settings.scan_fuzzy_threshold
        )

        # Refine to exact printing if set_code/collector_number available
        if match.uuid and (extracted.set_code or extracted.collector_number):
            refined_uuid = self._resolve_printing(
                match.matched_name or extracted.name, extracted.set_code, extracted.collector_number
            )
            if refined_uuid:
                match.uuid = refined_uuid

        match_ms = _ms_since(t0)

        card_summary = _build_card_summary(match) if match.uuid else None

        collection_added = False
        deck_added = None

        if match.uuid and add_to_collection:
            cards_data.add_to_collection(card_uuid=match.uuid, quantity_owned=1)
            collection_added = True

        if match.uuid and deck_id is not None:
            from mtgsim.api.data import decks_data

            decks_data.add_card_to_deck(deck_id=deck_id, card_uuid=match.uuid, count=1, board="main")
            deck_added = deck_id

        total_ms = _ms_since(t_total)

        # Log to scan database (fire-and-forget, don't fail the request)
        try:
            scan_id = log_scan(
                pipeline=pipeline_name,
                image_data=image_data,
                mime_type=mime_type,
                extracted_name=extracted.name,
                raw_text=extracted.raw_text,
                matched=match.uuid is not None,
                match_type=match.match_type,
                match_confidence=match.score,
                matched_card_uuid=match.uuid,
                matched_card_name=match.matched_name,
                added_to_collection=collection_added,
                added_to_deck_id=deck_added,
                timing={
                    "preprocess_ms": round(preprocess_ms, 2),
                    "extract_ms": round(extract_ms, 2),
                    "match_ms": round(match_ms, 2),
                    "total_ms": round(total_ms, 2),
                },
                params={"pipeline": pipeline_name, "fuzzy_threshold": settings.scan_fuzzy_threshold},
            )
            # Log LLM call linked to this scan
            if llm_usage:
                log_llm_call(
                    provider=llm_usage.provider,
                    model=llm_usage.model,
                    purpose="card_extraction",
                    prompt_tokens=llm_usage.prompt_tokens,
                    completion_tokens=llm_usage.completion_tokens,
                    latency_ms=llm_usage.latency_ms,
                    status=llm_usage.status,
                    scan_id=scan_id,
                    error_message=llm_usage.error_message,
                )
        except Exception:
            logger.exception("Failed to log scan attempt")

        return ScanResponse(
            extracted_name=extracted.name,
            matched=match.uuid is not None,
            match_type=match.match_type,
            match_confidence=match.score,
            card=card_summary,
            extraction=extraction_detail,
            added_to_collection=collection_added,
            added_to_deck=deck_added,
        )


def _build_card_summary(match: MatchResult) -> CardSummary | None:
    """Look up the matched card and return a CardSummary."""
    card = cards_data.get_card(match.uuid)
    if not card:
        return None
    return CardSummary(
        uuid=card["uuid"],
        name=card["name"],
        type=card.get("type", ""),
        mana_cost=card.get("mana_cost"),
        mana_value=card.get("mana_value"),
        rarity=card.get("rarity", ""),
        set_code=card.get("set_code", ""),
        color_identity=card.get("color_identity", []),
        tags=card.get("tags", []),
        text=card.get("oracle_text"),
        price=card.get("price"),
        image_url=card.get("image_url"),
        owns=card.get("owns", False),
        wants=card.get("wants", False),
        total_owned=card.get("total_owned", 0),
        total_wanted=card.get("total_wanted", 0),
    )


scan_service = ScanService(default_pipeline=settings.scan_default_pipeline)

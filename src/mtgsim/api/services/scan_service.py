"""Scan service — orchestrates card image extraction, matching, and optional collection/deck adds."""

import logging

from mtgdb.session import get_session

from mtgsim.api.data import cards_data
from mtgsim.api.models.card import CardSummary
from mtgsim.api.models.scan import ExtractionDetail, ScanResponse
from mtgsim.deck_import import MatchResult, _load_card_name_index, match_card_by_name
from mtgsim.extract.pipelines import ExtractionPipeline, get_pipeline
from mtgsim.extract.preprocess import preprocess_card_image
from mtgsim.settings import settings

logger = logging.getLogger("mtgsim.api.services.scan")


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

    async def scan_card(
        self,
        image_data: bytes,
        mime_type: str,
        pipeline_name: str | None = None,
        add_to_collection: bool = False,
        deck_id: int | None = None,
    ) -> ScanResponse:
        pipeline_name = pipeline_name or self.default_pipeline
        pipeline: ExtractionPipeline = get_pipeline(pipeline_name)

        # Preprocess image
        processed_data, processed_mime = preprocess_card_image(image_data, mime_type)

        # Extract card data from image
        extracted = pipeline.extract_bytes(processed_data, processed_mime)
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
        )

        # Match against database
        self._ensure_name_index()
        match = match_card_by_name(
            extracted.name, self._name_index, self._name_list, threshold=settings.scan_fuzzy_threshold
        )

        card_summary = _build_card_summary(match) if match.uuid else None

        added_to_collection = False
        added_to_deck = None

        if match.uuid and add_to_collection:
            cards_data.add_to_collection(card_uuid=match.uuid, quantity_owned=1)
            added_to_collection = True

        if match.uuid and deck_id is not None:
            from mtgsim.api.data import decks_data

            decks_data.add_card_to_deck(deck_id=deck_id, card_uuid=match.uuid, count=1, board="main")
            added_to_deck = deck_id

        return ScanResponse(
            extracted_name=extracted.name,
            matched=match.uuid is not None,
            match_type=match.match_type,
            match_confidence=match.score,
            card=card_summary,
            extraction=extraction_detail,
            added_to_collection=added_to_collection,
            added_to_deck=added_to_deck,
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

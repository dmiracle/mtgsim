"""Scan-related Pydantic models."""

from pydantic import BaseModel

from mtgsim.api.models.card import CardSummary
from mtgsim.domain.card import ManaCost


class ExtractionDetail(BaseModel):
    """Raw extraction output from the vision pipeline."""

    name: str
    mana_cost: ManaCost | None = None
    card_types: list[str] = []
    subtypes: list[str] = []
    oracle_text: str = ""
    rarity: str = "common"
    power: int | None = None
    toughness: int | None = None
    set_code: str = ""
    set_name: str = ""
    collector_number: str = ""
    finish: str = "normal"
    language: str = "en"
    border_color: str = ""
    frame_version: str = ""
    is_promo: bool = False
    is_reprint: bool = False


class ScanResponse(BaseModel):
    """Response from the card scan endpoint."""

    extracted_name: str
    matched: bool
    match_type: str  # "exact", "fuzzy", "none"
    match_confidence: float | None = None
    card: CardSummary | None = None
    extraction: ExtractionDetail
    added_to_collection: bool = False
    added_to_deck: int | None = None

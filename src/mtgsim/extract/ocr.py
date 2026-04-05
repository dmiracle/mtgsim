"""Tesseract-based OCR extraction pipeline.

Extracts all text from a card image using tesseract, then matches the raw text
against known cards using pluggable matching strategies. All parameters for
image preprocessing, OCR configuration, and text matching are configurable.
"""

import io
import logging
from pathlib import Path

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from pydantic import BaseModel

from mtgsim.domain.card import Card
from mtgsim.extract.matching import (
    CardRecord,
    FuzzyTextMatch,
    TextMatchParams,
    TextMatchStrategy,
)
from mtgsim.extract.pipelines import ExtractionPipeline

logger = logging.getLogger("mtgsim.extract.ocr")


class OCRPreprocessParams(BaseModel):
    """Image preprocessing parameters for OCR. All tunable."""

    # Convert to grayscale before OCR
    grayscale: bool = True

    # Contrast enhancement factor (1.0 = no change, >1 = more contrast)
    contrast: float = 1.5

    # Sharpness enhancement factor (1.0 = no change, >1 = sharper)
    sharpness: float = 2.0

    # Resize scale factor (relative to original). Upscaling can help tesseract.
    scale: float = 2.0

    # Binarize with threshold (0 = disabled, 1-255 = threshold value)
    binarize_threshold: int = 0

    # Apply median filter to reduce noise (0 = disabled, odd int = kernel size)
    denoise_kernel: int = 0


class OCRParams(BaseModel):
    """Tesseract OCR configuration."""

    # Page segmentation mode. 6 = uniform block of text, 3 = fully automatic.
    psm: int = 6

    # Language (eng = English). Tesseract must have the language data installed.
    lang: str = "eng"

    # Character allowlist (empty = all characters)
    allowlist: str = ""

    # Tesseract config string (advanced, passed directly)
    extra_config: str = ""


def preprocess_for_ocr(img: Image.Image, params: OCRPreprocessParams | None = None) -> Image.Image:
    """Apply preprocessing to an image for better OCR results."""
    params = params or OCRPreprocessParams()

    # EXIF rotation
    img = ImageOps.exif_transpose(img)

    # Convert mode
    if params.grayscale:
        img = img.convert("L")
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Scale up
    if params.scale != 1.0:
        w, h = img.size
        img = img.resize((int(w * params.scale), int(h * params.scale)), Image.LANCZOS)

    # Contrast
    if params.contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(params.contrast)

    # Sharpness
    if params.sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(params.sharpness)

    # Denoise
    if params.denoise_kernel > 0:
        img = img.filter(ImageFilter.MedianFilter(size=params.denoise_kernel))

    # Binarize
    if params.binarize_threshold > 0:
        img = img.point(lambda x: 255 if x > params.binarize_threshold else 0)

    return img


def run_tesseract(img: Image.Image, params: OCRParams | None = None) -> str:
    """Run tesseract OCR on a preprocessed image and return raw text."""
    params = params or OCRParams()

    config_parts = [f"--psm {params.psm}"]
    if params.allowlist:
        config_parts.append(f"-c tessedit_char_whitelist={params.allowlist}")
    if params.extra_config:
        config_parts.append(params.extra_config)

    config = " ".join(config_parts)
    text = pytesseract.image_to_string(img, lang=params.lang, config=config)
    return text.strip()


class TesseractExtractionPipeline(ExtractionPipeline):
    """OCR-based extraction: tesseract text -> text matching -> Card.

    All parameters are configurable:
    - preprocess_params: image preprocessing before OCR
    - ocr_params: tesseract configuration
    - match_params: text matching thresholds and weights
    - match_strategy: pluggable matching algorithm (default: FuzzyTextMatch)
    """

    def __init__(
        self,
        preprocess_params: OCRPreprocessParams | None = None,
        ocr_params: OCRParams | None = None,
        match_params: TextMatchParams | None = None,
        match_strategy: TextMatchStrategy | None = None,
    ):
        self.preprocess_params = preprocess_params or OCRPreprocessParams()
        self.ocr_params = ocr_params or OCRParams()
        self.match_params = match_params or TextMatchParams()
        self.match_strategy = match_strategy or FuzzyTextMatch()
        self._cards: list[CardRecord] | None = None

    def _ensure_card_index(self) -> None:
        """Lazily load card records from the database."""
        if self._cards is not None:
            return

        from mtgdb.models import MJCard
        from mtgdb.session import get_session
        from sqlmodel import select

        with get_session() as session:
            rows = session.exec(select(MJCard.uuid, MJCard.name, MJCard.type_line, MJCard.oracle_text)).all()

        # Deduplicate by name — keep one representative per card name
        seen_names: dict[str, CardRecord] = {}
        for uuid, name, type_line, oracle_text in rows:
            if name not in seen_names:
                seen_names[name] = CardRecord(
                    uuid=uuid,
                    name=name,
                    type_line=type_line or "",
                    oracle_text=oracle_text or "",
                )
        self._cards = list(seen_names.values())
        logger.info(f"Loaded {len(self._cards)} unique card names for OCR matching")

    def _ocr_image(self, img: Image.Image) -> str:
        """Preprocess and OCR an image."""
        processed = preprocess_for_ocr(img, self.preprocess_params)
        text = run_tesseract(processed, self.ocr_params)
        logger.debug(f"OCR raw text: {text!r}")
        return text

    def _match_and_build_card(self, ocr_text: str) -> Card:
        """Match OCR text against known cards and return a Card domain object."""
        self._ensure_card_index()
        matches = self.match_strategy.match(ocr_text, self._cards, self.match_params)

        if matches:
            best = matches[0]
            logger.info(f"OCR matched: {best.card_name} (score={best.score}, components={best.component_scores})")
            # Find the full card record to populate the Card object
            card_rec = next((c for c in self._cards if c.uuid == best.card_uuid), None)
            return Card(
                name=best.card_name,
                raw_text=ocr_text,
                oracle_text=card_rec.oracle_text if card_rec else "",
            )

        logger.warning(f"OCR no match for text: {ocr_text[:100]!r}")
        # Return a Card with just the raw text — the scan endpoint handles no-match
        # by using the extracted name for fuzzy matching at the service layer
        first_line = ocr_text.strip().splitlines()[0] if ocr_text.strip() else "Unknown"
        return Card(name=first_line, raw_text=ocr_text)

    def extract(self, image_path: Path) -> Card:
        img = Image.open(image_path)
        ocr_text = self._ocr_image(img)
        card = self._match_and_build_card(ocr_text)
        card.image_url = str(image_path)
        return card

    def extract_bytes(self, data: bytes, mime_type: str) -> Card:
        img = Image.open(io.BytesIO(data))
        ocr_text = self._ocr_image(img)
        return self._match_and_build_card(ocr_text)

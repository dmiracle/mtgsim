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
    contrast: float = 2.0

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

    # Page segmentation mode. 3 = fully automatic (best for cards with mixed regions).
    psm: int = 3

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


# Standard MTG card regions as percentage of height (portrait orientation).
# Card aspect ratio is ~63:88 (0.716).
CARD_REGIONS = {
    "name": (0.0, 0.07),  # Card name + mana cost
    "type_line": (0.07, 0.13),  # Type line
    "art": (0.13, 0.55),  # Card art (skip for OCR)
    "text_box": (0.55, 0.87),  # Oracle text + flavor text
    "footer": (0.87, 1.0),  # Collector number, set code, artist
}

# Aspect ratio range for a portrait-oriented MTG card
CARD_ASPECT_MIN = 0.60
CARD_ASPECT_MAX = 0.80


def detect_orientation(img: Image.Image) -> int:
    """Detect card orientation by testing rotations. Returns degrees (0, 90, 180, 270).

    Uses a simple heuristic: a correctly oriented card is taller than wide
    (portrait, aspect ratio ~0.72). If the image is landscape, try 90/270.
    Then pick the rotation that produces the most readable text from the
    text box region.
    """
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    ratio = w / h

    # Already portrait
    if CARD_ASPECT_MIN <= ratio <= CARD_ASPECT_MAX:
        return 0

    # Landscape — could be 90 or 270
    if ratio > 1.0:
        rotations = [90, 270]
    else:
        # Unusual ratio — try all
        rotations = [0, 90, 180, 270]

    best_rotation = 0
    best_text_len = 0

    for deg in rotations:
        rotated = img.rotate(deg, expand=True)
        rw, rh = rotated.size
        if not (CARD_ASPECT_MIN <= rw / rh <= CARD_ASPECT_MAX):
            continue
        # Quick OCR on text box region
        text_region = rotated.crop((0, int(rh * 0.55), rw, int(rh * 0.87)))
        processed = preprocess_for_ocr(text_region, OCRPreprocessParams(scale=2.0, contrast=2.0))
        text = run_tesseract(processed, OCRParams(psm=3))
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count > best_text_len:
            best_text_len = alpha_count
            best_rotation = deg

    return best_rotation


def extract_card_regions(img: Image.Image) -> dict[str, Image.Image]:
    """Split a portrait-oriented card image into named regions."""
    w, h = img.size
    regions = {}
    for name, (start, end) in CARD_REGIONS.items():
        regions[name] = img.crop((0, int(h * start), w, int(h * end)))
    return regions


def _text_quality(text: str) -> float:
    """Score text quality. Real English text scores higher than OCR garbage.

    Heuristic: count words >= 3 chars long that are mostly alphabetic.
    Garbage OCR produces short fragments with lots of symbols.
    """
    words = text.split()
    if not words:
        return 0.0
    good_words = [w for w in words if len(w) >= 3 and sum(c.isalpha() for c in w) / len(w) > 0.7]
    return len(good_words)


def ocr_card_regions(img: Image.Image, params: OCRPreprocessParams | None = None) -> str:
    """OCR a card image by extracting text from individual regions (skipping art).

    Returns all text concatenated with region labels for matching.
    """
    params = params or OCRPreprocessParams()
    regions = extract_card_regions(img)

    parts = []

    # Name bar — single line, high scale for small text
    name_params = OCRPreprocessParams(
        grayscale=params.grayscale,
        contrast=params.contrast,
        sharpness=params.sharpness,
        scale=3.0,
    )
    name_img = preprocess_for_ocr(regions["name"], name_params)
    name_text = run_tesseract(name_img, OCRParams(psm=7)).strip()
    if name_text:
        parts.append(name_text)

    # Type line — single line
    type_img = preprocess_for_ocr(regions["type_line"], name_params)
    type_text = run_tesseract(type_img, OCRParams(psm=7)).strip()
    if type_text:
        parts.append(type_text)

    # Text box — main content, fully automatic
    text_img = preprocess_for_ocr(regions["text_box"], params)
    text_text = run_tesseract(text_img, OCRParams(psm=3)).strip()
    if text_text:
        parts.append(text_text)

    # Footer — collector info
    footer_img = preprocess_for_ocr(regions["footer"], params)
    footer_text = run_tesseract(footer_img, OCRParams(psm=6)).strip()
    if footer_text:
        parts.append(footer_text)

    return "\n".join(parts)


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
        """Orient, extract text, and pick the best OCR result.

        Tries both region-based OCR (skipping art) and full-image OCR,
        then returns whichever produced more readable text.
        """
        img = ImageOps.exif_transpose(img)

        # Detect and correct orientation
        rotation = detect_orientation(img)
        if rotation:
            img = img.rotate(rotation, expand=True)
            logger.debug(f"Rotated image {rotation}°")

        # Try both approaches
        region_text = ocr_card_regions(img, self.preprocess_params)
        full_processed = preprocess_for_ocr(img, self.preprocess_params)
        full_text = run_tesseract(full_processed, self.ocr_params)

        # Pick the one with better text quality.
        # Real text has longer average word length than OCR garbage.
        region_score = _text_quality(region_text)
        full_score = _text_quality(full_text)

        if region_score > full_score:
            logger.debug(f"Using region OCR (quality={region_score:.1f} vs {full_score:.1f})")
            return region_text
        else:
            logger.debug(f"Using full-image OCR (quality={full_score:.1f} vs {region_score:.1f})")
            return full_text

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

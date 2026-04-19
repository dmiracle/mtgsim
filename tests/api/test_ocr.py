"""Tests for the tesseract OCR pipeline and text matching strategies."""

import io

from PIL import Image

from mtgsim.extract.matching import (
    CardRecord,
    FuzzyTextMatch,
    TextMatchParams,
)


def _make_test_image(fmt: str = "JPEG") -> bytes:
    img = Image.new("RGB", (100, 140), color="white")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


# --- Text matching strategy tests ---


SAMPLE_CARDS = [
    CardRecord(
        uuid="uuid-1",
        name="Lightning Bolt",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
    ),
    CardRecord(
        uuid="uuid-2",
        name="Child of Night",
        type_line="Creature — Vampire",
        oracle_text="Lifelink",
    ),
    CardRecord(
        uuid="uuid-3",
        name="Shivan Dragon",
        type_line="Creature — Dragon",
        oracle_text="Flying\n{R}: Shivan Dragon gets +1/+0 until end of turn.",
    ),
    CardRecord(
        uuid="uuid-4",
        name="Duress",
        type_line="Sorcery",
        oracle_text=(
            "Target opponent reveals their hand. You choose a noncreature, "
            "nonland card from it. That player discards that card."
        ),
    ),
]


class TestFuzzyTextMatch:
    """Tests for the FuzzyTextMatch strategy."""

    def test_exact_name_match(self):
        strategy = FuzzyTextMatch()
        results = strategy.match("Lightning Bolt", SAMPLE_CARDS)
        assert len(results) > 0
        assert results[0].card_name == "Lightning Bolt"
        assert results[0].component_scores["name"] == 100.0

    def test_ocr_noisy_name_match(self):
        """Noisy OCR text should still match the right card."""
        strategy = FuzzyTextMatch()
        # Typical OCR noise: extra chars, partial words
        results = strategy.match("Lightn1ng Bolt\nInstant\nLightning Bolt deals 3 damage", SAMPLE_CARDS)
        assert len(results) > 0
        assert results[0].card_name == "Lightning Bolt"

    def test_multiline_ocr_text(self):
        """Full card OCR text should boost match confidence via oracle text."""
        strategy = FuzzyTextMatch()
        ocr_text = "Child of Night\nCreature — Vampire\nLifelink"
        results = strategy.match(ocr_text, SAMPLE_CARDS)
        assert len(results) > 0
        assert results[0].card_name == "Child of Night"
        assert results[0].score > 70

    def test_no_match_below_threshold(self):
        """Garbage text should not match anything."""
        strategy = FuzzyTextMatch()
        params = TextMatchParams(threshold=80)
        results = strategy.match("xyzzy random gibberish 12345", SAMPLE_CARDS, params)
        assert len(results) == 0

    def test_threshold_configurable(self):
        """Lower threshold returns more results."""
        strategy = FuzzyTextMatch()
        low = TextMatchParams(threshold=30)
        high = TextMatchParams(threshold=90)
        results_low = strategy.match("Bolt", SAMPLE_CARDS, low)
        results_high = strategy.match("Bolt", SAMPLE_CARDS, high)
        assert len(results_low) >= len(results_high)

    def test_max_results_respected(self):
        strategy = FuzzyTextMatch()
        params = TextMatchParams(threshold=10, max_results=2)
        results = strategy.match("creature", SAMPLE_CARDS, params)
        assert len(results) <= 2

    def test_component_scores_present(self):
        """Results should have per-field score breakdown."""
        strategy = FuzzyTextMatch()
        results = strategy.match("Child of Night\nCreature — Vampire\nLifelink", SAMPLE_CARDS)
        assert len(results) > 0
        scores = results[0].component_scores
        assert "name" in scores

    def test_weight_affects_ranking(self):
        """Heavily weighting oracle text should favor cards with matching text."""
        strategy = FuzzyTextMatch()
        # Text that matches Duress oracle text but not name
        ocr_text = "Target opponent reveals their hand"
        oracle_heavy = TextMatchParams(name_weight=0.5, oracle_text_weight=5.0, threshold=30)
        results = strategy.match(ocr_text, SAMPLE_CARDS, oracle_heavy)
        assert len(results) > 0
        # Duress should rank high due to oracle text match
        duress_results = [r for r in results if r.card_name == "Duress"]
        assert len(duress_results) > 0

    def test_different_scorer(self):
        """Different scorers should work."""
        strategy = FuzzyTextMatch()
        params = TextMatchParams(name_scorer="WRatio", text_scorer="ratio", threshold=50)
        results = strategy.match("Lightning Bolt Instant", SAMPLE_CARDS, params)
        assert len(results) > 0


class TestOCRPreprocessing:
    """Tests for OCR image preprocessing."""

    def test_preprocess_produces_image(self):
        from mtgsim.extract.ocr import preprocess_for_ocr

        img = Image.new("RGB", (200, 280), color="white")
        result = preprocess_for_ocr(img)
        assert isinstance(result, Image.Image)

    def test_grayscale_conversion(self):
        from mtgsim.extract.ocr import OCRPreprocessParams, preprocess_for_ocr

        img = Image.new("RGB", (100, 140), color="red")
        params = OCRPreprocessParams(grayscale=True, scale=1.0, contrast=1.0, sharpness=1.0)
        result = preprocess_for_ocr(img, params)
        assert result.mode == "L"

    def test_scale_factor(self):
        from mtgsim.extract.ocr import OCRPreprocessParams, preprocess_for_ocr

        img = Image.new("RGB", (100, 140), color="white")
        params = OCRPreprocessParams(scale=3.0, grayscale=False, contrast=1.0, sharpness=1.0)
        result = preprocess_for_ocr(img, params)
        assert result.size == (300, 420)

    def test_binarize(self):
        from mtgsim.extract.ocr import OCRPreprocessParams, preprocess_for_ocr

        img = Image.new("L", (100, 140), color=128)
        params = OCRPreprocessParams(grayscale=True, scale=1.0, contrast=1.0, sharpness=1.0, binarize_threshold=100)
        result = preprocess_for_ocr(img, params)
        pixels = list(result.getdata())
        assert all(p in (0, 255) for p in pixels)


class TestTesseractPipeline:
    """Integration tests for the tesseract pipeline via the scan endpoint."""

    def test_scan_with_tesseract_pipeline(self, client):
        """Tesseract pipeline returns 200 and valid response shape."""
        data = _make_test_image()
        response = client.post(
            "/api/cards/scan?pipeline=tesseract",
            files={"image": ("card.jpg", data, "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert "extracted_name" in body
        assert "matched" in body
        assert "extraction" in body

    def test_tesseract_available_in_factory(self):
        """Tesseract is registered in the pipeline factory."""
        from mtgsim.extract.pipelines import get_pipeline

        pipeline = get_pipeline("tesseract")
        assert pipeline is not None

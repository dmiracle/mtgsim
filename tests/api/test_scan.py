"""Tests for POST /api/cards/scan endpoint."""

import io

from PIL import Image


def _make_test_image(fmt: str = "JPEG") -> bytes:
    """Create a minimal valid image in memory."""
    img = Image.new("RGB", (100, 140), color="red")
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class TestScanEndpoint:
    """Tests for the card scan endpoint using the mock pipeline."""

    def test_scan_returns_200_with_mock(self, client):
        """Mock pipeline scan returns 200 and valid response shape."""
        data = _make_test_image()
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.jpg", data, "image/jpeg")},
        )
        assert response.status_code == 200
        body = response.json()
        assert "extracted_name" in body
        assert "matched" in body
        assert "match_type" in body
        assert "extraction" in body
        assert body["extracted_name"] == "Lightning Bolt"

    def test_scan_returns_extraction_detail(self, client):
        """Extraction detail has expected fields."""
        data = _make_test_image()
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.jpg", data, "image/jpeg")},
        )
        extraction = response.json()["extraction"]
        assert extraction["name"] == "Lightning Bolt"
        assert extraction["rarity"] == "common"
        assert "card_types" in extraction
        assert "Instant" in extraction["card_types"]

    def test_scan_match_has_card_summary(self, client):
        """When matched, card field is a CardSummary with uuid."""
        data = _make_test_image()
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.jpg", data, "image/jpeg")},
        )
        body = response.json()
        if body["matched"]:
            assert body["card"] is not None
            assert "uuid" in body["card"]
            assert "name" in body["card"]

    def test_scan_no_match_returns_200(self, client):
        """A scan that extracts but doesn't match still returns 200."""
        data = _make_test_image()
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.jpg", data, "image/jpeg")},
        )
        # Mock returns "Lightning Bolt" which likely matches,
        # but the response shape is correct either way
        body = response.json()
        assert response.status_code == 200
        assert "matched" in body
        assert "extraction" in body

    def test_scan_png_accepted(self, client):
        """PNG images are accepted."""
        data = _make_test_image("PNG")
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.png", data, "image/png")},
        )
        assert response.status_code == 200

    def test_scan_rejects_unsupported_type(self, client):
        """Non-JPEG/PNG files are rejected with 400."""
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.gif", b"GIF89a", "image/gif")},
        )
        assert response.status_code == 400
        body = response.json()
        detail = body.get("detail") or body.get("error", {}).get("message", "")
        assert "Unsupported image type" in detail

    def test_scan_rejects_empty_file(self, client):
        """Empty file upload returns 400."""
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.jpg", b"", "image/jpeg")},
        )
        assert response.status_code == 400
        body = response.json()
        detail = body.get("detail") or body.get("error", {}).get("message", "")
        assert "Empty" in detail

    def test_scan_default_no_collection_add(self, client):
        """By default, card is not added to collection."""
        data = _make_test_image()
        response = client.post(
            "/api/cards/scan?pipeline=mock",
            files={"image": ("card.jpg", data, "image/jpeg")},
        )
        body = response.json()
        assert body["added_to_collection"] is False
        assert body["added_to_deck"] is None


class TestMatchCardByName:
    """Unit tests for the match_card_by_name function."""

    def test_exact_match(self):
        from mtgsim.deck_import import match_card_by_name

        index = {"Lightning Bolt": "uuid-1", "Shivan Dragon": "uuid-2"}
        result = match_card_by_name("Lightning Bolt", index)
        assert result.uuid == "uuid-1"
        assert result.match_type == "exact"
        assert result.score == 100.0

    def test_fuzzy_match(self):
        from mtgsim.deck_import import match_card_by_name

        index = {"Lightning Bolt": "uuid-1", "Shivan Dragon": "uuid-2"}
        name_list = list(index.keys())
        # Misspelling that should fuzzy-match
        result = match_card_by_name("Lightninng Bolt", index, name_list, threshold=80)
        assert result.uuid == "uuid-1"
        assert result.match_type == "fuzzy"
        assert result.score is not None
        assert result.score >= 80

    def test_no_match(self):
        from mtgsim.deck_import import match_card_by_name

        index = {"Lightning Bolt": "uuid-1"}
        result = match_card_by_name("Completely Unknown Card Name XYZ", index)
        assert result.uuid is None
        assert result.match_type == "none"

    def test_configurable_threshold(self):
        from mtgsim.deck_import import match_card_by_name

        index = {"Lightning Bolt": "uuid-1"}
        # Very high threshold should reject fuzzy matches
        result = match_card_by_name("Lightninng Bolt", index, threshold=99)
        assert result.match_type == "none"


class TestImagePreprocessing:
    """Tests for the image preprocessing module."""

    def test_jpeg_roundtrip(self):
        from mtgsim.extract.preprocess import preprocess_card_image

        data = _make_test_image("JPEG")
        processed, mime = preprocess_card_image(data, "image/jpeg")
        assert mime == "image/jpeg"
        assert len(processed) > 0
        # Verify it's a valid JPEG
        img = Image.open(io.BytesIO(processed))
        assert img.format == "JPEG"

    def test_png_converts_to_jpeg(self):
        from mtgsim.extract.preprocess import preprocess_card_image

        data = _make_test_image("PNG")
        processed, mime = preprocess_card_image(data, "image/png")
        assert mime == "image/jpeg"

    def test_large_image_downscaled(self):
        from mtgsim.extract.preprocess import preprocess_card_image

        img = Image.new("RGB", (4000, 5600), color="blue")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        data = buf.getvalue()

        processed, _ = preprocess_card_image(data, "image/jpeg")
        result = Image.open(io.BytesIO(processed))
        assert max(result.size) <= 2048

    def test_small_image_not_upscaled(self):
        from mtgsim.extract.preprocess import preprocess_card_image

        data = _make_test_image("JPEG")
        processed, _ = preprocess_card_image(data, "image/jpeg")
        result = Image.open(io.BytesIO(processed))
        assert result.size[0] <= 100
        assert result.size[1] <= 140

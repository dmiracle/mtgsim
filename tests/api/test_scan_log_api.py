"""Tests for the scan log API endpoints."""

import io
import os
import tempfile

from PIL import Image

from mtgsim.scan_log import db as scan_log_db
from mtgsim.scan_log.db import log_scan


def _make_test_image() -> bytes:
    img = Image.new("RGB", (100, 140), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _use_temp_db():
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    os.environ["SCAN_LOG_DB_PATH"] = path
    # Force engine re-creation so queries module picks up the new path
    scan_log_db._engine = None
    return path


def _cleanup_temp_db(path):
    scan_log_db._engine = None
    os.environ.pop("SCAN_LOG_DB_PATH", None)
    os.unlink(path)


def _seed_scans():
    """Create a few scan entries for testing."""
    data = _make_test_image()
    log_scan(
        pipeline="mock",
        image_data=data,
        mime_type="image/jpeg",
        extracted_name="Lightning Bolt",
        raw_text="Lightning Bolt\nInstant",
        matched=True,
        match_type="exact",
        match_confidence=100.0,
        matched_card_uuid="uuid-1",
        matched_card_name="Lightning Bolt",
        added_to_collection=False,
        added_to_deck_id=None,
        timing={"preprocess_ms": 10, "extract_ms": 5, "match_ms": 3, "total_ms": 20},
        params={"pipeline": "mock"},
    )
    log_scan(
        pipeline="tesseract",
        image_data=data,
        mime_type="image/jpeg",
        extracted_name="Zl",
        raw_text="Zl\ngarbage",
        matched=False,
        match_type="none",
        match_confidence=None,
        matched_card_uuid=None,
        matched_card_name=None,
        added_to_collection=False,
        added_to_deck_id=None,
        timing={"preprocess_ms": 15, "extract_ms": 200, "match_ms": 50, "total_ms": 270},
        params={"pipeline": "tesseract", "ocr_psm": 6},
    )


class TestScanLogAPI:
    def test_dashboard_returns_html(self, client):
        response = client.get("/api/scan-log/dashboard")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Scan Tuning Dashboard" in response.text

    def test_stats_endpoint(self, client):
        path = _use_temp_db()
        try:
            _seed_scans()
            response = client.get("/api/scan-log/stats")
            assert response.status_code == 200
            data = response.json()
            assert data["total_scans"] == 2
            assert data["total_matched"] == 1
            assert "pipelines" in data
        finally:
            _cleanup_temp_db(path)

    def test_scans_list_endpoint(self, client):
        path = _use_temp_db()
        try:
            _seed_scans()
            response = client.get("/api/scan-log/scans")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["data"]) == 2
        finally:
            _cleanup_temp_db(path)

    def test_scans_filter_by_pipeline(self, client):
        path = _use_temp_db()
        try:
            _seed_scans()
            response = client.get("/api/scan-log/scans?pipeline=mock")
            data = response.json()
            assert data["total"] == 1
            assert data["data"][0]["pipeline"] == "mock"
        finally:
            _cleanup_temp_db(path)

    def test_scans_filter_by_matched(self, client):
        path = _use_temp_db()
        try:
            _seed_scans()
            response = client.get("/api/scan-log/scans?matched=false")
            data = response.json()
            assert data["total"] == 1
            assert data["data"][0]["matched"] is False
        finally:
            _cleanup_temp_db(path)

    def test_scan_detail_endpoint(self, client):
        path = _use_temp_db()
        try:
            _seed_scans()
            response = client.get("/api/scan-log/scans/1")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["timing"] is not None
            assert data["params"] is not None
        finally:
            _cleanup_temp_db(path)

    def test_scan_detail_not_found(self, client):
        path = _use_temp_db()
        try:
            response = client.get("/api/scan-log/scans/9999")
            assert response.status_code == 404
        finally:
            _cleanup_temp_db(path)

    def test_label_scan(self, client):
        path = _use_temp_db()
        try:
            _seed_scans()
            response = client.post(
                "/api/scan-log/scans/1/label",
                json={"correct": True, "notes": "Spot on"},
            )
            assert response.status_code == 200
            assert response.json()["correct"] is True

            # Verify it stuck
            detail = client.get("/api/scan-log/scans/1").json()
            assert detail["correct"] is True
            assert detail["notes"] == "Spot on"
        finally:
            _cleanup_temp_db(path)

    def test_llm_costs_endpoint(self, client):
        path = _use_temp_db()
        try:
            response = client.get("/api/scan-log/llm-costs")
            assert response.status_code == 200
            data = response.json()
            assert "total_calls" in data
            assert "total_cost_usd" in data
            assert "models" in data
        finally:
            _cleanup_temp_db(path)

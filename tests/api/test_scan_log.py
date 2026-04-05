"""Tests for the scan logging database."""

import io
import os
import tempfile

from PIL import Image
from sqlmodel import Session, select

from mtgsim.scan_log import db as scan_log_db
from mtgsim.scan_log.db import (
    estimate_cost,
    get_engine,
    image_hash,
    log_llm_call,
    log_scan,
)
from mtgsim.scan_log.models import (
    LLMCall,
    ScanAttempt,
    ScanMatchCandidate,
    ScanParams,
    ScanTiming,
)


def _make_test_image() -> bytes:
    img = Image.new("RGB", (100, 140), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _use_temp_db():
    """Point scan_log at a temp file for test isolation."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    os.environ["SCAN_LOG_DB_PATH"] = path
    scan_log_db._engine = None
    return path


def _cleanup_temp_db(path):
    scan_log_db._engine = None
    os.environ.pop("SCAN_LOG_DB_PATH", None)
    os.unlink(path)


class TestScanLogging:
    """Tests for log_scan() and the scan_attempt table."""

    def test_log_scan_creates_attempt(self):
        path = _use_temp_db()
        try:
            data = _make_test_image()
            scan_id = log_scan(
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
            )
            assert scan_id is not None
            assert scan_id > 0

            with Session(get_engine()) as session:
                attempt = session.exec(select(ScanAttempt).where(ScanAttempt.id == scan_id)).first()
                assert attempt is not None
                assert attempt.pipeline == "mock"
                assert attempt.extracted_name == "Lightning Bolt"
                assert attempt.matched is True
                assert attempt.image_hash == image_hash(data)
        finally:
            _cleanup_temp_db(path)

    def test_log_scan_with_timing(self):
        path = _use_temp_db()
        try:
            data = _make_test_image()
            scan_id = log_scan(
                pipeline="tesseract",
                image_data=data,
                mime_type="image/jpeg",
                extracted_name="Test",
                raw_text="",
                matched=False,
                match_type="none",
                match_confidence=None,
                matched_card_uuid=None,
                matched_card_name=None,
                added_to_collection=False,
                added_to_deck_id=None,
                timing={"preprocess_ms": 12.5, "extract_ms": 150.0, "match_ms": 30.0, "total_ms": 200.0},
            )

            with Session(get_engine()) as session:
                timing = session.exec(select(ScanTiming).where(ScanTiming.scan_id == scan_id)).first()
                assert timing is not None
                assert timing.preprocess_ms == 12.5
                assert timing.extract_ms == 150.0
                assert timing.total_ms == 200.0
        finally:
            _cleanup_temp_db(path)

    def test_log_scan_with_params(self):
        path = _use_temp_db()
        try:
            data = _make_test_image()
            scan_id = log_scan(
                pipeline="tesseract",
                image_data=data,
                mime_type="image/jpeg",
                extracted_name="Test",
                raw_text="",
                matched=False,
                match_type="none",
                match_confidence=None,
                matched_card_uuid=None,
                matched_card_name=None,
                added_to_collection=False,
                added_to_deck_id=None,
                params={"pipeline": "tesseract", "fuzzy_threshold": 92},
            )

            with Session(get_engine()) as session:
                params = session.exec(select(ScanParams).where(ScanParams.scan_id == scan_id)).first()
                assert params is not None
                assert params.params_json["pipeline"] == "tesseract"
        finally:
            _cleanup_temp_db(path)

    def test_log_scan_with_candidates(self):
        path = _use_temp_db()
        try:
            data = _make_test_image()
            scan_id = log_scan(
                pipeline="tesseract",
                image_data=data,
                mime_type="image/jpeg",
                extracted_name="Bolt",
                raw_text="Bolt",
                matched=True,
                match_type="fuzzy",
                match_confidence=95.0,
                matched_card_uuid="uuid-1",
                matched_card_name="Lightning Bolt",
                added_to_collection=False,
                added_to_deck_id=None,
                candidates=[
                    {
                        "card_name": "Lightning Bolt",
                        "card_uuid": "uuid-1",
                        "score": 95.0,
                        "component_scores": {"name": 95.0},
                    },
                    {
                        "card_name": "Lightning Strike",
                        "card_uuid": "uuid-2",
                        "score": 80.0,
                        "component_scores": {"name": 80.0},
                    },
                ],
            )

            with Session(get_engine()) as session:
                candidates = session.exec(select(ScanMatchCandidate).where(ScanMatchCandidate.scan_id == scan_id)).all()
                assert len(candidates) == 2
                assert candidates[0].rank == 1
                assert candidates[0].card_name == "Lightning Bolt"
                assert candidates[1].rank == 2
        finally:
            _cleanup_temp_db(path)


class TestLLMCallLogging:
    """Tests for log_llm_call() and the llm_call table."""

    def test_log_llm_call_success(self):
        path = _use_temp_db()
        try:
            call_id = log_llm_call(
                provider="openai",
                model="gpt-4o",
                purpose="card_extraction",
                prompt_tokens=500,
                completion_tokens=100,
                latency_ms=2500.0,
            )
            assert call_id > 0

            with Session(get_engine()) as session:
                call = session.exec(select(LLMCall).where(LLMCall.id == call_id)).first()
                assert call is not None
                assert call.provider == "openai"
                assert call.model == "gpt-4o"
                assert call.prompt_tokens == 500
                assert call.completion_tokens == 100
                assert call.total_tokens == 600
                assert call.cost_usd > 0
                assert call.status == "success"
        finally:
            _cleanup_temp_db(path)

    def test_log_llm_call_error(self):
        path = _use_temp_db()
        try:
            call_id = log_llm_call(
                provider="openai",
                model="gpt-4o",
                purpose="card_extraction",
                prompt_tokens=0,
                completion_tokens=0,
                latency_ms=100.0,
                status="error",
                error_message="API rate limited",
            )

            with Session(get_engine()) as session:
                call = session.exec(select(LLMCall).where(LLMCall.id == call_id)).first()
                assert call.status == "error"
                assert call.error_message == "API rate limited"
        finally:
            _cleanup_temp_db(path)

    def test_log_llm_call_with_scan_id(self):
        path = _use_temp_db()
        try:
            data = _make_test_image()
            scan_id = log_scan(
                pipeline="openai",
                image_data=data,
                mime_type="image/jpeg",
                extracted_name="Test",
                raw_text="",
                matched=False,
                match_type="none",
                match_confidence=None,
                matched_card_uuid=None,
                matched_card_name=None,
                added_to_collection=False,
                added_to_deck_id=None,
            )

            call_id = log_llm_call(
                provider="openai",
                model="gpt-4o",
                purpose="card_extraction",
                prompt_tokens=500,
                completion_tokens=100,
                latency_ms=2000.0,
                scan_id=scan_id,
            )

            with Session(get_engine()) as session:
                call = session.exec(select(LLMCall).where(LLMCall.id == call_id)).first()
                assert call.scan_id == scan_id
        finally:
            _cleanup_temp_db(path)


class TestCostEstimation:
    """Tests for the cost estimation function."""

    def test_known_model_cost(self):
        cost = estimate_cost("openai", "gpt-4o", prompt_tokens=1000, completion_tokens=500)
        # gpt-4o: $2.50/1M input, $10.00/1M output
        expected = (1000 * 2.50 + 500 * 10.00) / 1_000_000
        assert abs(cost - expected) < 0.0001

    def test_unknown_model_returns_zero(self):
        cost = estimate_cost("unknown", "unknown-model", prompt_tokens=1000, completion_tokens=500)
        assert cost == 0.0


class TestImageHash:
    """Tests for image hashing."""

    def test_same_data_same_hash(self):
        data = _make_test_image()
        assert image_hash(data) == image_hash(data)

    def test_different_data_different_hash(self):
        data1 = _make_test_image()
        data2 = b"different"
        assert image_hash(data1) != image_hash(data2)


class TestScanEndpointLogs:
    """Integration test: scan endpoint writes to log DB."""

    def test_mock_scan_creates_log_entry(self, client):
        path = _use_temp_db()
        try:
            data = _make_test_image()
            response = client.post(
                "/api/cards/scan?pipeline=mock",
                files={"image": ("card.jpg", data, "image/jpeg")},
            )
            assert response.status_code == 200

            with Session(get_engine()) as session:
                attempts = session.exec(select(ScanAttempt)).all()
                assert len(attempts) >= 1
                latest = attempts[-1]
                assert latest.pipeline == "mock"
                assert latest.extracted_name == "Lightning Bolt"
        finally:
            _cleanup_temp_db(path)

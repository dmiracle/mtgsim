"""Tests for 17Lands personal data client."""

import pytest
from mtgdb.models import User17LEvent
from mtgdb.session import get_session, init_db
from mtgdb.sync.seventeenlands_client import SeventeenLandsClient
from sqlmodel import select


@pytest.fixture(autouse=True)
def _ensure_db():
    init_db()


class TestSeventeenLandsClient:
    """Tests for the client class (no network calls)."""

    def test_client_creates_with_defaults(self):
        client = SeventeenLandsClient(delay=0)
        assert client.delay == 0
        client.close()

    def test_client_context_manager(self):
        with SeventeenLandsClient(delay=0) as client:
            assert client._client is not None

    def test_throttle_respects_delay(self):
        import time

        client = SeventeenLandsClient(delay=0.1)
        client._last_request_at = time.time()
        start = time.time()
        client._throttle()
        elapsed = time.time() - start
        assert elapsed >= 0.05  # allow some tolerance
        client.close()


class TestUser17LEventModel:
    """Tests for the User17LEvent database model."""

    def test_create_event(self):
        with get_session() as session:
            event = User17LEvent(
                draft_id="test-draft-001",
                expansion="DSK",
                event_type="PremierDraft",
                wins=3,
                losses=1,
                event_data={"test": True},
            )
            session.add(event)
            session.commit()

            result = session.exec(select(User17LEvent).where(User17LEvent.draft_id == "test-draft-001")).first()
            assert result is not None
            assert result.expansion == "DSK"
            assert result.wins == 3
            assert result.event_data == {"test": True}

            # Cleanup
            session.delete(result)
            session.commit()

    def test_draft_id_unique(self):
        with get_session() as session:
            e1 = User17LEvent(draft_id="unique-test-001", expansion="DSK")
            session.add(e1)
            session.commit()

            e2 = User17LEvent(draft_id="unique-test-001", expansion="MKM")
            session.add(e2)
            with pytest.raises(Exception):
                session.commit()
            session.rollback()

            # Cleanup
            existing = session.exec(select(User17LEvent).where(User17LEvent.draft_id == "unique-test-001")).first()
            if existing:
                session.delete(existing)
                session.commit()

    def test_json_fields_default_empty(self):
        event = User17LEvent(draft_id="json-test-001")
        assert event.event_data == {}
        assert event.draft_data == {}
        assert event.game_data == {}
        assert event.deck_data == {}

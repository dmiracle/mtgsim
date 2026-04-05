"""Tests for pinned deck API endpoints."""

import pytest

# Known precon deck UUIDs from KLD set
DECK_UUID_1 = "2e76982c-0646-4bf1-b71b-f362e8537934"  # BlackAndGreenDelirium_KLD
DECK_UUID_2 = "d3260aa9-cc2f-47e5-b2f6-fe47e65ceaba"  # GreenAndWhiteHumans_KLD


@pytest.fixture(autouse=True)
def cleanup_pins(client):
    """Unpin only decks that were pinned during this test, preserving user pins."""
    before = {d["uuid"] for d in client.get("/api/decks/pinned").json()}
    yield
    after = {d["uuid"] for d in client.get("/api/decks/pinned").json()}
    for uuid in after - before:
        client.delete(f"/api/decks/pinned/{uuid}")


class TestListPinnedDecks:
    """Tests for GET /api/decks/pinned."""

    def test_returns_200(self, client):
        response = client.get("/api/decks/pinned")
        assert response.status_code == 200

    def test_returns_list(self, client):
        response = client.get("/api/decks/pinned")
        assert isinstance(response.json(), list)

    def test_returns_pinned_deck_after_pin(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        response = client.get("/api/decks/pinned")
        uuids = [d["uuid"] for d in response.json()]
        assert DECK_UUID_1 in uuids

    def test_pinned_deck_has_summary_fields(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        response = client.get("/api/decks/pinned")
        deck = [d for d in response.json() if d["uuid"] == DECK_UUID_1][0]
        assert "name" in deck
        assert "uuid" in deck
        assert "card_count" in deck
        assert "colors" in deck
        assert "source" in deck


class TestPinDeck:
    """Tests for POST /api/decks/pinned/{uuid}."""

    def test_pin_returns_200(self, client):
        response = client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        assert response.status_code == 200

    def test_pin_returns_created_true(self, client):
        response = client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        assert response.json()["created"] is True

    def test_pin_idempotent(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        response = client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        assert response.status_code == 200
        assert response.json()["created"] is False

    def test_pin_multiple_decks(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        client.post(f"/api/decks/pinned/{DECK_UUID_2}")
        response = client.get("/api/decks/pinned")
        uuids = [d["uuid"] for d in response.json()]
        assert DECK_UUID_1 in uuids
        assert DECK_UUID_2 in uuids


class TestUnpinDeck:
    """Tests for DELETE /api/decks/pinned/{uuid}."""

    def test_unpin_returns_200(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        response = client.delete(f"/api/decks/pinned/{DECK_UUID_1}")
        assert response.status_code == 200

    def test_unpin_removes_from_list(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        client.delete(f"/api/decks/pinned/{DECK_UUID_1}")
        response = client.get("/api/decks/pinned")
        uuids = [d["uuid"] for d in response.json()]
        assert DECK_UUID_1 not in uuids

    def test_unpin_nonexistent_returns_404(self, client):
        response = client.delete("/api/decks/pinned/nonexistent-uuid")
        assert response.status_code == 404

    def test_unpin_only_removes_specified(self, client):
        client.post(f"/api/decks/pinned/{DECK_UUID_1}")
        client.post(f"/api/decks/pinned/{DECK_UUID_2}")
        client.delete(f"/api/decks/pinned/{DECK_UUID_1}")
        response = client.get("/api/decks/pinned")
        uuids = [d["uuid"] for d in response.json()]
        assert DECK_UUID_1 not in uuids
        assert DECK_UUID_2 in uuids

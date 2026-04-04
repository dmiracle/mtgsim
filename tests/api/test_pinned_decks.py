"""Tests for pinned deck API endpoints."""

import pytest


@pytest.fixture(autouse=True)
def cleanup_pins(client):
    """Ensure no pinned decks leak between tests."""
    yield
    # Unpin everything after each test
    response = client.get("/api/decks/pinned")
    for deck in response.json():
        client.delete(f"/api/decks/pinned/{deck['file']}")


class TestListPinnedDecks:
    """Tests for GET /api/decks/pinned."""

    def test_returns_200(self, client):
        response = client.get("/api/decks/pinned")
        assert response.status_code == 200

    def test_returns_empty_list_initially(self, client):
        response = client.get("/api/decks/pinned")
        assert response.json() == []

    def test_returns_pinned_deck_after_pin(self, client, sample_deck_file):
        client.post(f"/api/decks/pinned/{sample_deck_file}")
        response = client.get("/api/decks/pinned")
        data = response.json()
        assert len(data) == 1
        assert data[0]["file"] == sample_deck_file

    def test_pinned_deck_has_summary_fields(self, client, sample_deck_file):
        client.post(f"/api/decks/pinned/{sample_deck_file}")
        response = client.get("/api/decks/pinned")
        deck = response.json()[0]
        assert "name" in deck
        assert "code" in deck
        assert "card_count" in deck
        assert "colors" in deck
        assert "source" in deck


class TestPinDeck:
    """Tests for POST /api/decks/pinned/{file}."""

    def test_pin_returns_200(self, client, sample_deck_file):
        response = client.post(f"/api/decks/pinned/{sample_deck_file}")
        assert response.status_code == 200

    def test_pin_returns_created_true(self, client, sample_deck_file):
        response = client.post(f"/api/decks/pinned/{sample_deck_file}")
        assert response.json()["created"] is True

    def test_pin_idempotent(self, client, sample_deck_file):
        client.post(f"/api/decks/pinned/{sample_deck_file}")
        response = client.post(f"/api/decks/pinned/{sample_deck_file}")
        assert response.status_code == 200
        assert response.json()["created"] is False

    def test_pin_multiple_decks(self, client):
        client.post("/api/decks/pinned/BlackAndGreenDelirium_KLD.json")
        client.post("/api/decks/pinned/GreenAndWhiteHumans_KLD.json")
        response = client.get("/api/decks/pinned")
        assert len(response.json()) == 2


class TestUnpinDeck:
    """Tests for DELETE /api/decks/pinned/{file}."""

    def test_unpin_returns_200(self, client, sample_deck_file):
        client.post(f"/api/decks/pinned/{sample_deck_file}")
        response = client.delete(f"/api/decks/pinned/{sample_deck_file}")
        assert response.status_code == 200

    def test_unpin_removes_from_list(self, client, sample_deck_file):
        client.post(f"/api/decks/pinned/{sample_deck_file}")
        client.delete(f"/api/decks/pinned/{sample_deck_file}")
        response = client.get("/api/decks/pinned")
        assert len(response.json()) == 0

    def test_unpin_nonexistent_returns_404(self, client):
        response = client.delete("/api/decks/pinned/nonexistent.json")
        assert response.status_code == 404

    def test_unpin_only_removes_specified(self, client):
        client.post("/api/decks/pinned/BlackAndGreenDelirium_KLD.json")
        client.post("/api/decks/pinned/GreenAndWhiteHumans_KLD.json")
        client.delete("/api/decks/pinned/BlackAndGreenDelirium_KLD.json")
        response = client.get("/api/decks/pinned")
        data = response.json()
        assert len(data) == 1
        assert data[0]["file"] == "GreenAndWhiteHumans_KLD.json"

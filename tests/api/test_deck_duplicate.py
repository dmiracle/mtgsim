"""Tests for POST /api/decks/{deck_id}/duplicate endpoint."""


class TestDuplicateDeck:
    """Tests for deck duplication."""

    def _create_deck_with_cards(self, client):
        """Helper: create a deck and add a card to it."""
        resp = client.post("/api/decks/create", json={"name": "Test Deck", "format": "standard"})
        deck_id = resp.json()["id"]
        # Use a known card UUID from KLD
        client.post(
            f"/api/decks/{deck_id}/cards",
            json={"card_uuid": "00010d56-fe38-5e35-8aed-518019aa36a5", "count": 4, "board": "main"},
        )
        return deck_id

    def _cleanup_deck(self, client, deck_id):
        client.delete(f"/api/decks/{deck_id}")

    def test_duplicate_returns_200(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        assert response.status_code == 200
        new_id = response.json()["id"]
        self._cleanup_deck(client, new_id)
        self._cleanup_deck(client, deck_id)

    def test_duplicate_has_copy_name(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        data = response.json()
        assert data["name"] == "Test Deck (Copy)"
        self._cleanup_deck(client, data["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_preserves_card_count(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        data = response.json()
        assert data["card_count"] == 4
        self._cleanup_deck(client, data["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_preserves_format(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        data = response.json()
        assert data["format"] == "standard"
        self._cleanup_deck(client, data["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_creates_new_deck(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        new_id = response.json()["id"]
        assert new_id != deck_id
        self._cleanup_deck(client, new_id)
        self._cleanup_deck(client, deck_id)

    def test_duplicate_nonexistent_returns_404(self, client):
        response = client.post("/api/decks/999999/duplicate")
        assert response.status_code == 404

    def test_duplicate_cards_are_independent(self, client):
        """Deleting original doesn't affect the copy."""
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        new_id = response.json()["id"]

        # Delete original
        self._cleanup_deck(client, deck_id)

        # Copy should still exist with cards
        detail = client.get(f"/api/decks/{new_id}")
        assert detail.status_code == 200
        self._cleanup_deck(client, new_id)

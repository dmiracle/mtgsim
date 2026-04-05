"""Tests for POST /api/decks/{file}/duplicate endpoint."""


class TestDuplicateUserDeck:
    """Tests for duplicating user-created decks."""

    def _create_deck_with_cards(self, client):
        resp = client.post("/api/decks/create", json={"name": "Test Deck", "format": "standard"})
        deck_id = resp.json()["id"]
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
        self._cleanup_deck(client, response.json()["id"])
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
        assert response.json()["card_count"] == 4
        self._cleanup_deck(client, response.json()["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_preserves_format(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        assert response.json()["format"] == "standard"
        self._cleanup_deck(client, response.json()["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_source_is_user(self, client):
        """Duplicated decks always have source='user'."""
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        assert response.json()["source"] == "user"
        self._cleanup_deck(client, response.json()["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_creates_new_deck(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        assert response.json()["id"] != deck_id
        self._cleanup_deck(client, response.json()["id"])
        self._cleanup_deck(client, deck_id)

    def test_duplicate_nonexistent_returns_404(self, client):
        response = client.post("/api/decks/999999/duplicate")
        assert response.status_code == 404

    def test_duplicate_cards_are_independent(self, client):
        deck_id = self._create_deck_with_cards(client)
        response = client.post(f"/api/decks/{deck_id}/duplicate")
        new_id = response.json()["id"]
        self._cleanup_deck(client, deck_id)
        detail = client.get(f"/api/decks/{new_id}")
        assert detail.status_code == 200
        self._cleanup_deck(client, new_id)


class TestDuplicatePreconDeck:
    """Tests for duplicating preconstructed decks."""

    def _cleanup_deck(self, client, deck_id):
        client.delete(f"/api/decks/{deck_id}")

    def test_duplicate_precon_returns_200(self, client, sample_deck_file):
        response = client.post(f"/api/decks/{sample_deck_file}/duplicate")
        assert response.status_code == 200
        self._cleanup_deck(client, response.json()["id"])

    def test_duplicate_precon_has_copy_name(self, client, sample_deck_file):
        response = client.post(f"/api/decks/{sample_deck_file}/duplicate")
        data = response.json()
        assert "(Copy)" in data["name"]
        self._cleanup_deck(client, data["id"])

    def test_duplicate_precon_source_is_user(self, client, sample_deck_file):
        """Duplicated precon decks become user decks."""
        response = client.post(f"/api/decks/{sample_deck_file}/duplicate")
        assert response.json()["source"] == "user"
        self._cleanup_deck(client, response.json()["id"])

    def test_duplicate_precon_has_cards(self, client, sample_deck_file):
        response = client.post(f"/api/decks/{sample_deck_file}/duplicate")
        assert response.json()["card_count"] > 0
        self._cleanup_deck(client, response.json()["id"])

    def test_duplicate_precon_nonexistent_returns_404(self, client):
        response = client.post("/api/decks/nonexistent_deck.json/duplicate")
        assert response.status_code == 404

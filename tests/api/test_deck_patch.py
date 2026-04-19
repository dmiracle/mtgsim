"""Tests for PATCH /api/decks/{deck_id} endpoint."""


class TestPatchDeck:
    """Tests for updating deck metadata."""

    def _create_deck(self, client):
        resp = client.post("/api/decks/create", json={"name": "Original Name", "format": "standard"})
        return resp.json()["id"]

    def _cleanup(self, client, deck_id):
        client.delete(f"/api/decks/{deck_id}")

    def test_rename_returns_200(self, client):
        deck_id = self._create_deck(client)
        response = client.patch(f"/api/decks/{deck_id}", json={"name": "New Name"})
        assert response.status_code == 200
        self._cleanup(client, deck_id)

    def test_rename_updates_name(self, client):
        deck_id = self._create_deck(client)
        data = client.patch(f"/api/decks/{deck_id}", json={"name": "New Name"}).json()
        assert data["name"] == "New Name"
        self._cleanup(client, deck_id)

    def test_update_description(self, client):
        deck_id = self._create_deck(client)
        data = client.patch(f"/api/decks/{deck_id}", json={"description": "A cool deck"}).json()
        assert data["description"] == "A cool deck"
        self._cleanup(client, deck_id)

    def test_update_format(self, client):
        deck_id = self._create_deck(client)
        data = client.patch(f"/api/decks/{deck_id}", json={"format": "modern"}).json()
        assert data["format"] == "modern"
        self._cleanup(client, deck_id)

    def test_update_multiple_fields(self, client):
        deck_id = self._create_deck(client)
        data = client.patch(
            f"/api/decks/{deck_id}",
            json={"name": "Updated", "description": "Desc", "format": "legacy"},
        ).json()
        assert data["name"] == "Updated"
        assert data["description"] == "Desc"
        assert data["format"] == "legacy"
        self._cleanup(client, deck_id)

    def test_partial_update_preserves_other_fields(self, client):
        deck_id = self._create_deck(client)
        data = client.patch(f"/api/decks/{deck_id}", json={"description": "Added"}).json()
        assert data["name"] == "Original Name"
        assert data["format"] == "standard"
        self._cleanup(client, deck_id)

    def test_nonexistent_deck_returns_404(self, client):
        response = client.patch("/api/decks/999999", json={"name": "X"})
        assert response.status_code == 404

    def test_empty_body_returns_200(self, client):
        deck_id = self._create_deck(client)
        response = client.patch(f"/api/decks/{deck_id}", json={})
        assert response.status_code == 200
        assert response.json()["name"] == "Original Name"
        self._cleanup(client, deck_id)

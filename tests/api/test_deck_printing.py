"""Tests for deck card image/printing selection."""


class TestCardPrintings:
    """Tests for GET /api/cards/{uuid}/printings."""

    def test_returns_200(self, client, sample_card_uuid):
        response = client.get(f"/api/cards/{sample_card_uuid}/printings")
        assert response.status_code == 200

    def test_returns_list(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/printings").json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_printing_has_fields(self, client, sample_card_uuid):
        data = client.get(f"/api/cards/{sample_card_uuid}/printings").json()
        printing = data[0]
        assert "uuid" in printing
        assert "set_code" in printing
        assert "set_name" in printing
        assert "number" in printing
        assert "image_url" in printing

    def test_nonexistent_returns_404(self, client):
        response = client.get("/api/cards/nonexistent-uuid/printings")
        assert response.status_code == 404


class TestSetPreferredPrinting:
    """Tests for PUT /api/decks/{deckId}/cards/{cardUuid}/printing."""

    def _create_deck_with_card(self, client):
        resp = client.post("/api/decks/create", json={"name": "Print Test"})
        deck_id = resp.json()["id"]
        card_uuid = "00010d56-fe38-5e35-8aed-518019aa36a5"
        client.post(f"/api/decks/{deck_id}/cards", json={"card_uuid": card_uuid, "count": 1})
        return deck_id, card_uuid

    def _cleanup(self, client, deck_id):
        client.delete(f"/api/decks/{deck_id}")

    def test_set_printing_returns_200(self, client):
        deck_id, card_uuid = self._create_deck_with_card(client)
        # Get another printing of the same card
        printings = client.get(f"/api/cards/{card_uuid}/printings").json()
        if len(printings) > 1:
            other = next(p for p in printings if p["uuid"] != card_uuid)
            response = client.put(
                f"/api/decks/{deck_id}/cards/{card_uuid}/printing",
                json={"printing_uuid": other["uuid"]},
            )
            assert response.status_code == 200
        self._cleanup(client, deck_id)

    def test_invalid_printing_returns_404(self, client):
        deck_id, card_uuid = self._create_deck_with_card(client)
        response = client.put(
            f"/api/decks/{deck_id}/cards/{card_uuid}/printing",
            json={"printing_uuid": "nonexistent-uuid"},
        )
        assert response.status_code == 404
        self._cleanup(client, deck_id)


class TestIntendedFormat:
    """Tests for intended_format on deck updates."""

    def _create_deck(self, client):
        resp = client.post("/api/decks/create", json={"name": "Format Test"})
        return resp.json()["id"]

    def _cleanup(self, client, deck_id):
        client.delete(f"/api/decks/{deck_id}")

    def test_set_intended_format(self, client):
        deck_id = self._create_deck(client)
        response = client.patch(f"/api/decks/{deck_id}", json={"intended_format": "standard"})
        assert response.status_code == 200
        self._cleanup(client, deck_id)

    def test_intended_format_independent_of_format(self, client):
        deck_id = self._create_deck(client)
        client.patch(f"/api/decks/{deck_id}", json={"format": "modern", "intended_format": "standard"})
        detail = client.get(f"/api/decks/{deck_id}").json()
        assert detail["meta"]["format"] == "modern"
        self._cleanup(client, deck_id)

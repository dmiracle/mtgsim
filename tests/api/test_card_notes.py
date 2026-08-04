"""Tests for user card note endpoints."""


class TestCardNotes:
    def _create(self, client, **overrides):
        payload = {"card_name": "Lightning Bolt", "body": "test note body"}
        payload.update(overrides)
        return client.post("/api/card-notes", json=payload)

    def test_create_returns_201(self, client):
        response = self._create(client)
        assert response.status_code == 201
        note = response.json()
        assert note["card_name"] == "Lightning Bolt"
        assert note["kind"] == "note"
        client.delete(f"/api/card-notes/{note['id']}")

    def test_unknown_card_404(self, client):
        response = self._create(client, card_name="Not A Real Card XYZ")
        assert response.status_code == 404

    def test_empty_body_422(self, client):
        response = self._create(client, body="")
        assert response.status_code == 422

    def test_face_name_canonicalizes(self, client):
        response = self._create(client, card_name="Malakir Rebirth")
        assert response.json()["card_name"] == "Malakir Rebirth // Malakir Mire"
        client.delete(f"/api/card-notes/{response.json()['id']}")

    def test_multiple_notes_and_kind_filter(self, client):
        a = self._create(client).json()
        b = self._create(client, kind="strategy", title="vs aggro").json()
        listed = client.get("/api/card-notes", params={"card_name": "Lightning Bolt", "kind": "strategy"}).json()
        assert any(n["id"] == b["id"] for n in listed["data"])
        assert all(n["kind"] == "strategy" for n in listed["data"])
        for note in (a, b):
            client.delete(f"/api/card-notes/{note['id']}")

    def test_update_patch(self, client):
        note = self._create(client).json()
        response = client.patch(f"/api/card-notes/{note['id']}", json={"body": "updated body"})
        assert response.status_code == 200
        assert response.json()["body"] == "updated body"
        assert response.json()["kind"] == "note"
        client.delete(f"/api/card-notes/{note['id']}")

    def test_text_search(self, client):
        note = self._create(client, body="synergizes with zzzuniquephrase").json()
        listed = client.get("/api/card-notes", params={"q": "zzzuniquephrase"}).json()
        assert listed["pagination"]["total"] == 1
        client.delete(f"/api/card-notes/{note['id']}")

    def test_delete_then_404(self, client):
        note = self._create(client).json()
        assert client.delete(f"/api/card-notes/{note['id']}").status_code == 204
        assert client.get(f"/api/card-notes/{note['id']}").status_code == 404

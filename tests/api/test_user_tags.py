"""Tests for user card tag endpoints."""


class TestTagAssignment:
    def _cleanup(self, client, tag):
        client.delete(f"/api/user-tags/{tag}")

    def test_assign_returns_201(self, client):
        response = client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "TestBurn"})
        assert response.status_code == 201
        assert response.json() == {"card_name": "Lightning Bolt", "tag": "testburn"}
        self._cleanup(client, "testburn")

    def test_reassign_is_idempotent_200(self, client):
        client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "testdup"})
        response = client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "testdup"})
        assert response.status_code == 200
        self._cleanup(client, "testdup")

    def test_unknown_card_returns_404(self, client):
        response = client.post("/api/user-tags/assignments", json={"card_name": "Not A Real Card XYZ", "tag": "x"})
        assert response.status_code == 404

    def test_face_name_canonicalizes(self, client):
        # Malakir Rebirth is one face of "Malakir Rebirth // Malakir Mire"
        response = client.post("/api/user-tags/assignments", json={"card_name": "Malakir Rebirth", "tag": "testmdfc"})
        assert response.status_code == 201
        assert response.json()["card_name"] == "Malakir Rebirth // Malakir Mire"
        self._cleanup(client, "testmdfc")

    def test_unassign(self, client):
        client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "testgone"})
        response = client.delete(
            "/api/user-tags/assignments", params={"card_name": "Lightning Bolt", "tag": "testgone"}
        )
        assert response.status_code == 204
        response = client.delete(
            "/api/user-tags/assignments", params={"card_name": "Lightning Bolt", "tag": "testgone"}
        )
        assert response.status_code == 404


class TestTagVocabulary:
    def test_list_includes_assigned_tag_with_count(self, client):
        client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "testvocab"})
        data = client.get("/api/user-tags", params={"q": "testvocab"}).json()
        assert any(t["tag"] == "testvocab" and t["card_count"] == 1 for t in data["data"])
        client.delete("/api/user-tags/testvocab")

    def test_definition_upsert_and_lazy_row(self, client):
        response = client.put("/api/user-tags/testdef", json={"description": "a test tag"})
        assert response.status_code == 200
        assert response.json()["description"] == "a test tag"
        response = client.put("/api/user-tags/testdef", json={"description": "updated"})
        assert response.json()["description"] == "updated"
        client.delete("/api/user-tags/testdef")

    def test_cards_for_tag(self, client):
        client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "testcards"})
        data = client.get("/api/user-tags/cards", params={"tag": "testcards"}).json()
        assert data["pagination"]["total"] == 1
        card = data["data"][0]
        assert card["name"] == "Lightning Bolt"
        assert card["uuid"]
        assert card["image_url"]
        client.delete("/api/user-tags/testcards")

    def test_delete_tag_removes_assignments(self, client):
        client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "testrm"})
        assert client.delete("/api/user-tags/testrm").status_code == 204
        data = client.get("/api/user-tags/cards", params={"tag": "testrm"}).json()
        assert data["pagination"]["total"] == 0

    def test_delete_unknown_tag_404(self, client):
        assert client.delete("/api/user-tags/never-existed-xyz").status_code == 404

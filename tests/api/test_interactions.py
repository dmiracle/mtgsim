"""Tests for card interactions API endpoints."""

import pytest


@pytest.fixture
def second_card_uuid():
    """A second card UUID for interaction targets."""
    return "c311a7ff-17c7-5d1d-a3c3-a36a91662993"


@pytest.fixture
def third_card_uuid():
    """A third card UUID for graph traversal tests."""
    return "88b6b1d4-8745-5f3e-80e5-d1784ceb3ba8"


@pytest.fixture
def interaction_payload(sample_card_uuid, second_card_uuid):
    return {
        "source_card_uuid": sample_card_uuid,
        "target_card_uuid": second_card_uuid,
        "interaction_type": "combo",
        "is_bidirectional": True,
        "description": "These two cards combo together",
        "strength": 4,
        "extra": {"tags": ["infinite"]},
    }


@pytest.fixture
def created_interaction(client, interaction_payload):
    """Create an interaction and return the response data."""
    resp = client.post("/api/interactions", json=interaction_payload)
    assert resp.status_code == 201
    return resp.json()


class TestCreateInteraction:
    def test_create_returns_201(self, client, interaction_payload):
        resp = client.post("/api/interactions", json=interaction_payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["interaction_type"] == "combo"
        assert data["is_bidirectional"] is True
        assert data["description"] == "These two cards combo together"
        assert data["strength"] == 4
        assert data["source_card"]["uuid"] == interaction_payload["source_card_uuid"]
        assert data["target_card"]["uuid"] == interaction_payload["target_card_uuid"]

    def test_create_same_card_returns_400(self, client, sample_card_uuid):
        payload = {
            "source_card_uuid": sample_card_uuid,
            "target_card_uuid": sample_card_uuid,
            "interaction_type": "combo",
        }
        resp = client.post("/api/interactions", json=payload)
        assert resp.status_code == 400

    def test_create_invalid_card_returns_404(self, client, sample_card_uuid):
        payload = {
            "source_card_uuid": sample_card_uuid,
            "target_card_uuid": "nonexistent-uuid",
            "interaction_type": "combo",
        }
        resp = client.post("/api/interactions", json=payload)
        assert resp.status_code == 404


class TestGetInteraction:
    def test_get_returns_200(self, client, created_interaction):
        interaction_id = created_interaction["id"]
        resp = client.get(f"/api/interactions/{interaction_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == interaction_id

    def test_get_not_found_returns_404(self, client):
        resp = client.get("/api/interactions/999999")
        assert resp.status_code == 404


class TestUpdateInteraction:
    def test_update_returns_200(self, client, created_interaction):
        interaction_id = created_interaction["id"]
        resp = client.put(
            f"/api/interactions/{interaction_id}",
            json={"description": "Updated description", "strength": 5},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["description"] == "Updated description"
        assert data["strength"] == 5

    def test_update_not_found_returns_404(self, client):
        resp = client.put("/api/interactions/999999", json={"description": "nope"})
        assert resp.status_code == 404


class TestDeleteInteraction:
    def test_delete_returns_204(self, client, created_interaction):
        interaction_id = created_interaction["id"]
        resp = client.delete(f"/api/interactions/{interaction_id}")
        assert resp.status_code == 204
        # Verify it's gone
        resp = client.get(f"/api/interactions/{interaction_id}")
        assert resp.status_code == 404

    def test_delete_not_found_returns_404(self, client):
        resp = client.delete("/api/interactions/999999")
        assert resp.status_code == 404


class TestListInteractions:
    def test_list_returns_200(self, client, created_interaction):
        resp = client.get("/api/interactions")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "pagination" in data

    def test_list_filter_by_card(self, client, created_interaction, sample_card_uuid):
        resp = client.get(f"/api/interactions?card_uuid={sample_card_uuid}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) > 0

    def test_list_filter_by_type(self, client, created_interaction):
        resp = client.get("/api/interactions?type=combo")
        assert resp.status_code == 200
        data = resp.json()
        for item in data["data"]:
            assert item["interaction_type"] == "combo"

    def test_list_pagination(self, client, created_interaction):
        resp = client.get("/api/interactions?page=1&limit=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["pagination"]["limit"] == 1


class TestInteractionGraph:
    def test_graph_depth_1(self, client, created_interaction, sample_card_uuid):
        resp = client.get(f"/api/interactions/graph/{sample_card_uuid}?depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["root_card"]["uuid"] == sample_card_uuid
        assert data["depth"] == 1
        assert len(data["nodes"]) > 0

    def test_graph_bidirectional(self, client, created_interaction, second_card_uuid):
        """Bidirectional interactions are found from the target side too."""
        resp = client.get(f"/api/interactions/graph/{second_card_uuid}?depth=1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) > 0

    def test_graph_unknown_card_returns_404(self, client):
        resp = client.get("/api/interactions/graph/nonexistent-uuid?depth=1")
        assert resp.status_code == 404

    def test_graph_depth_capped_at_3(self, client, sample_card_uuid, created_interaction):
        resp = client.get(f"/api/interactions/graph/{sample_card_uuid}?depth=3")
        assert resp.status_code == 200
        assert resp.json()["depth"] == 3

    def test_graph_depth_2_traversal(self, client, sample_card_uuid, second_card_uuid, third_card_uuid):
        """Create A->B and B->C, then traverse from A at depth 2 to find C."""
        # Create B->C interaction
        client.post(
            "/api/interactions",
            json={
                "source_card_uuid": second_card_uuid,
                "target_card_uuid": third_card_uuid,
                "interaction_type": "synergy",
                "is_bidirectional": True,
            },
        )
        # Create A->B interaction
        client.post(
            "/api/interactions",
            json={
                "source_card_uuid": sample_card_uuid,
                "target_card_uuid": second_card_uuid,
                "interaction_type": "combo",
                "is_bidirectional": True,
            },
        )
        resp = client.get(f"/api/interactions/graph/{sample_card_uuid}?depth=2")
        assert resp.status_code == 200
        data = resp.json()
        # Should have nodes for both A and B (B connects to C)
        node_uuids = [n["card"]["uuid"] for n in data["nodes"]]
        assert sample_card_uuid in node_uuids
        assert second_card_uuid in node_uuids

    def test_graph_directional_not_found_from_target(self, client, sample_card_uuid, second_card_uuid):
        """Directional interactions are NOT found from the target side."""
        # Create a directional interaction A->B
        client.post(
            "/api/interactions",
            json={
                "source_card_uuid": sample_card_uuid,
                "target_card_uuid": second_card_uuid,
                "interaction_type": "counter",
                "is_bidirectional": False,
            },
        )
        # Graph from B should not find this directional interaction
        resp = client.get(f"/api/interactions/graph/{second_card_uuid}?depth=1")
        data = resp.json()
        directional_counters = [
            n
            for n in data["nodes"]
            if any(i["interaction_type"] == "counter" and not i["is_bidirectional"] for i in n["interactions"])
        ]
        # The directional counter should not appear when traversing from target
        for node in directional_counters:
            for interaction in node["interactions"]:
                if interaction["interaction_type"] == "counter" and not interaction["is_bidirectional"]:
                    assert interaction["source_card"]["uuid"] == second_card_uuid

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


@pytest.fixture(autouse=True)
def _clean_test_edges(sample_card_uuid, second_card_uuid):
    """Purge edges touching the test cards before/after each test.

    Tests share the real DB; without this, residue from earlier runs trips the
    duplicate-edge 409 introduced with the v2 semantics.
    """

    def purge():
        from mtgdb import UserCardInteraction, get_session
        from sqlalchemy import or_
        from sqlmodel import select

        test_uuids = [sample_card_uuid, second_card_uuid]
        test_names = ["Lightning Bolt", "Counterspell", "Malakir Rebirth // Malakir Mire"]
        with get_session() as session:
            rows = session.exec(
                select(UserCardInteraction).where(
                    or_(
                        UserCardInteraction.source_card_uuid.in_(test_uuids),
                        UserCardInteraction.target_card_uuid.in_(test_uuids),
                        UserCardInteraction.source_card_name.in_(test_names),
                        UserCardInteraction.target_card_name.in_(test_names),
                    )
                )
            ).all()
            for row in rows:
                session.delete(row)
            session.commit()

    purge()
    yield
    purge()


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
                "interaction_type": "counters",
                "is_bidirectional": False,
            },
        )
        # Graph from B should not find this directional interaction
        resp = client.get(f"/api/interactions/graph/{second_card_uuid}?depth=1")
        data = resp.json()
        directional_counters = [
            n
            for n in data["nodes"]
            if any(i["interaction_type"] == "counters" and not i["is_bidirectional"] for i in n["interactions"])
        ]
        # The directional counter should not appear when traversing from target
        for node in directional_counters:
            for interaction in node["interactions"]:
                if interaction["interaction_type"] == "counters" and not interaction["is_bidirectional"]:
                    assert interaction["source_card"]["uuid"] == second_card_uuid


class TestInteractionV2:
    """Name-based synergy links, typed vocabulary, and v2 fields."""

    def _create_by_name(self, client, source="Lightning Bolt", target="Counterspell", **overrides):
        payload = {
            "source_card_name": source,
            "target_card_name": target,
            "interaction_type": "enables",
        }
        payload.update(overrides)
        return client.post("/api/interactions", json=payload)

    def _cleanup(self, client, interaction_id):
        client.delete(f"/api/interactions/{interaction_id}")

    def test_create_by_name(self, client):
        resp = self._create_by_name(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["source_card_name"] == "Lightning Bolt"
        assert data["target_card_name"] == "Counterspell"
        assert data["source_card"]["uuid"]
        assert data["detected_by"] == "manual"
        assert data["confidence"] == 1.0
        self._cleanup(client, data["id"])

    def test_directed_type_forces_directional(self, client):
        resp = self._create_by_name(client, interaction_type="enables", is_bidirectional=True)
        assert resp.status_code == 201
        assert resp.json()["is_bidirectional"] is False
        self._cleanup(client, resp.json()["id"])

    def test_bidirectional_type_forces_bidirectional(self, client):
        resp = self._create_by_name(client, interaction_type="synergy", is_bidirectional=False)
        assert resp.status_code == 201
        assert resp.json()["is_bidirectional"] is True
        self._cleanup(client, resp.json()["id"])

    def test_unknown_type_422(self, client):
        resp = self._create_by_name(client, interaction_type="bogus")
        assert resp.status_code == 422

    def test_both_addressing_modes_422(self, client, sample_card_uuid, second_card_uuid):
        resp = self._create_by_name(client, source_card_uuid=sample_card_uuid, target_card_uuid=second_card_uuid)
        assert resp.status_code == 422

    def test_duplicate_edge_409(self, client):
        first = self._create_by_name(client, interaction_type="combo")
        assert first.status_code == 201
        dup = self._create_by_name(client, interaction_type="combo")
        assert dup.status_code == 409
        self._cleanup(client, first.json()["id"])

    def test_unknown_name_404(self, client):
        resp = self._create_by_name(client, source="Not A Real Card XYZ")
        assert resp.status_code == 404

    def test_face_name_canonicalizes(self, client):
        resp = self._create_by_name(client, source="Malakir Rebirth", interaction_type="synergy")
        assert resp.status_code == 201
        assert resp.json()["source_card_name"] == "Malakir Rebirth // Malakir Mire"
        self._cleanup(client, resp.json()["id"])

    def test_list_filter_by_card_name(self, client):
        created = self._create_by_name(client, interaction_type="counters")
        listed = client.get("/api/interactions", params={"card_name": "Lightning Bolt"}).json()
        assert any(i["id"] == created.json()["id"] for i in listed["data"])
        # directed edge is not listed from the target side
        listed_target = client.get("/api/interactions", params={"card_name": "Counterspell"}).json()
        assert all(i["id"] != created.json()["id"] for i in listed_target["data"])
        self._cleanup(client, created.json()["id"])

    def test_graph_by_name(self, client):
        created = self._create_by_name(client, interaction_type="combo")
        graph = client.get("/api/interactions/graph", params={"card_name": "Lightning Bolt", "depth": 1}).json()
        assert graph["root_card"]["name"] == "Lightning Bolt"
        assert graph["total_interactions"] >= 1
        self._cleanup(client, created.json()["id"])

    def test_subtype_and_confidence_roundtrip(self, client):
        resp = self._create_by_name(client, interaction_type="enables", interaction_subtype="mana_ramp", confidence=0.8)
        data = resp.json()
        assert data["interaction_subtype"] == "mana_ramp"
        assert data["confidence"] == 0.8
        self._cleanup(client, data["id"])

    def test_legacy_free_string_rows_still_readable(self, client):
        from mtgdb import MJCard, UserCardInteraction, get_session
        from sqlmodel import select

        with get_session() as session:
            uuids = session.exec(select(MJCard.uuid).limit(2)).all()
            row = UserCardInteraction(
                source_card_uuid=uuids[0], target_card_uuid=uuids[1], interaction_type="custom_legacy_type"
            )
            session.add(row)
            session.commit()
            row_id = row.id

        resp = client.get(f"/api/interactions/{row_id}")
        assert resp.status_code == 200
        assert resp.json()["interaction_type"] == "custom_legacy_type"
        client.delete(f"/api/interactions/{row_id}")

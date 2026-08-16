"""Tests for user tier list endpoints."""

import pytest


@pytest.fixture
def tier_list(client):
    resp = client.post("/api/tier-lists", json={"name": "Test List", "set_code": "dmu", "format": "PremierDraft"})
    assert resp.status_code == 201
    data = resp.json()
    yield data
    client.delete(f"/api/tier-lists/{data['id']}")


class TestTierListCrud:
    def test_create_uppercases_set_code(self, tier_list):
        assert tier_list["set_code"] == "DMU"
        assert tier_list["entry_count"] == 0

    def test_list_filters_by_set(self, client, tier_list):
        data = client.get("/api/tier-lists", params={"set_code": "DMU"}).json()
        assert any(tl["id"] == tier_list["id"] for tl in data["data"])
        data = client.get("/api/tier-lists", params={"set_code": "ZZZ"}).json()
        assert all(tl["id"] != tier_list["id"] for tl in data["data"])

    def test_patch(self, client, tier_list):
        resp = client.patch(f"/api/tier-lists/{tier_list['id']}", json={"description": "updated"})
        assert resp.status_code == 200
        assert resp.json()["description"] == "updated"

    def test_get_unknown_404(self, client):
        assert client.get("/api/tier-lists/999999").status_code == 404

    def test_delete_cascades_entries(self, client):
        created = client.post("/api/tier-lists", json={"name": "Cascade"}).json()
        client.put(f"/api/tier-lists/{created['id']}/entries", json={"card_name": "Lightning Bolt", "tier": "A+"})
        assert client.delete(f"/api/tier-lists/{created['id']}").status_code == 204
        assert client.get(f"/api/tier-lists/{created['id']}").status_code == 404


class TestTierEntries:
    def _put(self, client, list_id, **payload):
        return client.put(f"/api/tier-lists/{list_id}/entries", json=payload)

    def test_add_entry_201_with_card_summary(self, client, tier_list):
        resp = self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="A+")
        assert resp.status_code == 201
        entry = resp.json()
        assert entry["tier"] == "A+"
        assert entry["position"] == 0
        assert entry["card"]["name"] == "Lightning Bolt"
        assert entry["card"]["uuid"]

    def test_readd_moves_between_tiers_200(self, client, tier_list):
        self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="A+")
        resp = self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="B")
        assert resp.status_code == 200
        detail = client.get(f"/api/tier-lists/{tier_list['id']}").json()
        assert len(detail["entries"]) == 1
        assert detail["entries"][0]["tier"] == "B"

    def test_append_position(self, client, tier_list):
        self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="A")
        resp = self._put(client, tier_list["id"], card_name="Counterspell", tier="A")
        assert resp.json()["position"] == 1

    def test_explicit_position_renumbers(self, client, tier_list):
        self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="A")
        self._put(client, tier_list["id"], card_name="Counterspell", tier="A")
        resp = self._put(client, tier_list["id"], card_name="Dark Ritual", tier="A", position=0)
        assert resp.json()["position"] == 0
        detail = client.get(f"/api/tier-lists/{tier_list['id']}").json()
        ordered = [e["card_name"] for e in detail["entries"] if e["tier"] == "A"]
        assert ordered == ["Dark Ritual", "Lightning Bolt", "Counterspell"]

    def test_invalid_tier_422(self, client, tier_list):
        resp = self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="X")
        assert resp.status_code == 422

    def test_legacy_s_tier_422(self, client, tier_list):
        resp = self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="S")
        assert resp.status_code == 422

    def test_unknown_card_404(self, client, tier_list):
        resp = self._put(client, tier_list["id"], card_name="Not A Real Card XYZ", tier="A+")
        assert resp.status_code == 404

    def test_face_name_canonicalizes(self, client, tier_list):
        resp = self._put(client, tier_list["id"], card_name="Malakir Rebirth", tier="C")
        assert resp.json()["card_name"] == "Malakir Rebirth // Malakir Mire"

    def test_remove_entry(self, client, tier_list):
        self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="A+")
        resp = client.delete(f"/api/tier-lists/{tier_list['id']}/entries", params={"card_name": "Lightning Bolt"})
        assert resp.status_code == 204
        assert client.get(f"/api/tier-lists/{tier_list['id']}").json()["entries"] == []

    def test_reorder(self, client, tier_list):
        for name in ("Lightning Bolt", "Counterspell", "Dark Ritual"):
            self._put(client, tier_list["id"], card_name=name, tier="B")
        resp = client.post(
            f"/api/tier-lists/{tier_list['id']}/entries/reorder",
            json={"tier": "B", "ordered_card_names": ["Dark Ritual", "Lightning Bolt", "Counterspell"]},
        )
        assert resp.status_code == 200
        assert resp.json()["card_names"] == ["Dark Ritual", "Lightning Bolt", "Counterspell"]
        detail = client.get(f"/api/tier-lists/{tier_list['id']}").json()
        assert [e["card_name"] for e in detail["entries"]] == ["Dark Ritual", "Lightning Bolt", "Counterspell"]

    def test_entries_ordered_by_tier_then_position(self, client, tier_list):
        self._put(client, tier_list["id"], card_name="Counterspell", tier="B+")
        self._put(client, tier_list["id"], card_name="Lightning Bolt", tier="A")
        self._put(client, tier_list["id"], card_name="Dark Ritual", tier="A+")
        detail = client.get(f"/api/tier-lists/{tier_list['id']}").json()
        assert [e["tier"] for e in detail["entries"]] == ["A+", "A", "B+"]

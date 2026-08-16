"""Tests for user-data integration in card search (#162)."""

import pytest


@pytest.fixture
def tagged_bolt(client):
    client.post("/api/user-tags/assignments", json={"card_name": "Lightning Bolt", "tag": "zztestsearch"})
    yield "zztestsearch"
    client.delete("/api/user-tags/zztestsearch")


@pytest.fixture
def tiered_list(client):
    resp = client.post("/api/tier-lists", json={"name": "Search Test", "set_code": "DMU"})
    list_id = resp.json()["id"]
    client.put(f"/api/tier-lists/{list_id}/entries", json={"card_name": "Cut Down", "tier": "A-"})
    client.put(f"/api/tier-lists/{list_id}/entries", json={"card_name": "Phyrexian Missionary", "tier": "A+"})
    client.put(f"/api/tier-lists/{list_id}/entries", json={"card_name": "Shivan Devastator", "tier": "B"})
    yield list_id
    client.delete(f"/api/tier-lists/{list_id}")


class TestUserTagFilter:
    def test_filter_by_user_tag(self, client, tagged_bolt):
        data = client.get("/api/cards", params={"user_tags": tagged_bolt, "unique": True}).json()
        assert data["pagination"]["total"] == 1
        assert data["data"][0]["name"] == "Lightning Bolt"

    def test_filter_combines_with_unique(self, client, tagged_bolt):
        data = client.get("/api/cards", params={"user_tags": tagged_bolt, "unique": True}).json()
        assert data["pagination"]["total"] == 1

    def test_unknown_user_tag_matches_nothing(self, client):
        data = client.get("/api/cards", params={"user_tags": "zzno-such-tag"}).json()
        assert data["pagination"]["total"] == 0

    def test_summary_carries_user_tags_and_note_count(self, client, tagged_bolt):
        note = client.post("/api/card-notes", json={"card_name": "Lightning Bolt", "body": "search test note"}).json()
        data = client.get("/api/cards", params={"user_tags": tagged_bolt, "unique": True}).json()
        card = data["data"][0]
        assert tagged_bolt in card["user_tags"]
        assert card["note_count"] >= 1
        client.delete(f"/api/card-notes/{note['id']}")


class TestTierFilter:
    def test_filter_to_list_members(self, client, tiered_list):
        data = client.get("/api/cards", params={"tier_list_id": tiered_list, "unique": True}).json()
        names = {c["name"] for c in data["data"]}
        assert names == {"Cut Down", "Phyrexian Missionary", "Shivan Devastator"}

    def test_filter_to_specific_tiers(self, client, tiered_list):
        data = client.get("/api/cards", params={"tier_list_id": tiered_list, "tiers": "A+,A-", "unique": True}).json()
        names = {c["name"] for c in data["data"]}
        assert names == {"Cut Down", "Phyrexian Missionary"}

    def test_sort_by_tier(self, client, tiered_list):
        data = client.get("/api/cards", params={"tier_list_id": tiered_list, "sort": "tier", "unique": True}).json()
        names = [c["name"] for c in data["data"]]
        assert names == ["Phyrexian Missionary", "Cut Down", "Shivan Devastator"]

    def test_tier_sort_without_list_falls_back(self, client):
        resp = client.get("/api/cards", params={"q": "bolt", "sort": "tier", "limit": 5})
        assert resp.status_code == 200


class TestCardDetailUserData:
    def test_detail_embeds_notes_and_placements(self, client, tiered_list):
        note = client.post("/api/card-notes", json={"card_name": "Cut Down", "body": "detail test"}).json()
        results = client.get("/api/cards", params={"q": "Cut Down", "unique": True}).json()["data"]
        uuid = next(c["uuid"] for c in results if c["name"] == "Cut Down")
        detail = client.get(f"/api/cards/{uuid}").json()
        assert any(n["body"] == "detail test" for n in detail["notes"])
        assert detail["note_count"] >= 1
        assert any(p["tier_list_id"] == tiered_list and p["tier"] == "A-" for p in detail["tier_placements"])
        client.delete(f"/api/card-notes/{note['id']}")


class TestAvailableTagsUnion:
    def test_user_tags_appear_with_source(self, client, tagged_bolt):
        tags = client.get("/api/cards/tags").json()
        user_entries = [t for t in tags if t.get("source") == "user"]
        assert any(t["tag"] == tagged_bolt for t in user_entries)
        assert any(t.get("source") == "scryfall" for t in tags)

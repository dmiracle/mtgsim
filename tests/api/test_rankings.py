"""Tests for /api/rankings (pairwise card rankings)."""

import pytest


@pytest.fixture
def ranking(client):
    resp = client.post("/api/rankings", json={"name": "Test Ranking", "filters": {"sets": "DMU", "rarity": "common"}})
    assert resp.status_code == 201
    data = resp.json()
    yield data
    client.delete(f"/api/rankings/{data['id']}")


def test_create_keeps_filters(ranking):
    assert ranking["filters"] == {"sets": "DMU", "rarity": "common"}
    assert ranking["comparison_count"] == 0


def test_round_records_every_pair_best_first(client, ranking):
    names = ["Cut Down", "Phyrexian Missionary", "Shivan Devastator", "Sheoldred, the Apocalypse"]
    resp = client.post(f"/api/rankings/{ranking['id']}/rounds", json={"ordered_card_names": names})
    assert resp.json() == {"comparisons_added": 6}
    detail = client.get(f"/api/rankings/{ranking['id']}").json()
    pairs = {(c["winner_name"], c["loser_name"]) for c in detail["comparisons"]}
    assert ("Cut Down", "Sheoldred, the Apocalypse") in pairs
    assert ("Phyrexian Missionary", "Shivan Devastator") in pairs
    assert len(pairs) == 6


def test_round_rejects_duplicates(client, ranking):
    resp = client.post(f"/api/rankings/{ranking['id']}/rounds", json={"ordered_card_names": ["Cut Down", "Cut Down"]})
    assert resp.status_code == 422


def test_listed_with_comparison_count(client, ranking):
    client.post(f"/api/rankings/{ranking['id']}/rounds", json={"ordered_card_names": ["Cut Down", "Shivan Devastator"]})
    listed = {r["id"]: r for r in client.get("/api/rankings").json()}
    assert listed[ranking["id"]]["comparison_count"] == 1


def test_delete_then_404(client):
    created = client.post("/api/rankings", json={"name": "Doomed"}).json()
    assert client.delete(f"/api/rankings/{created['id']}").status_code == 204
    assert client.get(f"/api/rankings/{created['id']}").status_code == 404


def test_exclude_then_restore(client, ranking):
    url = f"/api/rankings/{ranking['id']}/exclusions"
    assert client.post(url, json={"card_name": "Shivan Devastator"}).status_code == 204
    assert client.post(url, json={"card_name": "Shivan Devastator"}).status_code == 204
    assert client.get(f"/api/rankings/{ranking['id']}").json()["excluded_names"] == ["Shivan Devastator"]
    assert client.delete(url, params={"card_name": "Shivan Devastator"}).status_code == 204
    assert client.get(f"/api/rankings/{ranking['id']}").json()["excluded_names"] == []
    assert client.delete(url, params={"card_name": "Shivan Devastator"}).status_code == 404


def test_exclude_unknown_ranking_404(client):
    assert client.post("/api/rankings/999999/exclusions", json={"card_name": "Cut Down"}).status_code == 404


def test_delete_ranking_with_exclusions(client):
    created = client.post("/api/rankings", json={"name": "Doomed"}).json()
    client.post(f"/api/rankings/{created['id']}/exclusions", json={"card_name": "Cut Down"})
    assert client.delete(f"/api/rankings/{created['id']}").status_code == 204

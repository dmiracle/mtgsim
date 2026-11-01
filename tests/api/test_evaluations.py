"""Tests for /api/evaluation-sets (situational card evaluations)."""

import pytest


@pytest.fixture
def evaluation_set(client):
    resp = client.post("/api/evaluation-sets", json={"name": "Test Evaluations", "set_code": "dmu"})
    assert resp.status_code == 201
    data = resp.json()
    yield data
    client.delete(f"/api/evaluation-sets/{data['id']}")


def test_create_uppercases_set_code(evaluation_set):
    assert evaluation_set["set_code"] == "DMU"
    assert evaluation_set["entry_count"] == 0


def test_put_then_detail(client, evaluation_set):
    body = {"card_name": "cut down", "developing": 4, "parity": 4, "behind": 5, "ahead": None}
    resp = client.put(f"/api/evaluation-sets/{evaluation_set['id']}/entries", json=body)
    assert resp.json() == {**body, "card_name": "Cut Down"}
    detail = client.get(f"/api/evaluation-sets/{evaluation_set['id']}").json()
    assert detail["entry_count"] == 1
    assert detail["entries"] == [{**body, "card_name": "Cut Down"}]


def test_put_replaces_and_all_null_removes(client, evaluation_set):
    url = f"/api/evaluation-sets/{evaluation_set['id']}/entries"
    client.put(url, json={"card_name": "Cut Down", "developing": 2, "ahead": 3})
    client.put(url, json={"card_name": "Cut Down", "behind": 5})
    entries = client.get(f"/api/evaluation-sets/{evaluation_set['id']}").json()["entries"]
    assert entries == [{"card_name": "Cut Down", "developing": None, "parity": None, "behind": 5, "ahead": None}]
    client.put(url, json={"card_name": "Cut Down"})
    assert client.get(f"/api/evaluation-sets/{evaluation_set['id']}").json()["entries"] == []


def test_rejects_out_of_range_stars(client, evaluation_set):
    resp = client.put(
        f"/api/evaluation-sets/{evaluation_set['id']}/entries", json={"card_name": "Cut Down", "parity": 6}
    )
    assert resp.status_code == 422


def test_unknown_card_404(client, evaluation_set):
    resp = client.put(
        f"/api/evaluation-sets/{evaluation_set['id']}/entries", json={"card_name": "Not A Card Xyz", "parity": 3}
    )
    assert resp.status_code == 404


def test_listed_with_entry_count(client, evaluation_set):
    client.put(f"/api/evaluation-sets/{evaluation_set['id']}/entries", json={"card_name": "Cut Down", "parity": 3})
    listed = {s["id"]: s for s in client.get("/api/evaluation-sets").json()}
    assert listed[evaluation_set["id"]]["entry_count"] == 1


def test_delete_then_404(client):
    created = client.post("/api/evaluation-sets", json={"name": "Doomed"}).json()
    assert client.delete(f"/api/evaluation-sets/{created['id']}").status_code == 204
    assert client.get(f"/api/evaluation-sets/{created['id']}").status_code == 404

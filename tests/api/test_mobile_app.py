"""The API serves the mobile PWA build at the site root when mobile/dist exists."""

import pytest

from mtgsim.api.main import mobile_dist

pytestmark = pytest.mark.skipif(not mobile_dist.exists(), reason="mobile/dist not built")


def test_root_serves_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_client_routes_fall_back_to_index(client):
    resp = client.get("/rank/1/results")
    assert resp.status_code == 200
    assert resp.text == client.get("/").text


def test_build_files_are_served(client):
    resp = client.get("/manifest.webmanifest")
    assert resp.status_code == 200
    assert "Card Review" in resp.text


def test_unknown_api_path_is_still_404(client):
    assert client.get("/api/no-such-endpoint").status_code == 404


def test_api_routes_still_win(client):
    assert client.get("/api/rankings").headers["content-type"].startswith("application/json")


def test_no_path_traversal(client):
    resp = client.get("/..%2F..%2Fpyproject.toml")
    assert "[project]" not in resp.text

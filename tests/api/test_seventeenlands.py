"""Tests for 17Lands API endpoints."""


class TestListDatasets:
    """Tests for GET /api/17lands/datasets endpoint."""

    def test_list_datasets_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/17lands/datasets")
        assert response.status_code == 200

    def test_list_datasets_response_structure(self, client):
        """Response has correct structure."""
        response = client.get("/api/17lands/datasets")
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_list_datasets_pagination(self, client):
        """Pagination metadata is present."""
        response = client.get("/api/17lands/datasets?page=1&limit=10")
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
        assert "total" in data["pagination"]

    def test_list_datasets_filter_by_expansion(self, client):
        """Filter by expansion returns 200."""
        response = client.get("/api/17lands/datasets?expansion=MH3")
        assert response.status_code == 200

    def test_list_datasets_filter_by_format(self, client):
        """Filter by format returns 200."""
        response = client.get("/api/17lands/datasets?format=PremierDraft")
        assert response.status_code == 200

    def test_list_datasets_filter_has_draft(self, client):
        """Filter by has_draft returns 200."""
        response = client.get("/api/17lands/datasets?has_draft=true")
        assert response.status_code == 200

    def test_list_datasets_limit_validation(self, client):
        """Limit cannot exceed 100."""
        response = client.get("/api/17lands/datasets?limit=200")
        assert response.status_code == 422


class TestListExpansions:
    """Tests for GET /api/17lands/expansions endpoint."""

    def test_list_expansions_returns_200(self, client):
        """Basic request returns 200."""
        response = client.get("/api/17lands/expansions")
        assert response.status_code == 200

    def test_list_expansions_returns_list(self, client):
        """Response is a list."""
        response = client.get("/api/17lands/expansions")
        data = response.json()
        assert isinstance(data, list)

    def test_list_expansions_entry_structure(self, client):
        """Expansion entries have correct fields."""
        response = client.get("/api/17lands/expansions")
        data = response.json()
        if data:
            entry = data[0]
            assert "expansion" in entry
            assert "dataset_count" in entry
            assert "formats" in entry
            assert isinstance(entry["formats"], list)

"""Tests for the SQL query profiler."""


class TestProfilerHeaders:
    """Profiling headers are present on API responses."""

    def test_query_count_header(self, client):
        response = client.get("/api/cards?limit=1")
        assert "X-Query-Count" in response.headers
        assert int(response.headers["X-Query-Count"]) >= 1

    def test_query_time_header(self, client):
        response = client.get("/api/cards?limit=1")
        assert "X-Query-Time-Ms" in response.headers
        assert float(response.headers["X-Query-Time-Ms"]) >= 0

    def test_response_time_header(self, client):
        response = client.get("/api/cards?limit=1")
        assert "X-Response-Time-Ms" in response.headers
        assert float(response.headers["X-Response-Time-Ms"]) >= 0

    def test_no_headers_on_health(self, client):
        response = client.get("/health")
        assert "X-Query-Count" not in response.headers


class TestDebugQueriesEndpoint:
    """Tests for GET /api/debug/queries."""

    def test_returns_200(self, client):
        # Make a request first so there's something in the history
        client.get("/api/cards?limit=1")
        response = client.get("/api/debug/queries")
        assert response.status_code == 200

    def test_returns_list(self, client):
        client.get("/api/cards?limit=1")
        response = client.get("/api/debug/queries")
        data = response.json()
        assert isinstance(data, list)

    def test_profile_has_expected_fields(self, client):
        client.get("/api/cards?limit=1")
        response = client.get("/api/debug/queries")
        data = response.json()
        assert len(data) > 0
        profile = data[0]
        assert "method" in profile
        assert "path" in profile
        assert "query_count" in profile
        assert "total_query_ms" in profile
        assert "request_ms" in profile
        assert "queries" in profile

    def test_profile_queries_have_sql(self, client):
        client.get("/api/cards?limit=1")
        response = client.get("/api/debug/queries")
        data = response.json()
        # Find a profile that has queries (not the debug endpoint itself)
        card_profiles = [p for p in data if p["path"] == "/api/cards"]
        assert len(card_profiles) > 0
        assert len(card_profiles[0]["queries"]) > 0
        assert "sql" in card_profiles[0]["queries"][0]
        assert "duration_ms" in card_profiles[0]["queries"][0]

    def test_filter_by_path(self, client):
        client.get("/api/cards?limit=1")
        client.get("/api/sets?limit=1")
        response = client.get("/api/debug/queries?path=/api/cards")
        data = response.json()
        assert all("/api/cards" in p["path"] for p in data)

    def test_filter_by_min_queries(self, client):
        client.get("/api/cards?limit=1")
        response = client.get("/api/debug/queries?min_queries=1")
        data = response.json()
        assert all(p["query_count"] >= 1 for p in data)

    def test_limit_parameter(self, client):
        for _ in range(5):
            client.get("/api/cards?limit=1")
        response = client.get("/api/debug/queries?limit=2")
        data = response.json()
        assert len(data) <= 2

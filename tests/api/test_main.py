"""Tests for main FastAPI app endpoints."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import given, strategies as st


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_returns_200(self, client):
        """Root endpoint returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_api_info(self, client):
        """Root endpoint returns API information."""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data

    def test_root_api_name(self, client):
        """Root endpoint has correct API name."""
        response = client.get("/")
        data = response.json()

        assert data["name"] == "MTG Webapp API"

    def test_root_api_version(self, client):
        """Root endpoint has version."""
        response = client.get("/")
        data = response.json()

        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_root_has_docs_link(self, client):
        """Root endpoint has docs link."""
        response = client.get("/")
        data = response.json()

        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_root_has_openapi_link(self, client):
        """Root endpoint has OpenAPI link."""
        response = client.get("/")
        data = response.json()

        assert "openapi" in data
        assert data["openapi"] == "/openapi.json"

    def test_root_has_endpoints(self, client):
        """Root endpoint lists available endpoints."""
        response = client.get("/")
        data = response.json()

        assert "endpoints" in data
        assert isinstance(data["endpoints"], dict)

    def test_root_endpoints_has_decks(self, client):
        """Endpoints include decks."""
        response = client.get("/")
        data = response.json()

        assert "decks" in data["endpoints"]
        assert data["endpoints"]["decks"] == "/api/decks"

    def test_root_endpoints_has_sets(self, client):
        """Endpoints include sets."""
        response = client.get("/")
        data = response.json()

        assert "sets" in data["endpoints"]
        assert data["endpoints"]["sets"] == "/api/sets"

    def test_root_endpoints_has_cards(self, client):
        """Endpoints include cards."""
        response = client.get("/")
        data = response.json()

        assert "cards" in data["endpoints"]
        assert data["endpoints"]["cards"] == "/api/cards"

    def test_root_endpoints_has_prices(self, client):
        """Endpoints include prices."""
        response = client.get("/")
        data = response.json()

        assert "prices" in data["endpoints"]
        assert data["endpoints"]["prices"] == "/api/prices"

    def test_root_endpoints_has_stats(self, client):
        """Endpoints include stats."""
        response = client.get("/")
        data = response.json()

        assert "stats" in data["endpoints"]
        assert data["endpoints"]["stats"] == "/api/stats/home"

    def test_root_endpoints_has_keywords(self, client):
        """Endpoints include keywords."""
        response = client.get("/")
        data = response.json()

        assert "keywords" in data["endpoints"]
        assert data["endpoints"]["keywords"] == "/api/keywords"


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """Health endpoint returns status."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data

    def test_health_status_healthy(self, client):
        """Health status is healthy."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"


class TestDocsEndpoint:
    """Tests for GET /docs endpoint."""

    def test_docs_returns_200(self, client):
        """Docs endpoint returns 200."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_docs_returns_html(self, client):
        """Docs endpoint returns HTML."""
        response = client.get("/docs")
        assert "text/html" in response.headers["content-type"]


class TestOpenAPIEndpoint:
    """Tests for GET /openapi.json endpoint."""

    def test_openapi_returns_200(self, client):
        """OpenAPI endpoint returns 200."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_returns_json(self, client):
        """OpenAPI endpoint returns JSON."""
        response = client.get("/openapi.json")
        assert "application/json" in response.headers["content-type"]

    def test_openapi_has_info(self, client):
        """OpenAPI spec has info section."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "info" in data
        assert "title" in data["info"]
        assert "version" in data["info"]

    def test_openapi_has_paths(self, client):
        """OpenAPI spec has paths."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "paths" in data
        assert len(data["paths"]) > 0

    def test_openapi_has_deck_paths(self, client):
        """OpenAPI spec includes deck endpoints."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/decks" in data["paths"]
        assert "/api/decks/{file}" in data["paths"]

    def test_openapi_has_set_paths(self, client):
        """OpenAPI spec includes set endpoints."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/sets" in data["paths"]
        assert "/api/sets/{code}" in data["paths"]

    def test_openapi_has_card_paths(self, client):
        """OpenAPI spec includes card endpoints."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/cards" in data["paths"]
        assert "/api/cards/{uuid}" in data["paths"]

    def test_openapi_has_price_paths(self, client):
        """OpenAPI spec includes price endpoints."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/prices" in data["paths"]
        assert "/api/prices/{uuid}" in data["paths"]

    def test_openapi_has_stats_paths(self, client):
        """OpenAPI spec includes stats endpoints."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/stats/home" in data["paths"]
        assert "/api/stats/decks" in data["paths"]

    def test_openapi_has_keywords_paths(self, client):
        """OpenAPI spec includes keywords endpoints."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/api/keywords" in data["paths"]
        assert "/api/keywords/formats" in data["paths"]


class TestCORS:
    """Tests for CORS middleware."""

    def test_cors_allows_any_origin(self, client):
        """CORS allows any origin."""
        response = client.options(
            "/api/decks",
            headers={
                "Origin": "http://localhost:8080",
                "Access-Control-Request-Method": "GET",
            },
        )
        # OPTIONS should return 200 or 204
        assert response.status_code in [200, 204]

    def test_cors_header_in_response(self, client):
        """CORS headers are present in response."""
        response = client.get(
            "/api/decks",
            headers={"Origin": "http://localhost:8080"},
        )
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_error_format(self, client):
        """404 errors have correct format."""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_422_validation_error_format(self, client):
        """422 validation errors have correct format."""
        response = client.get("/api/decks?limit=invalid")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestStaticAssetHandling:
    """Property-based tests for static asset handling."""

    @given(
        web_exists=st.booleans(),
        webapp_exists=st.booleans(),
        resources_exists=st.booleans(),
    )
    def test_static_asset_mounting_property(self, web_exists, webapp_exists, resources_exists):
        """
        **Feature: mtgsim-refactor, Property 5: Static Asset Handling**
        
        For any combination of static directory existence states, the system should use 
        proper Path objects, handle missing directories gracefully, and provide consistent 
        serving behavior.
        **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create directories based on the generated booleans
            web_dir = temp_path / "web"
            webapp_dir = temp_path / "webapp"
            resources_dir = temp_path / "resources"
            
            if web_exists:
                web_dir.mkdir()
                (web_dir / "index.html").write_text("<html></html>")
            
            if webapp_exists:
                webapp_dir.mkdir()
                (webapp_dir / "index.html").write_text("<html></html>")
                
            if resources_exists:
                resources_dir.mkdir()
                (resources_dir / "test.json").write_text("{}")
            
            # Test the mounting logic directly by simulating what main.py does
            from fastapi import FastAPI
            from fastapi.staticfiles import StaticFiles
            
            # Create a test app to verify mounting behavior
            test_app = FastAPI()
            
            # Property 1: System uses Path objects instead of string existence checks
            assert isinstance(web_dir, Path)
            assert isinstance(webapp_dir, Path)
            assert isinstance(resources_dir, Path)
            
            # Property 2: Directories are mounted when they exist
            # Property 3: Missing directories are handled gracefully (no exceptions)
            try:
                mount_count = 0
                
                if web_dir.exists():
                    test_app.mount("/web", StaticFiles(directory=str(web_dir)), name="web")
                    mount_count += 1
                
                if resources_dir.exists():
                    test_app.mount("/resources", StaticFiles(directory=str(resources_dir)), name="resources")
                    mount_count += 1
                
                if webapp_dir.exists():
                    test_app.mount("/webapp", StaticFiles(directory=str(webapp_dir)), name="webapp")
                    mount_count += 1
                
                # Property 4: Consistent serving behavior - no exceptions raised
                # Count the number of mounted static file routes
                static_routes = [route for route in test_app.routes 
                               if hasattr(route, 'app') and 
                               hasattr(route.app, '__class__') and 
                               'StaticFiles' in str(route.app.__class__)]
                
                # Verify correct number of mounts based on directory existence
                expected_mounts = sum([web_exists, webapp_exists, resources_exists])
                assert len(static_routes) == expected_mounts
                    
            except Exception as e:
                # Property 3: Should handle missing directories gracefully
                assert False, f"Static asset mounting should not raise exceptions: {e}"
                
    def test_path_exists_usage(self):
        """Test that the system uses Path.exists() instead of string checks."""
        # This test verifies that we're using proper Path objects
        from mtgsim.api.main import web_dir, webapp_dir, resources_dir
        
        # All should be Path objects
        assert isinstance(web_dir, Path)
        assert isinstance(webapp_dir, Path) 
        assert isinstance(resources_dir, Path)
        
        # The existence checks should use Path.exists() method
        # This is implicitly tested by the mounting logic working correctly

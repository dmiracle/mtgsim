"""Pytest fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient

from mtgsim.api.main import app


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def sample_deck_file():
    """Sample deck filename for testing."""
    return "AggressiveRecruitment_KLD.json"


@pytest.fixture
def sample_set_code():
    """Sample set code for testing."""
    return "KLD"


@pytest.fixture
def sample_card_uuid():
    """Sample card UUID for testing."""
    return "00010d56-fe38-5e35-8aed-518019aa36a5"


@pytest.fixture
def sample_search_query():
    """Sample search query for testing."""
    return "Lightning"

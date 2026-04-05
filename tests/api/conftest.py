"""Pytest fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient

from mtgsim.api.data import close_databases, init_databases
from mtgsim.api.main import app
from mtgsim.api.profiler import attach_profiler


@pytest.fixture(scope="session", autouse=True)
def setup_databases():
    """Initialize databases for all tests."""
    init_databases()

    from mtgdb.session import get_engine

    engine = get_engine()
    attach_profiler(engine)

    from mtgdb.embeddings.vec import load_sqlite_vec, register_sqlite_vec

    register_sqlite_vec(engine)
    # Also load on existing pooled connection
    with engine.connect() as conn:
        load_sqlite_vec(conn.connection.dbapi_connection)
    yield
    close_databases()


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def sample_deck_file():
    """Sample deck filename for testing."""
    return "BlackAndGreenDelirium_KLD.json"


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

"""Pytest fixtures for mtgdb tests."""

import tempfile
from pathlib import Path

import pytest
from mtgdb.models import MJCard, MJSet, UserCard, UserDeck
from mtgdb.session import init_db
from sqlmodel import Session


@pytest.fixture
def temp_db_path():
    """Create a temporary database file path."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        yield Path(f.name)


@pytest.fixture
def initialized_db(temp_db_path):
    """Initialize a temporary database with all tables."""
    engine = init_db(temp_db_path)
    yield temp_db_path, engine
    engine.dispose()
    temp_db_path.unlink(missing_ok=True)


@pytest.fixture
def session(initialized_db):
    """Provide a database session for testing."""
    db_path, engine = initialized_db
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_set():
    """Sample MJSet for testing."""
    return MJSet(
        code="TST",
        name="Test Set",
        type="expansion",
        release_date="2024-01-01",
        base_set_size=100,
        total_set_size=120,
    )


@pytest.fixture
def sample_card():
    """Sample MJCard for testing."""
    return MJCard(
        uuid="test-uuid-1234",
        name="Test Card",
        set_code="TST",
        mana_cost="{1}{R}",
        mana_value=2.0,
        type_line="Creature - Test",
        oracle_text="Test creature deals 1 damage.",
        power="2",
        toughness="1",
        rarity="common",
        colors=["R"],
        color_identity=["R"],
        types=["Creature"],
        subtypes=["Test"],
        keywords=["Haste"],
    )


@pytest.fixture
def sample_user_card():
    """Sample UserCard for testing."""
    return UserCard(
        card_uuid="test-uuid-1234",
        quantity_owned=4,
        quantity_owned_foil=1,
        quantity_wanted=2,
        condition="NM",
    )


@pytest.fixture
def sample_user_deck():
    """Sample UserDeck for testing."""
    return UserDeck(
        name="Test Deck",
        description="A test deck",
        format="standard",
    )

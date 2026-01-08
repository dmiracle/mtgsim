"""Tests for the unified database schema.

Validates that:
1. All tables are created correctly
2. Models work as expected
3. Foreign keys are properly set up
4. Card model tracks owns/wants correctly
"""

import tempfile
from pathlib import Path

import pytest
from sqlmodel import select

from mtgsim.db.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
    MJSet,
    UserCard,
    UserDeck,
    UserDeckCard,
)
from mtgsim.db.session import close_db, get_session, init_db


@pytest.fixture
def test_db_path():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.sqlite"
        yield db_path


@pytest.fixture
def initialized_db(test_db_path):
    """Initialize the test database."""
    init_db(test_db_path)
    yield test_db_path
    close_db()


class TestSchemaCreation:
    """Tests for schema creation."""

    def test_all_tables_created(self, initialized_db):
        """Verify all 10 tables are created."""
        import sqlite3

        conn = sqlite3.connect(initialized_db)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()

        expected_tables = {
            "mj_card",
            "mj_card_identifier",
            "mj_card_legality",
            "mj_card_price",
            "mj_set",
            "mj_deck",
            "mj_deck_card",
            "user_card",
            "user_deck",
            "user_deck_card",
        }

        assert expected_tables.issubset(tables), f"Missing tables: {expected_tables - tables}"

    def test_reference_tables_queryable(self, initialized_db):
        """Verify reference tables can be queried."""
        with get_session(initialized_db) as session:
            session.exec(select(MJCard)).first()
            session.exec(select(MJSet)).first()
            session.exec(select(MJDeck)).first()
            session.exec(select(MJCardIdentifier)).first()
            session.exec(select(MJCardLegality)).first()
            session.exec(select(MJCardPrice)).first()
            session.exec(select(MJDeckCard)).first()

    def test_user_tables_queryable(self, initialized_db):
        """Verify user tables can be queried."""
        with get_session(initialized_db) as session:
            session.exec(select(UserCard)).first()
            session.exec(select(UserDeck)).first()
            session.exec(select(UserDeckCard)).first()


class TestMJCardModel:
    """Tests for MJCard model."""

    def test_create_mj_card(self, initialized_db):
        """Test creating a reference card."""
        with get_session(initialized_db) as session:
            card = MJCard(
                uuid="test-uuid-123",
                name="Lightning Bolt",
                set_code="LEA",
                mana_cost="{R}",
                mana_value=1.0,
                type_line="Instant",
                oracle_text="Lightning Bolt deals 3 damage to any target.",
                rarity="common",
                colors=["R"],
                color_identity=["R"],
                types=["Instant"],
            )
            session.add(card)
            session.commit()

            # Query back
            result = session.exec(select(MJCard).where(MJCard.uuid == "test-uuid-123")).first()

            assert result is not None
            assert result.name == "Lightning Bolt"
            assert result.colors == ["R"]
            assert result.types == ["Instant"]

    def test_mj_card_json_arrays(self, initialized_db):
        """Test JSON array columns work correctly."""
        with get_session(initialized_db) as session:
            card = MJCard(
                uuid="test-multicolor",
                name="Nicol Bolas",
                set_code="M19",
                colors=["U", "B", "R"],
                color_identity=["U", "B", "R"],
                types=["Creature", "Legendary"],
                subtypes=["Elder", "Dragon"],
                supertypes=["Legendary"],
                keywords=["Flying"],
            )
            session.add(card)
            session.commit()

            result = session.exec(select(MJCard).where(MJCard.uuid == "test-multicolor")).first()

            assert result.colors == ["U", "B", "R"]
            assert result.subtypes == ["Elder", "Dragon"]
            assert result.keywords == ["Flying"]


class TestUserCardModel:
    """Tests for UserCard model (collection tracking)."""

    def test_create_collection_entry(self, initialized_db):
        """Test creating a collection entry."""
        with get_session(initialized_db) as session:
            # Create reference card first
            mj_card = MJCard(uuid="ref-123", name="Test Card", set_code="TST")
            session.add(mj_card)
            session.commit()

            # Add to collection
            card = UserCard(
                card_uuid="ref-123",
                quantity_owned=4,
                quantity_owned_foil=1,
            )
            session.add(card)
            session.commit()

            assert card.owns is True
            assert card.wants is False
            assert card.total_owned == 5

    def test_card_owns_property(self, initialized_db):
        """Test owns property calculation."""
        with get_session(initialized_db) as session:
            mj_card = MJCard(uuid="owns-test", name="Test", set_code="TST")
            session.add(mj_card)
            session.commit()

            # Card with no ownership
            card1 = UserCard(card_uuid="owns-test", quantity_owned=0, quantity_owned_foil=0)
            assert card1.owns is False

            # Card with regular ownership
            card2 = UserCard(card_uuid="owns-test", quantity_owned=1, quantity_owned_foil=0)
            assert card2.owns is True

            # Card with foil ownership only
            card3 = UserCard(card_uuid="owns-test", quantity_owned=0, quantity_owned_foil=2)
            assert card3.owns is True

    def test_card_wants_property(self, initialized_db):
        """Test wants property calculation."""
        with get_session(initialized_db) as session:
            mj_card = MJCard(uuid="wants-test", name="Test", set_code="TST")
            session.add(mj_card)
            session.commit()

            # Card not wanted
            card1 = UserCard(card_uuid="wants-test", quantity_wanted=0, quantity_wanted_foil=0)
            assert card1.wants is False

            # Card wanted (regular)
            card2 = UserCard(card_uuid="wants-test", quantity_wanted=2, quantity_wanted_foil=0)
            assert card2.wants is True

            # Card wanted (foil only)
            card3 = UserCard(card_uuid="wants-test", quantity_wanted=0, quantity_wanted_foil=1)
            assert card3.wants is True

    def test_card_both_owns_and_wants(self, initialized_db):
        """Test card can be both owned and wanted."""
        with get_session(initialized_db) as session:
            mj_card = MJCard(uuid="both-test", name="Test", set_code="TST")
            session.add(mj_card)
            session.commit()

            card = UserCard(
                card_uuid="both-test",
                quantity_owned=2,
                quantity_wanted=4,  # Want more copies
            )
            session.add(card)
            session.commit()

            assert card.owns is True
            assert card.wants is True
            assert card.total_owned == 2
            assert card.total_wanted == 4


class TestUserDeckModel:
    """Tests for UserDeck model."""

    def test_create_deck(self, initialized_db):
        """Test creating a user deck."""
        with get_session(initialized_db) as session:
            deck = UserDeck(
                name="My Commander Deck",
                description="A fun commander deck",
                format="commander",
            )
            session.add(deck)
            session.commit()

            result = session.exec(select(UserDeck).where(UserDeck.name == "My Commander Deck")).first()
            assert result is not None
            assert result.format == "commander"

    def test_add_cards_to_deck(self, initialized_db):
        """Test adding cards to a deck."""
        with get_session(initialized_db) as session:
            # Create reference card
            mj_card = MJCard(uuid="deck-card-1", name="Sol Ring", set_code="CMD")
            session.add(mj_card)

            # Create deck
            deck = UserDeck(name="Test Deck")
            session.add(deck)
            session.commit()

            # Add card to deck
            deck_card = UserDeckCard(
                deck_id=deck.id,
                card_uuid="deck-card-1",
                board="main",
                count=1,
            )
            session.add(deck_card)
            session.commit()

            # Query deck cards
            result = session.exec(select(UserDeckCard).where(UserDeckCard.deck_id == deck.id)).all()
            assert len(result) == 1
            assert result[0].card_uuid == "deck-card-1"


class TestMJSetModel:
    """Tests for MJSet model."""

    def test_create_set(self, initialized_db):
        """Test creating a set."""
        with get_session(initialized_db) as session:
            mj_set = MJSet(
                code="TST",
                name="Test Set",
                type="expansion",
                release_date="2024-01-01",
                base_set_size=100,
                total_set_size=120,
            )
            session.add(mj_set)
            session.commit()

            result = session.exec(select(MJSet).where(MJSet.code == "TST")).first()
            assert result is not None
            assert result.name == "Test Set"
            assert result.base_set_size == 100


class TestMJDeckModel:
    """Tests for MJDeck model (precon decks)."""

    def test_create_precon_deck(self, initialized_db):
        """Test creating a precon deck."""
        with get_session(initialized_db) as session:
            deck = MJDeck(
                uuid="precon-uuid-1",
                file_name="test_deck.json",
                name="Test Commander Deck",
                code="CMD",
                type="Commander",
                main_board_count=99,
                commander_count=1,
            )
            session.add(deck)
            session.commit()

            result = session.exec(select(MJDeck).where(MJDeck.uuid == "precon-uuid-1")).first()
            assert result is not None
            assert result.main_board_count == 99


class TestForeignKeys:
    """Tests for foreign key relationships."""

    def test_card_references_mj_card(self, initialized_db):
        """Test UserCard.card_uuid references MJCard.uuid."""
        with get_session(initialized_db) as session:
            mj_card = MJCard(uuid="fk-test-1", name="FK Test Card", set_code="TST")
            session.add(mj_card)
            session.commit()

            card = UserCard(card_uuid="fk-test-1", quantity_owned=1)
            session.add(card)
            session.commit()

            # Both should exist
            assert session.exec(select(MJCard).where(MJCard.uuid == "fk-test-1")).first()
            assert session.exec(select(UserCard).where(UserCard.card_uuid == "fk-test-1")).first()

    def test_mj_card_identifier_references_mj_card(self, initialized_db):
        """Test MJCardIdentifier.card_uuid references MJCard.uuid."""
        with get_session(initialized_db) as session:
            mj_card = MJCard(uuid="id-test-1", name="ID Test Card", set_code="TST")
            session.add(mj_card)
            session.commit()

            identifier = MJCardIdentifier(
                card_uuid="id-test-1",
                scryfall_id="scryfall-123",
            )
            session.add(identifier)
            session.commit()

            result = session.exec(select(MJCardIdentifier).where(MJCardIdentifier.card_uuid == "id-test-1")).first()
            assert result is not None
            assert result.scryfall_id == "scryfall-123"

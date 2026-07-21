"""Tests for mtgdb models."""

from datetime import datetime

from mtgdb.models import (
    MJCard,
    MJCardIdentifier,
    MJCardLegality,
    MJCardPrice,
    MJDeck,
    MJDeckCard,
    MJKeyword,
    MJSet,
    UserCard,
    UserDeck,
    UserDeckCard,
)
from sqlmodel import select


class TestMJCard:
    """Tests for MJCard model."""

    def test_create_card(self, sample_card):
        """Test creating a card with all fields."""
        assert sample_card.uuid == "test-uuid-1234"
        assert sample_card.name == "Test Card"
        assert sample_card.set_code == "TST"
        assert sample_card.mana_cost == "{1}{R}"
        assert sample_card.mana_value == 2.0

    def test_card_json_fields(self, sample_card):
        """Test JSON array fields."""
        assert sample_card.colors == ["R"]
        assert sample_card.types == ["Creature"]
        assert sample_card.keywords == ["Haste"]

    def test_card_defaults(self):
        """Test default values for optional fields."""
        card = MJCard(uuid="min-uuid", name="Minimal", set_code="MIN")
        assert card.colors == []
        assert card.rarity is None

    def test_persist_card(self, session, sample_card):
        """Test persisting card to database."""
        session.add(sample_card)
        session.commit()

        result = session.exec(select(MJCard).where(MJCard.uuid == "test-uuid-1234")).first()
        assert result is not None
        assert result.name == "Test Card"
        assert result.colors == ["R"]


class TestMJSet:
    """Tests for MJSet model."""

    def test_create_set(self, sample_set):
        """Test creating a set."""
        assert sample_set.code == "TST"
        assert sample_set.name == "Test Set"
        assert sample_set.type == "expansion"

    def test_set_defaults(self):
        """Test default values."""
        s = MJSet(code="DEF", name="Default Set", type="core")
        assert s.base_set_size == 0
        assert s.is_foil_only is False

    def test_persist_set(self, session, sample_set):
        """Test persisting set to database."""
        session.add(sample_set)
        session.commit()

        result = session.exec(select(MJSet).where(MJSet.code == "TST")).first()
        assert result is not None
        assert result.name == "Test Set"


class TestMJCardIdentifier:
    """Tests for MJCardIdentifier model."""

    def test_create_identifier(self, session, sample_card):
        """Test creating card identifiers."""
        session.add(sample_card)
        session.commit()

        identifier = MJCardIdentifier(
            card_uuid=sample_card.uuid,
            scryfall_id="scryfall-123",
            tcgplayer_product_id="tcg-456",
        )
        session.add(identifier)
        session.commit()

        result = session.exec(select(MJCardIdentifier).where(MJCardIdentifier.card_uuid == sample_card.uuid)).first()
        assert result is not None
        assert result.scryfall_id == "scryfall-123"


class TestMJCardLegality:
    """Tests for MJCardLegality model."""

    def test_create_legality(self, session, sample_card):
        """Test creating card legality."""
        session.add(sample_card)
        session.commit()

        legality = MJCardLegality(
            card_uuid=sample_card.uuid,
            format="standard",
            status="Legal",
        )
        session.add(legality)
        session.commit()

        result = session.exec(select(MJCardLegality).where(MJCardLegality.card_uuid == sample_card.uuid)).first()
        assert result is not None
        assert result.format == "standard"
        assert result.status == "Legal"


class TestMJCardPrice:
    """Tests for MJCardPrice model."""

    def test_create_price(self, session, sample_card):
        """Test creating card price."""
        session.add(sample_card)
        session.commit()

        price = MJCardPrice(
            card_uuid=sample_card.uuid,
            provider="tcgplayer",
            listing_type="retail",
            finish="normal",
            currency="USD",
            price=1.50,
            updated_at=datetime.utcnow(),
        )
        session.add(price)
        session.commit()

        result = session.exec(select(MJCardPrice).where(MJCardPrice.card_uuid == sample_card.uuid)).first()
        assert result is not None
        assert result.price == 1.50


class TestMJDeck:
    """Tests for MJDeck model."""

    def test_create_deck(self):
        """Test creating a precon deck."""
        deck = MJDeck(
            uuid="deck-uuid",
            file_name="TestDeck_TST",
            name="Test Deck",
            code="TST",
            main_board_count=60,
            side_board_count=15,
        )
        assert deck.name == "Test Deck"
        assert deck.main_board_count == 60


class TestMJDeckCard:
    """Tests for MJDeckCard model."""

    def test_create_deck_card(self, session):
        """Test creating a deck card entry."""
        deck = MJDeck(
            uuid="deck-uuid-2",
            file_name="TestDeck2_TST",
            name="Test Deck 2",
            code="TST",
        )
        session.add(deck)
        session.commit()

        deck_card = MJDeckCard(
            deck_uuid=deck.uuid,
            name="Lightning Bolt",
            board="mainBoard",
            count=4,
            mana_cost="{R}",
            mana_value=1.0,
            colors=["R"],
            types=["Instant"],
        )
        session.add(deck_card)
        session.commit()

        result = session.exec(select(MJDeckCard).where(MJDeckCard.deck_uuid == deck.uuid)).first()
        assert result is not None
        assert result.count == 4


class TestMJKeyword:
    """Tests for MJKeyword model."""

    def test_create_keyword(self, session):
        """Test creating a keyword."""
        keyword = MJKeyword(name="Flying", type="keywordAbilities")
        session.add(keyword)
        session.commit()

        result = session.exec(select(MJKeyword).where(MJKeyword.name == "Flying")).first()
        assert result is not None
        assert result.type == "keywordAbilities"


class TestUserCard:
    """Tests for UserCard model."""

    def test_create_user_card(self, sample_user_card):
        """Test creating a user card entry."""
        assert sample_user_card.quantity_owned == 4
        assert sample_user_card.quantity_owned_foil == 1

    def test_owns_property(self, sample_user_card):
        """Test owns property."""
        assert sample_user_card.owns is True

        empty_card = UserCard(card_uuid="empty")
        assert empty_card.owns is False

    def test_wants_property(self, sample_user_card):
        """Test wants property."""
        assert sample_user_card.wants is True

        no_want = UserCard(card_uuid="no-want", quantity_owned=1)
        assert no_want.wants is False

    def test_total_owned(self, sample_user_card):
        """Test total_owned property."""
        assert sample_user_card.total_owned == 5  # 4 + 1 foil

    def test_total_wanted(self, sample_user_card):
        """Test total_wanted property."""
        assert sample_user_card.total_wanted == 2

    def test_persist_user_card(self, session, sample_card, sample_user_card):
        """Test persisting user card."""
        session.add(sample_card)
        session.commit()

        session.add(sample_user_card)
        session.commit()

        result = session.exec(select(UserCard).where(UserCard.card_uuid == "test-uuid-1234")).first()
        assert result is not None
        assert result.quantity_owned == 4


class TestUserDeck:
    """Tests for UserDeck model."""

    def test_create_user_deck(self, sample_user_deck):
        """Test creating a user deck."""
        assert sample_user_deck.name == "Test Deck"
        assert sample_user_deck.format == "standard"

    def test_persist_user_deck(self, session, sample_user_deck):
        """Test persisting user deck."""
        session.add(sample_user_deck)
        session.commit()

        result = session.exec(select(UserDeck).where(UserDeck.name == "Test Deck")).first()
        assert result is not None
        assert result.format == "standard"


class TestUserDeckCard:
    """Tests for UserDeckCard model."""

    def test_create_user_deck_card(self, session, sample_card, sample_user_deck):
        """Test creating a user deck card entry."""
        session.add(sample_card)
        session.add(sample_user_deck)
        session.commit()

        deck_card = UserDeckCard(
            deck_id=sample_user_deck.id,
            card_uuid=sample_card.uuid,
            board="main",
            count=4,
            is_foil=False,
        )
        session.add(deck_card)
        session.commit()

        result = session.exec(select(UserDeckCard).where(UserDeckCard.deck_id == sample_user_deck.id)).first()
        assert result is not None
        assert result.count == 4

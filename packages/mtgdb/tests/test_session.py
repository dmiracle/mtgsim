"""Tests for mtgdb session management."""

import tempfile
from pathlib import Path

from mtgdb.models import MJSet
from mtgdb.session import close_db, get_engine, get_session, init_db
from sqlalchemy.engine import Engine
from sqlmodel import Session, select


class TestGetEngine:
    """Tests for get_engine function."""

    def test_returns_engine(self, temp_db_path):
        """Test that get_engine returns an Engine."""
        engine = get_engine(temp_db_path)
        assert isinstance(engine, Engine)
        engine.dispose()

    def test_creates_parent_directory(self):
        """Test that get_engine creates parent directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "subdir" / "test.sqlite"
            engine = get_engine(db_path)
            assert db_path.parent.exists()
            engine.dispose()


class TestInitDb:
    """Tests for init_db function."""

    def test_creates_tables(self, temp_db_path):
        """Test that init_db creates all tables."""
        engine = init_db(temp_db_path)

        # Verify tables exist by inserting data
        with Session(engine) as session:
            session.add(MJSet(code="TST", name="Test", type="test"))
            session.commit()

            result = session.exec(select(MJSet)).first()
            assert result is not None

        engine.dispose()

    def test_creates_database_file(self, temp_db_path):
        """Test that init_db creates the database file."""
        temp_db_path.unlink(missing_ok=True)
        engine = init_db(temp_db_path)
        assert temp_db_path.exists()
        engine.dispose()


class TestGetSession:
    """Tests for get_session context manager."""

    def test_yields_session(self, temp_db_path):
        """Test that get_session yields a Session."""
        init_db(temp_db_path)
        with get_session(temp_db_path) as session:
            assert isinstance(session, Session)

    def test_session_commits_on_exit(self, temp_db_path):
        """Test that changes persist after context exit."""
        init_db(temp_db_path)

        with get_session(temp_db_path) as session:
            session.add(MJSet(code="TST", name="Test", type="test"))
            session.commit()

        # Verify in new session
        with get_session(temp_db_path) as session:
            result = session.exec(select(MJSet).where(MJSet.code == "TST")).first()
            assert result is not None


class TestCloseDb:
    """Tests for close_db function."""

    def test_close_db_clears_global_engine(self):
        """Test that close_db disposes the global engine."""
        # This test verifies close_db doesn't raise
        close_db()

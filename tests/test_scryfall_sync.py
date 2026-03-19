"""Tests for Scryfall oracle tag sync."""

import json
import tempfile
from pathlib import Path

import pytest
from mtgdb.models import MJCardTag
from mtgdb.session import get_engine, init_db
from mtgdb.sync.scryfall import sync_tags
from sqlmodel import Session, select


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Ensure database is initialized."""
    init_db()


@pytest.fixture
def sample_tags_file():
    """Create a temporary tags JSON file for testing."""
    data = {
        "mana-dork": ["Llanowar Elves", "Birds of Paradise", "Elvish Mystic"],
        "ramp": ["Llanowar Elves", "Cultivate", "Kodama's Reach"],
        "removal": ["Lightning Bolt", "Swords to Plowshares"],
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        return Path(f.name)


class TestSyncTags:
    """Tests for sync_tags function."""

    def test_sync_tags_populates_table(self, sample_tags_file):
        """sync_tags inserts rows into mj_card_tag."""
        sync_tags(sample_tags_file)

        engine = get_engine()
        with Session(engine) as session:
            results = session.exec(select(MJCardTag)).all()
            assert len(results) == 8  # 3 + 3 + 2

    def test_sync_tags_correct_data(self, sample_tags_file):
        """sync_tags stores correct card_name and tag pairs."""
        sync_tags(sample_tags_file)

        engine = get_engine()
        with Session(engine) as session:
            dorks = session.exec(select(MJCardTag).where(MJCardTag.tag == "mana-dork")).all()
            names = {t.card_name for t in dorks}
            assert names == {"Llanowar Elves", "Birds of Paradise", "Elvish Mystic"}

    def test_sync_tags_clears_old_data(self, sample_tags_file):
        """sync_tags replaces existing data on re-sync."""
        sync_tags(sample_tags_file)
        sync_tags(sample_tags_file)

        engine = get_engine()
        with Session(engine) as session:
            results = session.exec(select(MJCardTag)).all()
            assert len(results) == 8

    def test_sync_tags_missing_file(self):
        """sync_tags handles missing file gracefully."""
        sync_tags(Path("/nonexistent/file.json"))

    def test_sync_tags_card_in_multiple_tags(self, sample_tags_file):
        """A card can appear in multiple tags."""
        sync_tags(sample_tags_file)

        engine = get_engine()
        with Session(engine) as session:
            llanowar = session.exec(select(MJCardTag).where(MJCardTag.card_name == "Llanowar Elves")).all()
            tags = {t.tag for t in llanowar}
            assert tags == {"mana-dork", "ramp"}

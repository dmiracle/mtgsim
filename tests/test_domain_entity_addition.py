"""Property-based tests for domain entity addition correctness.

Feature: domain-api-consolidation, Property 3: Domain Entity Addition Correctness
Validates: Requirements 1.1, 2.2
"""

import tempfile
from datetime import datetime
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlmodel import Session, select

from mtgsim.db.domain_models import DomainCard
from mtgsim.db.domain_session import init_domain_db
from mtgsim.db.reference_models import MTGJsonCard, MTGJsonDeck, MTGJsonSet


class TestDomainEntityAdditionCorrectness:
    """Property-based tests for domain entity addition correctness."""

    def setup_method(self):
        """Set up a temporary database for each test."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".sqlite")
        self.temp_db_path = Path(self.temp_db.name)
        self.temp_db.close()

        # Initialize the temporary database
        self.engine = init_domain_db(self.temp_db_path)

        # Keep track of used identifiers to avoid duplicates within a test
        self.used_uuids = set()
        self.used_codes = set()
        self.used_filenames = set()

    def teardown_method(self):
        """Clean up the temporary database."""
        if self.temp_db_path.exists():
            self.temp_db_path.unlink()

    @given(
        uuid=st.text(min_size=36, max_size=36, alphabet="0123456789abcdef-"),
        name=st.text(min_size=1, max_size=50),
        mana_cost=st.one_of(st.none(), st.text(min_size=1, max_size=10)),
        set_code=st.text(min_size=3, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        rarity=st.sampled_from(["common", "uncommon", "rare", "mythic"]),
        colors=st.lists(st.sampled_from(["W", "U", "B", "R", "G"]), min_size=0, max_size=3, unique=True),
        types=st.lists(st.text(min_size=1, max_size=10), min_size=1, max_size=3, unique=True),
    )
    @settings(max_examples=3)
    def test_card_addition_preserves_all_reference_data(
        self, uuid: str, name: str, mana_cost: str, set_code: str, rarity: str, colors: list[str], types: list[str]
    ):
        """
        Property 3: Domain Entity Addition Correctness - Card Data Preservation
        For any card added to the domain tables, it should contain all enhanced fields
        properly transformed from the reference data.
        **Validates: Requirements 1.1, 2.2**
        """
        # Make UUID unique within this test run
        counter = 0
        original_uuid = uuid
        while uuid in self.used_uuids:
            counter += 1
            uuid = f"{original_uuid[:-2]}{counter:02d}"
        self.used_uuids.add(uuid)

        # Make set code unique within this test run
        counter = 0
        original_set_code = set_code
        while set_code in self.used_codes:
            counter += 1
            set_code = f"{original_set_code[:-1]}{counter}"
        self.used_codes.add(set_code)

        # Create unique scryfall_id based on uuid
        scryfall_id = f"test-scryfall-{uuid[-8:]}"

        with Session(self.engine) as session:
            # Create a reference card with test data
            ref_card = MTGJsonCard(
                uuid=uuid,
                name=name,
                mana_cost=mana_cost,
                mana_value=3.0 if mana_cost else 0.0,
                type="Creature — Human Wizard",
                oracle_text="Test oracle text",
                flavor_text="Test flavor text",
                power="2",
                toughness="3",
                rarity=rarity,
                set_code=set_code,
                colors=colors,
                color_identity=colors,
                types=types,
                subtypes=["Human", "Wizard"],
                supertypes=["Legendary"] if len(types) > 2 else [],
                legalities={"standard": "legal", "modern": "legal"},
                scryfall_id=scryfall_id,  # Use unique scryfall_id
                has_foil=True,
                has_non_foil=True,
                is_reprint=False,
            )
            session.add(ref_card)
            session.commit()

            # Import the transformation function
            from mtgsim.cli.domain_commands import transform_reference_card_to_domain

            # Transform to domain card
            domain_card = transform_reference_card_to_domain(ref_card, session)
            session.commit()

            # Verify all essential fields are preserved
            assert domain_card.uuid == ref_card.uuid
            assert domain_card.name == ref_card.name
            assert domain_card.mana_cost == ref_card.mana_cost
            assert domain_card.mana_value == ref_card.mana_value
            assert domain_card.type_line == ref_card.type
            assert domain_card.oracle_text == ref_card.oracle_text
            assert domain_card.flavor_text == ref_card.flavor_text
            assert domain_card.power == ref_card.power
            assert domain_card.toughness == ref_card.toughness
            assert domain_card.rarity == ref_card.rarity
            assert domain_card.set_code == ref_card.set_code
            assert domain_card.legalities == ref_card.legalities
            assert domain_card.scryfall_id == scryfall_id
            assert domain_card.has_foil == ref_card.has_foil
            assert domain_card.has_non_foil == ref_card.has_non_foil
            assert domain_card.is_reprint == ref_card.is_reprint

            # Verify computed properties work
            assert set(domain_card.color_identity) == set(colors)  # Use set comparison for order independence
            assert len(domain_card.type_list) == len(types)

            # Verify metadata fields are set
            assert domain_card.source == "mtgjson"
            assert isinstance(domain_card.added_at, datetime)

    @given(
        code=st.text(min_size=3, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        name=st.text(min_size=1, max_size=50),
        set_type=st.sampled_from(["expansion", "core", "masters"]),
        release_date=st.dates(min_value=datetime(2020, 1, 1).date(), max_value=datetime(2025, 12, 31).date()).map(str),
        base_set_size=st.integers(min_value=50, max_value=300),
    )
    @settings(max_examples=3)
    def test_set_addition_preserves_all_reference_data(
        self, code: str, name: str, set_type: str, release_date: str, base_set_size: int
    ):
        """
        Property 3: Domain Entity Addition Correctness - Set Data Preservation
        For any set added to the domain tables, it should contain all enhanced fields
        properly transformed from the reference data.
        **Validates: Requirements 1.1, 2.2**
        """
        # Make code unique within this test run
        counter = 0
        original_code = code
        while code in self.used_codes:
            counter += 1
            code = f"{original_code[:-1]}{counter}"
        self.used_codes.add(code)

        with Session(self.engine) as session:
            # Create a reference set with test data
            ref_set = MTGJsonSet(
                code=code,
                name=name,
                type=set_type,
                release_date=release_date,
                base_set_size=base_set_size,
                total_set_size=base_set_size + 20,
                block="Test Block",
                keyrune_code=code.lower(),
                is_foil_only=False,
                is_online_only=False,
                languages=["en", "es"],
                translations={"es": f"{name} (Spanish)"},
            )
            session.add(ref_set)
            session.commit()

            # Import the transformation function
            from mtgsim.cli.domain_commands import transform_reference_set_to_domain

            # Transform to domain set
            domain_set = transform_reference_set_to_domain(ref_set, session)
            session.add(domain_set)
            session.commit()

            # Verify all essential fields are preserved
            assert domain_set.code == ref_set.code
            assert domain_set.name == ref_set.name
            assert domain_set.type == ref_set.type
            assert domain_set.release_date == ref_set.release_date
            assert domain_set.base_set_size == ref_set.base_set_size
            assert domain_set.total_set_size == ref_set.total_set_size
            assert domain_set.block == ref_set.block
            assert domain_set.keyrune_code == ref_set.keyrune_code
            assert domain_set.is_foil_only == ref_set.is_foil_only
            assert domain_set.is_online_only == ref_set.is_online_only
            assert domain_set.languages == ref_set.languages
            assert domain_set.translations == ref_set.translations

            # Verify metadata fields are set
            assert domain_set.source == "mtgjson"
            assert isinstance(domain_set.added_at, datetime)

    @given(
        uuid=st.text(min_size=36, max_size=36, alphabet="0123456789abcdef-"),
        name=st.text(min_size=1, max_size=50),
        code=st.text(min_size=3, max_size=5, alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        deck_type=st.sampled_from(["constructed", "commander"]),
        main_board_count=st.integers(min_value=60, max_value=80),
        side_board_count=st.integers(min_value=0, max_value=15),
    )
    @settings(max_examples=3)
    def test_deck_addition_preserves_all_reference_data(
        self, uuid: str, name: str, code: str, deck_type: str, main_board_count: int, side_board_count: int
    ):
        """
        Property 3: Domain Entity Addition Correctness - Deck Data Preservation
        For any deck added to the domain tables, it should contain all enhanced fields
        properly transformed from the reference data.
        **Validates: Requirements 1.1, 2.2**
        """
        # Make UUID unique within this test run
        counter = 0
        original_uuid = uuid
        while uuid in self.used_uuids:
            counter += 1
            uuid = f"{original_uuid[:-2]}{counter:02d}"
        self.used_uuids.add(uuid)

        # Make filename unique within this test run
        filename = f"{name.replace(' ', '_').lower()}.json"
        counter = 0
        original_filename = filename
        while filename in self.used_filenames:
            counter += 1
            filename = f"{original_filename[:-5]}_{counter}.json"
        self.used_filenames.add(filename)

        with Session(self.engine) as session:
            # Create a reference deck with test data
            ref_deck = MTGJsonDeck(
                uuid=uuid,
                file_name=filename,  # Use the unique filename
                code=code,
                name=name,
                type=deck_type,
                release_date="2024-01-01",
                main_board_count=main_board_count,
                side_board_count=side_board_count,
                commander_count=1 if deck_type == "commander" else 0,
                commander=[{"name": "Test Commander", "uuid": "commander-uuid"}] if deck_type == "commander" else [],
                meta={"format": deck_type, "archetype": "test"},
            )
            session.add(ref_deck)
            session.commit()

            # Import the transformation function
            from mtgsim.cli.domain_commands import transform_reference_deck_to_domain

            # Transform to domain deck
            domain_deck = transform_reference_deck_to_domain(ref_deck, session)
            session.add(domain_deck)
            session.commit()

            # Verify all essential fields are preserved
            assert domain_deck.uuid == ref_deck.uuid
            assert domain_deck.file_name == ref_deck.file_name
            assert domain_deck.code == ref_deck.code
            assert domain_deck.name == ref_deck.name
            assert domain_deck.type == ref_deck.type
            assert domain_deck.release_date == ref_deck.release_date
            assert domain_deck.main_board_count == ref_deck.main_board_count
            assert domain_deck.side_board_count == ref_deck.side_board_count
            assert domain_deck.commander_count == ref_deck.commander_count
            assert domain_deck.commander == ref_deck.commander
            # MTGJsonDeck doesn't have meta field, so domain deck should have empty meta
            assert domain_deck.meta == {}

            # Verify metadata fields are set
            assert domain_deck.source == "mtgjson"
            assert isinstance(domain_deck.added_at, datetime)

    def test_card_addition_creates_proper_relationships(self):
        """
        Property 3: Domain Entity Addition Correctness - Relationship Creation
        For any card added to domain tables, all relationship links should be
        properly created and navigable.
        **Validates: Requirements 1.1, 2.2**
        """
        with Session(self.engine) as session:
            # Create a reference card with relationship data
            ref_card = MTGJsonCard(
                uuid="test-card-uuid",
                name="Test Card",
                mana_cost="{2}{U}{R}",
                type="Instant — Arcane",
                colors=["U", "R"],
                color_identity=["U", "R"],
                types=["Instant"],
                subtypes=["Arcane"],
                supertypes=["Legendary"],
                set_code="TST",
                rarity="rare",
            )
            session.add(ref_card)
            session.commit()

            # Import the transformation function
            from mtgsim.cli.domain_commands import transform_reference_card_to_domain

            # Transform to domain card
            domain_card = transform_reference_card_to_domain(ref_card, session)
            session.commit()

            # Refresh to load relationships
            session.refresh(domain_card)

            # Verify color relationships
            assert len(domain_card.color_links) == 2
            color_values = {link.color for link in domain_card.color_links}
            assert color_values == {"U", "R"}

            # Verify type relationships
            assert len(domain_card.card_types) == 1
            assert domain_card.card_types[0].card_type == "Instant"

            # Verify supertype relationships
            assert len(domain_card.supertypes) == 1
            assert domain_card.supertypes[0].supertype == "Legendary"

            # Verify subtype relationships
            assert len(domain_card.subtype_links) == 1
            assert domain_card.subtype_links[0].subtype == "Arcane"

            # Verify computed properties work through relationships
            assert set(domain_card.color_identity) == {"U", "R"}  # Use set comparison for order independence
            assert domain_card.type_list == ["Instant"]
            assert domain_card.subtypes == ["Arcane"]

    def test_mana_cost_parsing_correctness(self):
        """
        Property 3: Domain Entity Addition Correctness - Mana Cost Parsing
        For any card with a mana cost, the individual mana components should be
        correctly parsed and stored in separate fields.
        **Validates: Requirements 1.1, 2.2**
        """
        test_cases = [
            ("{2}{W}{U}", {"white": 1, "blue": 1, "generic": 2}),
            ("{X}{R}{R}{R}", {"red": 3, "generic": 0}),  # X is not counted as generic
            ("{5}{B}{G}", {"black": 1, "green": 1, "generic": 5}),
            ("{C}{C}{W}", {"white": 1, "colorless": 2}),
            ("", {"white": 0, "blue": 0, "black": 0, "red": 0, "green": 0, "colorless": 0, "generic": 0}),
        ]

        with Session(self.engine) as session:
            for mana_cost, expected_counts in test_cases:
                # Create reference card
                ref_card = MTGJsonCard(
                    uuid=f"test-{hash(mana_cost)}",
                    name="Test Card",
                    mana_cost=mana_cost,
                    set_code="TST",
                    rarity="common",
                )
                session.add(ref_card)
                session.commit()

                # Import the transformation function
                from mtgsim.cli.domain_commands import transform_reference_card_to_domain

                # Transform to domain card
                domain_card = transform_reference_card_to_domain(ref_card, session)
                session.commit()

                # Verify mana cost parsing
                assert domain_card.mana_cost_white == expected_counts.get("white", 0)
                assert domain_card.mana_cost_blue == expected_counts.get("blue", 0)
                assert domain_card.mana_cost_black == expected_counts.get("black", 0)
                assert domain_card.mana_cost_red == expected_counts.get("red", 0)
                assert domain_card.mana_cost_green == expected_counts.get("green", 0)
                assert domain_card.mana_cost_colorless == expected_counts.get("colorless", 0)
                assert domain_card.mana_cost_generic == expected_counts.get("generic", 0)

                # Clean up for next iteration
                session.delete(domain_card)
                session.delete(ref_card)
                session.commit()

    def test_selective_entity_addition_isolation(self):
        """
        Property 3: Domain Entity Addition Correctness - Selective Addition
        For any card addition operation, only the specified card should be added
        to the domain tables without affecting other entities.
        **Validates: Requirements 5.2**
        """
        with Session(self.engine) as session:
            # Create multiple reference cards
            ref_cards = [
                MTGJsonCard(uuid="card-1", name="Card 1", set_code="TST", rarity="common"),
                MTGJsonCard(uuid="card-2", name="Card 2", set_code="TST", rarity="uncommon"),
                MTGJsonCard(uuid="card-3", name="Card 3", set_code="TST", rarity="rare"),
            ]

            for card in ref_cards:
                session.add(card)
            session.commit()

            # Import the transformation function
            from mtgsim.cli.domain_commands import transform_reference_card_to_domain

            # Add only the first card
            transform_reference_card_to_domain(ref_cards[0], session)
            session.commit()

            # Verify only one card exists in domain tables
            domain_cards = session.exec(select(DomainCard)).all()
            assert len(domain_cards) == 1
            assert domain_cards[0].uuid == "card-1"

            # Add the second card
            transform_reference_card_to_domain(ref_cards[1], session)
            session.commit()

            # Verify exactly two cards exist in domain tables
            domain_cards = session.exec(select(DomainCard)).all()
            assert len(domain_cards) == 2
            domain_uuids = {card.uuid for card in domain_cards}
            assert domain_uuids == {"card-1", "card-2"}

            # Verify the third card is still not added
            assert "card-3" not in domain_uuids

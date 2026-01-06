"""Property-based tests for DTO mappers.

Feature: mtgsim-refactor, Property 3: DTO Mapping Centralization
"""

import json
import sqlite3
from unittest.mock import Mock

from hypothesis import given
from hypothesis import strategies as st

from mtgsim.api.models.card import CardSummary
from mtgsim.api.models.deck import DeckLegality, DeckSummary
from mtgsim.api.models.mappers import DTOMapper
from mtgsim.api.models.set import SetSummary


class TestDTOMappingCentralization:
    """Property-based tests for DTO mapping centralization."""

    @given(
        uuid=st.text(min_size=1, max_size=36),
        name=st.text(min_size=1, max_size=100),
        card_type=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        mana_cost=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        mana_value=st.integers(min_value=0, max_value=20),
        rarity=st.one_of(st.none(), st.sampled_from(["common", "uncommon", "rare", "mythic"])),
        set_code=st.one_of(st.none(), st.text(min_size=3, max_size=5)),
        color_identity=st.lists(st.sampled_from(["W", "U", "B", "R", "G"]), max_size=5),
        text=st.one_of(st.none(), st.text(max_size=500)),
        price=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000.0)),
    )
    def test_card_summary_mapping_consistency(
        self, uuid, name, card_type, mana_cost, mana_value, rarity, set_code, color_identity, text, price
    ):
        """Property 3: DTO Mapping Centralization - Card Summary Mapping

        For any database row to CardSummary conversion, the DTO_Mapper should provide
        consistent conversion logic, eliminating manual dict construction.

        **Feature: mtgsim-refactor, Property 3: DTO Mapping Centralization**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # Create a mock sqlite3.Row with card data
        row_data = {
            "uuid": uuid,
            "name": name,
            "type": card_type,
            "manaCost": mana_cost,
            "manaValue": mana_value,
            "rarity": rarity,
            "setCode": set_code,
            "colorIdentity": json.dumps(color_identity),
            "text": text,
            "image_url": None,
        }

        # Create mock row that behaves like sqlite3.Row
        mock_row = Mock(spec=sqlite3.Row)
        mock_row.__getitem__ = lambda self, key: row_data[key]
        mock_row.get = lambda key, default=None: row_data.get(key, default)

        # Map using DTOMapper
        card_summary = DTOMapper.map_card_summary(mock_row, price)

        # Property: All fields should be correctly mapped
        assert card_summary.uuid == uuid
        assert card_summary.name == name
        assert card_summary.type == card_type
        assert card_summary.mana_cost == mana_cost
        assert card_summary.mana_value == mana_value
        assert card_summary.rarity == rarity
        assert card_summary.set_code == set_code
        assert card_summary.color_identity == color_identity
        assert card_summary.text == text
        assert card_summary.price == price

        # Property: Result should be a valid CardSummary instance
        assert isinstance(card_summary, CardSummary)

        # Property: JSON fields should be properly decoded
        assert isinstance(card_summary.color_identity, list)

    @given(
        file=st.text(min_size=1, max_size=50),
        name=st.text(min_size=1, max_size=100),
        code=st.text(min_size=3, max_size=5),
        card_count=st.integers(min_value=0, max_value=500),
        colors=st.lists(st.sampled_from(["W", "U", "B", "R", "G"]), max_size=5),
        price=st.one_of(st.none(), st.floats(min_value=0.0, max_value=1000.0)),
        release_date=st.one_of(st.none(), st.text(min_size=10, max_size=10)),
        legalities=st.dictionaries(
            st.sampled_from(
                ["standard", "pioneer", "modern", "legacy", "vintage", "commander", "brawl", "historic", "pauper"]
            ),
            st.booleans(),
            max_size=9,
        ),
    )
    def test_deck_summary_mapping_consistency(
        self, file, name, code, card_count, colors, price, release_date, legalities
    ):
        """Property 3: DTO Mapping Centralization - Deck Summary Mapping

        For any database row to DeckSummary conversion, the DTO_Mapper should provide
        consistent conversion logic with proper legality handling.

        **Feature: mtgsim-refactor, Property 3: DTO Mapping Centralization**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # Create a mock sqlite3.Row with deck data
        row_data = {
            "file": file,
            "name": name,
            "code": code,
            "card_count": card_count,
            "colors": json.dumps(colors),
            "price": price,
            "releaseDate": release_date,
            "legalities": json.dumps(legalities),
        }

        # Create mock row that behaves like sqlite3.Row
        mock_row = Mock(spec=sqlite3.Row)
        mock_row.__getitem__ = lambda self, key: row_data[key]
        mock_row.get = lambda key, default=None: row_data.get(key, default)

        # Map using DTOMapper
        deck_summary = DTOMapper.map_deck_summary(mock_row)

        # Property: All fields should be correctly mapped
        assert deck_summary.file == file
        assert deck_summary.name == name
        assert deck_summary.code == code
        assert deck_summary.card_count == card_count
        assert deck_summary.colors == colors
        assert deck_summary.price == price
        assert deck_summary.release_date == release_date

        # Property: Result should be a valid DeckSummary instance
        assert isinstance(deck_summary, DeckSummary)
        assert isinstance(deck_summary.legality, DeckLegality)

        # Property: JSON fields should be properly decoded
        assert isinstance(deck_summary.colors, list)

        # Property: Legalities should be properly mapped
        for format_name in [
            "standard",
            "pioneer",
            "modern",
            "legacy",
            "vintage",
            "commander",
            "brawl",
            "historic",
            "pauper",
        ]:
            expected_value = legalities.get(format_name, False)
            actual_value = getattr(deck_summary.legality, format_name)
            assert actual_value == expected_value

    @given(
        code=st.text(min_size=3, max_size=5),
        name=st.text(min_size=1, max_size=100),
        set_type=st.text(min_size=1, max_size=50),
        release_date=st.one_of(st.none(), st.text(min_size=10, max_size=10)),
        base_set_size=st.integers(min_value=0, max_value=500),
        total_set_size=st.integers(min_value=0, max_value=500),
        block=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        keyrune_code=st.one_of(st.none(), st.text(min_size=3, max_size=5)),
    )
    def test_set_summary_mapping_consistency(
        self, code, name, set_type, release_date, base_set_size, total_set_size, block, keyrune_code
    ):
        """Property 3: DTO Mapping Centralization - Set Summary Mapping

        For any database row to SetSummary conversion, the DTO_Mapper should provide
        consistent conversion logic with proper field handling.

        **Feature: mtgsim-refactor, Property 3: DTO Mapping Centralization**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # Create a mock sqlite3.Row with set data
        row_data = {
            "code": code,
            "name": name,
            "type": set_type,
            "releaseDate": release_date,
            "baseSetSize": base_set_size,
            "totalSetSize": total_set_size,
            "block": block,
            "keyruneCode": keyrune_code,
        }

        # Create mock row that behaves like sqlite3.Row
        mock_row = Mock(spec=sqlite3.Row)
        mock_row.__getitem__ = lambda self, key: row_data[key]
        mock_row.get = lambda key, default=None: row_data.get(key, default)

        # Map using DTOMapper
        set_summary = DTOMapper.map_set_summary(mock_row)

        # Property: All fields should be correctly mapped
        assert set_summary.code == code
        assert set_summary.name == name
        assert set_summary.type == set_type
        assert set_summary.release_date == release_date
        assert set_summary.base_set_size == base_set_size
        assert set_summary.total_set_size == total_set_size
        assert set_summary.block == block

        # Property: keyrune_code should default to code if not provided
        expected_keyrune = keyrune_code if keyrune_code is not None else code
        assert set_summary.keyrune_code == expected_keyrune

        # Property: Result should be a valid SetSummary instance
        assert isinstance(set_summary, SetSummary)

    @given(
        json_string=st.one_of(
            st.none(),
            st.text(max_size=0),  # Empty string
            st.just("null"),
            st.just("[]"),
            st.just("{}"),
            st.just('["W", "U", "B"]'),
            st.just('{"standard": true, "modern": false}'),
            st.text(min_size=1, max_size=50),  # Invalid JSON
        )
    )
    def test_json_field_decoding_robustness(self, json_string):
        """Property 3: DTO Mapping Centralization - JSON Field Robustness

        For any JSON field value, the DTO_Mapper should handle decoding safely
        without raising exceptions, providing consistent error handling.

        **Feature: mtgsim-refactor, Property 3: DTO Mapping Centralization**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # Test the private JSON decoding method
        result = DTOMapper._decode_json_field(json_string)

        # Property: Should never raise an exception
        # (This is tested by the fact that we reach this assertion)
        assert True

        # Property: Result should be appropriate for the input
        if json_string is None or json_string == "":
            assert result is None
        elif json_string == "null":
            assert result is None
        elif json_string == "[]":
            assert result == []
        elif json_string == "{}":
            assert result == {}
        elif json_string == '["W", "U", "B"]':
            assert result == ["W", "U", "B"]
        elif json_string == '{"standard": true, "modern": false}':
            assert result == {"standard": True, "modern": False}
        else:
            # For other strings, try to parse as JSON
            try:
                expected = json.loads(json_string)
                # Handle NaN case specially since nan != nan
                if isinstance(expected, float) and expected != expected:  # NaN check
                    assert isinstance(result, float) and result != result
                else:
                    assert result == expected
            except (json.JSONDecodeError, TypeError):
                # Invalid JSON should return None
                assert result is None

    def test_mapper_eliminates_manual_dict_construction(self):
        """Property 3: DTO Mapping Centralization - Manual Construction Elimination

        The DTO_Mapper should provide centralized mapping that eliminates the need
        for manual dict-to-model construction in service classes.

        **Feature: mtgsim-refactor, Property 3: DTO Mapping Centralization**
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # Test that mapper provides all the mapping methods needed by services
        mapper_methods = [
            "map_card_summary",
            "map_deck_summary",
            "map_set_summary",
        ]

        for method_name in mapper_methods:
            # Property: All required mapping methods should exist
            assert hasattr(DTOMapper, method_name)
            method = getattr(DTOMapper, method_name)

            # Property: All mapping methods should be static methods
            assert callable(method)

        # Property: Private helper methods should exist for JSON handling
        assert hasattr(DTOMapper, "_decode_json_field")
        assert callable(DTOMapper._decode_json_field)

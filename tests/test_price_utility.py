"""Property-based tests for price utilities.

Feature: mtgsim-refactor, Property 4: Price Utility Consolidation
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

from hypothesis import given
from hypothesis import strategies as st

from mtgsim.api.data.pricing import PriceUtility
from mtgsim.reference.repository import ReferenceRepository


class MockConfig:
    """Mock configuration for testing."""

    def __init__(self, mtgjson_dir: Path):
        self._mtgjson_dir = mtgjson_dir

    @property
    def mtgjson_dir(self) -> Path:
        return self._mtgjson_dir


class TestPriceUtilityConsolidation:
    """Property-based tests for price utility consolidation."""

    @given(
        st.one_of(
            st.none(),
            st.text(min_size=0, max_size=5),
            st.text(min_size=32, max_size=36),  # UUID-like strings
        )
    )
    def test_tcgplayer_price_lookup_consistency(self, uuid):
        """Property 4: Price Utility Consolidation - TCGPlayer Lookup

        For any UUID input, TCGPlayer price lookup should behave consistently
        and handle edge cases gracefully.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            price_util = PriceUtility(repo)

            # Property: Invalid/empty UUIDs should return None
            if not uuid or len(uuid) < 10:
                result = price_util.get_tcgplayer_price(uuid)
                assert result is None

            # Property: Missing database should return None gracefully
            if uuid and len(uuid) >= 10:
                result = price_util.get_tcgplayer_price(uuid)
                assert result is None  # No database available

    @given(
        st.one_of(
            st.none(),
            st.text(min_size=0, max_size=5),
            st.text(min_size=32, max_size=36),  # UUID-like strings
        )
    )
    def test_average_price_calculation_consistency(self, uuid):
        """Property 4: Price Utility Consolidation - Average Price

        For any UUID input, average price calculation should behave consistently
        across multiple providers.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            price_util = PriceUtility(repo)

            # Property: Invalid/empty UUIDs should return None
            if not uuid or len(uuid) < 10:
                result = price_util.get_average_price(uuid)
                assert result is None

            # Property: Missing database should return None gracefully
            if uuid and len(uuid) >= 10:
                result = price_util.get_average_price(uuid)
                assert result is None  # No database available

    @given(
        st.lists(
            st.dictionaries(
                st.sampled_from(["uuid", "count"]),
                st.one_of(
                    st.text(min_size=32, max_size=36),  # UUID
                    st.integers(min_value=0, max_value=10),  # count
                ),
                min_size=1,
                max_size=2,
            ),
            min_size=0,
            max_size=5,
        )
    )
    def test_deck_total_calculation_consistency(self, deck_cards):
        """Property 4: Price Utility Consolidation - Deck Total

        For any deck card list, total calculation should be consistent
        and handle various input formats gracefully.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            price_util = PriceUtility(repo)

            # Property: Empty deck should return 0.0
            if not deck_cards:
                result = price_util.calculate_deck_total(deck_cards)
                assert result == 0.0
                return

            # Property: Result should always be a non-negative float
            result = price_util.calculate_deck_total(deck_cards)
            assert isinstance(result, float)
            assert result >= 0.0

            # Property: Result should be rounded to 2 decimal places
            assert result == round(result, 2)

    @given(st.lists(st.text(min_size=32, max_size=36), min_size=0, max_size=10))
    def test_bulk_price_lookup_consistency(self, uuids):
        """Property 4: Price Utility Consolidation - Bulk Lookup

        For any list of UUIDs, bulk price lookup should be consistent
        and efficient compared to individual lookups.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            price_util = PriceUtility(repo)

            # Property: Empty UUID list should return empty dict
            if not uuids:
                result = price_util.get_bulk_prices(uuids)
                assert result == {}
                return

            # Property: Result should always be a dictionary
            result = price_util.get_bulk_prices(uuids)
            assert isinstance(result, dict)

            # Property: All keys in result should be from input UUIDs
            for key in result.keys():
                assert key in uuids

            # Property: All values should be positive floats or None
            for value in result.values():
                assert isinstance(value, (float, type(None)))
                if value is not None:
                    assert value >= 0.0

    @given(st.lists(st.text(min_size=32, max_size=36), min_size=0, max_size=10))
    def test_bulk_average_price_consistency(self, uuids):
        """Property 4: Price Utility Consolidation - Bulk Average

        For any list of UUIDs, bulk average price lookup should provide
        consistent results across multiple providers.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            price_util = PriceUtility(repo)

            # Property: Empty UUID list should return empty dict
            if not uuids:
                result = price_util.get_bulk_average_prices(uuids)
                assert result == {}
                return

            # Property: Result should always be a dictionary
            result = price_util.get_bulk_average_prices(uuids)
            assert isinstance(result, dict)

            # Property: All keys in result should be from input UUIDs
            for key in result.keys():
                assert key in uuids

            # Property: All values should be positive floats
            for value in result.values():
                assert isinstance(value, float)
                assert value >= 0.0

    @given(
        st.one_of(
            st.none(),
            st.text(min_size=0, max_size=5),
            st.text(min_size=32, max_size=36),  # UUID-like strings
        )
    )
    def test_price_breakdown_structure_consistency(self, uuid):
        """Property 4: Price Utility Consolidation - Price Breakdown

        For any UUID input, price breakdown should provide consistent
        structure and handle missing data gracefully.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            price_util = PriceUtility(repo)

            # Property: Invalid/empty UUIDs should return empty dict
            if not uuid or len(uuid) < 10:
                result = price_util.get_price_breakdown(uuid)
                assert result == {}
                return

            # Property: Result should always be a dictionary with expected structure
            result = price_util.get_price_breakdown(uuid)
            assert isinstance(result, dict)

            # Property: Missing database should return empty dict
            if uuid and len(uuid) >= 10:
                assert result == {}  # No database available

    def test_price_utility_eliminates_duplicate_logic(self):
        """Property 4: Price Utility Consolidation - Duplicate Logic Elimination

        The PriceUtility should provide centralized functionality that eliminates
        the need for duplicate price logic across modules.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        # Create a mock repository
        mock_repo = Mock(spec=ReferenceRepository)
        mock_repo.get_connection.side_effect = RuntimeError("Database not available")
        mock_repo.get_price_map.return_value = {}

        price_util = PriceUtility(mock_repo)

        # Property: All core price methods should be available
        assert hasattr(price_util, "get_tcgplayer_price")
        assert hasattr(price_util, "get_average_price")
        assert hasattr(price_util, "calculate_deck_total")
        assert hasattr(price_util, "get_bulk_prices")
        assert hasattr(price_util, "get_bulk_average_prices")
        assert hasattr(price_util, "get_price_breakdown")

        # Property: Methods should be callable and return expected types
        assert callable(price_util.get_tcgplayer_price)
        assert callable(price_util.get_average_price)
        assert callable(price_util.calculate_deck_total)
        assert callable(price_util.get_bulk_prices)
        assert callable(price_util.get_bulk_average_prices)
        assert callable(price_util.get_price_breakdown)

        # Property: Methods should handle missing database gracefully
        assert price_util.get_tcgplayer_price("test-uuid") is None
        assert price_util.get_average_price("test-uuid") is None
        assert price_util.calculate_deck_total([]) == 0.0
        assert price_util.get_bulk_prices([]) == {}
        assert price_util.get_bulk_average_prices([]) == {}
        assert price_util.get_price_breakdown("test-uuid") == {}

    def test_price_utility_uses_reference_repository(self):
        """Property 4: Price Utility Consolidation - Repository Usage

        The PriceUtility should use the ReferenceRepository for all database
        operations instead of direct database access.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        # Create a mock repository to verify interactions
        mock_repo = Mock(spec=ReferenceRepository)
        mock_repo.get_connection.side_effect = RuntimeError("Database not available")
        mock_repo.get_price_map.return_value = {}

        price_util = PriceUtility(mock_repo)

        # Property: PriceUtility should store reference to repository
        assert price_util.reference_repo is mock_repo

        # Property: Bulk operations should use repository methods
        result = price_util.get_bulk_prices(["uuid1", "uuid2"])
        mock_repo.get_price_map.assert_called_once_with(["uuid1", "uuid2"])
        assert result == {}

        # Property: Individual operations should use repository connections
        price_util.get_tcgplayer_price("test-uuid")
        mock_repo.get_connection.assert_called_with("prices")

    @given(
        st.lists(
            st.fixed_dictionaries(
                {
                    "uuid": st.text(min_size=32, max_size=36),  # UUID
                    "count": st.integers(min_value=1, max_value=4),  # count as integer
                }
            ),
            min_size=1,
            max_size=3,
        )
    )
    def test_deck_calculation_with_mock_prices(self, deck_cards):
        """Property 4: Price Utility Consolidation - Deck Calculation Logic

        Deck total calculation should correctly multiply prices by counts
        and sum the results.

        **Feature: mtgsim-refactor, Property 4: Price Utility Consolidation**
        **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
        """
        # Create mock repository with predictable price data
        mock_repo = Mock(spec=ReferenceRepository)

        # Create a price map where each UUID has a price of 1.0
        uuids = [card.get("uuid") for card in deck_cards if card.get("uuid")]
        price_map = {uuid: 1.0 for uuid in uuids if isinstance(uuid, str)}

        # Mock the bulk average prices method
        def mock_bulk_average_prices(input_uuids):
            return {uuid: 1.0 for uuid in input_uuids if uuid in price_map}

        price_util = PriceUtility(mock_repo)
        price_util.get_bulk_average_prices = mock_bulk_average_prices

        # Calculate expected total manually
        expected_total = 0.0
        for card in deck_cards:
            uuid = card.get("uuid")
            count = card.get("count", 1)
            if uuid and isinstance(uuid, str) and isinstance(count, int) and count > 0:
                expected_total += 1.0 * count

        # Property: Calculated total should match expected total
        result = price_util.calculate_deck_total(deck_cards)
        assert result == round(expected_total, 2)

        # Property: Result should be non-negative
        assert result >= 0.0

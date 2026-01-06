"""Property-based tests for reference repository.

Feature: mtgsim-refactor, Property 2: Reference Database Unification
"""

import sqlite3
import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from mtgsim.config import MTGSimConfig
from mtgsim.reference.repository import ReferenceRepository


class MockConfig:
    """Mock configuration for testing."""

    def __init__(self, mtgjson_dir: Path):
        self._mtgjson_dir = mtgjson_dir

    @property
    def mtgjson_dir(self) -> Path:
        return self._mtgjson_dir


class TestReferenceDatabaseUnification:
    """Property-based tests for reference database unification."""

    @given(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=10))
    def test_reference_repository_provides_unified_access(self, db_names):
        """Property 2: Reference Database Unification

        For any reference database operation, the Reference_Repository should provide
        the access mechanism with consistent error handling, helper methods for common
        operations, and elimination of raw sqlite3 usage in data modules.

        **Feature: mtgsim-refactor, Property 2: Reference Database Unification**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock config pointing to temp directory
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)

            # Property: Repository should handle missing databases gracefully
            for db_name in ["sets", "decks", "prices", "printings"]:
                try:
                    repo.get_connection(db_name)
                    # If we get here, the database exists (shouldn't in temp dir)
                    raise AssertionError(f"Expected RuntimeError for missing {db_name} database")
                except RuntimeError as e:
                    # Property: Error messages should be informative
                    assert "database not available" in str(e).lower()
                    assert "mtgsim db sync" in str(e).lower()

            # Property: Status should reflect database availability
            status = repo.status()
            assert isinstance(status, dict)
            assert all(db in status for db in ["sets", "decks", "prices", "printings"])
            assert all(not available for available in status.values())

    @given(st.lists(st.text(min_size=32, max_size=36), min_size=0, max_size=5))
    def test_price_map_functionality(self, uuids):
        """Property 2: Reference Database Unification - Price Map

        The price map functionality should handle any list of UUIDs consistently.

        **Feature: mtgsim-refactor, Property 2: Reference Database Unification**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)

            # Property: Empty UUID list should return empty dict
            if not uuids:
                price_map = repo.get_price_map(uuids)
                assert price_map == {}

            # Property: Missing prices database should return empty dict
            price_map = repo.get_price_map(uuids)
            assert isinstance(price_map, dict)
            assert price_map == {}  # No database available

            # Property: bulk_prices should be equivalent to get_price_map
            bulk_prices = repo.get_bulk_prices(uuids)
            assert bulk_prices == price_map

    @given(
        st.one_of(
            st.none(),
            st.text(),
            st.just("[]"),
            st.just("{}"),
            st.just('["test"]'),
            st.just('{"key": "value"}'),
            st.just("invalid json"),
        )
    )
    def test_json_decoding_safety(self, json_value):
        """Property 2: Reference Database Unification - JSON Decoding

        JSON decoding should safely handle any input without raising exceptions.

        **Feature: mtgsim-refactor, Property 2: Reference Database Unification**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        mock_config = MTGSimConfig()
        repo = ReferenceRepository(mock_config)

        # Property: decode_json_field should never raise exceptions
        result = repo.decode_json_field(json_value)

        # Property: Result should always be a valid Python object
        assert result is not None

        # Property: None or empty input should return empty list
        if json_value is None or json_value == "":
            assert result == []

        # Property: Valid JSON should be decoded correctly
        if json_value == "[]":
            assert result == []
        elif json_value == "{}":
            assert result == {}
        elif json_value == '["test"]':
            assert result == ["test"]
        elif json_value == '{"key": "value"}':
            assert result == {"key": "value"}

        # Property: Invalid JSON should return empty list (safe fallback)
        if json_value == "invalid json":
            assert result == []

    @given(
        st.integers(min_value=1, max_value=5),
        st.integers(min_value=1, max_value=20),
    )
    def test_pagination_consistency(self, page, limit):
        """Property 2: Reference Database Unification - Pagination

        Pagination should work consistently across all database operations.

        **Feature: mtgsim-refactor, Property 2: Reference Database Unification**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a mock database with test data
            db_path = Path(temp_dir) / "test.sqlite"
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            # Insert test data
            for i in range(50):
                conn.execute("INSERT INTO test VALUES (?, ?)", (i, f"item_{i}"))
            conn.commit()
            conn.close()

            # Mock config to use our test database
            mock_config = MockConfig(Path(temp_dir))
            repo = ReferenceRepository(mock_config)
            # Manually add our test database to connections
            test_conn = sqlite3.connect(db_path)
            test_conn.row_factory = sqlite3.Row
            repo._connections["test"] = test_conn
            repo._initialized = True

            # Property: Pagination should return consistent results
            query = "SELECT * FROM test ORDER BY id"
            rows, total = repo.execute_paginated_query("test", query, [], page, limit)

            # Property: Total count should be consistent regardless of page/limit
            assert total == 50

            # Property: Number of returned rows should not exceed limit
            assert len(rows) <= limit

            # Property: For valid pages, should return expected number of rows
            expected_rows = min(limit, max(0, total - (page - 1) * limit))
            assert len(rows) == expected_rows

            # Property: Row data should be accessible as dict-like objects
            for row in rows:
                assert row["id"] is not None
                assert row["name"] is not None
                assert isinstance(row["id"], int)
                assert isinstance(row["name"], str)

            test_conn.close()

    def test_connection_lifecycle(self):
        """Property 2: Reference Database Unification - Connection Lifecycle

        Database connections should be managed consistently with proper lifecycle.

        **Feature: mtgsim-refactor, Property 2: Reference Database Unification**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        mock_config = MTGSimConfig()
        repo = ReferenceRepository(mock_config)

        # Property: Repository should start uninitialized
        assert not repo._initialized
        assert len(repo._connections) == 0

        # Property: Init should be idempotent
        repo.init()
        first_init_state = repo._initialized
        first_connections = dict(repo._connections)

        repo.init()  # Second call
        assert repo._initialized == first_init_state
        assert repo._connections == first_connections

        # Property: Close should clean up all connections
        repo.close()
        assert not repo._initialized
        assert len(repo._connections) == 0

    @given(st.text(min_size=1, max_size=50))
    def test_query_execution_safety(self, query_text):
        """Property 2: Reference Database Unification - Query Safety

        Query execution should handle various inputs safely.

        **Feature: mtgsim-refactor, Property 2: Reference Database Unification**
        **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**
        """
        mock_config = MTGSimConfig()
        repo = ReferenceRepository(mock_config)

        # Property: Queries on missing databases should raise RuntimeError
        try:
            repo.execute_query("nonexistent", query_text, [])
            raise AssertionError("Expected RuntimeError for missing database")
        except RuntimeError as e:
            assert "database not available" in str(e).lower()

        try:
            repo.execute_single_query("nonexistent", query_text, [])
            raise AssertionError("Expected RuntimeError for missing database")
        except RuntimeError as e:
            assert "database not available" in str(e).lower()

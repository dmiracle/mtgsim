"""Property-based tests for reference table sync integrity.

**Feature: domain-api-consolidation, Property 2: Reference Table Sync Integrity**
**Validates: Requirements 2.1, 2.2**
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from mtgsim.cli.domain_commands import copy_table_with_prefix
from mtgsim.config import MERGED_DB_PATH
from mtgsim.db.domain_session import init_domain_db


class TestReferenceTableSyncIntegrity:
    """Test reference table sync integrity properties."""

    @pytest.fixture
    def temp_source_db(self):
        """Create a temporary source database with test data."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            source_path = Path(f.name)

        # Create source database with test table
        conn = sqlite3.connect(source_path)
        cursor = conn.cursor()

        # Create a test table with sample data
        cursor.execute("""
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER,
                data TEXT
            )
        """)

        # Insert test data
        test_data = [
            (1, "test1", 100, "data1"),
            (2, "test2", 200, "data2"),
            (3, "test3", 300, "data3"),
        ]
        cursor.executemany("INSERT INTO test_table VALUES (?, ?, ?, ?)", test_data)
        conn.commit()
        conn.close()

        yield source_path, test_data

        # Cleanup
        source_path.unlink()

    @pytest.fixture
    def temp_target_db(self):
        """Create a temporary target database."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            target_path = Path(f.name)

        # Initialize empty database
        conn = sqlite3.connect(target_path)
        conn.close()

        yield target_path

        # Cleanup
        target_path.unlink()

    def test_sync_preserves_all_data(self, temp_source_db, temp_target_db):
        """Test that sync copies all data from source to target with prefix.

        **Feature: domain-api-consolidation, Property 2: Reference Table Sync Integrity**
        **Validates: Requirements 2.1, 2.2**
        """
        source_path, expected_data = temp_source_db
        target_path = temp_target_db

        # Perform sync
        rows_copied = copy_table_with_prefix(source_path, target_path, "test_table", "mtgjson_")

        # Verify row count
        assert rows_copied == len(expected_data)

        # Verify all data was copied correctly
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM mtgjson_test_table ORDER BY id")
        actual_data = cursor.fetchall()
        conn.close()

        assert actual_data == expected_data

    @given(
        table_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=("Ll", "Lu"))).filter(
            lambda x: x.isidentifier()
            and not x.startswith("_")
            and x.lower()
            not in {
                "select",
                "from",
                "where",
                "insert",
                "update",
                "delete",
                "create",
                "drop",
                "alter",
                "table",
                "index",
                "view",
                "database",
                "schema",
                "primary",
                "key",
                "foreign",
                "references",
                "constraint",
                "unique",
                "not",
                "null",
                "default",
                "check",
                "and",
                "or",
                "in",
                "like",
                "between",
                "is",
                "exists",
                "case",
                "when",
                "then",
                "else",
                "end",
                "if",
                "while",
                "for",
            }
        ),
        prefix=st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Ll", "Lu"))).map(
            lambda x: x + "_"
        ),
        num_rows=st.integers(min_value=0, max_value=100),
    )
    def test_sync_integrity_property(self, table_name, prefix, num_rows):
        """Property test: For any table sync operation, all source data appears in target with prefix.

        **Feature: domain-api-consolidation, Property 2: Reference Table Sync Integrity**
        **Validates: Requirements 2.1, 2.2**
        """
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as source_f:
            source_path = Path(source_f.name)
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as target_f:
            target_path = Path(target_f.name)

        try:
            # Create source database with random data
            source_conn = sqlite3.connect(source_path)
            source_cursor = source_conn.cursor()

            # Create table with simple schema
            source_cursor.execute(f"""
                CREATE TABLE {table_name} (
                    id INTEGER PRIMARY KEY,
                    value TEXT
                )
            """)

            # Insert random data
            test_data = [(i, f"value_{i}") for i in range(num_rows)]
            if test_data:
                source_cursor.executemany(f"INSERT INTO {table_name} VALUES (?, ?)", test_data)

            source_conn.commit()
            source_conn.close()

            # Create empty target database
            target_conn = sqlite3.connect(target_path)
            target_conn.close()

            # Perform sync
            rows_copied = copy_table_with_prefix(source_path, target_path, table_name, prefix)

            # Verify sync integrity
            assert rows_copied == num_rows

            # Verify target table exists with correct name
            target_conn = sqlite3.connect(target_path)
            target_cursor = target_conn.cursor()

            target_table_name = f"{prefix}{table_name}"

            # Check table exists
            target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (target_table_name,))
            assert target_cursor.fetchone() is not None

            # Check data integrity
            target_cursor.execute(f"SELECT COUNT(*) FROM {target_table_name}")
            actual_count = target_cursor.fetchone()[0]
            assert actual_count == num_rows

            if num_rows > 0:
                # Verify data matches
                target_cursor.execute(f"SELECT * FROM {target_table_name} ORDER BY id")
                actual_data = target_cursor.fetchall()
                assert actual_data == test_data

            target_conn.close()

        finally:
            # Cleanup
            source_path.unlink(missing_ok=True)
            target_path.unlink(missing_ok=True)

    def test_real_database_sync_integrity(self):
        """Test sync integrity with real MTGJSON database.

        **Feature: domain-api-consolidation, Property 2: Reference Table Sync Integrity**
        **Validates: Requirements 2.1, 2.2**
        """
        # Skip if reference database doesn't exist
        if not MERGED_DB_PATH.exists():
            pytest.skip("Reference database not found")

        # Use a temporary domain database for testing
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            temp_domain_path = Path(f.name)

        try:
            # Initialize temporary domain database
            init_domain_db(temp_domain_path)

            # Test syncing a small table (sets is smaller than cards)
            rows_copied = copy_table_with_prefix(MERGED_DB_PATH, temp_domain_path, "sets", "mtgjson_")

            # Verify sync worked
            assert rows_copied > 0

            # Verify data integrity by comparing counts
            source_conn = sqlite3.connect(MERGED_DB_PATH)
            source_cursor = source_conn.cursor()
            source_cursor.execute("SELECT COUNT(*) FROM sets")
            source_count = source_cursor.fetchone()[0]
            source_conn.close()

            target_conn = sqlite3.connect(temp_domain_path)
            target_cursor = target_conn.cursor()
            target_cursor.execute("SELECT COUNT(*) FROM mtgjson_sets")
            target_count = target_cursor.fetchone()[0]
            target_conn.close()

            assert source_count == target_count == rows_copied

        finally:
            # Cleanup
            temp_domain_path.unlink(missing_ok=True)

    def test_sync_idempotence(self, temp_source_db, temp_target_db):
        """Test that syncing the same table multiple times produces the same result.

        **Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
        **Validates: Requirements 2.3**
        """
        source_path, expected_data = temp_source_db
        target_path = temp_target_db

        # Perform sync twice
        rows_copied_1 = copy_table_with_prefix(source_path, target_path, "test_table", "mtgjson_")
        rows_copied_2 = copy_table_with_prefix(source_path, target_path, "test_table", "mtgjson_")

        # Both syncs should copy the same number of rows
        assert rows_copied_1 == rows_copied_2 == len(expected_data)

        # Verify final data is correct
        conn = sqlite3.connect(target_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM mtgjson_test_table ORDER BY id")
        actual_data = cursor.fetchall()
        conn.close()

        assert actual_data == expected_data

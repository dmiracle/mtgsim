"""Tests for sync validation and integrity checking functionality.

**Feature: domain-api-consolidation**
**Validates: Requirements 2.4, 5.3**
"""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from mtgsim.cli.domain_commands import validate_source_database_schema, verify_sync_integrity


class TestSyncValidation:
    """Test sync validation and integrity checking."""

    @pytest.fixture
    def temp_database(self):
        """Create a temporary database with test tables."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            db_path = Path(f.name)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create test tables
        cursor.execute("CREATE TABLE table1 (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("CREATE TABLE table2 (id INTEGER PRIMARY KEY, value INTEGER)")
        cursor.execute("INSERT INTO table1 VALUES (1, 'test1'), (2, 'test2')")
        cursor.execute("INSERT INTO table2 VALUES (1, 100), (2, 200)")

        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        db_path.unlink()

    def test_validate_source_database_schema_success(self, temp_database):
        """Test successful schema validation when all required tables exist."""
        required_tables = ["table1", "table2"]

        result = validate_source_database_schema(temp_database, required_tables)

        assert result is True

    def test_validate_source_database_schema_missing_tables(self, temp_database):
        """Test schema validation failure when required tables are missing."""
        required_tables = ["table1", "table2", "nonexistent_table"]

        result = validate_source_database_schema(temp_database, required_tables)

        assert result is False

    def test_validate_source_database_schema_nonexistent_db(self):
        """Test schema validation failure when database doesn't exist."""
        nonexistent_path = Path("/nonexistent/database.sqlite")
        required_tables = ["table1"]

        result = validate_source_database_schema(nonexistent_path, required_tables)

        assert result is False

    def test_verify_sync_integrity_success(self, temp_database):
        """Test successful integrity verification when row counts match."""
        # Create target database with matching data
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            target_path = Path(f.name)

        try:
            target_conn = sqlite3.connect(target_path)
            target_cursor = target_conn.cursor()

            # Create target tables with same data
            target_cursor.execute("CREATE TABLE prefix_table1 (id INTEGER PRIMARY KEY, name TEXT)")
            target_cursor.execute("CREATE TABLE prefix_table2 (id INTEGER PRIMARY KEY, value INTEGER)")
            target_cursor.execute("INSERT INTO prefix_table1 VALUES (1, 'test1'), (2, 'test2')")
            target_cursor.execute("INSERT INTO prefix_table2 VALUES (1, 100), (2, 200)")

            target_conn.commit()
            target_conn.close()

            # Test integrity verification
            table_mappings = [("table1", "prefix_table1"), ("table2", "prefix_table2")]

            result = verify_sync_integrity(temp_database, target_path, table_mappings)

            assert result is True

        finally:
            target_path.unlink()

    def test_verify_sync_integrity_count_mismatch(self, temp_database):
        """Test integrity verification failure when row counts don't match."""
        # Create target database with different data counts
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            target_path = Path(f.name)

        try:
            target_conn = sqlite3.connect(target_path)
            target_cursor = target_conn.cursor()

            # Create target tables with different row counts
            target_cursor.execute("CREATE TABLE prefix_table1 (id INTEGER PRIMARY KEY, name TEXT)")
            target_cursor.execute("CREATE TABLE prefix_table2 (id INTEGER PRIMARY KEY, value INTEGER)")
            target_cursor.execute("INSERT INTO prefix_table1 VALUES (1, 'test1')")  # Only 1 row instead of 2
            target_cursor.execute("INSERT INTO prefix_table2 VALUES (1, 100), (2, 200)")

            target_conn.commit()
            target_conn.close()

            # Test integrity verification
            table_mappings = [("table1", "prefix_table1"), ("table2", "prefix_table2")]

            result = verify_sync_integrity(temp_database, target_path, table_mappings)

            assert result is False

        finally:
            target_path.unlink()

    def test_verify_sync_integrity_missing_target_table(self, temp_database):
        """Test integrity verification failure when target table doesn't exist."""
        # Create target database without one of the expected tables
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
            target_path = Path(f.name)

        try:
            target_conn = sqlite3.connect(target_path)
            target_cursor = target_conn.cursor()

            # Create only one target table
            target_cursor.execute("CREATE TABLE prefix_table1 (id INTEGER PRIMARY KEY, name TEXT)")
            target_cursor.execute("INSERT INTO prefix_table1 VALUES (1, 'test1'), (2, 'test2')")

            target_conn.commit()
            target_conn.close()

            # Test integrity verification with missing table
            table_mappings = [
                ("table1", "prefix_table1"),
                ("table2", "prefix_table2"),  # This table doesn't exist in target
            ]

            result = verify_sync_integrity(temp_database, target_path, table_mappings)

            assert result is False

        finally:
            target_path.unlink()

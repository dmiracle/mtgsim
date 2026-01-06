"""Property-based tests for sync operation idempotence.

**Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
**Validates: Requirements 2.3**
"""

import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from mtgsim.cli.domain_commands import copy_table_with_prefix


class TestSyncOperationIdempotence:
    """Test sync operation idempotence properties."""

    @contextmanager
    def temp_databases(self):
        """Create temporary source and target databases as context manager."""
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as source_f:
            source_path = Path(source_f.name)
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as target_f:
            target_path = Path(target_f.name)

        try:
            yield source_path, target_path
        finally:
            # Cleanup
            source_path.unlink(missing_ok=True)
            target_path.unlink(missing_ok=True)

    def create_test_table(self, db_path: Path, table_name: str, data: list[tuple]):
        """Create a test table with the given data."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create table with flexible schema based on data
        if data:
            # Determine column count from first row (excluding the id which we'll auto-generate)
            col_count = len(data[0]) - 1  # Subtract 1 because first element is the id
            columns = ", ".join([f"col{i} TEXT" for i in range(col_count)])
            cursor.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, {columns})")

            # Insert data (data already includes id as first element)
            placeholders = ", ".join(["?" for _ in range(len(data[0]))])
            cursor.executemany(f"INSERT INTO {table_name} VALUES ({placeholders})", data)
        else:
            # Empty table
            cursor.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, value TEXT)")

        conn.commit()
        conn.close()

    def get_table_state(self, db_path: Path, table_name: str) -> tuple[int, list[tuple]]:
        """Get the current state of a table (row count and all data)."""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]

            cursor.execute(f"SELECT * FROM {table_name} ORDER BY id")
            data = cursor.fetchall()

            return count, data
        except sqlite3.OperationalError:
            # Table doesn't exist
            return 0, []
        finally:
            conn.close()

    @given(
        table_name=st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=("Ll", "Lu"))).filter(
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
        prefix=st.text(min_size=1, max_size=8, alphabet=st.characters(whitelist_categories=("Ll", "Lu"))).map(
            lambda x: x + "_"
        ),
        num_rows=st.integers(min_value=0, max_value=50),
        num_sync_operations=st.integers(min_value=2, max_value=5),
    )
    @settings(max_examples=20)  # Reduce examples for faster testing
    def test_sync_operation_idempotence_property(self, table_name, prefix, num_rows, num_sync_operations):
        """Property test: For any sync operation, running it multiple times produces the same result.

        **Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
        **Validates: Requirements 2.3**
        """
        with self.temp_databases() as (source_path, target_path):
            # Generate test data
            test_data = [(i, f"value_{i}", f"data_{i}") for i in range(1, num_rows + 1)]

            # Create source database with test data
            self.create_test_table(source_path, table_name, test_data)

            # Create empty target database
            conn = sqlite3.connect(target_path)
            conn.close()

            target_table_name = f"{prefix}{table_name}"

            # Perform multiple sync operations
            sync_results = []
            table_states = []

            for _i in range(num_sync_operations):
                # Perform sync
                rows_copied = copy_table_with_prefix(source_path, target_path, table_name, prefix)
                sync_results.append(rows_copied)

                # Capture table state after sync
                count, data = self.get_table_state(target_path, target_table_name)
                table_states.append((count, data))

            # Verify idempotence: all sync operations should return the same result
            assert all(result == sync_results[0] for result in sync_results), (
                f"Sync operations returned different row counts: {sync_results}"
            )

            # Verify idempotence: all table states should be identical
            for i, (count, data) in enumerate(table_states):
                assert count == table_states[0][0], (
                    f"Table row count differs after sync {i + 1}: expected {table_states[0][0]}, got {count}"
                )
                assert data == table_states[0][1], f"Table data differs after sync {i + 1}"

            # Verify final state matches expected data
            final_count, final_data = table_states[0]
            assert final_count == num_rows, f"Final row count {final_count} doesn't match expected {num_rows}"

            if num_rows > 0:
                # Remove the auto-generated id column for comparison
                final_data_without_id = [row[1:] for row in final_data]
                expected_data_without_id = [row[1:] for row in test_data]
                assert final_data_without_id == expected_data_without_id, "Final table data doesn't match expected data"

    @given(
        data_modifications=st.lists(
            st.tuples(
                st.text(min_size=1, max_size=10),  # value
                st.text(min_size=1, max_size=10),  # data
            ),
            min_size=0,
            max_size=20,
        ),
        num_sync_operations=st.integers(min_value=2, max_value=4),
    )
    @settings(max_examples=15)  # Reduce examples for faster testing
    def test_sync_idempotence_with_data_variations(self, data_modifications, num_sync_operations):
        """Property test: Sync idempotence holds regardless of data content variations.

        **Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
        **Validates: Requirements 2.3**
        """
        with self.temp_databases() as (source_path, target_path):
            table_name = "test_table"
            prefix = "sync_"

            # Create test data with variations
            test_data = [(i, value, data) for i, (value, data) in enumerate(data_modifications, 1)]

            # Create source database
            self.create_test_table(source_path, table_name, test_data)

            # Create empty target database
            conn = sqlite3.connect(target_path)
            conn.close()

            target_table_name = f"{prefix}{table_name}"

            # Perform multiple sync operations and track results
            sync_results = []

            for _ in range(num_sync_operations):
                rows_copied = copy_table_with_prefix(source_path, target_path, table_name, prefix)
                sync_results.append(rows_copied)

            # Verify all sync operations returned the same result
            assert all(result == sync_results[0] for result in sync_results), (
                f"Sync operations with data variations returned different results: {sync_results}"
            )

            # Verify final table state
            final_count, final_data = self.get_table_state(target_path, target_table_name)
            assert final_count == len(test_data), (
                f"Final row count {final_count} doesn't match expected {len(test_data)}"
            )

    def test_sync_idempotence_with_existing_target_table(self):
        """Test that sync idempotence works when target table already exists.

        **Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
        **Validates: Requirements 2.3**
        """
        with self.temp_databases() as (source_path, target_path):
            table_name = "existing_table"
            prefix = "test_"

            # Create source data
            source_data = [(1, "source1", "data1"), (2, "source2", "data2")]
            self.create_test_table(source_path, table_name, source_data)

            # Create target database with existing table (different data)
            target_table_name = f"{prefix}{table_name}"
            conn = sqlite3.connect(target_path)
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE {target_table_name} (id INTEGER PRIMARY KEY, col0 TEXT, col1 TEXT)")
            cursor.execute(f"INSERT INTO {target_table_name} VALUES (1, 'old1', 'olddata1')")
            conn.commit()
            conn.close()

            # Perform multiple sync operations
            results = []
            states = []

            for _ in range(3):
                rows_copied = copy_table_with_prefix(source_path, target_path, table_name, prefix)
                results.append(rows_copied)

                count, data = self.get_table_state(target_path, target_table_name)
                states.append((count, data))

            # Verify idempotence
            assert all(result == results[0] for result in results), (
                f"Sync results differ when target table exists: {results}"
            )

            assert all(state == states[0] for state in states), (
                "Table states differ after repeated syncs with existing target table"
            )

            # Verify final state matches source (old data should be replaced)
            final_count, final_data = states[0]
            assert final_count == len(source_data)

            # Compare data (excluding auto-generated IDs)
            final_data_without_id = [row[1:] for row in final_data]
            source_data_without_id = [row[1:] for row in source_data]
            assert final_data_without_id == source_data_without_id

    def test_sync_idempotence_empty_source_table(self):
        """Test sync idempotence with empty source table.

        **Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
        **Validates: Requirements 2.3**
        """
        with self.temp_databases() as (source_path, target_path):
            table_name = "empty_table"
            prefix = "empty_"

            # Create empty source table
            self.create_test_table(source_path, table_name, [])

            # Create empty target database
            conn = sqlite3.connect(target_path)
            conn.close()

            # Perform multiple sync operations
            results = []
            states = []

            for _ in range(3):
                rows_copied = copy_table_with_prefix(source_path, target_path, table_name, prefix)
                results.append(rows_copied)

                count, data = self.get_table_state(target_path, f"{prefix}{table_name}")
                states.append((count, data))

            # Verify idempotence with empty table
            assert all(result == 0 for result in results), f"Empty table sync should always return 0 rows: {results}"

            assert all(count == 0 for count, _ in states), "Empty table should remain empty after all syncs"

            assert all(data == [] for _, data in states), "Empty table should have no data after all syncs"

    @given(
        schema_variations=st.lists(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Ll", "Lu"))),
            min_size=1,
            max_size=5,
        ).map(lambda cols: list(set(cols)))  # Remove duplicates
    )
    @settings(max_examples=10)  # Reduce examples for faster testing
    def test_sync_idempotence_different_schemas(self, schema_variations):
        """Property test: Sync idempotence works with different table schemas.

        **Feature: domain-api-consolidation, Property 4: Sync Operation Idempotence**
        **Validates: Requirements 2.3**
        """
        assume(len(schema_variations) > 0)  # Ensure we have at least one column

        with self.temp_databases() as (source_path, target_path):
            table_name = "schema_test"
            prefix = "schema_"

            # Create source table with dynamic schema
            conn = sqlite3.connect(source_path)
            cursor = conn.cursor()

            # Create columns based on schema variations
            columns = ", ".join([f"{col} TEXT" for col in schema_variations])
            cursor.execute(f"CREATE TABLE {table_name} (id INTEGER PRIMARY KEY, {columns})")

            # Insert test data
            test_values = [f"val_{i}" for i in range(len(schema_variations))]
            placeholders = ", ".join(["?" for _ in range(len(schema_variations) + 1)])  # +1 for id
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", [1] + test_values)

            conn.commit()
            conn.close()

            # Create empty target database
            conn = sqlite3.connect(target_path)
            conn.close()

            # Perform multiple sync operations
            results = []
            states = []

            for _ in range(3):
                rows_copied = copy_table_with_prefix(source_path, target_path, table_name, prefix)
                results.append(rows_copied)

                count, data = self.get_table_state(target_path, f"{prefix}{table_name}")
                states.append((count, data))

            # Verify idempotence across different schemas
            assert all(result == results[0] for result in results), f"Schema variation sync results differ: {results}"

            assert all(state == states[0] for state in states), "Table states differ with schema variations"

            # Verify final state
            final_count, final_data = states[0]
            assert final_count == 1, "Should have exactly one row"
            assert len(final_data) == 1, "Should have exactly one data row"
            assert len(final_data[0]) == len(schema_variations) + 1, "Row should have correct number of columns"

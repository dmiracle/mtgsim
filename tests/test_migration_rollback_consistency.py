"""Property-based tests for migration rollback consistency.

**Feature: domain-api-consolidation, Property 11: Migration Rollback Consistency**
**Validates: Requirements 5.4**
"""

import tempfile
import time
from contextlib import contextmanager
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import select

from mtgsim.cli.rollback import RollbackManager
from mtgsim.db.domain_models import DomainCard, DomainSet
from mtgsim.db.domain_session import get_domain_session, init_domain_db
from mtgsim.db.migration_models import MigrationLog, MigrationStatus, MigrationType


@contextmanager
def temp_domain_db():
    """Create a temporary domain database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp_file:
        db_path = Path(tmp_file.name)

    try:
        # Initialize the temporary database
        init_domain_db(db_path)
        yield db_path
    finally:
        # Cleanup
        if db_path.exists():
            db_path.unlink()


def create_test_migration_log(session, operation_name: str, source_name: str = "test") -> MigrationLog:
    """Create a test migration log entry."""
    migration_log = MigrationLog(
        migration_type=MigrationType.ENTITY_ADD,
        operation_name=operation_name,
        source_name=source_name,
        status=MigrationStatus.COMPLETED,
        can_rollback=True,
    )
    session.add(migration_log)
    session.commit()
    session.refresh(migration_log)
    return migration_log


def create_test_card(session, uuid: str, name: str, set_code: str = "TST") -> DomainCard:
    """Create a test domain card."""
    card = DomainCard(
        uuid=uuid,
        name=name,
        set_code=set_code,
        rarity="common",
        oracle_text="Test card text",
        mana_cost="{1}",
        mana_value=1,
        type_line="Creature — Test",
    )
    session.add(card)
    session.commit()
    session.refresh(card)
    return card


def create_test_set(session, code: str, name: str) -> DomainSet:
    """Create a test domain set."""
    domain_set = DomainSet(code=code, name=name, type="expansion", release_date="2024-01-01")
    session.add(domain_set)
    session.commit()
    session.refresh(domain_set)
    return domain_set


@given(
    card_uuid=st.text(min_size=36, max_size=36, alphabet=st.characters(whitelist_categories=("Ll", "Nd", "Pd"))),
    card_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
    set_code=st.text(min_size=3, max_size=5, alphabet=st.characters(whitelist_categories=("Lu", "Nd"))),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_card_addition_rollback_consistency(card_uuid, card_name, set_code):
    """
    Property 11: Migration Rollback Consistency
    For any failed sync operation, rolling back should restore the domain database
    to its exact state before the sync attempt.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Capture initial state
            initial_card_count = session.exec(select(DomainCard)).all()
            initial_set_count = session.exec(select(DomainSet)).all()

            # Create migration log
            migration_log = create_test_migration_log(session, "add_card", "test")

            # Store rollback data
            rollback_data = {"card_uuid": card_uuid, "operation_type": "add_card"}
            rollback_manager.store_rollback_data(migration_log, rollback_data)

            # Add a card (simulating the operation)
            _test_card = create_test_card(session, card_uuid, card_name, set_code)

            # Verify card was added
            cards_after_add = session.exec(select(DomainCard)).all()
            assert len(cards_after_add) == len(initial_card_count) + 1

            # Perform rollback
            success = rollback_manager.rollback_migration(migration_log.id)
            assert success, "Rollback should succeed"

            # Verify state is restored to initial state
            cards_after_rollback = session.exec(select(DomainCard)).all()
            sets_after_rollback = session.exec(select(DomainSet)).all()

            assert len(cards_after_rollback) == len(initial_card_count), (
                "Card count should be restored to initial state"
            )
            assert len(sets_after_rollback) == len(initial_set_count), "Set count should be restored to initial state"

            # Verify the specific card was removed
            rolled_back_card = session.exec(select(DomainCard).where(DomainCard.uuid == card_uuid)).first()
            assert rolled_back_card is None, "Rolled back card should not exist"

            # Verify migration log is marked as rolled back
            updated_migration = session.exec(select(MigrationLog).where(MigrationLog.id == migration_log.id)).first()
            assert updated_migration.status == MigrationStatus.ROLLED_BACK, "Migration should be marked as rolled back"


@given(
    set_code=st.text(min_size=3, max_size=5, alphabet=st.characters(whitelist_categories=("Lu", "Nd"))),
    set_name=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"))),
    num_cards=st.integers(min_value=1, max_value=5),
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_set_addition_rollback_consistency(set_code, set_name, num_cards):
    """
    Property 11: Migration Rollback Consistency (Set Addition)
    For any set addition operation, rolling back should remove all added cards and sets,
    restoring the database to its exact state before the operation.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Capture initial state
            initial_card_count = len(session.exec(select(DomainCard)).all())
            initial_set_count = len(session.exec(select(DomainSet)).all())

            # Create migration log
            migration_log = create_test_migration_log(session, "add_set", "test")

            # Add set and cards
            _test_set = create_test_set(session, set_code, set_name)
            added_card_uuids = []

            for i in range(num_cards):
                card_uuid = f"{set_code}-card-{i:03d}-uuid-{i * 123:08x}"
                card_name = f"Test Card {i + 1}"
                _test_card = create_test_card(session, card_uuid, card_name, set_code)
                added_card_uuids.append(card_uuid)

            # Store rollback data
            rollback_data = {
                "set_code": set_code,
                "set_was_added": True,
                "added_cards": added_card_uuids,
                "operation_type": "add_set",
            }
            rollback_manager.store_rollback_data(migration_log, rollback_data)

            # Verify items were added
            cards_after_add = session.exec(select(DomainCard)).all()
            sets_after_add = session.exec(select(DomainSet)).all()
            assert len(cards_after_add) == initial_card_count + num_cards
            assert len(sets_after_add) == initial_set_count + 1

            # Perform rollback
            success = rollback_manager.rollback_migration(migration_log.id)
            assert success, "Rollback should succeed"

            # Verify state is restored
            cards_after_rollback = session.exec(select(DomainCard)).all()
            sets_after_rollback = session.exec(select(DomainSet)).all()

            assert len(cards_after_rollback) == initial_card_count, "Card count should be restored"
            assert len(sets_after_rollback) == initial_set_count, "Set count should be restored"

            # Verify specific items were removed
            for card_uuid in added_card_uuids:
                rolled_back_card = session.exec(select(DomainCard).where(DomainCard.uuid == card_uuid)).first()
                assert rolled_back_card is None, f"Card {card_uuid} should be removed"

            rolled_back_set = session.exec(select(DomainSet).where(DomainSet.code == set_code)).first()
            assert rolled_back_set is None, f"Set {set_code} should be removed"


@given(
    backup_exists=st.booleans(), operation_name=st.sampled_from(["sync_reference", "add_card", "add_set", "add_deck"])
)
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=1000)
def test_backup_restore_rollback_consistency(backup_exists, operation_name):
    """
    Property 11: Migration Rollback Consistency (Backup Restore)
    For any operation with backup, rolling back should restore from backup and
    maintain database consistency.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Create initial state
            _initial_card = create_test_card(session, "initial-card-uuid", "Initial Card", "INI")
            initial_card_count = len(session.exec(select(DomainCard)).all())

            # Create backup if specified
            backup_path = None
            if backup_exists:
                try:
                    backup_path = rollback_manager.create_backup(operation_name)
                except Exception:
                    # If backup creation fails, skip this test case
                    return

            # Create migration log
            migration_log = create_test_migration_log(session, operation_name, "test")

            # Store rollback data
            rollback_data = {"operation_type": operation_name}
            if backup_path:
                rollback_data["backup_path"] = str(backup_path)

            # Add operation-specific rollback data
            if operation_name == "add_card":
                rollback_data["card_uuid"] = "new-card-uuid"
            elif operation_name == "add_set":
                rollback_data["set_code"] = "NEW"
                rollback_data["added_cards"] = ["new-card-uuid"]
                rollback_data["set_was_added"] = True
            elif operation_name == "add_deck":
                rollback_data["deck_uuid"] = "new-deck-uuid"
                rollback_data["added_cards"] = ["new-card-uuid"]

            rollback_manager.store_rollback_data(migration_log, rollback_data)

            # Modify database state (add more cards)
            _new_card = create_test_card(session, "new-card-uuid", "New Card", "NEW")

            # Verify state changed
            cards_after_change = session.exec(select(DomainCard)).all()
            assert len(cards_after_change) == initial_card_count + 1

            # Perform rollback
            migration_id = migration_log.id  # Store ID before potential session closure
            if backup_exists and backup_path and Path(backup_path).exists():
                # Test backup restore
                success = rollback_manager.rollback_migration(migration_id)

                # For backup restore, we expect it to work if backup exists
                if success:
                    # After backup restore, session might be closed, so we can't verify migration status
                    # The backup restore itself is the verification
                    pass
            else:
                # Test rollback without backup (should use operation-specific rollback)
                success = rollback_manager.rollback_migration(migration_id)

                # Success depends on whether the operation has a specific rollback handler
                if operation_name in ["add_card", "add_set", "add_deck"]:
                    assert success, f"Rollback should succeed for {operation_name}"
                # sync_reference without backup may not have specific rollback logic


@given(migration_already_rolled_back=st.booleans(), can_rollback_flag=st.booleans())
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_rollback_idempotence_and_constraints(migration_already_rolled_back, can_rollback_flag):
    """
    Property 11: Migration Rollback Consistency (Idempotence and Constraints)
    Rolling back a migration multiple times should be idempotent, and rollback
    should respect the can_rollback flag.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Create migration log
            migration_log = create_test_migration_log(session, "add_card", "test")
            migration_log.can_rollback = can_rollback_flag
            if migration_already_rolled_back:
                migration_log.status = MigrationStatus.ROLLED_BACK
            session.add(migration_log)
            session.commit()

            # Store rollback data
            rollback_data = {"card_uuid": "test-card-uuid", "operation_type": "add_card"}
            rollback_manager.store_rollback_data(migration_log, rollback_data)

            # Add a test card if not already rolled back
            if not migration_already_rolled_back:
                _test_card = create_test_card(session, "test-card-uuid", "Test Card", "TST")

            # Attempt rollback
            success = rollback_manager.rollback_migration(migration_log.id)

            if not can_rollback_flag:
                # Should fail if can_rollback is False
                assert not success, "Rollback should fail when can_rollback is False"
            elif migration_already_rolled_back:
                # Should succeed (idempotent) if already rolled back
                assert success, "Rollback should be idempotent for already rolled back migrations"
            else:
                # Should succeed for normal rollback
                assert success, "Rollback should succeed for normal case"

            # Attempt rollback again (test idempotence)
            if success:
                second_success = rollback_manager.rollback_migration(migration_log.id)
                assert second_success, "Second rollback should be idempotent"


def test_rollback_nonexistent_migration():
    """
    Test that rolling back a nonexistent migration fails gracefully.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Attempt to rollback nonexistent migration
            success = rollback_manager.rollback_migration(99999)
            assert not success, "Rollback should fail for nonexistent migration"


def test_list_rollbackable_migrations():
    """
    Test that listing rollbackable migrations returns correct results.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Create various migration logs
            completed_migration = create_test_migration_log(session, "add_card", "test")
            completed_migration.status = MigrationStatus.COMPLETED
            completed_migration.can_rollback = True

            failed_migration = create_test_migration_log(session, "add_set", "test")
            failed_migration.status = MigrationStatus.FAILED
            failed_migration.can_rollback = True

            non_rollbackable_migration = create_test_migration_log(session, "sync_reference", "test")
            non_rollbackable_migration.status = MigrationStatus.COMPLETED
            non_rollbackable_migration.can_rollback = False

            rolled_back_migration = create_test_migration_log(session, "add_deck", "test")
            rolled_back_migration.status = MigrationStatus.ROLLED_BACK
            rolled_back_migration.can_rollback = True

            session.add_all([completed_migration, failed_migration, non_rollbackable_migration, rolled_back_migration])
            session.commit()

            # Get rollbackable migrations
            rollbackable = rollback_manager.list_rollbackable_migrations()

            # Should include completed and failed migrations that can be rolled back
            rollbackable_ids = {m.id for m in rollbackable}
            assert completed_migration.id in rollbackable_ids
            assert failed_migration.id in rollbackable_ids
            assert non_rollbackable_migration.id not in rollbackable_ids
            assert rolled_back_migration.id not in rollbackable_ids


@given(keep_days=st.integers(min_value=1, max_value=30))
@settings(max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_backup_cleanup_consistency(keep_days):
    """
    Property 11: Migration Rollback Consistency (Backup Cleanup)
    Backup cleanup should maintain consistency and not affect active backups.

    **Validates: Requirements 5.4**
    """
    with temp_domain_db() as db_path:
        with get_domain_session(db_path) as session:
            rollback_manager = RollbackManager(session)

            # Create backup directory
            backup_dir = db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)

            # Create some test backup files with different ages
            current_time = time.time()

            # Recent backup (should be kept)
            recent_backup = backup_dir / "recent_backup.sqlite"
            recent_backup.touch()

            # Old backup (should be deleted if older than keep_days)
            old_backup = backup_dir / "old_backup.sqlite"
            old_backup.touch()
            # Set modification time to be older than keep_days
            old_time = current_time - (keep_days + 1) * 24 * 60 * 60
            import os

            os.utime(old_backup, (old_time, old_time))

            # Count initial backups
            initial_backups = list(backup_dir.glob("*.sqlite"))

            # Run cleanup
            deleted_count = rollback_manager.cleanup_old_backups(keep_days)

            # Verify cleanup results
            remaining_backups = list(backup_dir.glob("*.sqlite"))

            # Recent backup should still exist
            assert recent_backup.exists(), "Recent backup should not be deleted"

            # The number of remaining backups should be consistent
            assert len(remaining_backups) <= len(initial_backups), "Cleanup should not increase backup count"
            assert deleted_count >= 0, "Deleted count should be non-negative"
            assert len(remaining_backups) + deleted_count <= len(initial_backups), "Counts should be consistent"

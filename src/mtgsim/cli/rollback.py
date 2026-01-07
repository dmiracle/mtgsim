"""Rollback functionality for domain database operations."""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlmodel import select, text

from mtgsim.config import DOMAIN_DB_PATH
from mtgsim.db.domain_session import get_domain_session
from mtgsim.db.migration_models import MigrationLog, MigrationStatus

console = Console()


class RollbackManager:
    """Manages rollback operations for domain database migrations."""

    def __init__(self, session):
        self.session = session

    def create_backup(self, operation_name: str) -> Path:
        """Create a backup of the domain database before an operation.
        
        Args:
            operation_name: Name of the operation for backup naming
            
        Returns:
            Path to the created backup file
        """
        if not DOMAIN_DB_PATH.exists():
            raise FileNotFoundError(f"Domain database not found at {DOMAIN_DB_PATH}")

        # Create backup directory
        backup_dir = DOMAIN_DB_PATH.parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        # Generate backup filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{operation_name}_{timestamp}.sqlite"
        backup_path = backup_dir / backup_filename

        # Copy database file
        shutil.copy2(DOMAIN_DB_PATH, backup_path)
        
        console.print(f"✅ Backup created: {backup_path}", style="green")
        return backup_path

    def store_rollback_data(self, migration_log: MigrationLog, rollback_data: Dict[str, Any]) -> None:
        """Store rollback data in the migration log.
        
        Args:
            migration_log: Migration log entry to update
            rollback_data: Data needed for rollback operation
        """
        migration_log.rollback_data = rollback_data
        migration_log.can_rollback = True
        self.session.add(migration_log)
        self.session.commit()

    def capture_table_state(self, table_name: str) -> Dict[str, Any]:
        """Capture the current state of a table for rollback purposes.
        
        Args:
            table_name: Name of the table to capture
            
        Returns:
            Dictionary containing table state information
        """
        try:
            # Get row count before operation
            count_result = self.session.exec(text(f"SELECT COUNT(*) FROM {table_name}")).first()
            row_count = count_result if count_result is not None else 0

            # Get table schema
            schema_result = self.session.exec(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name=:table_name"),
                {"table_name": table_name}
            ).first()

            return {
                "table_name": table_name,
                "row_count_before": row_count,
                "schema": schema_result,
                "exists": schema_result is not None
            }
        except Exception as e:
            console.print(f"⚠️  Warning: Could not capture state for table {table_name}: {e}", style="yellow")
            return {
                "table_name": table_name,
                "row_count_before": 0,
                "schema": None,
                "exists": False,
                "error": str(e)
            }

    def rollback_migration(self, migration_id: int) -> bool:
        """Rollback a specific migration operation.
        
        Args:
            migration_id: ID of the migration to rollback
            
        Returns:
            True if rollback was successful, False otherwise
        """
        # Get migration log entry
        migration_log = self.session.exec(
            select(MigrationLog).where(MigrationLog.id == migration_id)
        ).first()

        if not migration_log:
            console.print(f"❌ Migration {migration_id} not found", style="red")
            return False

        if not migration_log.can_rollback:
            console.print(f"❌ Migration {migration_id} cannot be rolled back", style="red")
            return False

        if migration_log.status == MigrationStatus.ROLLED_BACK:
            console.print(f"⚠️  Migration {migration_id} is already rolled back", style="yellow")
            return True

        console.print(f"🔄 Rolling back migration: {migration_log.operation_name}")

        try:
            rollback_data = migration_log.rollback_data or {}
            
            # Restore from backup if available
            if "backup_path" in rollback_data:
                return self._restore_from_backup(migration_log, rollback_data["backup_path"])
            
            # Perform operation-specific rollback
            if migration_log.operation_name == "sync_reference":
                return self._rollback_sync_reference(migration_log, rollback_data)
            elif migration_log.operation_name in ["add_card", "collect_card"]:
                return self._rollback_add_card(migration_log, rollback_data)
            elif migration_log.operation_name == "add_set":
                return self._rollback_add_set(migration_log, rollback_data)
            elif migration_log.operation_name == "add_deck":
                return self._rollback_add_deck(migration_log, rollback_data)
            else:
                console.print(f"❌ No rollback handler for operation: {migration_log.operation_name}", style="red")
                return False

        except Exception as e:
            console.print(f"❌ Rollback failed: {e}", style="red")
            migration_log.error_message = f"Rollback failed: {e}"
            self.session.add(migration_log)
            self.session.commit()
            return False

    def _restore_from_backup(self, migration_log: MigrationLog, backup_path: str) -> bool:
        """Restore database from backup file.
        
        Args:
            migration_log: Migration log entry
            backup_path: Path to backup file
            
        Returns:
            True if restore was successful
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            console.print(f"❌ Backup file not found: {backup_path}", style="red")
            return False

        try:
            # Close current session to release database lock
            self.session.close()

            # Replace current database with backup
            shutil.copy2(backup_file, DOMAIN_DB_PATH)

            # Reopen session
            with get_domain_session() as new_session:
                # Mark migration as rolled back
                migration_log.status = MigrationStatus.ROLLED_BACK
                migration_log.completed_at = datetime.utcnow()
                new_session.add(migration_log)
                new_session.commit()

            console.print(f"✅ Database restored from backup: {backup_path}", style="green")
            return True

        except Exception as e:
            console.print(f"❌ Failed to restore from backup: {e}", style="red")
            return False

    def _rollback_sync_reference(self, migration_log: MigrationLog, rollback_data: Dict[str, Any]) -> bool:
        """Rollback reference table sync operation.
        
        Args:
            migration_log: Migration log entry
            rollback_data: Rollback data containing table information
            
        Returns:
            True if rollback was successful
        """
        tables_to_rollback = rollback_data.get("tables", [])
        
        if not tables_to_rollback:
            console.print("❌ No table information found for rollback", style="red")
            return False

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                for table_info in tables_to_rollback:
                    table_name = table_info["table_name"]
                    task = progress.add_task(f"Rolling back {table_name}...", total=None)

                    if table_info.get("exists", False):
                        # Table existed before, restore to previous state
                        row_count_before = table_info.get("row_count_before", 0)
                        
                        # If table was empty before, truncate it
                        if row_count_before == 0:
                            self.session.exec(text(f"DELETE FROM {table_name}"))
                        else:
                            # More complex rollback would require row-level tracking
                            console.print(f"⚠️  Cannot fully rollback {table_name} - table had existing data", style="yellow")
                    else:
                        # Table didn't exist before, drop it
                        self.session.exec(text(f"DROP TABLE IF EXISTS {table_name}"))

                    progress.update(task, description=f"✅ {table_name} rolled back")

            # Mark migration as rolled back
            migration_log.status = MigrationStatus.ROLLED_BACK
            migration_log.completed_at = datetime.utcnow()
            self.session.add(migration_log)
            self.session.commit()

            console.print("✅ Reference sync rollback completed", style="green")
            return True

        except Exception as e:
            console.print(f"❌ Reference sync rollback failed: {e}", style="red")
            return False

    def _rollback_add_card(self, migration_log: MigrationLog, rollback_data: Dict[str, Any]) -> bool:
        """Rollback card addition operation.
        
        Args:
            migration_log: Migration log entry
            rollback_data: Rollback data containing card information
            
        Returns:
            True if rollback was successful
        """
        card_uuid = rollback_data.get("card_uuid")
        if not card_uuid:
            console.print("❌ No card UUID found for rollback", style="red")
            return False

        try:
            # Remove card and related data
            from mtgsim.db.domain_models import (
                DomainCard,
                DomainCardColorLink,
                DomainCardSubtypeLink,
                DomainCardSupertypeLink,
                DomainCardTypeLink,
            )

            # Delete related links first (foreign key constraints)
            card = self.session.exec(select(DomainCard).where(DomainCard.uuid == card_uuid)).first()
            if card:
                # Delete relationship links using proper SQLModel syntax
                color_links = self.session.exec(select(DomainCardColorLink).where(DomainCardColorLink.card_id == card.id)).all()
                for link in color_links:
                    self.session.delete(link)
                
                type_links = self.session.exec(select(DomainCardTypeLink).where(DomainCardTypeLink.card_id == card.id)).all()
                for link in type_links:
                    self.session.delete(link)
                
                supertype_links = self.session.exec(select(DomainCardSupertypeLink).where(DomainCardSupertypeLink.card_id == card.id)).all()
                for link in supertype_links:
                    self.session.delete(link)
                
                subtype_links = self.session.exec(select(DomainCardSubtypeLink).where(DomainCardSubtypeLink.card_id == card.id)).all()
                for link in subtype_links:
                    self.session.delete(link)
                
                # Delete the card itself
                self.session.delete(card)

            # Mark migration as rolled back
            migration_log.status = MigrationStatus.ROLLED_BACK
            migration_log.completed_at = datetime.utcnow()
            self.session.add(migration_log)
            self.session.commit()

            console.print(f"✅ Card {card_uuid} rollback completed", style="green")
            return True

        except Exception as e:
            console.print(f"❌ Card rollback failed: {e}", style="red")
            return False

    def _rollback_add_set(self, migration_log: MigrationLog, rollback_data: Dict[str, Any]) -> bool:
        """Rollback set addition operation.
        
        Args:
            migration_log: Migration log entry
            rollback_data: Rollback data containing set information
            
        Returns:
            True if rollback was successful
        """
        set_code = rollback_data.get("set_code")
        added_cards = rollback_data.get("added_cards", [])

        if not set_code:
            console.print("❌ No set code found for rollback", style="red")
            return False

        try:
            from mtgsim.db.domain_models import (
                DomainCard,
                DomainSet,
                DomainCardColorLink,
                DomainCardSubtypeLink,
                DomainCardSupertypeLink,
                DomainCardTypeLink,
            )

            # Remove all cards that were added as part of this set operation
            for card_uuid in added_cards:
                card = self.session.exec(select(DomainCard).where(DomainCard.uuid == card_uuid)).first()
                if card:
                    # Delete relationship links first using proper SQLModel syntax
                    color_links = self.session.exec(select(DomainCardColorLink).where(DomainCardColorLink.card_id == card.id)).all()
                    for link in color_links:
                        self.session.delete(link)
                    
                    type_links = self.session.exec(select(DomainCardTypeLink).where(DomainCardTypeLink.card_id == card.id)).all()
                    for link in type_links:
                        self.session.delete(link)
                    
                    supertype_links = self.session.exec(select(DomainCardSupertypeLink).where(DomainCardSupertypeLink.card_id == card.id)).all()
                    for link in supertype_links:
                        self.session.delete(link)
                    
                    subtype_links = self.session.exec(select(DomainCardSubtypeLink).where(DomainCardSubtypeLink.card_id == card.id)).all()
                    for link in subtype_links:
                        self.session.delete(link)
                    
                    # Delete the card
                    self.session.delete(card)

            # Remove the set if it was added
            domain_set = self.session.exec(select(DomainSet).where(DomainSet.code == set_code)).first()
            if domain_set and rollback_data.get("set_was_added", False):
                self.session.delete(domain_set)

            # Mark migration as rolled back
            migration_log.status = MigrationStatus.ROLLED_BACK
            migration_log.completed_at = datetime.utcnow()
            self.session.add(migration_log)
            self.session.commit()

            console.print(f"✅ Set {set_code} rollback completed ({len(added_cards)} cards removed)", style="green")
            return True

        except Exception as e:
            console.print(f"❌ Set rollback failed: {e}", style="red")
            return False

    def _rollback_add_deck(self, migration_log: MigrationLog, rollback_data: Dict[str, Any]) -> bool:
        """Rollback deck addition operation.
        
        Args:
            migration_log: Migration log entry
            rollback_data: Rollback data containing deck information
            
        Returns:
            True if rollback was successful
        """
        deck_uuid = rollback_data.get("deck_uuid")
        added_cards = rollback_data.get("added_cards", [])

        if not deck_uuid:
            console.print("❌ No deck UUID found for rollback", style="red")
            return False

        try:
            from mtgsim.db.domain_models import (
                DomainCard,
                DomainDeck,
                DomainDeckCard,
                DomainCardColorLink,
                DomainCardSubtypeLink,
                DomainCardSupertypeLink,
                DomainCardTypeLink,
            )

            # Remove deck cards
            deck_cards = self.session.exec(select(DomainDeckCard).where(DomainDeckCard.deck_uuid == deck_uuid)).all()
            for deck_card in deck_cards:
                self.session.delete(deck_card)

            # Remove individual cards that were added
            for card_uuid in added_cards:
                card = self.session.exec(select(DomainCard).where(DomainCard.uuid == card_uuid)).first()
                if card:
                    # Delete relationship links first using proper SQLModel syntax
                    color_links = self.session.exec(select(DomainCardColorLink).where(DomainCardColorLink.card_id == card.id)).all()
                    for link in color_links:
                        self.session.delete(link)
                    
                    type_links = self.session.exec(select(DomainCardTypeLink).where(DomainCardTypeLink.card_id == card.id)).all()
                    for link in type_links:
                        self.session.delete(link)
                    
                    supertype_links = self.session.exec(select(DomainCardSupertypeLink).where(DomainCardSupertypeLink.card_id == card.id)).all()
                    for link in supertype_links:
                        self.session.delete(link)
                    
                    subtype_links = self.session.exec(select(DomainCardSubtypeLink).where(DomainCardSubtypeLink.card_id == card.id)).all()
                    for link in subtype_links:
                        self.session.delete(link)
                    
                    # Delete the card
                    self.session.delete(card)

            # Remove the deck
            deck = self.session.exec(select(DomainDeck).where(DomainDeck.uuid == deck_uuid)).first()
            if deck:
                self.session.delete(deck)

            # Mark migration as rolled back
            migration_log.status = MigrationStatus.ROLLED_BACK
            migration_log.completed_at = datetime.utcnow()
            self.session.add(migration_log)
            self.session.commit()

            console.print(f"✅ Deck {deck_uuid} rollback completed ({len(added_cards)} cards removed)", style="green")
            return True

        except Exception as e:
            console.print(f"❌ Deck rollback failed: {e}", style="red")
            return False

    def list_rollbackable_migrations(self) -> List[MigrationLog]:
        """Get list of migrations that can be rolled back.
        
        Returns:
            List of migration log entries that can be rolled back
        """
        return self.session.exec(
            select(MigrationLog)
            .where(MigrationLog.can_rollback == True)
            .where(MigrationLog.status.in_([MigrationStatus.COMPLETED, MigrationStatus.FAILED]))
            .order_by(MigrationLog.started_at.desc())
        ).all()

    def cleanup_old_backups(self, keep_days: int = 7) -> int:
        """Clean up old backup files.
        
        Args:
            keep_days: Number of days to keep backups
            
        Returns:
            Number of backup files deleted
        """
        backup_dir = DOMAIN_DB_PATH.parent / "backups"
        if not backup_dir.exists():
            return 0

        cutoff_time = datetime.utcnow().timestamp() - (keep_days * 24 * 60 * 60)
        deleted_count = 0

        for backup_file in backup_dir.glob("*.sqlite"):
            if backup_file.stat().st_mtime < cutoff_time:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                    console.print(f"🗑️  Deleted old backup: {backup_file.name}", style="dim")
                except Exception as e:
                    console.print(f"⚠️  Could not delete backup {backup_file.name}: {e}", style="yellow")

        if deleted_count > 0:
            console.print(f"✅ Cleaned up {deleted_count} old backup files", style="green")

        return deleted_count


# CLI commands for rollback functionality
rollback_app = typer.Typer(help="Rollback operations for domain database")


@rollback_app.command("list")
def list_rollbackable():
    """List migrations that can be rolled back."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            rollback_manager = RollbackManager(session)
            migrations = rollback_manager.list_rollbackable_migrations()

            if not migrations:
                console.print("No rollbackable migrations found", style="yellow")
                return

            table = Table(title="Rollbackable Migrations")
            table.add_column("ID", style="cyan")
            table.add_column("Operation", style="magenta")
            table.add_column("Source", style="blue")
            table.add_column("Started", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Rows Affected", justify="right", style="green")

            for migration in migrations:
                status_color = {
                    "COMPLETED": "green",
                    "FAILED": "red",
                    "IN_PROGRESS": "yellow",
                }.get(migration.status, "white")

                table.add_row(
                    str(migration.id),
                    migration.operation_name,
                    migration.source_name,
                    migration.started_at.strftime("%Y-%m-%d %H:%M:%S"),
                    f"[{status_color}]{migration.status}[/{status_color}]",
                    str(migration.rows_affected or 0),
                )

            console.print(table)

    except Exception as e:
        console.print(f"❌ Failed to list rollbackable migrations: {e}", style="red")
        raise typer.Exit(1)


@rollback_app.command("execute")
def execute_rollback(
    migration_id: int = typer.Argument(..., help="ID of the migration to rollback"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation prompt"),
):
    """Execute rollback for a specific migration."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist", style="red")
        raise typer.Exit(1)

    if not confirm:
        confirm_rollback = typer.confirm(
            f"Are you sure you want to rollback migration {migration_id}? This action cannot be undone."
        )
        if not confirm_rollback:
            console.print("Rollback cancelled", style="yellow")
            return

    try:
        with get_domain_session() as session:
            rollback_manager = RollbackManager(session)
            success = rollback_manager.rollback_migration(migration_id)

            if success:
                console.print(f"✅ Migration {migration_id} rolled back successfully", style="green")
            else:
                console.print(f"❌ Failed to rollback migration {migration_id}", style="red")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"❌ Rollback execution failed: {e}", style="red")
        raise typer.Exit(1)


@rollback_app.command("cleanup-backups")
def cleanup_backups(
    keep_days: int = typer.Option(7, help="Number of days to keep backup files"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation prompt"),
):
    """Clean up old backup files."""
    if not confirm:
        confirm_cleanup = typer.confirm(
            f"Are you sure you want to delete backup files older than {keep_days} days?"
        )
        if not confirm_cleanup:
            console.print("Cleanup cancelled", style="yellow")
            return

    try:
        with get_domain_session() as session:
            rollback_manager = RollbackManager(session)
            deleted_count = rollback_manager.cleanup_old_backups(keep_days)

            if deleted_count == 0:
                console.print("No old backup files found to delete", style="yellow")
            else:
                console.print(f"✅ Deleted {deleted_count} old backup files", style="green")

    except Exception as e:
        console.print(f"❌ Backup cleanup failed: {e}", style="red")
        raise typer.Exit(1)
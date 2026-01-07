"""Comprehensive logging manager for migration activities."""

import logging
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, ProgressColumn, Task, TaskID
from rich.text import Text
from sqlmodel import Session

from mtgsim.config import DOMAIN_DB_PATH
from mtgsim.db.migration_models import MigrationLog, MigrationStatus

console = Console()


class MigrationProgressColumn(ProgressColumn):
    """Custom progress column for migration operations."""

    def render(self, task: Task) -> Text:
        """Render the migration progress with status indicators."""
        if task.completed is None:
            return Text("⏳ Starting...", style="yellow")

        if task.total is None:
            # Indeterminate progress
            return Text(f"🔄 {task.description}", style="blue")

        percentage = (task.completed / task.total) * 100 if task.total > 0 else 0

        if percentage >= 100:
            return Text(f"✅ {task.description}", style="green")
        elif percentage > 0:
            return Text(f"🔄 {task.description} ({percentage:.1f}%)", style="blue")
        else:
            return Text(f"⏳ {task.description}", style="yellow")


class MigrationLogger:
    """Comprehensive logging manager for migration operations."""

    def __init__(self, session: Session, log_level: str = "INFO"):
        self.session = session
        self.logger = self._setup_logger(log_level)
        self.current_migration: MigrationLog | None = None
        self.progress: Progress | None = None
        self.current_task: TaskID | None = None

    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Set up structured logging for migration operations."""
        logger = logging.getLogger("mtgsim.migration")
        logger.setLevel(getattr(logging, log_level.upper()))

        # Clear existing handlers
        logger.handlers.clear()

        # Create log directory
        log_dir = DOMAIN_DB_PATH.parent / "logs"
        log_dir.mkdir(exist_ok=True)

        # File handler for detailed logs
        log_file = log_dir / f"migration_{datetime.utcnow().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Rich console handler for user-friendly output
        rich_handler = RichHandler(console=console, show_time=True, show_path=False, markup=True)
        rich_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(rich_handler)

        return logger

    def start_migration(
        self,
        operation_name: str,
        source_name: str,
        migration_type: str = "ENTITY_ADD",
        parameters: dict[str, Any] | None = None,
        total_items: int | None = None,
    ) -> MigrationLog:
        """Start logging a migration operation with progress tracking."""
        from mtgsim.db.migration_models import MigrationType

        # Create migration log entry
        migration_log = MigrationLog(
            migration_type=getattr(MigrationType, migration_type, MigrationType.ENTITY_ADD),
            operation_name=operation_name,
            source_name=source_name,
            status=MigrationStatus.IN_PROGRESS,
            total_items=total_items,
            parameters=parameters or {},
        )
        migration_log.mark_started()

        self.session.add(migration_log)
        self.session.commit()
        self.session.refresh(migration_log)

        self.current_migration = migration_log

        # Log operation start
        self.logger.info(
            f"🚀 Starting migration: {operation_name}",
            extra={
                "migration_id": migration_log.id,
                "operation": operation_name,
                "source": source_name,
                "type": migration_type,
                "total_items": total_items,
            },
        )

        # Initialize progress tracking if total items specified
        if total_items is not None:
            self.progress = Progress(MigrationProgressColumn(), console=console, transient=False)
            self.progress.start()
            self.current_task = self.progress.add_task(f"Processing {operation_name}", total=total_items)

        return migration_log

    def log_progress(self, processed: int = 1, failed: int = 0, skipped: int = 0, message: str | None = None) -> None:
        """Log progress update for the current migration."""
        if not self.current_migration:
            return

        # Update migration log counters
        self.current_migration.update_progress(
            processed=self.current_migration.processed_items + processed,
            failed=self.current_migration.failed_items + failed,
            skipped=self.current_migration.skipped_items + skipped,
        )
        self.session.add(self.current_migration)
        self.session.commit()

        # Update progress bar
        if self.progress and self.current_task is not None:
            self.progress.advance(self.current_task, processed)

        # Log progress message
        if message:
            self.logger.info(
                message,
                extra={
                    "migration_id": self.current_migration.id,
                    "processed": self.current_migration.processed_items,
                    "failed": self.current_migration.failed_items,
                    "skipped": self.current_migration.skipped_items,
                },
            )

    def log_item_processed(
        self, item_id: str, item_type: str, status: str = "success", details: dict[str, Any] | None = None
    ) -> None:
        """Log processing of an individual item."""
        if not self.current_migration:
            return

        log_level = logging.INFO if status == "success" else logging.WARNING
        status_icon = "✅" if status == "success" else "⚠️"

        self.logger.log(
            log_level,
            f"{status_icon} {item_type} {item_id}: {status}",
            extra={
                "migration_id": self.current_migration.id,
                "item_id": item_id,
                "item_type": item_type,
                "status": status,
                "details": details or {},
            },
        )

        # Update progress
        if status == "success":
            self.log_progress(processed=1)
        elif status == "failed":
            self.log_progress(failed=1)
        elif status == "skipped":
            self.log_progress(skipped=1)

    def log_error(self, error: Exception, context: dict[str, Any] | None = None) -> None:
        """Log an error during migration."""
        if not self.current_migration:
            return

        error_details = {"error_type": type(error).__name__, "error_message": str(error), "context": context or {}}

        self.logger.error(
            f"❌ Migration error: {error}",
            extra={"migration_id": self.current_migration.id, "error_details": error_details},
            exc_info=True,
        )

        # Update migration log with error
        self.current_migration.mark_failed(str(error), error_details)
        self.session.add(self.current_migration)
        self.session.commit()

    def complete_migration(self, result_summary: dict[str, Any] | None = None) -> None:
        """Complete the current migration with success."""
        if not self.current_migration:
            return

        # Calculate final statistics
        summary = result_summary or {}
        summary.update(
            {
                "total_processed": self.current_migration.processed_items,
                "total_failed": self.current_migration.failed_items,
                "total_skipped": self.current_migration.skipped_items,
                "rows_affected": (self.current_migration.processed_items - self.current_migration.failed_items),
            }
        )

        # Mark migration as completed
        self.current_migration.mark_completed(summary)
        self.current_migration.rows_affected = summary["rows_affected"]
        self.session.add(self.current_migration)
        self.session.commit()

        # Stop progress tracking
        if self.progress:
            if self.current_task is not None:
                self.progress.update(
                    self.current_task,
                    completed=self.current_migration.total_items or self.current_migration.processed_items,
                )
            self.progress.stop()
            self.progress = None
            self.current_task = None

        # Log completion
        self.logger.info(
            f"✅ Migration completed: {self.current_migration.operation_name}",
            extra={
                "migration_id": self.current_migration.id,
                "duration_seconds": self.current_migration.duration_seconds,
                "result_summary": summary,
            },
        )

        # Display final summary
        self._display_completion_summary(summary)

        self.current_migration = None

    def fail_migration(self, error: Exception, context: dict[str, Any] | None = None) -> None:
        """Fail the current migration with error details."""
        if not self.current_migration:
            return

        self.log_error(error, context)

        # Stop progress tracking
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.current_task = None

        # Display failure summary
        console.print(f"\n❌ Migration failed: {self.current_migration.operation_name}", style="red")
        console.print(f"   Error: {error}", style="red")
        console.print(f"   Processed: {self.current_migration.processed_items}", style="yellow")
        console.print(f"   Failed: {self.current_migration.failed_items}", style="red")

        self.current_migration = None

    def _display_completion_summary(self, summary: dict[str, Any]) -> None:
        """Display a formatted completion summary."""
        console.print("\n✅ Migration Summary", style="green bold")
        console.print(f"   Operation: {self.current_migration.operation_name}")
        console.print(f"   Duration: {self.current_migration.duration_seconds:.2f}s")
        console.print(f"   Processed: {summary['total_processed']}", style="green")

        if summary["total_failed"] > 0:
            console.print(f"   Failed: {summary['total_failed']}", style="red")

        if summary["total_skipped"] > 0:
            console.print(f"   Skipped: {summary['total_skipped']}", style="yellow")

        console.print(f"   Rows Affected: {summary['rows_affected']}", style="blue")

    def log_validation_check(
        self, check_name: str, table_name: str, passed: bool, error_details: list | None = None
    ) -> None:
        """Log validation check results."""
        from mtgsim.db.migration_models import DataIntegrityCheck

        # Create integrity check record
        integrity_check = DataIntegrityCheck(
            check_name=check_name,
            table_name=table_name,
            check_type="migration_validation",
            passed=passed,
            error_count=len(error_details) if error_details else 0,
            error_details=error_details or [],
            migration_log_id=self.current_migration.id if self.current_migration else None,
        )
        self.session.add(integrity_check)
        self.session.commit()

        # Log validation result
        status_icon = "✅" if passed else "❌"
        status_style = "green" if passed else "red"

        self.logger.info(
            f"{status_icon} Validation: {check_name} on {table_name}",
            extra={
                "migration_id": self.current_migration.id if self.current_migration else None,
                "check_name": check_name,
                "table_name": table_name,
                "passed": passed,
                "error_count": len(error_details) if error_details else 0,
            },
        )

        console.print(
            f"{status_icon} {check_name} ({table_name}): {'PASSED' if passed else 'FAILED'}", style=status_style
        )

        if not passed and error_details:
            for error in error_details[:5]:  # Show first 5 errors
                console.print(f"   • {error}", style="red dim")
            if len(error_details) > 5:
                console.print(f"   ... and {len(error_details) - 5} more errors", style="red dim")

    def log_rollback_operation(
        self, migration_id: int, rollback_type: str, success: bool, details: dict[str, Any] | None = None
    ) -> None:
        """Log rollback operation details."""
        status_icon = "✅" if success else "❌"
        status_style = "green" if success else "red"

        self.logger.info(
            f"{status_icon} Rollback {rollback_type} for migration {migration_id}: "
            f"{'SUCCESS' if success else 'FAILED'}",
            extra={
                "rollback_migration_id": migration_id,
                "rollback_type": rollback_type,
                "success": success,
                "details": details or {},
            },
        )

        console.print(
            f"{status_icon} Rollback ({rollback_type}) for migration {migration_id}: "
            f"{'SUCCESS' if success else 'FAILED'}",
            style=status_style,
        )

    def get_migration_history(self, limit: int = 10) -> list[MigrationLog]:
        """Get recent migration history for reporting."""
        from sqlmodel import select

        return self.session.exec(select(MigrationLog).order_by(MigrationLog.started_at.desc()).limit(limit)).all()

    def generate_migration_report(self, days: int = 7) -> dict[str, Any]:
        """Generate a comprehensive migration report."""
        from datetime import timedelta

        from sqlmodel import select

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Get migration statistics
        migrations = self.session.exec(select(MigrationLog).where(MigrationLog.started_at >= cutoff_date)).all()

        # Calculate statistics
        total_migrations = len(migrations)
        successful_migrations = len([m for m in migrations if m.status == MigrationStatus.COMPLETED])
        failed_migrations = len([m for m in migrations if m.status == MigrationStatus.FAILED])

        total_rows_affected = sum(m.rows_affected or 0 for m in migrations)
        avg_duration = (
            sum(m.duration_seconds or 0 for m in migrations) / total_migrations if total_migrations > 0 else 0
        )

        # Group by operation type
        operations_summary = {}
        for migration in migrations:
            op_name = migration.operation_name
            if op_name not in operations_summary:
                operations_summary[op_name] = {"count": 0, "successful": 0, "failed": 0, "total_rows": 0}

            operations_summary[op_name]["count"] += 1
            operations_summary[op_name]["total_rows"] += migration.rows_affected or 0

            if migration.status == MigrationStatus.COMPLETED:
                operations_summary[op_name]["successful"] += 1
            elif migration.status == MigrationStatus.FAILED:
                operations_summary[op_name]["failed"] += 1

        return {
            "period_days": days,
            "total_migrations": total_migrations,
            "successful_migrations": successful_migrations,
            "failed_migrations": failed_migrations,
            "success_rate": (successful_migrations / total_migrations * 100) if total_migrations > 0 else 0,
            "total_rows_affected": total_rows_affected,
            "average_duration_seconds": avg_duration,
            "operations_summary": operations_summary,
            "recent_migrations": [
                {
                    "id": m.id,
                    "operation": m.operation_name,
                    "status": m.status,
                    "started_at": m.started_at.isoformat(),
                    "duration": m.duration_seconds,
                    "rows_affected": m.rows_affected,
                }
                for m in migrations[:10]  # Last 10 migrations
            ],
        }


def create_migration_logger(session: Session, log_level: str = "INFO") -> MigrationLogger:
    """Factory function to create a migration logger."""
    return MigrationLogger(session, log_level)

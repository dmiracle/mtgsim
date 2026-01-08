"""CLI commands for domain database management."""

import sqlite3
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlmodel import select, text

from mtgsim.cli.logging_manager import create_migration_logger
from mtgsim.cli.rollback import RollbackManager, rollback_app
from mtgsim.config import DOMAIN_DB_PATH, MERGED_DB_PATH
from mtgsim.db.domain_session import (
    create_domain_tables_only,
    create_reference_tables_only,
    get_domain_session,
    init_domain_db,
    validate_domain_schema,
)
from mtgsim.db.migration_models import MigrationLog, SchemaVersion

console = Console()
domain_app = typer.Typer(help="Domain database operations")

# Add rollback commands as a subcommand
domain_app.add_typer(rollback_app, name="rollback")


@domain_app.command("migration-report")
def migration_report(
    days: int = typer.Option(7, help="Number of days to include in report"),
    format: str = typer.Option("table", help="Output format: 'table' or 'json'"),
):
    """Generate a comprehensive migration report."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            logger = create_migration_logger(session)
            report = logger.generate_migration_report(days)

            if format == "json":
                import json

                console.print(json.dumps(report, indent=2))
                return

            # Display table format
            console.print(f"\n[bold]Migration Report - Last {days} Days[/bold]")

            # Summary statistics
            summary_table = Table(title="Summary Statistics")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", justify="right", style="green")

            summary_table.add_row("Total Migrations", str(report["total_migrations"]))
            summary_table.add_row("Successful", str(report["successful_migrations"]))
            summary_table.add_row("Failed", str(report["failed_migrations"]))
            summary_table.add_row("Success Rate", f"{report['success_rate']:.1f}%")
            summary_table.add_row("Total Rows Affected", f"{report['total_rows_affected']:,}")
            summary_table.add_row("Average Duration", f"{report['average_duration_seconds']:.2f}s")

            console.print(summary_table)

            # Operations breakdown
            if report["operations_summary"]:
                console.print("\n[bold]Operations Breakdown[/bold]")
                ops_table = Table()
                ops_table.add_column("Operation", style="cyan")
                ops_table.add_column("Count", justify="right", style="blue")
                ops_table.add_column("Successful", justify="right", style="green")
                ops_table.add_column("Failed", justify="right", style="red")
                ops_table.add_column("Rows Affected", justify="right", style="magenta")

                for op_name, stats in report["operations_summary"].items():
                    ops_table.add_row(
                        op_name,
                        str(stats["count"]),
                        str(stats["successful"]),
                        str(stats["failed"]),
                        f"{stats['total_rows']:,}",
                    )

                console.print(ops_table)

            # Recent migrations
            if report["recent_migrations"]:
                console.print("\n[bold]Recent Migrations[/bold]")
                recent_table = Table()
                recent_table.add_column("ID", style="cyan")
                recent_table.add_column("Operation", style="magenta")
                recent_table.add_column("Status", style="yellow")
                recent_table.add_column("Started", style="blue")
                recent_table.add_column("Duration", justify="right", style="green")
                recent_table.add_column("Rows", justify="right", style="green")

                for migration in report["recent_migrations"]:
                    status_color = {
                        "COMPLETED": "green",
                        "FAILED": "red",
                        "IN_PROGRESS": "yellow",
                        "ROLLED_BACK": "orange1",
                    }.get(migration["status"], "white")

                    recent_table.add_row(
                        str(migration["id"]),
                        migration["operation"],
                        f"[{status_color}]{migration['status']}[/{status_color}]",
                        migration["started_at"][:19].replace("T", " "),
                        f"{migration['duration']:.2f}s" if migration["duration"] else "N/A",
                        str(migration["rows_affected"] or 0),
                    )

                console.print(recent_table)

    except Exception as e:
        console.print(f"❌ Failed to generate migration report: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("logs")
def view_logs(
    lines: int = typer.Option(50, help="Number of log lines to display"),
    level: str = typer.Option("INFO", help="Minimum log level to display"),
    follow: bool = typer.Option(False, help="Follow log file (like tail -f)"),
):
    """View migration logs."""
    log_dir = DOMAIN_DB_PATH.parent / "logs"

    if not log_dir.exists():
        console.print("❌ No log directory found", style="red")
        raise typer.Exit(1)

    # Find the most recent log file
    log_files = list(log_dir.glob("migration_*.log"))
    if not log_files:
        console.print("❌ No migration log files found", style="red")
        raise typer.Exit(1)

    latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

    try:
        if follow:
            console.print(f"📄 Following log file: {latest_log}")
            console.print("Press Ctrl+C to stop")

            import subprocess

            subprocess.run(["tail", "-f", str(latest_log)])
        else:
            console.print(f"📄 Last {lines} lines from: {latest_log}")

            with open(latest_log) as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                for line in recent_lines:
                    line = line.strip()
                    if level.upper() in line or level == "DEBUG":
                        # Color code log levels
                        if "ERROR" in line:
                            console.print(line, style="red")
                        elif "WARNING" in line:
                            console.print(line, style="yellow")
                        elif "INFO" in line:
                            console.print(line, style="white")
                        else:
                            console.print(line, style="dim")

    except KeyboardInterrupt:
        console.print("\n👋 Log following stopped", style="yellow")
    except Exception as e:
        console.print(f"❌ Failed to view logs: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("init")
def init_domain():
    """Initialize the domain database with all tables."""
    try:
        console.print(f"Initializing domain database at: {DOMAIN_DB_PATH}")

        # Initialize the database
        init_domain_db()

        # Validate the schema
        with get_domain_session() as session:
            if validate_domain_schema(session):
                console.print("✅ Domain database initialized successfully", style="green")

                # Add initial schema version record
                schema_version = SchemaVersion(
                    version="1.0.0", description="Initial domain database schema with reference and domain tables"
                )
                session.add(schema_version)
                session.commit()

                console.print("✅ Schema version 1.0.0 recorded", style="green")
            else:
                console.print("❌ Schema validation failed", style="red")
                raise typer.Exit(1)

    except Exception as e:
        console.print(f"❌ Failed to initialize domain database: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("status")
def domain_status():
    """Show domain database status and statistics."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            # Check schema validity
            schema_valid = validate_domain_schema(session)

            console.print(f"Domain Database: {DOMAIN_DB_PATH}")
            console.print(f"Schema Valid: {'✅ Yes' if schema_valid else '❌ No'}")

            if not schema_valid:
                console.print("Run 'init' to fix schema issues.", style="yellow")
                return

            # Create status table
            table = Table(title="Domain Database Status")
            table.add_column("Table", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Count", justify="right", style="green")

            # Reference tables
            ref_tables = [
                ("mtgjson_cards", "Reference"),
                ("mtgjson_sets", "Reference"),
                ("mtgjson_deck", "Reference"),
                ("mtgjson_deckcard", "Reference"),
                ("mtgjson_cardPrices", "Reference"),
            ]

            # Domain tables
            domain_tables = [
                ("domain_card", "Domain"),
                ("domain_set", "Domain"),
                ("domain_deck", "Domain"),
                ("domain_deck_card", "Domain"),
            ]

            # System tables
            system_tables = [
                ("migration_log", "System"),
                ("schema_version", "System"),
                ("data_integrity_check", "System"),
            ]

            all_tables = ref_tables + domain_tables + system_tables

            for table_name, table_type in all_tables:
                try:
                    count = session.exec(text(f"SELECT COUNT(*) FROM {table_name}")).first()
                    table.add_row(table_name, table_type, str(count))
                except Exception as e:
                    table.add_row(table_name, table_type, f"Error: {e}")

            console.print(table)

            # Show recent migrations
            from mtgsim.db.migration_models import MigrationLog

            recent_migrations = session.exec(
                select(MigrationLog).order_by(MigrationLog.started_at.desc()).limit(5)
            ).all()

            if recent_migrations:
                console.print("\n[bold]Recent Migrations:[/bold]")
                for migration in recent_migrations:
                    status_color = {
                        "COMPLETED": "green",
                        "FAILED": "red",
                        "IN_PROGRESS": "yellow",
                        "PENDING": "blue",
                    }.get(migration.status, "white")

                    console.print(
                        f"  {migration.started_at.strftime('%Y-%m-%d %H:%M:%S')} - "
                        f"{migration.operation_name} ({migration.source_name}) - "
                        f"[{status_color}]{migration.status}[/{status_color}]"
                    )

    except Exception as e:
        console.print(f"❌ Failed to get domain database status: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("create-tables")
def create_tables(
    table_type: str = typer.Option("all", help="Type of tables to create: 'all', 'domain', or 'reference'"),
):
    """Create specific table types in the domain database."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'init' first.", style="red")
        raise typer.Exit(1)

    try:
        from mtgsim.db.domain_session import get_domain_engine

        engine = get_domain_engine()

        if table_type == "domain":
            create_domain_tables_only(engine)
            console.print("✅ Domain tables created", style="green")
        elif table_type == "reference":
            create_reference_tables_only(engine)
            console.print("✅ Reference tables created", style="green")
        elif table_type == "all":
            init_domain_db()
            console.print("✅ All tables created", style="green")
        else:
            console.print(f"❌ Invalid table type: {table_type}", style="red")
            console.print("Valid options: 'all', 'domain', 'reference'")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"❌ Failed to create tables: {e}", style="red")
        raise typer.Exit(1)


def copy_table_with_prefix(
    source_db_path: Path, target_db_path: Path, table_name: str, prefix: str = "mtgjson_"
) -> int:
    """Copy a table from source database to target database with a prefix.

    Args:
        source_db_path: Path to source SQLite database
        target_db_path: Path to target SQLite database
        table_name: Name of table to copy
        prefix: Prefix to add to table name in target database

    Returns:
        Number of rows copied
    """
    target_table_name = f"{prefix}{table_name}"

    # Connect to both databases
    source_conn = sqlite3.connect(source_db_path)
    target_conn = sqlite3.connect(target_db_path)

    try:
        # Get source table schema
        source_cursor = source_conn.cursor()
        source_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        schema_result = source_cursor.fetchone()

        if not schema_result:
            raise ValueError(f"Table '{table_name}' not found in source database")

        # Modify schema to use target table name
        create_sql = schema_result[0].replace(f"CREATE TABLE {table_name}", f"CREATE TABLE {target_table_name}")
        create_sql = create_sql.replace(f'CREATE TABLE "{table_name}"', f'CREATE TABLE "{target_table_name}"')

        # Create target table
        target_cursor = target_conn.cursor()
        target_cursor.execute(f"DROP TABLE IF EXISTS {target_table_name}")
        target_cursor.execute(create_sql)

        # Copy data
        source_cursor.execute(f"SELECT * FROM {table_name}")
        rows = source_cursor.fetchall()

        if rows:
            # Get column count for placeholders
            column_count = len(rows[0])
            placeholders = ",".join(["?" for _ in range(column_count)])

            target_cursor.executemany(f"INSERT INTO {target_table_name} VALUES ({placeholders})", rows)

        target_conn.commit()
        return len(rows)

    finally:
        source_conn.close()
        target_conn.close()


def log_migration_start(session, operation_name: str, source_name: str) -> MigrationLog:
    """Log the start of a migration operation."""
    migration_log = MigrationLog(
        migration_type="REFERENCE_SYNC",  # Set the migration type
        operation_name=operation_name,
        source_name=source_name,
        started_at=datetime.utcnow(),
        status="IN_PROGRESS",
    )
    session.add(migration_log)
    session.commit()
    session.refresh(migration_log)
    return migration_log


def log_migration_complete(session, migration_log: MigrationLog, rows_affected: int = 0):
    """Log the completion of a migration operation."""
    migration_log.completed_at = datetime.utcnow()
    migration_log.status = "COMPLETED"
    migration_log.rows_affected = rows_affected
    session.add(migration_log)
    session.commit()


def validate_source_database_schema(source_db_path: Path, required_tables: list[str]) -> bool:
    """Validate that the source database contains all required tables.

    Args:
        source_db_path: Path to source database
        required_tables: List of table names that must exist

    Returns:
        True if all required tables exist, False otherwise
    """
    try:
        conn = sqlite3.connect(source_db_path)
        cursor = conn.cursor()

        # Get list of existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}

        conn.close()

        # Check if all required tables exist
        missing_tables = set(required_tables) - existing_tables
        if missing_tables:
            console.print(f"❌ Missing tables in source database: {', '.join(missing_tables)}", style="red")
            return False

        return True

    except Exception as e:
        console.print(f"❌ Error validating source database schema: {e}", style="red")
        return False


def verify_sync_integrity(source_db_path: Path, target_db_path: Path, table_mappings: list[tuple[str, str]]) -> bool:
    """Verify that sync operation completed successfully by comparing row counts.

    Args:
        source_db_path: Path to source database
        target_db_path: Path to target database
        table_mappings: List of (source_table, target_table) pairs

    Returns:
        True if all table row counts match, False otherwise
    """
    try:
        source_conn = sqlite3.connect(source_db_path)
        target_conn = sqlite3.connect(target_db_path)

        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()

        integrity_passed = True

        for source_table, target_table in table_mappings:
            # Get source table count
            source_cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            source_count = source_cursor.fetchone()[0]

            # Get target table count
            try:
                target_cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
                target_count = target_cursor.fetchone()[0]
            except sqlite3.OperationalError:
                console.print(f"❌ Target table {target_table} does not exist", style="red")
                integrity_passed = False
                continue

            # Compare counts
            if source_count != target_count:
                console.print(
                    f"❌ Row count mismatch for {source_table} -> {target_table}: "
                    f"source={source_count}, target={target_count}",
                    style="red",
                )
                integrity_passed = False
            else:
                console.print(f"✅ {source_table} -> {target_table}: {source_count} rows", style="green")

        source_conn.close()
        target_conn.close()

        return integrity_passed

    except Exception as e:
        console.print(f"❌ Error verifying sync integrity: {e}", style="red")
        return False


def log_integrity_check(session, check_name: str, table_name: str, passed: bool, error_details: list = None):
    """Log the results of an integrity check."""
    from mtgsim.db.migration_models import DataIntegrityCheck

    integrity_check = DataIntegrityCheck(
        check_name=check_name,
        table_name=table_name,
        check_type="sync_verification",
        passed=passed,
        error_count=0 if passed else len(error_details or []),
        error_details=error_details or [],
    )
    session.add(integrity_check)
    session.commit()


def log_migration_error(session, migration_log: MigrationLog, error_message: str):
    """Log an error in a migration operation."""
    migration_log.completed_at = datetime.utcnow()
    migration_log.status = "FAILED"
    migration_log.error_message = error_message
    session.add(migration_log)
    session.commit()


@domain_app.command("sync-reference")
def sync_reference():
    """Sync reference database tables to domain database."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    if not MERGED_DB_PATH.exists():
        console.print(f"❌ Reference database not found at {MERGED_DB_PATH}", style="red")
        console.print("Run 'mtgjson sync' to download reference data first.", style="yellow")
        raise typer.Exit(1)

    # Define tables to sync
    tables_to_sync = [
        ("cards", "Cards"),
        ("sets", "Sets"),
        ("deck", "Decks"),
        ("deckcard", "Deck Cards"),
        ("cardPrices", "Prices"),
    ]

    # Validate source database schema before starting
    required_tables = [table_name for table_name, _ in tables_to_sync]
    if not validate_source_database_schema(MERGED_DB_PATH, required_tables):
        console.print("❌ Source database schema validation failed", style="red")
        raise typer.Exit(1)

    with get_domain_session() as session:
        # Initialize logging and rollback managers
        logger = create_migration_logger(session, "INFO")
        rollback_manager = RollbackManager(session)

        # Create backup before starting
        try:
            backup_path = rollback_manager.create_backup("sync_reference")
        except Exception as e:
            console.print(f"❌ Failed to create backup: {e}", style="red")
            raise typer.Exit(1)

        # Start migration with comprehensive logging
        migration_log = logger.start_migration(
            operation_name="sync_reference",
            source_name="mtgjson",
            migration_type="REFERENCE_SYNC",
            parameters={
                "source_db": str(MERGED_DB_PATH),
                "target_db": str(DOMAIN_DB_PATH),
                "tables": [table_name for table_name, _ in tables_to_sync],
            },
            total_items=len(tables_to_sync),
        )

        try:
            # Capture table states for rollback
            table_states = []
            for table_name, _ in tables_to_sync:
                target_table = f"mtgjson_{table_name}"
                table_state = rollback_manager.capture_table_state(target_table)
                table_states.append(table_state)

            # Store rollback data
            rollback_data = {
                "backup_path": str(backup_path),
                "tables": table_states,
                "operation_type": "sync_reference",
            }
            rollback_manager.store_rollback_data(migration_log, rollback_data)

            total_rows = 0
            table_mappings = []

            for table_name, display_name in tables_to_sync:
                try:
                    logger.log_item_processed(
                        item_id=table_name,
                        item_type="table_sync",
                        status="starting",
                        details={"display_name": display_name},
                    )

                    rows_copied = copy_table_with_prefix(MERGED_DB_PATH, DOMAIN_DB_PATH, table_name, "mtgjson_")
                    total_rows += rows_copied

                    # Track table mappings for integrity verification
                    table_mappings.append((table_name, f"mtgjson_{table_name}"))

                    logger.log_item_processed(
                        item_id=table_name,
                        item_type="table_sync",
                        status="success",
                        details={
                            "display_name": display_name,
                            "rows_copied": rows_copied,
                            "target_table": f"mtgjson_{table_name}",
                        },
                    )

                except Exception as e:
                    logger.log_item_processed(
                        item_id=table_name,
                        item_type="table_sync",
                        status="failed",
                        details={"display_name": display_name, "error": str(e)},
                    )
                    raise

            # Verify sync integrity with detailed logging
            console.print("\n🔍 Verifying sync integrity...")

            for source_table, target_table in table_mappings:
                try:
                    # Get source and target counts
                    source_conn = sqlite3.connect(MERGED_DB_PATH)
                    target_conn = sqlite3.connect(DOMAIN_DB_PATH)

                    source_cursor = source_conn.cursor()
                    target_cursor = target_conn.cursor()

                    source_cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
                    source_count = source_cursor.fetchone()[0]

                    target_cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
                    target_count = target_cursor.fetchone()[0]

                    source_conn.close()
                    target_conn.close()

                    # Log validation check
                    passed = source_count == target_count
                    error_details = (
                        [] if passed else [f"Row count mismatch: source={source_count}, target={target_count}"]
                    )

                    logger.log_validation_check(
                        check_name="row_count_verification",
                        table_name=target_table,
                        passed=passed,
                        error_details=error_details,
                    )

                    if not passed:
                        raise ValueError(f"Integrity check failed for {target_table}")

                except Exception as e:
                    logger.log_validation_check(
                        check_name="row_count_verification",
                        table_name=target_table,
                        passed=False,
                        error_details=[str(e)],
                    )
                    raise

            # Complete migration successfully
            logger.complete_migration(
                {
                    "tables_synced": len(tables_to_sync),
                    "total_rows_copied": total_rows,
                    "backup_created": str(backup_path),
                    "integrity_checks_passed": len(table_mappings),
                }
            )

        except Exception as e:
            logger.fail_migration(
                e,
                {
                    "tables_processed": len([t for t in tables_to_sync if t[0] in [tm[0] for tm in table_mappings]]),
                    "backup_path": str(backup_path),
                },
            )
            console.print(f"💡 Use 'domain rollback execute {migration_log.id}' to restore from backup", style="blue")
            raise typer.Exit(1)


@domain_app.command("sync-mtgjson")
def sync_mtgjson():
    """Sync MTGJSON tables from mtgjson-merged.sqlite to domain database."""
    # This is an alias for sync-reference for backward compatibility
    sync_reference()


def transform_reference_card_to_domain(ref_card, session):
    """Transform a reference card to enhanced domain model."""
    from mtgsim.db.domain_models import (
        DomainCard,
        DomainCardColorLink,
        DomainCardSubtypeLink,
        DomainCardSupertypeLink,
        DomainCardTypeLink,
    )

    # Create the domain card with enhanced fields
    domain_card = DomainCard(
        uuid=ref_card.uuid,
        name=ref_card.name,
        mana_cost=ref_card.mana_cost,
        mana_value=ref_card.mana_value,
        type_line=ref_card.type,
        oracle_text=ref_card.oracle_text or ref_card.text or "",
        flavor_text=ref_card.flavor_text or "",
        power=ref_card.power,
        toughness=ref_card.toughness,
        loyalty=ref_card.loyalty,
        defense=ref_card.defense,
        set_code=ref_card.set_code,
        collector_number=ref_card.number,
        rarity=ref_card.rarity or "common",
        layout=ref_card.layout,
        border_color=ref_card.border_color,
        frame_version=ref_card.frame_version,
        artist=ref_card.artist,
        legalities=ref_card.legalities or {},
        scryfall_id=ref_card.scryfall_id,
        mtgo_id=ref_card.mtgo_id,
        arena_id=ref_card.arena_id,
        tcgplayer_id=ref_card.tcgplayer_id,
        cardmarket_id=ref_card.cardmarket_id,
        has_foil=ref_card.has_foil,
        has_non_foil=ref_card.has_non_foil,
        is_reprint=ref_card.is_reprint,
        is_foil_only=ref_card.is_foil_only,
        is_online_only=ref_card.is_online_only,
        added_at=datetime.utcnow(),
        source="mtgjson",
    )

    # Parse mana cost components if available
    if ref_card.mana_cost:
        # Simple parsing - count occurrences of each mana symbol
        mana_cost = ref_card.mana_cost
        domain_card.mana_cost_white = mana_cost.count("{W}")
        domain_card.mana_cost_blue = mana_cost.count("{U}")
        domain_card.mana_cost_black = mana_cost.count("{B}")
        domain_card.mana_cost_red = mana_cost.count("{R}")
        domain_card.mana_cost_green = mana_cost.count("{G}")
        domain_card.mana_cost_colorless = mana_cost.count("{C}")

        # Count generic mana (numbers in braces)
        import re

        generic_matches = re.findall(r"\{(\d+)\}", mana_cost)
        domain_card.mana_cost_generic = sum(int(match) for match in generic_matches)

    # Add the card to session first to get an ID
    session.add(domain_card)
    session.flush()  # This assigns the ID without committing

    # Handle color identity relationships
    if ref_card.color_identity:
        for color in ref_card.color_identity:
            color_link = DomainCardColorLink(card_id=domain_card.id, color=color)
            session.add(color_link)

    # Handle type relationships
    if ref_card.types:
        for card_type in ref_card.types:
            type_link = DomainCardTypeLink(card_id=domain_card.id, card_type=card_type)
            session.add(type_link)

    # Handle supertype relationships
    if ref_card.supertypes:
        for supertype in ref_card.supertypes:
            supertype_link = DomainCardSupertypeLink(card_id=domain_card.id, supertype=supertype)
            session.add(supertype_link)

    # Handle subtype relationships
    if ref_card.subtypes:
        for subtype in ref_card.subtypes:
            subtype_link = DomainCardSubtypeLink(card_id=domain_card.id, subtype=subtype)
            session.add(subtype_link)

    return domain_card


def transform_reference_set_to_domain(ref_set, session):
    """Transform a reference set to enhanced domain model."""
    from mtgsim.db.domain_models import DomainSet

    domain_set = DomainSet(
        code=ref_set.code,
        name=ref_set.name,
        type=ref_set.type,
        release_date=ref_set.release_date,
        base_set_size=ref_set.base_set_size,
        total_set_size=ref_set.total_set_size,
        block=ref_set.block,
        parent_code=ref_set.parent_code,
        keyrune_code=ref_set.keyrune_code,
        is_foil_only=ref_set.is_foil_only,
        is_online_only=ref_set.is_online_only,
        is_partial_preview=ref_set.is_partial_preview,
        mtgo_code=ref_set.mtgo_code,
        tcgplayer_group_id=ref_set.tcgplayer_group_id,
        cardmarket_id=ref_set.cardmarket_id,
        cardsphere_set_id=ref_set.cardsphere_set_id,
        languages=ref_set.languages or [],
        translations=ref_set.translations or {},
        token_set_code=ref_set.token_set_code,
        added_at=datetime.utcnow(),
        source="mtgjson",
    )

    return domain_set


def transform_reference_deck_to_domain(ref_deck, session):
    """Transform a reference deck to enhanced domain model."""
    from mtgsim.db.domain_models import DomainDeck

    domain_deck = DomainDeck(
        uuid=ref_deck.uuid,
        file_name=ref_deck.file_name,
        code=ref_deck.code,
        name=ref_deck.name,
        type=ref_deck.type,
        release_date=ref_deck.release_date,
        main_board_count=ref_deck.main_board_count,
        side_board_count=ref_deck.side_board_count,
        commander_count=ref_deck.commander_count,
        commander=ref_deck.commander or [],
        meta={},  # MTGJsonDeck doesn't have meta field, use empty dict
        added_at=datetime.utcnow(),
        source="mtgjson",
    )

    return domain_deck


@domain_app.command("add-card")
def add_card(uuid: str = typer.Argument(..., help="UUID of the card to add to domain tables")):
    """Add a specific card to user's domain tables."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            rollback_manager = RollbackManager(session)

            # Check if card already exists in domain tables
            from mtgsim.db.domain_models import DomainCard

            existing_card = session.exec(select(DomainCard).where(DomainCard.uuid == uuid)).first()

            if existing_card:
                console.print(f"✅ Card {uuid} already exists in domain tables", style="yellow")
                console.print(f"   Name: {existing_card.name}")
                console.print(f"   Set: {existing_card.set_code}")
                return

            # Find card in reference tables
            from mtgsim.db.reference_models import MTGJsonCard

            ref_card = session.exec(select(MTGJsonCard).where(MTGJsonCard.uuid == uuid)).first()

            if not ref_card:
                console.print(f"❌ Card {uuid} not found in reference tables", style="red")
                console.print("Run 'domain sync-reference' to populate reference tables first.", style="yellow")
                raise typer.Exit(1)

            # Log migration start
            migration_log = log_migration_start(session, "add_card", "mtgjson")

            try:
                # Store rollback data
                rollback_data = {"card_uuid": uuid, "operation_type": "add_card"}
                rollback_manager.store_rollback_data(migration_log, rollback_data)

                # Transform and add to domain tables
                domain_card = transform_reference_card_to_domain(ref_card, session)

                # Also ensure the set exists in domain tables
                if ref_card.set_code:
                    from mtgsim.db.domain_models import DomainSet
                    from mtgsim.db.reference_models import MTGJsonSet

                    existing_set = session.exec(select(DomainSet).where(DomainSet.code == ref_card.set_code)).first()
                    if not existing_set:
                        ref_set = session.exec(select(MTGJsonSet).where(MTGJsonSet.code == ref_card.set_code)).first()
                        if ref_set:
                            domain_set = transform_reference_set_to_domain(ref_set, session)
                            session.add(domain_set)

                session.commit()

                log_migration_complete(session, migration_log, 1)
                console.print("✅ Card added to domain tables successfully", style="green")
                console.print(f"   UUID: {domain_card.uuid}")
                console.print(f"   Name: {domain_card.name}")
                console.print(f"   Set: {domain_card.set_code}")
                console.print(f"   Rarity: {domain_card.rarity}")

            except Exception as e:
                log_migration_error(session, migration_log, str(e))
                console.print(f"💡 Use 'domain rollback execute {migration_log.id}' to rollback changes", style="blue")
                raise

    except Exception as e:
        console.print(f"❌ Failed to add card: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("add-set")
def add_set(code: str = typer.Argument(..., help="Set code to add all cards from")):
    """Add all cards from a set to user's domain tables."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            rollback_manager = RollbackManager(session)

            # Find set in reference tables
            from mtgsim.db.reference_models import MTGJsonCard, MTGJsonSet

            ref_set = session.exec(select(MTGJsonSet).where(MTGJsonSet.code == code)).first()

            if not ref_set:
                console.print(f"❌ Set {code} not found in reference tables", style="red")
                console.print("Run 'domain sync-reference' to populate reference tables first.", style="yellow")
                raise typer.Exit(1)

            # Check if set already exists in domain tables
            from mtgsim.db.domain_models import DomainCard, DomainSet

            existing_set = session.exec(select(DomainSet).where(DomainSet.code == code)).first()
            set_was_added = False

            if existing_set:
                console.print(f"✅ Set {code} already exists in domain tables", style="yellow")
                console.print(f"   Name: {existing_set.name}")
            else:
                # Add the set first
                domain_set = transform_reference_set_to_domain(ref_set, session)
                session.add(domain_set)
                session.flush()
                set_was_added = True

            # Get all cards from this set in reference tables
            ref_cards = session.exec(select(MTGJsonCard).where(MTGJsonCard.set_code == code)).all()

            if not ref_cards:
                console.print(f"❌ No cards found for set {code} in reference tables", style="red")
                raise typer.Exit(1)

            # Log migration start
            migration_log = log_migration_start(session, "add_set", "mtgjson")

            try:
                cards_added = 0
                cards_skipped = 0
                added_card_uuids = []

                # Store rollback data
                rollback_data = {
                    "set_code": code,
                    "set_was_added": set_was_added,
                    "added_cards": [],  # Will be populated as we add cards
                    "operation_type": "add_set",
                }
                rollback_manager.store_rollback_data(migration_log, rollback_data)

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(f"Adding cards from set {code}...", total=len(ref_cards))

                    for ref_card in ref_cards:
                        # Check if card already exists
                        existing_card = session.exec(select(DomainCard).where(DomainCard.uuid == ref_card.uuid)).first()

                        if existing_card:
                            cards_skipped += 1
                        else:
                            # Transform and add card
                            transform_reference_card_to_domain(ref_card, session)
                            cards_added += 1
                            added_card_uuids.append(ref_card.uuid)

                        progress.advance(task)

                # Update rollback data with added cards
                rollback_data["added_cards"] = added_card_uuids
                rollback_manager.store_rollback_data(migration_log, rollback_data)

                session.commit()

                log_migration_complete(session, migration_log, cards_added)
                console.print(f"✅ Set {code} processing completed", style="green")
                console.print(f"   Set Name: {ref_set.name}")
                console.print(f"   Cards Added: {cards_added}")
                console.print(f"   Cards Skipped (already exist): {cards_skipped}")
                console.print(f"   Total Cards: {len(ref_cards)}")

            except Exception as e:
                log_migration_error(session, migration_log, str(e))
                console.print(f"💡 Use 'domain rollback execute {migration_log.id}' to rollback changes", style="blue")
                raise

    except Exception as e:
        console.print(f"❌ Failed to add set: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("add-deck")
def add_deck(uuid: str = typer.Argument(..., help="UUID of the deck to add to domain tables")):
    """Add a deck and its cards to user's domain tables."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            # Check if deck already exists in domain tables
            from mtgsim.db.domain_models import DomainDeck

            existing_deck = session.exec(select(DomainDeck).where(DomainDeck.uuid == uuid)).first()

            if existing_deck:
                console.print(f"✅ Deck {uuid} already exists in domain tables", style="yellow")
                console.print(f"   Name: {existing_deck.name}")
                console.print(f"   Code: {existing_deck.code}")
                return

            # Find deck in reference tables
            from mtgsim.db.reference_models import MTGJsonDeck, MTGJsonDeckCard

            ref_deck = session.exec(select(MTGJsonDeck).where(MTGJsonDeck.uuid == uuid)).first()

            if not ref_deck:
                console.print(f"❌ Deck {uuid} not found in reference tables", style="red")
                console.print("Run 'domain sync-reference' to populate reference tables first.", style="yellow")
                raise typer.Exit(1)

            # Log migration start
            migration_log = log_migration_start(session, "add_deck", "mtgjson")

            try:
                # Transform and add deck
                domain_deck = transform_reference_deck_to_domain(ref_deck, session)
                session.add(domain_deck)
                session.flush()

                # Get all deck cards from reference tables
                ref_deck_cards = session.exec(select(MTGJsonDeckCard).where(MTGJsonDeckCard.deck_uuid == uuid)).all()

                cards_added = 0
                unique_cards_added = 0

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Adding deck cards...", total=len(ref_deck_cards))

                    for ref_deck_card in ref_deck_cards:
                        # Transform deck card to domain model
                        from mtgsim.db.domain_models import DomainDeckCard

                        domain_deck_card = DomainDeckCard(
                            deck_uuid=ref_deck_card.deck_uuid,
                            card_uuid=ref_deck_card.card_uuid,
                            name=ref_deck_card.name,
                            board=ref_deck_card.board,
                            count=ref_deck_card.count,
                            mana_cost=ref_deck_card.mana_cost,
                            mana_value=ref_deck_card.mana_value,
                            color_identity=ref_deck_card.color_identity or [],
                            colors=ref_deck_card.colors or [],
                            types=ref_deck_card.types or [],
                            subtypes=ref_deck_card.subtypes or [],
                            supertypes=ref_deck_card.supertypes or [],
                            printings=ref_deck_card.printings or [],
                            is_foil=ref_deck_card.is_foil,
                            is_etched=ref_deck_card.is_etched,
                            is_starter=ref_deck_card.is_starter,
                            is_reprint=ref_deck_card.is_reprint,
                            has_foil=ref_deck_card.has_foil,
                            has_non_foil=ref_deck_card.has_non_foil,
                        )
                        session.add(domain_deck_card)
                        cards_added += 1

                        # Also add the individual card to domain tables if it doesn't exist
                        if ref_deck_card.card_uuid:
                            from mtgsim.db.domain_models import DomainCard
                            from mtgsim.db.reference_models import MTGJsonCard

                            existing_card = session.exec(
                                select(DomainCard).where(DomainCard.uuid == ref_deck_card.card_uuid)
                            ).first()
                            if not existing_card:
                                ref_card = session.exec(
                                    select(MTGJsonCard).where(MTGJsonCard.uuid == ref_deck_card.card_uuid)
                                ).first()
                                if ref_card:
                                    transform_reference_card_to_domain(ref_card, session)
                                    unique_cards_added += 1

                        progress.advance(task)

                session.commit()

                log_migration_complete(session, migration_log, cards_added + unique_cards_added)
                console.print("✅ Deck added to domain tables successfully", style="green")
                console.print(f"   UUID: {domain_deck.uuid}")
                console.print(f"   Name: {domain_deck.name}")
                console.print(f"   Code: {domain_deck.code}")
                console.print(f"   Deck Cards Added: {cards_added}")
                console.print(f"   Unique Cards Added: {unique_cards_added}")

            except Exception as e:
                log_migration_error(session, migration_log, str(e))
                raise

    except Exception as e:
        console.print(f"❌ Failed to add deck: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("collect-card")
def collect_card(
    uuid: str = typer.Argument(..., help="UUID of the card to add to collection"),
    quantity: int = typer.Option(1, help="Quantity to add to collection"),
    foil: bool = typer.Option(False, help="Mark as foil card"),
    wanted: bool = typer.Option(False, help="Mark as wanted (not owned)"),
):
    """Add a card to user's collection with ownership tracking."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            rollback_manager = RollbackManager(session)

            from mtgsim.db.domain_models import DomainCard

            # Check if card already exists in domain tables
            existing_card = session.exec(select(DomainCard).where(DomainCard.uuid == uuid)).first()

            if existing_card:
                # Log migration start for collection update
                migration_log = log_migration_start(session, "collect_card", "user_collection")

                try:
                    # Store rollback data for existing card update
                    rollback_data = {
                        "card_uuid": uuid,
                        "operation_type": "update_collection",
                        "previous_state": {
                            "is_owned": existing_card.is_owned,
                            "quantity_owned": existing_card.quantity_owned,
                            "is_wanted": existing_card.is_wanted,
                            "is_foil": existing_card.is_foil,
                        },
                    }
                    rollback_manager.store_rollback_data(migration_log, rollback_data)

                    # Update existing card collection status
                    if wanted:
                        existing_card.is_wanted = True
                        console.print("✅ Card marked as wanted", style="green")
                    else:
                        existing_card.is_owned = True
                        existing_card.quantity_owned += quantity
                        existing_card.is_foil = foil or existing_card.is_foil
                        console.print(f"✅ Added {quantity} copies to collection", style="green")

                    existing_card.updated_at = datetime.utcnow()
                    session.add(existing_card)
                    session.commit()

                    log_migration_complete(session, migration_log, 1)
                    console.print(f"   Name: {existing_card.name}")
                    console.print(f"   Set: {existing_card.set_code}")
                    console.print(f"   Owned: {existing_card.quantity_owned}")
                    console.print(f"   Wanted: {existing_card.is_wanted}")
                    console.print(f"   Foil: {existing_card.is_foil}")
                    return

                except Exception as e:
                    log_migration_error(session, migration_log, str(e))
                    console.print(
                        f"💡 Use 'domain rollback execute {migration_log.id}' to rollback changes", style="blue"
                    )
                    raise

            # Card doesn't exist in domain tables, need to add it first
            from mtgsim.db.reference_models import MTGJsonCard

            ref_card = session.exec(select(MTGJsonCard).where(MTGJsonCard.uuid == uuid)).first()

            if not ref_card:
                console.print(f"❌ Card {uuid} not found in reference tables", style="red")
                console.print("Run 'domain sync-reference' to populate reference tables first.", style="yellow")
                raise typer.Exit(1)

            # Log migration start
            migration_log = log_migration_start(session, "collect_card", "user_collection")

            try:
                # Store rollback data
                rollback_data = {"card_uuid": uuid, "operation_type": "add_to_collection"}
                rollback_manager.store_rollback_data(migration_log, rollback_data)

                # Transform and add to domain tables with collection info
                domain_card = transform_reference_card_to_domain(ref_card, session)

                # Set collection properties
                if wanted:
                    domain_card.is_wanted = True
                    domain_card.is_owned = False
                    domain_card.quantity_owned = 0
                else:
                    domain_card.is_owned = True
                    domain_card.quantity_owned = quantity
                    domain_card.is_wanted = False

                domain_card.is_foil = foil
                domain_card.source = "user_collection"

                session.commit()

                log_migration_complete(session, migration_log, 1)
                console.print("✅ Card added to collection successfully", style="green")
                console.print(f"   UUID: {domain_card.uuid}")
                console.print(f"   Name: {domain_card.name}")
                console.print(f"   Set: {domain_card.set_code}")
                console.print(f"   Owned: {domain_card.quantity_owned}")
                console.print(f"   Wanted: {domain_card.is_wanted}")
                console.print(f"   Foil: {domain_card.is_foil}")

            except Exception as e:
                log_migration_error(session, migration_log, str(e))
                console.print(f"💡 Use 'domain rollback execute {migration_log.id}' to rollback changes", style="blue")
                raise

    except Exception as e:
        console.print(f"❌ Failed to add card to collection: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("remove-card")
def remove_card(
    uuid: str = typer.Argument(..., help="UUID of the card to remove from collection"),
    quantity: int = typer.Option(1, help="Quantity to remove from collection"),
    remove_all: bool = typer.Option(False, help="Remove all copies from collection"),
):
    """Remove a card from user's collection."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            from mtgsim.db.domain_models import DomainCard

            # Find card in domain tables
            existing_card = session.exec(select(DomainCard).where(DomainCard.uuid == uuid)).first()

            if not existing_card:
                console.print(f"❌ Card {uuid} not found in collection", style="red")
                raise typer.Exit(1)

            # Log migration start
            migration_log = log_migration_start(session, "remove_card", "user_collection")

            try:
                if remove_all:
                    # Remove completely from domain tables
                    session.delete(existing_card)
                    console.print("✅ Card removed completely from collection", style="green")
                else:
                    # Reduce quantity or mark as not owned
                    if existing_card.quantity_owned <= quantity:
                        existing_card.is_owned = False
                        existing_card.quantity_owned = 0
                        existing_card.is_foil = False
                        console.print("✅ Card marked as not owned", style="green")
                    else:
                        existing_card.quantity_owned -= quantity
                        console.print(f"✅ Removed {quantity} copies from collection", style="green")

                    existing_card.updated_at = datetime.utcnow()
                    session.add(existing_card)

                session.commit()

                log_migration_complete(session, migration_log, 1)
                console.print(f"   Name: {existing_card.name}")
                console.print(f"   Set: {existing_card.set_code}")
                if not remove_all:
                    console.print(f"   Owned: {existing_card.quantity_owned}")
                    console.print(f"   Wanted: {existing_card.is_wanted}")

            except Exception as e:
                log_migration_error(session, migration_log, str(e))
                raise

    except Exception as e:
        console.print(f"❌ Failed to remove card from collection: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("collection-stats")
def collection_stats():
    """Show user collection statistics."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            from mtgsim.db.domain_models import DomainCard, DomainDeck, DomainSet

            # Get collection statistics
            owned_cards = session.exec(select(DomainCard).where(DomainCard.is_owned)).all()
            wanted_cards = session.exec(select(DomainCard).where(DomainCard.is_wanted)).all()
            total_cards = session.exec(select(DomainCard)).all()

            sets_with_cards = session.exec(select(DomainSet)).all()
            decks = session.exec(select(DomainDeck)).all()

            # Calculate statistics
            total_owned_quantity = sum(card.quantity_owned for card in owned_cards)
            foil_cards = len([card for card in owned_cards if card.is_foil])

            # Group by rarity
            rarity_stats = {}
            for card in owned_cards:
                rarity = card.rarity or "unknown"
                if rarity not in rarity_stats:
                    rarity_stats[rarity] = {"count": 0, "quantity": 0}
                rarity_stats[rarity]["count"] += 1
                rarity_stats[rarity]["quantity"] += card.quantity_owned

            # Group by set
            set_stats = {}
            for card in owned_cards:
                set_code = card.set_code or "unknown"
                if set_code not in set_stats:
                    set_stats[set_code] = {"count": 0, "quantity": 0}
                set_stats[set_code]["count"] += 1
                set_stats[set_code]["quantity"] += card.quantity_owned

            # Display statistics
            console.print("\n[bold]Collection Statistics[/bold]")

            # Overview table
            overview_table = Table(title="Overview")
            overview_table.add_column("Metric", style="cyan")
            overview_table.add_column("Value", justify="right", style="green")

            overview_table.add_row("Unique Cards Owned", str(len(owned_cards)))
            overview_table.add_row("Total Card Quantity", str(total_owned_quantity))
            overview_table.add_row("Foil Cards", str(foil_cards))
            overview_table.add_row("Cards Wanted", str(len(wanted_cards)))
            overview_table.add_row("Total Cards in Database", str(len(total_cards)))
            overview_table.add_row("Sets with Cards", str(len(sets_with_cards)))
            overview_table.add_row("Decks", str(len(decks)))

            console.print(overview_table)

            # Rarity breakdown
            if rarity_stats:
                console.print("\n[bold]By Rarity[/bold]")
                rarity_table = Table()
                rarity_table.add_column("Rarity", style="cyan")
                rarity_table.add_column("Unique Cards", justify="right", style="green")
                rarity_table.add_column("Total Quantity", justify="right", style="green")

                for rarity, stats in sorted(rarity_stats.items()):
                    rarity_table.add_row(rarity.title(), str(stats["count"]), str(stats["quantity"]))

                console.print(rarity_table)

            # Top sets
            if set_stats:
                console.print("\n[bold]Top Sets (by card count)[/bold]")
                set_table = Table()
                set_table.add_column("Set Code", style="cyan")
                set_table.add_column("Unique Cards", justify="right", style="green")
                set_table.add_column("Total Quantity", justify="right", style="green")

                # Show top 10 sets by card count
                top_sets = sorted(set_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:10]
                for set_code, stats in top_sets:
                    set_table.add_row(set_code, str(stats["count"]), str(stats["quantity"]))

                console.print(set_table)

    except Exception as e:
        console.print(f"❌ Failed to get collection statistics: {e}", style="red")
        raise typer.Exit(1)


@domain_app.command("list-collection")
def list_collection(
    owned_only: bool = typer.Option(True, help="Show only owned cards"),
    wanted_only: bool = typer.Option(False, help="Show only wanted cards"),
    set_code: str = typer.Option(None, help="Filter by set code"),
    rarity: str = typer.Option(None, help="Filter by rarity"),
    limit: int = typer.Option(20, help="Maximum number of cards to show"),
):
    """List cards in user's collection."""
    if not DOMAIN_DB_PATH.exists():
        console.print("❌ Domain database does not exist. Run 'domain init' first.", style="red")
        raise typer.Exit(1)

    try:
        with get_domain_session() as session:
            from mtgsim.db.domain_models import DomainCard

            # Build query
            query = select(DomainCard)

            if owned_only and not wanted_only:
                query = query.where(DomainCard.is_owned)
            elif wanted_only and not owned_only:
                query = query.where(DomainCard.is_wanted)
            elif wanted_only and owned_only:
                query = query.where(DomainCard.is_owned | DomainCard.is_wanted)

            if set_code:
                query = query.where(DomainCard.set_code == set_code.upper())

            if rarity:
                query = query.where(DomainCard.rarity == rarity.lower())

            # Order by name and limit
            query = query.order_by(DomainCard.name).limit(limit)

            cards = session.exec(query).all()

            if not cards:
                console.print("No cards found matching the criteria.", style="yellow")
                return

            # Display cards
            table = Table(title=f"Collection ({len(cards)} cards)")
            table.add_column("Name", style="cyan")
            table.add_column("Set", style="magenta")
            table.add_column("Rarity", style="yellow")
            table.add_column("Owned", justify="right", style="green")
            table.add_column("Wanted", justify="center", style="blue")
            table.add_column("Foil", justify="center", style="gold1")

            for card in cards:
                owned_qty = str(card.quantity_owned) if card.is_owned else "0"
                wanted_mark = "✓" if card.is_wanted else ""
                foil_mark = "✓" if card.is_foil else ""

                table.add_row(
                    card.name,
                    card.set_code or "N/A",
                    (card.rarity or "unknown").title(),
                    owned_qty,
                    wanted_mark,
                    foil_mark,
                )

            console.print(table)

            if len(cards) == limit:
                console.print(f"\n[yellow]Showing first {limit} results. Use --limit to see more.[/yellow]")

    except Exception as e:
        console.print(f"❌ Failed to list collection: {e}", style="red")
        raise typer.Exit(1)

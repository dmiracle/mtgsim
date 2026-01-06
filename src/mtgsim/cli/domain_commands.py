"""CLI commands for domain database management."""

import sqlite3
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlmodel import text

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
                ("mtgjson_card", "Reference"),
                ("mtgjson_set", "Reference"),
                ("mtgjson_deck", "Reference"),
                ("mtgjson_deck_card", "Reference"),
                ("mtgjson_price", "Reference"),
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
            recent_migrations = session.exec(text("SELECT * FROM migration_log ORDER BY started_at DESC LIMIT 5")).all()

            if recent_migrations:
                console.print("\n[bold]Recent Migrations:[/bold]")
                for migration in recent_migrations:
                    status_color = {
                        "completed": "green",
                        "failed": "red",
                        "in_progress": "yellow",
                        "pending": "blue",
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
        operation_name=operation_name,
        source_name=source_name,
        started_at=datetime.utcnow(),
        status="in_progress"
    )
    session.add(migration_log)
    session.commit()
    session.refresh(migration_log)
    return migration_log


def log_migration_complete(session, migration_log: MigrationLog, rows_affected: int = 0):
    """Log the completion of a migration operation."""
    migration_log.completed_at = datetime.utcnow()
    migration_log.status = "completed"
    migration_log.rows_affected = rows_affected
    session.add(migration_log)
    session.commit()


def log_migration_error(session, migration_log: MigrationLog, error_message: str):
    """Log an error in a migration operation."""
    migration_log.completed_at = datetime.utcnow()
    migration_log.status = "failed"
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
    
    console.print("🔄 Syncing reference tables to domain database...")
    
    with get_domain_session() as session:
        migration_log = log_migration_start(session, "sync_reference", "mtgjson")
        
        try:
            total_rows = 0
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                
                # Define tables to sync
                tables_to_sync = [
                    ("card", "Cards"),
                    ("set", "Sets"), 
                    ("deck", "Decks"),
                    ("deck_card", "Deck Cards"),
                    ("price", "Prices")
                ]
                
                for table_name, display_name in tables_to_sync:
                    task = progress.add_task(f"Syncing {display_name}...", total=None)
                    
                    try:
                        rows_copied = copy_table_with_prefix(
                            MERGED_DB_PATH, DOMAIN_DB_PATH, table_name, "mtgjson_"
                        )
                        total_rows += rows_copied
                        progress.update(task, description=f"✅ {display_name}: {rows_copied:,} rows")
                        
                    except Exception as e:
                        progress.update(task, description=f"❌ {display_name}: {e}")
                        raise
            
            log_migration_complete(session, migration_log, total_rows)
            console.print(f"✅ Reference sync completed. {total_rows:,} total rows synced.", style="green")
            
        except Exception as e:
            log_migration_error(session, migration_log, str(e))
            console.print(f"❌ Reference sync failed: {e}", style="red")
            raise typer.Exit(1)


@domain_app.command("sync-mtgjson")
def sync_mtgjson():
    """Sync MTGJSON tables from mtgjson-merged.sqlite to domain database."""
    # This is an alias for sync-reference for backward compatibility
    sync_reference()

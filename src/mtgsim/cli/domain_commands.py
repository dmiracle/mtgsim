"""CLI commands for domain database management."""

import typer
from rich.console import Console
from rich.table import Table
from sqlmodel import text

from mtgsim.config import DOMAIN_DB_PATH
from mtgsim.db.domain_session import (
    create_domain_tables_only,
    create_reference_tables_only,
    get_domain_session,
    init_domain_db,
    validate_domain_schema,
)
from mtgsim.db.migration_models import SchemaVersion

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

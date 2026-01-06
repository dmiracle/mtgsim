"""Domain database session management for unified reference and domain tables."""

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine, text

from mtgsim.config import DOMAIN_DB_PATH, ensure_dirs

from .domain_models import (
    DomainCard,
    DomainCardColorLink,
    DomainCardSubtypeLink,
    DomainCardSupertypeLink,
    DomainCardTypeLink,
    DomainDeck,
    DomainDeckCard,
    DomainSet,
)
from .migration_models import (
    DataIntegrityCheck,
    MigrationLog,
    SchemaVersion,
)

# Import all models to ensure they're registered with SQLModel
from .reference_models import (
    MTGJsonCard,
    MTGJsonDeck,
    MTGJsonDeckCard,
    MTGJsonPrice,
    MTGJsonSet,
)


def get_domain_engine(db_path: Path | None = None):
    """Get SQLite engine for the domain database."""
    if db_path is None:
        db_path = DOMAIN_DB_PATH

    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create engine with foreign key support
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        echo=False,  # Set to True for SQL debugging
    )

    return engine


def init_domain_db(db_path: Path | None = None):
    """Initialize the domain database with all tables."""
    ensure_dirs()
    engine = get_domain_engine(db_path)

    # Create all tables
    SQLModel.metadata.create_all(engine)

    return engine


def get_domain_session(db_path: Path | None = None) -> Session:
    """Get a session for the domain database."""
    engine = get_domain_engine(db_path)
    return Session(engine)


def create_domain_tables_only(engine):
    """Create only domain tables (not reference tables)."""
    domain_tables = [
        DomainCard.__table__,
        DomainSet.__table__,
        DomainDeck.__table__,
        DomainDeckCard.__table__,
        DomainCardColorLink.__table__,
        DomainCardTypeLink.__table__,
        DomainCardSupertypeLink.__table__,
        DomainCardSubtypeLink.__table__,
        MigrationLog.__table__,
        SchemaVersion.__table__,
        DataIntegrityCheck.__table__,
    ]

    SQLModel.metadata.create_all(engine, tables=domain_tables)


def create_reference_tables_only(engine):
    """Create only reference tables (mtgjson_*)."""
    reference_tables = [
        MTGJsonCard.__table__,
        MTGJsonSet.__table__,
        MTGJsonDeck.__table__,
        MTGJsonDeckCard.__table__,
        MTGJsonPrice.__table__,
    ]

    SQLModel.metadata.create_all(engine, tables=reference_tables)


def validate_domain_schema(session: Session) -> bool:
    """Validate that the domain database schema is correct."""
    try:
        # Test that we can query each table
        session.exec(text("SELECT COUNT(*) FROM migration_log")).first()
        session.exec(text("SELECT COUNT(*) FROM schema_version")).first()
        session.exec(text("SELECT COUNT(*) FROM data_integrity_check")).first()

        # Test reference tables
        session.exec(text("SELECT COUNT(*) FROM mtgjson_card")).first()
        session.exec(text("SELECT COUNT(*) FROM mtgjson_set")).first()
        session.exec(text("SELECT COUNT(*) FROM mtgjson_deck")).first()

        # Test domain tables
        session.exec(text("SELECT COUNT(*) FROM domain_card")).first()
        session.exec(text("SELECT COUNT(*) FROM domain_set")).first()
        session.exec(text("SELECT COUNT(*) FROM domain_deck")).first()

        return True
    except Exception as e:
        print(f"Schema validation error: {e}")
        return False

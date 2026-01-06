from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from .deck_models import Deck, DeckCard, DeckList

DATABASE_PATH = Path.home() / ".mtgsim" / "mtgsim.db"


def get_engine(db_path: Path | None = None):
    if db_path is None:
        db_path = DATABASE_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}")


def init_db(db_path: Path | None = None):
    engine = get_engine(db_path)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session(db_path: Path | None = None) -> Session:
    engine = get_engine(db_path)
    return Session(engine)


def init_deck_db():
    from .deck_models import get_deck_engine

    engine = get_deck_engine()
    # Only create deck-related tables, not all SQLModel tables
    DeckList.metadata.create_all(
        engine,
        tables=[
            DeckList.__table__,
            Deck.__table__,
            DeckCard.__table__,
        ],
    )
    return engine

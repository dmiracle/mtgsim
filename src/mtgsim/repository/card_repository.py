from sqlmodel import Session, select

from ..db.models import (
    CardColorLink,
    CardDB,
    CardLegalityLink,
    CardSubtypeLink,
    CardSupertypeLink,
    CardTypeLink,
    Format,
)
from ..domain.card import Card, CardType, Color, ManaCost, Rarity, Supertype


def card_to_db(card: Card, **metadata) -> CardDB:
    """Convert a Card domain model to a CardDB database model."""
    db_card = CardDB(
        name=card.name,
        mana_cost_white=card.mana_cost.white if card.mana_cost else 0,
        mana_cost_blue=card.mana_cost.blue if card.mana_cost else 0,
        mana_cost_black=card.mana_cost.black if card.mana_cost else 0,
        mana_cost_red=card.mana_cost.red if card.mana_cost else 0,
        mana_cost_green=card.mana_cost.green if card.mana_cost else 0,
        mana_cost_colorless=card.mana_cost.colorless if card.mana_cost else 0,
        mana_cost_generic=card.mana_cost.generic if card.mana_cost else 0,
        oracle_text=card.oracle_text,
        flavor_text=card.flavor_text,
        text_box=card.text_box,
        raw_text=card.raw_text,
        image_url=card.image_url,
        power=card.power,
        toughness=card.toughness,
        loyalty=card.loyalty,
        defense=card.defense,
        rarity=card.rarity.value,
        **metadata,
    )
    return db_card


def db_to_card(db_card: CardDB) -> Card:
    """Convert a CardDB database model to a Card domain model."""
    mana_cost = None
    if any(
        [
            db_card.mana_cost_white,
            db_card.mana_cost_blue,
            db_card.mana_cost_black,
            db_card.mana_cost_red,
            db_card.mana_cost_green,
            db_card.mana_cost_colorless,
            db_card.mana_cost_generic,
        ]
    ):
        mana_cost = ManaCost(
            white=db_card.mana_cost_white,
            blue=db_card.mana_cost_blue,
            black=db_card.mana_cost_black,
            red=db_card.mana_cost_red,
            green=db_card.mana_cost_green,
            colorless=db_card.mana_cost_colorless,
            generic=db_card.mana_cost_generic,
        )

    return Card(
        name=db_card.name,
        mana_cost=mana_cost,
        card_types=[CardType(link.card_type) for link in db_card.card_types],
        supertypes=[Supertype(link.supertype) for link in db_card.supertypes],
        subtypes=[link.subtype for link in db_card.subtypes],
        oracle_text=db_card.oracle_text,
        flavor_text=db_card.flavor_text,
        text_box=db_card.text_box,
        raw_text=db_card.raw_text,
        image_url=db_card.image_url,
        power=db_card.power,
        toughness=db_card.toughness,
        loyalty=db_card.loyalty,
        defense=db_card.defense,
        color_identity=[Color(link.color) for link in db_card.colors],
        rarity=Rarity(db_card.rarity),
    )


class CardRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, card: Card, **metadata) -> CardDB:
        """Add a card to the database."""
        db_card = card_to_db(card, **metadata)
        self.session.add(db_card)
        self.session.flush()

        for ct in card.card_types:
            self.session.add(CardTypeLink(card_id=db_card.id, card_type=ct.value))

        for st in card.supertypes:
            self.session.add(CardSupertypeLink(card_id=db_card.id, supertype=st.value))

        for subtype in card.subtypes:
            self.session.add(CardSubtypeLink(card_id=db_card.id, subtype=subtype))

        for color in card.color_identity:
            self.session.add(CardColorLink(card_id=db_card.id, color=color.value))

        self.session.commit()
        self.session.refresh(db_card)
        return db_card

    def get_by_id(self, card_id: int) -> CardDB | None:
        """Get a card by its database ID."""
        return self.session.get(CardDB, card_id)

    def get_by_name(self, name: str) -> list[CardDB]:
        """Get all cards matching a name."""
        statement = select(CardDB).where(CardDB.name == name)
        return list(self.session.exec(statement).all())

    def search_by_name(self, name_part: str) -> list[CardDB]:
        """Search cards by partial name match."""
        statement = select(CardDB).where(CardDB.name.contains(name_part))
        return list(self.session.exec(statement).all())

    def get_owned(self) -> list[CardDB]:
        """Get all owned cards."""
        statement = select(CardDB).where(CardDB.is_owned)
        return list(self.session.exec(statement).all())

    def get_wanted(self) -> list[CardDB]:
        """Get all wanted cards."""
        statement = select(CardDB).where(CardDB.is_wanted)
        return list(self.session.exec(statement).all())

    def get_by_set(self, set_code: str) -> list[CardDB]:
        """Get all cards from a specific set."""
        statement = select(CardDB).where(CardDB.set_code == set_code)
        return list(self.session.exec(statement).all())

    def set_owned(self, card_id: int, owned: bool = True, quantity: int = 1) -> CardDB | None:
        """Mark a card as owned."""
        db_card = self.get_by_id(card_id)
        if db_card:
            db_card.is_owned = owned
            db_card.quantity_owned = quantity
            self.session.commit()
            self.session.refresh(db_card)
        return db_card

    def set_wanted(self, card_id: int, wanted: bool = True) -> CardDB | None:
        """Mark a card as wanted."""
        db_card = self.get_by_id(card_id)
        if db_card:
            db_card.is_wanted = wanted
            self.session.commit()
            self.session.refresh(db_card)
        return db_card

    def set_legality(self, card_id: int, format: Format, legality: str = "legal") -> None:
        """Set the legality of a card in a format."""
        existing = self.session.exec(
            select(CardLegalityLink).where(
                CardLegalityLink.card_id == card_id,
                CardLegalityLink.format == format.value,
            )
        ).first()

        if existing:
            existing.legality = legality
        else:
            self.session.add(CardLegalityLink(card_id=card_id, format=format.value, legality=legality))
        self.session.commit()

    def delete(self, card_id: int) -> bool:
        """Delete a card from the database."""
        db_card = self.get_by_id(card_id)
        if db_card:
            self.session.delete(db_card)
            self.session.commit()
            return True
        return False

    def all(self) -> list[CardDB]:
        """Get all cards."""
        statement = select(CardDB)
        return list(self.session.exec(statement).all())

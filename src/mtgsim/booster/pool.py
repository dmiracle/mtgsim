"""Card pool loading for booster generation."""

from mtgdb.models import MJCard, MJCardIdentifier, MJSet
from mtgdb.session import get_session
from sqlmodel import select

from .models import BoosterCard


def _build_image_url(scryfall_id: str | None) -> str | None:
    if not scryfall_id:
        return None
    return f"https://cards.scryfall.io/large/front/{scryfall_id[0]}/{scryfall_id[1]}/{scryfall_id}.jpg?v=1"


class SetPool:
    """Pre-loaded card pool for a set, split by rarity."""

    def __init__(self, set_code: str):
        self.set_code = set_code
        self.set_name = ""
        self.commons: list[BoosterCard] = []
        self.uncommons: list[BoosterCard] = []
        self.rares: list[BoosterCard] = []
        self.mythics: list[BoosterCard] = []
        self.basics: list[BoosterCard] = []
        self._load()

    def _load(self):
        with get_session() as session:
            # Get set name
            set_row = session.exec(select(MJSet.name).where(MJSet.code == self.set_code)).first()
            self.set_name = set_row or self.set_code

            # Get all cards with identifiers
            query = (
                select(MJCard, MJCardIdentifier)
                .outerjoin(MJCardIdentifier, MJCard.uuid == MJCardIdentifier.card_uuid)
                .where(MJCard.set_code == self.set_code)
            )
            results = session.exec(query).all()

            for card, identifier in results:
                bc = BoosterCard(
                    uuid=card.uuid,
                    name=card.name,
                    set_code=card.set_code,
                    number=card.number,
                    rarity=card.rarity or "common",
                    slot="",
                    image_url=_build_image_url(identifier.scryfall_id if identifier else None),
                    mana_cost=card.mana_cost,
                    mana_value=card.mana_value,
                    type_line=card.type_line,
                    colors=card.colors or [],
                )

                is_basic = card.type_line and "Basic Land" in card.type_line

                if is_basic:
                    self.basics.append(bc)
                elif card.rarity == "common":
                    self.commons.append(bc)
                elif card.rarity == "uncommon":
                    self.uncommons.append(bc)
                elif card.rarity == "rare":
                    self.rares.append(bc)
                elif card.rarity == "mythic":
                    self.mythics.append(bc)
                else:
                    # special/bonus go to rares
                    self.rares.append(bc)

    @property
    def all_cards(self) -> list[BoosterCard]:
        return self.commons + self.uncommons + self.rares + self.mythics + self.basics

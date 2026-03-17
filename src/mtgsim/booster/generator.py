"""Booster pack generators.

Each generator implements a different booster type (Play, Draft, Set).
The strategy pattern allows adding new booster types for older sets.
"""

import random
from abc import ABC, abstractmethod

from .models import BoosterCard, BoosterPack
from .pool import SetPool


class BoosterGenerator(ABC):
    """Base class for booster pack generators."""

    booster_type: str = "unknown"

    def __init__(self, pool: SetPool):
        self.pool = pool

    @abstractmethod
    def generate(self) -> BoosterPack:
        """Generate a single booster pack."""

    def _pick(self, cards: list[BoosterCard], n: int = 1) -> list[BoosterCard]:
        """Pick n random cards from a list (with replacement across packs, without within a pack)."""
        if not cards:
            return []
        return random.sample(cards, min(n, len(cards)))

    def _pick_one(self, cards: list[BoosterCard]) -> BoosterCard | None:
        if not cards:
            return None
        return random.choice(cards)

    def _with_slot(self, card: BoosterCard, slot: str, is_foil: bool = False) -> BoosterCard:
        """Return a copy of the card with the slot and foil status set."""
        return card.model_copy(update={"slot": slot, "is_foil": is_foil})


class PlayBoosterGenerator(BoosterGenerator):
    """Modern Play Booster (2024+).

    14 playable cards:
    - Slots 1-6: Commons (6)
    - Slot 7: Common (98.44%) — simplified to always common
    - Slots 8-10: Uncommons (3)
    - Slot 11: Rare (85.7%) / Mythic (14.3%) — 1:7 mythic rate
    - Slot 12: Land (basic from set, or common land if no basics)
    - Slot 13: Non-foil wildcard (any rarity)
    - Slot 14: Foil wildcard (any rarity, foil)
    """

    booster_type = "play"

    # Mythic rate: 1 in 7
    MYTHIC_RATE = 1 / 7

    # Wildcard rarity weights
    WILDCARD_WEIGHTS = {"common": 60, "uncommon": 25, "rare": 12, "mythic": 3}

    def generate(self) -> BoosterPack:
        cards: list[BoosterCard] = []

        # Slots 1-7: 7 commons
        commons = self._pick(self.pool.commons, 7)
        cards.extend(self._with_slot(c, "common") for c in commons)

        # Slots 8-10: 3 uncommons
        uncommons = self._pick(self.pool.uncommons, 3)
        cards.extend(self._with_slot(c, "uncommon") for c in uncommons)

        # Slot 11: rare/mythic
        rm = self._pick_rare_mythic()
        if rm:
            cards.append(self._with_slot(rm, "rare_mythic"))

        # Slot 12: land
        land = self._pick_land()
        if land:
            cards.append(self._with_slot(land, "land"))

        # Slot 13: non-foil wildcard
        wc = self._pick_wildcard()
        if wc:
            cards.append(self._with_slot(wc, "wildcard"))

        # Slot 14: foil wildcard
        foil = self._pick_wildcard()
        if foil:
            cards.append(self._with_slot(foil, "foil_wildcard", is_foil=True))

        return BoosterPack(
            set_code=self.pool.set_code,
            set_name=self.pool.set_name,
            booster_type=self.booster_type,
            cards=cards,
        )

    def _pick_rare_mythic(self) -> BoosterCard | None:
        if random.random() < self.MYTHIC_RATE and self.pool.mythics:
            return self._pick_one(self.pool.mythics)
        return self._pick_one(self.pool.rares) or self._pick_one(self.pool.mythics)

    def _pick_land(self) -> BoosterCard | None:
        if self.pool.basics:
            return self._pick_one(self.pool.basics)
        # Fallback: pick a common land
        lands = [c for c in self.pool.commons if c.type_line and "Land" in c.type_line]
        if lands:
            return self._pick_one(lands)
        return None

    def _pick_wildcard(self) -> BoosterCard | None:
        rarity = random.choices(
            list(self.WILDCARD_WEIGHTS.keys()),
            weights=list(self.WILDCARD_WEIGHTS.values()),
        )[0]
        pool_map = {
            "common": self.pool.commons,
            "uncommon": self.pool.uncommons,
            "rare": self.pool.rares,
            "mythic": self.pool.mythics,
        }
        pool = pool_map.get(rarity, self.pool.commons)
        return self._pick_one(pool) if pool else self._pick_one(self.pool.commons)


class DraftBoosterGenerator(BoosterGenerator):
    """Classic Draft Booster (pre-2024).

    15 playable cards:
    - Slots 1-10: Commons (10)
    - Slots 11-13: Uncommons (3)
    - Slot 14: Rare (86.5%) / Mythic (13.5%) — 1:7.4 mythic rate
    - Slot 15: Basic land
    - ~33% chance one common is replaced by a foil of any rarity
    """

    booster_type = "draft"

    MYTHIC_RATE = 1 / 7.4
    FOIL_CHANCE = 1 / 3
    FOIL_WEIGHTS = {"common": 71, "uncommon": 21, "rare": 7, "mythic": 1}

    def generate(self) -> BoosterPack:
        cards: list[BoosterCard] = []

        # Slots 1-10: 10 commons
        n_commons = 10
        has_foil = random.random() < self.FOIL_CHANCE
        if has_foil:
            n_commons = 9

        commons = self._pick(self.pool.commons, n_commons)
        cards.extend(self._with_slot(c, "common") for c in commons)

        # Optional foil replacing a common
        if has_foil:
            foil = self._pick_foil()
            if foil:
                cards.append(self._with_slot(foil, "foil_wildcard", is_foil=True))

        # Slots 11-13: 3 uncommons
        uncommons = self._pick(self.pool.uncommons, 3)
        cards.extend(self._with_slot(c, "uncommon") for c in uncommons)

        # Slot 14: rare/mythic
        rm = self._pick_rare_mythic()
        if rm:
            cards.append(self._with_slot(rm, "rare_mythic"))

        # Slot 15: basic land
        land = self._pick_land()
        if land:
            cards.append(self._with_slot(land, "land"))

        return BoosterPack(
            set_code=self.pool.set_code,
            set_name=self.pool.set_name,
            booster_type=self.booster_type,
            cards=cards,
        )

    def _pick_rare_mythic(self) -> BoosterCard | None:
        if random.random() < self.MYTHIC_RATE and self.pool.mythics:
            return self._pick_one(self.pool.mythics)
        return self._pick_one(self.pool.rares) or self._pick_one(self.pool.mythics)

    def _pick_land(self) -> BoosterCard | None:
        if self.pool.basics:
            return self._pick_one(self.pool.basics)
        return None

    def _pick_foil(self) -> BoosterCard | None:
        rarity = random.choices(
            list(self.FOIL_WEIGHTS.keys()),
            weights=list(self.FOIL_WEIGHTS.values()),
        )[0]
        pool_map = {
            "common": self.pool.commons,
            "uncommon": self.pool.uncommons,
            "rare": self.pool.rares,
            "mythic": self.pool.mythics,
        }
        pool = pool_map.get(rarity, self.pool.commons)
        return self._pick_one(pool) if pool else self._pick_one(self.pool.commons)


# Play Booster sets (MKM onward)
PLAY_BOOSTER_SETS = {
    "MKM",
    "OTJ",
    "MH3",
    "BLB",
    "DSK",
    "FDN",
    "INO",
    "AKR",
    "FIN",
    "OM1",
    "TLA",
    "SPM",
    "ECL",
    "OM2",
    "SOS",
    "TMT",
    "MSH",
}


def get_generator_for_set(pool: SetPool) -> BoosterGenerator:
    """Return the appropriate generator based on set release."""
    if pool.set_code in PLAY_BOOSTER_SETS:
        return PlayBoosterGenerator(pool)
    # Default to draft booster for older sets
    return DraftBoosterGenerator(pool)


def generate_booster(set_code: str, booster_type: str | None = None) -> BoosterPack:
    """Generate a booster pack for the given set.

    Args:
        set_code: Set code (e.g., "DSK", "MH3")
        booster_type: Force a specific booster type ("play" or "draft").
                      If None, auto-detects based on set.
    """
    pool = SetPool(set_code)
    if not pool.all_cards:
        raise ValueError(f"No cards found for set {set_code}")

    if booster_type == "play":
        gen = PlayBoosterGenerator(pool)
    elif booster_type == "draft":
        gen = DraftBoosterGenerator(pool)
    else:
        gen = get_generator_for_set(pool)

    return gen.generate()

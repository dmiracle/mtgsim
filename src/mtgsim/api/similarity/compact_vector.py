"""Compact card feature vector — low-dimensional grouped representation.

Groups keywords into functional categories (evasion, removal, etc.),
collapses subtypes to a boolean, and uses normalized numeric values.
Produces a ~60-dimensional vector suitable for cosine similarity,
deck profiling, and visualization.
"""

from mtgdb.models import MJCard

# ── Keyword groups ────────────────────────────────────────────────────

KEYWORD_GROUPS: dict[str, list[str]] = {
    "evasion": [
        "Flying",
        "Menace",
        "Fear",
        "Intimidate",
        "Shadow",
        "Horsemanship",
        "Skulk",
        "Landwalk",
    ],
    "first_strike": ["First strike", "Double strike"],
    "trample": ["Trample"],
    "haste": ["Haste"],
    "vigilance": ["Vigilance"],
    "lifelink": ["Lifelink"],
    "deathtouch": ["Deathtouch"],
    "reach": ["Reach", "Defender"],
    "indestructible": ["Indestructible", "Hexproof", "Shroud", "Ward", "Protection"],
    "flash": ["Flash"],
    "token_creation": ["Treasure", "Food", "Clue", "Blood", "Map", "Investigate"],
    "graveyard": ["Flashback", "Unearth", "Embalm", "Eternalize", "Escape", "Dredge", "Delve"],
    "cost_reduction": ["Convoke", "Affinity", "Improvise", "Emerge", "Delve"],
    "card_selection": ["Scry", "Surveil", "Mill"],
    "counters": ["Proliferate"],
    "equipment": ["Equip"],
    "etb_effects": ["Landfall", "Constellation"],
    "cycling": ["Cycling", "Typecycling", "Landcycling"],
    "morph": ["Morph", "Megamorph", "Disguise", "Manifest"],
    "combat_tricks": ["Prowess", "Ninjutsu", "Bushido"],
    "go_wide": ["Goad", "Myriad", "Melee"],
    "modal": ["Kicker", "Entwine", "Overload", "Escalate"],
    "transform": ["Transform", "Disturb", "Daybound", "Nightbound"],
    "crew": ["Crew"],
    "enchant": ["Enchant"],
    "partner": ["Partner", "Friends forever", "Choose a Background"],
}

# Build reverse lookup: keyword -> group name
_KEYWORD_TO_GROUP: dict[str, str] = {}
for group, kws in KEYWORD_GROUPS.items():
    for kw in kws:
        _KEYWORD_TO_GROUP[kw] = group

# ── Compact vector layout ─────────────────────────────────────────────

COMPACT_DIMENSIONS: list[str] = [
    # Colors (5)
    "color_W",
    "color_U",
    "color_B",
    "color_R",
    "color_G",
    # Color count (1) — normalized 0-5
    "color_count",
    # Colorless flag (1)
    "is_colorless",
    # Card type flags (8)
    "is_creature",
    "is_instant",
    "is_sorcery",
    "is_enchantment",
    "is_artifact",
    "is_land",
    "is_planeswalker",
    "is_battle",
    # Mana value (1) — normalized 0-1 (capped at 10)
    "mana_value",
    # Power and toughness (2) — normalized 0-1 (capped at 10)
    "power",
    "toughness",
    # Has P/T flag (1)
    "has_stats",
    # Has subtypes (1)
    "has_subtypes",
    # Is legendary (1)
    "is_legendary",
    # Has oracle text (1) — distinguishes vanilla creatures
    "has_oracle_text",
    # Is multicolored (1)
    "is_multicolor",
    # Text length bucket (1) — normalized proxy for card complexity
    "text_complexity",
    # Rarity signal (4) — one-hot
    "is_common",
    "is_uncommon",
    "is_rare",
    "is_mythic",
    # Is reprint (1)
    "is_reprint",
    # Oracle tags (9)
    "tag_boardwipe",
    "tag_counterspell",
    "tag_draw",
    "tag_lifegain",
    "tag_mana_dork",
    "tag_mana_rock",
    "tag_ramp",
    "tag_removal",
    "tag_tutor",
    # Keyword groups (26)
    *[f"kw_{group}" for group in KEYWORD_GROUPS],
]

_DIM_INDEX = {name: i for i, name in enumerate(COMPACT_DIMENSIONS)}


def compact_size() -> int:
    return len(COMPACT_DIMENSIONS)


def compact_dimension_names() -> list[str]:
    return list(COMPACT_DIMENSIONS)


def encode_compact(card: MJCard, tags: list[str] | None = None) -> list[float]:
    """Encode a card as a compact feature vector.

    Returns a float vector of length compact_size() (~60 dims).
    Values are 0.0/1.0 for binary features, 0.0-1.0 for normalized numerics.
    """
    vec = [0.0] * len(COMPACT_DIMENSIONS)

    def _set(name: str, value: float = 1.0):
        idx = _DIM_INDEX.get(name)
        if idx is not None:
            vec[idx] = value

    # Colors
    colors = card.color_identity or []
    for c in colors:
        _set(f"color_{c}")
    _set("color_count", len(colors) / 5.0)
    if not colors:
        _set("is_colorless")
    if len(colors) > 1:
        _set("is_multicolor")

    # Card types
    type_map = {
        "Creature": "is_creature",
        "Instant": "is_instant",
        "Sorcery": "is_sorcery",
        "Enchantment": "is_enchantment",
        "Artifact": "is_artifact",
        "Land": "is_land",
        "Planeswalker": "is_planeswalker",
        "Battle": "is_battle",
    }
    for t in card.types or []:
        dim = type_map.get(t)
        if dim:
            _set(dim)

    # Mana value (normalized, capped at 10)
    if card.mana_value is not None:
        _set("mana_value", min(card.mana_value, 10.0) / 10.0)

    # Power/toughness (normalized, capped at 10)
    if card.power is not None and card.toughness is not None:
        _set("has_stats")
        try:
            _set("power", min(float(card.power), 10.0) / 10.0)
        except ValueError:
            pass
        try:
            _set("toughness", min(float(card.toughness), 10.0) / 10.0)
        except ValueError:
            pass

    # Has subtypes
    if card.subtypes:
        _set("has_subtypes")

    # Is legendary
    if card.supertypes and "Legendary" in card.supertypes:
        _set("is_legendary")

    # Has oracle text (vanilla creatures have none)
    if card.oracle_text:
        _set("has_oracle_text")
        # Text complexity: normalized length (cap at 500 chars)
        _set("text_complexity", min(len(card.oracle_text), 500) / 500.0)

    # Rarity
    rarity_map = {"common": "is_common", "uncommon": "is_uncommon", "rare": "is_rare", "mythic": "is_mythic"}
    if card.rarity:
        dim = rarity_map.get(card.rarity)
        if dim:
            _set(dim)

    # Is reprint
    if card.is_reprint:
        _set("is_reprint")

    # Tags
    if tags:
        tag_map = {
            "boardwipe": "tag_boardwipe",
            "counterspell": "tag_counterspell",
            "draw": "tag_draw",
            "lifegain": "tag_lifegain",
            "mana-dork": "tag_mana_dork",
            "mana-rock": "tag_mana_rock",
            "ramp": "tag_ramp",
            "removal": "tag_removal",
            "tutor": "tag_tutor",
        }
        for tag in tags:
            dim = tag_map.get(tag)
            if dim:
                _set(dim)

    # Keyword groups
    for kw in card.keywords or []:
        group = _KEYWORD_TO_GROUP.get(kw)
        if group:
            _set(f"kw_{group}")

    return vec

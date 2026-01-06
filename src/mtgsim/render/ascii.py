from ..domain.card import Card, CardType


def render_card(card: Card, width: int = 40) -> str:
    """Render a card as ASCII art."""
    lines = []
    border = "+" + "-" * (width - 2) + "+"
    empty = "|" + " " * (width - 2) + "|"

    lines.append(border)

    # Name and mana cost line
    mana_str = ""
    if card.mana_cost:
        parts = []
        if card.mana_cost.generic:
            parts.append(str(card.mana_cost.generic))
        if card.mana_cost.white:
            parts.append("W" * card.mana_cost.white)
        if card.mana_cost.blue:
            parts.append("U" * card.mana_cost.blue)
        if card.mana_cost.black:
            parts.append("B" * card.mana_cost.black)
        if card.mana_cost.red:
            parts.append("R" * card.mana_cost.red)
        if card.mana_cost.green:
            parts.append("G" * card.mana_cost.green)
        if card.mana_cost.colorless:
            parts.append("C" * card.mana_cost.colorless)
        mana_str = "".join(parts)

    name_width = width - 4 - len(mana_str)
    name = card.name[:name_width]
    name_line = f"| {name:<{name_width}} {mana_str} |"
    lines.append(name_line)

    lines.append(border)

    # Type line
    type_parts = []
    if card.supertypes:
        type_parts.extend([st.value for st in card.supertypes])
    type_parts.extend([ct.value for ct in card.card_types])
    if card.subtypes:
        type_parts.append("—")
        type_parts.extend(card.subtypes)

    type_str = " ".join(type_parts)[: width - 4]
    lines.append(f"| {type_str:<{width - 4}} |")

    lines.append(border)

    # Oracle text
    if card.oracle_text:
        text_width = width - 4
        words = card.oracle_text.replace("\n", " \n ").split(" ")
        current_line = ""
        for word in words:
            if word == "\n":
                lines.append(f"| {current_line:<{text_width}} |")
                current_line = ""
            elif len(current_line) + len(word) + 1 <= text_width:
                current_line = f"{current_line} {word}".strip()
            else:
                lines.append(f"| {current_line:<{text_width}} |")
                current_line = word
        if current_line:
            lines.append(f"| {current_line:<{text_width}} |")
    else:
        lines.append(empty)

    lines.append(border)

    # P/T or Loyalty
    bottom_right = ""
    if CardType.CREATURE in card.card_types and card.power is not None and card.toughness is not None:
        bottom_right = f"{card.power}/{card.toughness}"
    elif CardType.PLANESWALKER in card.card_types and card.loyalty is not None:
        bottom_right = f"[{card.loyalty}]"
    elif CardType.BATTLE in card.card_types and card.defense is not None:
        bottom_right = f"<{card.defense}>"

    if bottom_right:
        pt_line = f"| {'':<{width - 4 - len(bottom_right)}}{bottom_right} |"
        lines.append(pt_line)
        lines.append(border)

    return "\n".join(lines)

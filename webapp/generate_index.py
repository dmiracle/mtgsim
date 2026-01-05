#!/usr/bin/env python3
"""Generate deck index for the webapp."""

import json
from pathlib import Path

FORMATS = ['standard', 'pioneer', 'modern', 'legacy', 'vintage', 'commander', 'brawl', 'historic', 'pauper']

def extract_deck_name(filename: str) -> str:
    """Extract readable deck name from filename."""
    name = filename.replace('.json', '')
    parts = name.rsplit('_', 1)
    if len(parts) == 2:
        name = parts[0]
    result = []
    for i, c in enumerate(name):
        if c.isupper() and i > 0 and name[i-1].islower():
            result.append(' ')
        result.append(c)
    return ''.join(result)

def calculate_deck_legality(deck_data: dict) -> dict:
    """Calculate which formats the deck is legal in."""
    all_cards = (
        deck_data.get('commander', []) +
        deck_data.get('mainBoard', []) +
        deck_data.get('sideBoard', [])
    )

    legality = {fmt: True for fmt in FORMATS}

    for card in all_cards:
        card_legalities = card.get('legalities', {})
        for fmt in FORMATS:
            if legality[fmt]:
                status = card_legalities.get(fmt, '')
                if status != 'Legal':
                    legality[fmt] = False

    return {fmt: legality[fmt] for fmt in FORMATS}

def load_set_release_dates(set_dir: Path) -> dict:
    """Load release dates from all set files."""
    release_dates = {}
    for set_file in set_dir.glob('*.json'):
        try:
            with open(set_file) as f:
                data = json.load(f)
            code = data.get('data', {}).get('code', '')
            release_date = data.get('data', {}).get('releaseDate', '')
            if code:
                release_dates[code] = release_date
        except:
            pass
    return release_dates

def main():
    deck_dir = Path(__file__).parent.parent / 'resources' / 'AllDeckFiles'
    set_dir = Path(__file__).parent.parent / 'resources' / 'AllSetFiles'
    output_file = Path(__file__).parent / 'decks.json'

    release_dates = load_set_release_dates(set_dir)

    decks = []
    for deck_file in sorted(deck_dir.glob('*.json')):
        try:
            with open(deck_file) as f:
                data = json.load(f)

            deck_data = data.get('data', {})
            card_count = 0
            if 'mainBoard' in deck_data:
                card_count += sum(c.get('count', 1) for c in deck_data['mainBoard'])
            if 'commander' in deck_data:
                card_count += sum(c.get('count', 1) for c in deck_data['commander'])

            legality = calculate_deck_legality(deck_data)
            code = deck_data.get('code', '')

            decks.append({
                'file': deck_file.name,
                'name': extract_deck_name(deck_file.name),
                'code': code,
                'cardCount': card_count,
                'legality': legality,
                'releaseDate': release_dates.get(code, '')
            })
        except Exception as e:
            print(f"Error processing {deck_file.name}: {e}")

    with open(output_file, 'w') as f:
        json.dump(decks, f)

    print(f"Generated index with {len(decks)} decks")

if __name__ == '__main__':
    main()

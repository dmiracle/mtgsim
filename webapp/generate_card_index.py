#!/usr/bin/env python3
"""Generate card index from AllPrintings.sqlite for the webapp."""

import json
import sqlite3
from pathlib import Path

def main():
    db_path = Path(__file__).parent.parent / 'resources' / 'AllPrintings.sqlite'
    output_file = Path(__file__).parent / 'card_index.json'

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get cards with identifiers - minimal data for display
    cursor = conn.execute('''
        SELECT
            c.uuid, c.name, c.type, c.manaCost, c.rarity,
            c.setCode, c.power, c.toughness, c.colorIdentity,
            i.scryfallId
        FROM cards c
        LEFT JOIN cardIdentifiers i ON c.uuid = i.uuid
        WHERE c.language = 'English' OR c.language IS NULL
    ''')

    def parse_list(val):
        if not val:
            return None
        if val.startswith('['):
            return json.loads(val)
        return [x.strip() for x in val.split(',') if x.strip()]

    card_index = {}
    count = 0
    for row in cursor:
        uuid = row['uuid']
        # Minimal data - exclude nulls
        card = {'n': row['name']}  # name is required
        if row['type']: card['t'] = row['type']
        if row['manaCost']: card['m'] = row['manaCost']
        if row['rarity']: card['r'] = row['rarity']
        if row['setCode']: card['s'] = row['setCode']
        if row['power']: card['p'] = row['power']
        if row['toughness']: card['o'] = row['toughness']
        ci = parse_list(row['colorIdentity'])
        if ci: card['c'] = ci
        if row['scryfallId']: card['i'] = row['scryfallId']
        card_index[uuid] = card
        count += 1

    conn.close()

    with open(output_file, 'w') as f:
        json.dump(card_index, f, separators=(',', ':'))

    print(f"Generated card index with {count} cards")
    print(f"File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")

if __name__ == '__main__':
    main()

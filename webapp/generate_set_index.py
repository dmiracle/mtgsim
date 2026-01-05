#!/usr/bin/env python3
"""Generate set index from AllSetFiles for the webapp."""

import json
from pathlib import Path

def main():
    set_dir = Path(__file__).parent.parent / 'resources' / 'AllSetFiles'
    output_file = Path(__file__).parent / 'sets.json'

    sets = []
    for set_file in sorted(set_dir.glob('*.json')):
        try:
            with open(set_file) as f:
                data = json.load(f)

            set_data = data.get('data', {})
            sets.append({
                'code': set_data.get('code', ''),
                'name': set_data.get('name', ''),
                'type': set_data.get('type', ''),
                'releaseDate': set_data.get('releaseDate', ''),
                'baseSetSize': set_data.get('baseSetSize', 0),
                'totalSetSize': set_data.get('totalSetSize', 0),
                'block': set_data.get('block', ''),
                'keyruneCode': set_data.get('keyruneCode', set_data.get('code', '').lower())
            })
        except Exception as e:
            print(f"Error processing {set_file.name}: {e}")

    with open(output_file, 'w') as f:
        json.dump(sets, f)

    print(f"Generated index with {len(sets)} sets")

if __name__ == '__main__':
    main()

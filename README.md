# MTGSim

A Magic: The Gathering card simulation and image extraction toolkit.

## Features

- **Card Extraction**: Extract card data from images using AI pipelines
- **ASCII Art Rendering**: Display cards as ASCII art in terminal
- **Database Management**: Track owned and wanted cards
- **MTGJSON Sync**: Download and sync reference data from MTGJSON

## Installation

```bash
uv sync
```

## Usage

```bash
# Display help
mtgsim --help

# Initialize database
mtgsim db init

# Sync reference data
mtgsim db sync

# Sync deck data
mtgsim db sync-decks

# Extract card from image
mtgsim extract path/to/card.jpg

# Create a card
mtgsim card "Lightning Bolt" --types Instant --mana R --oracle "Deal 3 damage to any target."
```

## CLI Commands

- `mtgsim card` - Generate and display ASCII card
- `mtgsim extract` - Extract card data from image
- `mtgsim db init` - Initialize database
- `mtgsim db sync` - Sync MTGJSON reference data
- `mtgsim db sync-decks` - Sync deck data
- `mtgsim db add` - Add card to database
- `mtgsim db list` - List cards
- `mtgsim db search` - Search cards
- `mtgsim db own` - Mark card as owned
- `mtgsim db want` - Mark card as wanted
- `mtgsim mtgjson info` - Show MTGJSON reference info
- `mtgsim mtgjson stats` - Show reference statistics

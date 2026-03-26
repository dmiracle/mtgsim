# Flashcard Study System — Backend API Definition

This document defines the flashcard backend API as consumed by the frontend.

---

## 1. Generate Flashcards

`POST /api/flashcards/generate`

Generates a batch of flashcards for a user from MTG data and stores them in the SRS system.

**Request body:** `GenerateRequest`
- `user_id`: string (required)
- `card_type`: string (required) — one of: `keyword_definition`, `card_oracle`, `card_mana_cost`, `card_stats`
- `set_code`: string | null — required for card-based types (`card_oracle`, `card_mana_cost`, `card_stats`)
- `rarity`: string | null — optional filter for card generation

**Response:** `GenerateResponse`
- `created`: integer — number of flashcards created
- `collection`: string — name of the collection created (e.g. `keywords_keyword_abilities`, `card_oracle_FIN`)

**Notes:**
- `keyword_definition`: generates one card per keyword, grouped by type (keyword_abilities, keyword_actions, ability_words). No set_code needed.
- `card_oracle`: shows card name + image, answer is oracle text + mana cost + type line. Requires set_code.
- `card_mana_cost`: shows card name + oracle text + type line, answer is mana cost + mana value. Requires set_code.
- `card_stats`: shows card name + oracle text + type line, answer is power/toughness. Requires set_code. Only creatures.
- If a collection already has flashcards, generation is skipped (returns 0).

---

## 2. Get Next Flashcard

`GET /api/flashcards/next`

Returns the next flashcard due for study based on the SM-2 spaced repetition algorithm.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | yes | User identifier |
| collection | string | no | Filter to a specific collection name |

**Response:** `FlashcardQuestion | null`
- `flashcard_id`: integer — ID to use when recording the review
- `question`: object — varies by card_type (see question formats below)
- `collection`: string | null — which collection this card belongs to

Returns `null` if no cards are available (all reviewed or none generated).

### Question Formats

**keyword_definition:**
```json
{
  "card_type": "keyword_definition",
  "keyword": "Flying",
  "keyword_type": "keyword_abilities"
}
```

**card_oracle:**
```json
{
  "card_type": "card_oracle",
  "card_name": "Lightning Bolt",
  "set_code": "M10",
  "image_url": "https://cards.scryfall.io/large/front/..."
}
```

**card_mana_cost:**
```json
{
  "card_type": "card_mana_cost",
  "card_name": "Lightning Bolt",
  "oracle_text": "Lightning Bolt deals 3 damage to any target.",
  "type_line": "Instant"
}
```

**card_stats:**
```json
{
  "card_type": "card_stats",
  "card_name": "Tarmogoyf",
  "oracle_text": "Tarmogoyf's power is equal to...",
  "type_line": "Creature — Lhurgoyf"
}
```

---

## 3. Record Review

`POST /api/flashcards/review`

Records a user's review of a flashcard, updating the SRS schedule.

**Request body:** `ReviewRequest`
- `user_id`: string (required)
- `flashcard_id`: integer (required) — from the `/next` response
- `rating`: integer (required, 0-5) — SM-2 scale:
  - 0 = complete blackout
  - 1 = incorrect, remembered on seeing answer
  - 2 = incorrect, easy recall after seeing answer
  - 3 = correct with difficulty
  - 4 = correct
  - 5 = perfect recall
- `response_time_ms`: integer (required, >= 0) — how long the user took to answer

**Response:** `ReviewResponse`
- `next_review_at`: string | null — ISO datetime of when this card is next due
- `interval`: integer — days until next review
- `ease_factor`: float — updated ease factor for this card

---

## 4. List Collections

`GET /api/flashcards/collections`

Returns all flashcard collections for a user.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | yes | User identifier |

**Response:** array of `CollectionInfo`
- `id`: integer
- `name`: string — e.g. `keywords_keyword_abilities`, `card_oracle_FIN`
- `card_count`: integer — number of flashcards in this collection

---

## 5. Study Stats

`GET /api/flashcards/stats`

Returns study statistics for a user.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| user_id | string | yes | User identifier |

**Response:** `StudyStats`
- `total_cards`: integer — total flashcards across all collections
- `cards_due`: integer — cards due for review now
- `cards_new`: integer — cards never reviewed
- `reviews_today`: integer — reviews completed today
- `collections`: array of `CollectionInfo`

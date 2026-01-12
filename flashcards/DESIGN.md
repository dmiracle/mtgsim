# MTG Flashcards Webapp Design

## Overview

A single-page web application for learning MTG keywords and abilities using spaced repetition powered by [ts-fsrs](https://github.com/open-spaced-repetition/ts-fsrs).

## Data Source

`mtg_flashcards.json` contains 3 categories:
- **abilityWords** (62 terms): Battalion, Landfall, Delirium, etc.
- **keywordAbilities** (~180 terms): Flying, Trample, Cascade, etc.
- **keywordActions** (~60 terms): Scry, Mill, Proliferate, etc.

Each entry has `{term, definition}` format.

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Framework | Vanilla JS + HTML/CSS | No build step, static hosting |
| SRS Engine | ts-fsrs (CDN) | Proven FSRS v6 implementation |
| Storage | localStorage | Offline-first, no backend needed |
| Styling | CSS Variables | Dark/light mode, responsive |

## Architecture

```
flashcards/
├── index.html          # Single page app
├── app.js              # Main application logic
├── storage.js          # localStorage wrapper for cards/logs
├── styles.css          # Styling
└── mtg_flashcards.json # Card data (already exists)
```

## Core Data Models

### Stored Card State (per term)
```typescript
interface StoredCard {
  id: string;              // "keywordAbilities:Flying"
  category: string;        // "keywordAbilities"
  term: string;            // "Flying"
  // FSRS Card fields
  due: string;             // ISO date
  stability: number;
  difficulty: number;
  elapsed_days: number;
  scheduled_days: number;
  learning_steps: number;
  reps: number;
  lapses: number;
  state: number;           // 0=New, 1=Learning, 2=Review, 3=Relearning
  last_review: string | null;
}
```

### Review Log Entry
```typescript
interface StoredReviewLog {
  id: string;              // Card ID
  rating: number;          // 1=Again, 2=Hard, 3=Good, 4=Easy
  state: number;
  due: string;
  stability: number;
  difficulty: number;
  elapsed_days: number;
  last_elapsed_days: number;
  scheduled_days: number;
  learning_steps: number;
  review: string;          // ISO date of review
}
```

## User Interface

### Main Views

1. **Dashboard** (default)
   - Cards due today count
   - New cards available count
   - Category filter toggles
   - "Start Review" button
   - Stats summary (streak, total reviews)

2. **Review Session**
   - Card front: Term name + category badge
   - Card back: Full definition (revealed on tap/space)
   - Rating buttons: Again / Hard / Good / Easy
   - Progress indicator: "5 of 12 remaining"
   - Exit button (saves progress)

3. **Settings** (optional, phase 2)
   - New cards per day limit
   - FSRS parameters (retention target, fuzz)
   - Export/import data
   - Reset progress

### Wireframes

```
┌─────────────────────────────────────┐
│  MTG Flashcards              [⚙]   │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │    Due Today: 12            │   │
│   │    New Available: 45        │   │
│   └─────────────────────────────┘   │
│                                     │
│   Categories:                       │
│   [✓] Ability Words                 │
│   [✓] Keyword Abilities             │
│   [✓] Keyword Actions               │
│                                     │
│        ┌─────────────────┐          │
│        │  Start Review   │          │
│        └─────────────────┘          │
│                                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ← Exit                    5/12     │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │      [Keyword Ability]      │   │
│   │                             │   │
│   │         FLYING              │   │
│   │                             │   │
│   │    (tap to reveal)          │   │
│   └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  ← Exit                    5/12     │
├─────────────────────────────────────┤
│                                     │
│   ┌─────────────────────────────┐   │
│   │      [Keyword Ability]      │   │
│   │                             │   │
│   │         FLYING              │   │
│   │                             │   │
│   │  This creature can't be     │   │
│   │  blocked except by          │   │
│   │  creatures with flying      │   │
│   │  or reach.                  │   │
│   └─────────────────────────────┘   │
│                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐  │
│  │Again │ │ Hard │ │ Good │ │Easy│  │
│  │ <1m  │ │ <10m │ │ 1d   │ │ 4d │  │
│  └──────┘ └──────┘ └──────┘ └────┘  │
└─────────────────────────────────────┘
```

## Application Flow

### Initialization
1. Load `mtg_flashcards.json`
2. Load stored cards from localStorage
3. For each term in JSON:
   - If no stored card exists, create new card with `createEmptyCard()`
   - If stored card exists, reconstruct FSRS Card object
4. Calculate due cards and display dashboard

### Review Session
1. User clicks "Start Review"
2. Collect due cards (where `due <= now`)
3. Optionally add new cards (up to daily limit)
4. Sort: Learning > Relearning > Due > New
5. For each card:
   - Show term (front)
   - User taps to reveal definition (back)
   - User rates: Again(1) / Hard(2) / Good(3) / Easy(4)
   - Call `fsrs.next(card, now, rating)`
   - Save updated card to localStorage
   - Save review log entry
6. When queue empty, show completion summary

### Scheduling Logic
```javascript
import { fsrs, createEmptyCard, Rating, State } from 'ts-fsrs';

const f = fsrs({
  request_retention: 0.9,
  maximum_interval: 365,
  enable_fuzz: true,
  enable_short_term: true
});

function reviewCard(card, rating) {
  const now = new Date();
  const result = f.next(card, now, rating);
  // result.card = updated card state
  // result.log = review log entry
  return result;
}
```

## localStorage Schema

```
mtg-flashcards-cards    → { [id]: StoredCard }
mtg-flashcards-logs     → StoredReviewLog[]
mtg-flashcards-settings → { newCardsPerDay: 20, ... }
mtg-flashcards-stats    → { totalReviews: 0, streak: 0, lastReviewDate: null }
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space / Enter | Reveal answer |
| 1 | Rate Again |
| 2 | Rate Hard |
| 3 | Rate Good |
| 4 | Rate Easy |
| Escape | Exit review session |

## Implementation Phases

### Phase 1: MVP
- [x] Data model design
- [ ] Load flashcard JSON
- [ ] Initialize ts-fsrs
- [ ] localStorage persistence
- [ ] Basic review UI (show term → reveal definition → rate)
- [ ] Dashboard with due count

### Phase 2: Polish
- [ ] Category filtering
- [ ] Progress stats (streak, total reviews, accuracy)
- [ ] Keyboard shortcuts
- [ ] Mobile-responsive layout
- [ ] Dark/light mode toggle

### Phase 3: Advanced
- [ ] Export/import progress as JSON
- [ ] Customizable FSRS parameters
- [ ] Review history visualization
- [ ] "Cramming" mode (review all regardless of schedule)

## File Size Estimates

| File | Size |
|------|------|
| index.html | ~3 KB |
| app.js | ~8 KB |
| storage.js | ~2 KB |
| styles.css | ~4 KB |
| ts-fsrs (CDN) | ~15 KB gzipped |
| mtg_flashcards.json | ~95 KB |
| **Total** | ~127 KB |

## Design Decisions

1. **New card limit**: None - all new cards available
2. **Session length**: No cap - review all due cards
3. **Category mixing**: Separate - review one category at a time
4. **Undo**: Not supported

## References

- [FSRS Algorithm](https://github.com/open-spaced-repetition/fsrs4anki/wiki/The-Algorithm)
- [ts-fsrs Documentation](https://open-spaced-repetition.github.io/ts-fsrs/)
- [ts-fsrs CDN](https://unpkg.com/ts-fsrs/dist/index.umd.js)

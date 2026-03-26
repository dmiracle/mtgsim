# Flashcard Study System — Feature Requirements

## 1. Study Dashboard

- Display study statistics: total cards, cards due, new cards, reviews completed today
- Show list of collections with card counts
- Quick-start study: button to begin studying due cards across all collections
- Per-collection study: button on each collection to study only that collection

---

## 2. Flashcard Generation

### 2.1 Generate Dialog
- Select flashcard type: Keyword Definitions, Card Oracle Text, Card Mana Costs, Card Stats
- For card-based types: searchable set selector (reuse existing set picker)
- Optional rarity filter for card-based types
- Show estimated card count before generating
- Generate button with loading state
- Result: show number created and collection name

### 2.2 Generation Types
- **Keyword Definitions**: question shows keyword name + type, answer is the definition
- **Card Oracle Text**: question shows card name + image, answer is oracle text + mana cost + type line
- **Card Mana Cost**: question shows card name + oracle text + type line, answer is mana cost + mana value
- **Card Stats**: question shows card name + oracle text + type line, answer is power/toughness

---

## 3. Study Session

### 3.1 Card Display
- Full-screen centered card with question on front
- Flip animation to reveal answer
- Question varies by card type:
  - Keyword: show keyword name prominently, keyword type as subtitle
  - Card Oracle: show card name + card image (if available)
  - Card Mana Cost: show card name + oracle text + type line
  - Card Stats: show card name + oracle text + type line
- Answer varies by card type:
  - Keyword: show definition text
  - Card Oracle: show oracle text, mana cost (rendered as symbols), type line
  - Card Mana Cost: show mana cost (rendered as symbols) + mana value
  - Card Stats: show power/toughness

### 3.2 Rating
- After revealing the answer, show rating buttons (0-5 scale)
- Visual labels for each rating:
  - 0: Blackout (no recall)
  - 1: Wrong (recognized answer)
  - 2: Wrong (easy after seeing)
  - 3: Hard (correct with effort)
  - 4: Good (correct)
  - 5: Perfect (instant recall)
- Color coding: 0-2 red/danger, 3 warning, 4-5 success/green
- Track response time automatically (from card reveal to rating click)
- After rating, show next review interval briefly, then advance to next card

### 3.3 Session Progress
- Show progress: cards reviewed / total due in current session
- Show current collection name (if filtered)
- Session complete screen when no more cards are due
- Option to return to dashboard or continue with new cards

---

## 4. Flashcard Card Component

- Flip card with front/back sides
- Smooth CSS 3D flip animation on reveal
- Front: question content (varies by type)
- Back: answer content (varies by type)
- Mana symbols rendered using mana-font (same as rest of app)
- Card images displayed when available (card_oracle type)
- Responsive: works on mobile and desktop

---

## 5. Card Recall Challenge (Scratch-to-Reveal)

A specialized flashcard mode where the learner is shown a blurred card image and must recall card properties before revealing.

### 5.1 Blurred Card Display
- Show the full card image with a heavy blur overlay (CSS filter or canvas)
- Card name is visible (unblurred) as the prompt
- Below the image, show what the learner should try to recall:
  - Mana value
  - Power/toughness (for creatures)
  - Keywords / special abilities
  - Mana cost
- These are prompts only — the user mentally recalls, no input fields

### 5.2 Scratch-to-Reveal Interaction
- User draws/scratches on the blurred image with mouse or touch to progressively unblur regions
- Uses a canvas overlay: drawing clears the blur mask, revealing the card art underneath
- Eraser-style circular brush, adjustable size
- Progressive reveal — the more you scratch, the more you see
- On mobile: touch/finger drawing works the same as mouse
- "Reveal All" button to instantly unblur the entire card

### 5.3 Self-Rating
- This is a self-study tool — the user rates their own recall
- After revealing (partially or fully), user rates themselves using the standard SM-2 scale (0-5)
- Same rating buttons as the standard flashcard flow (Section 3.2)
- No automated scoring or answer checking

### 5.4 Card Recall Prompt Types
- **Full Recall**: prompts user to recall MV, P/T, keywords, and mana cost
- **Stat Check**: prompts user to recall MV and P/T
- **Ability Recall**: prompts user to recall keywords/abilities
- **Cost Recall**: prompts user to recall mana cost

---

## 6. Navigation

- Flashcards accessible from sidebar navigation (new nav item)
- Route: `/flashcards` — study dashboard
- Route: `/flashcards/study` — active study session (with optional collection query param)
- Route: `/flashcards/generate` — generation dialog

---

## 6. Cross-Cutting

- User ID: use a simple localStorage-based user ID (no auth system)
- Theme: all flashcard components use the existing theme system
- Mana symbols: reuse ManaSymbols component for mana cost rendering
- Set selector: reuse existing set search/picker from draft simulator
- Responsive: flashcard study view should work well on mobile (primary study device)
- Keyboard shortcuts: Space to flip, 0-5 keys to rate

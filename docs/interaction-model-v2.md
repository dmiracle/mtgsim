# Card Interaction Model v2 — Data Models, Classifiers & Critique

## Context

The basic interaction system (PR #60) stores simple card-to-card edges. Now we need a richer model that handles three tiers of interaction complexity:

1. **Generic/Broad** — "Put +1/+1 counter on target creature" applies to every creature. Storing N x M edges is wasteful.
2. **Specific** — Splinter Twin + Deceiver Exarch. Traditional combo edges.
3. **Game-State-Aware** — An instant removal spell is more valuable during Declare Blockers than Main Phase.

The model must be extensible (new classifier types without schema changes), graph-friendly (network visualization), and grounded in available data.

---

## A. Core Data Models

### A1. InteractionPattern (Tier 1 — Broad Interactions)

Instead of card-to-card edges, store what a card does and a **selector predicate** for what it applies to.

| Field | Type | Notes |
|---|---|---|
| `id` | `int` | PK |
| `card_uuid` | `str` | FK → mj_card.uuid, indexed |
| `effect_type` | `str` | indexed — "removal", "counter_placement", "mana_production", "buff", "tribal_lord" |
| `effect_subtype` | `str \| None` | "destroy", "exile", "plus_one_counter", "tap_for_mana" |
| `target_selector` | `dict` (JSON) | Predicate describing what cards this applies to (see below) |
| `direction` | `str` | "provides" or "benefits_from" |
| `detected_by` | `str` | indexed — "manual", "keyword_match", "text_parse", "tag_match", "llm" |
| `confidence` | `float` | 0.0–1.0 |
| `description` | `str \| None` | |
| `extra` | `dict` (JSON) | |
| `created_at` / `updated_at` | `datetime` | |

**target_selector structure:**

```json
{
    "types": ["Creature"],
    "subtypes": ["Elf"],
    "keywords": ["flying"],
    "min_mana_value": 3,
    "max_mana_value": 5,
    "colors": ["G"],
    "oracle_text_contains": ["token"],
    "tags": ["mana-dork"],
    "match_mode": "all"
}
```

**Selectivity rule of thumb:** If an interaction applies to >20 cards, use a pattern. Below that, use explicit edges.

### A2. InteractionEdge (Tier 2 — Evolve Existing UserCardInteraction)

Add columns to the existing `user_card_interaction` table:

| New Field | Type | Notes |
|---|---|---|
| `interaction_subtype` | `str \| None` | indexed — "infinite_loop", "etb_trigger", "tribal", etc. |
| `detected_by` | `str` | default "manual" — "manual", "keyword_match", "text_parse", "co_occurrence", "llm" |
| `confidence` | `float` | default 1.0 |
| `win_rate_correlation` | `float \| None` | from 17Lands co-occurrence |
| `co_occurrence_count` | `int \| None` | games/decks where both appeared |

All new columns are nullable/defaulted — existing data migrates automatically.

### A3. InteractionContext (Tier 3 — Game-State/Phase Annotations)

Attaches to either an edge or a pattern to express "this interaction has strength X in context Y."

| Field | Type | Notes |
|---|---|---|
| `id` | `int` | PK |
| `edge_id` | `int \| None` | FK → user_card_interaction.id (exactly one of edge_id/pattern_id set) |
| `pattern_id` | `int \| None` | FK → interaction_pattern.id |
| `game_state` | `str \| None` | "developing", "ahead", "behind", "parity" (matches UserCardRating) |
| `phase` | `str \| None` | MTG phase enum value |
| `turn_range` | `str \| None` | "early" (1-3), "mid" (4-7), "late" (8+) |
| `context_strength` | `int \| None` | 1-5, overrides base strength in this context |
| `context_notes` | `str \| None` | |
| `detected_by` | `str` | default "manual" |
| `confidence` | `float` | default 1.0 |

### A4. MTG Phase/Step Enums

```
UNTAP → UPKEEP → DRAW → MAIN_1 → COMBAT_BEGIN → COMBAT_ATTACKERS →
COMBAT_BLOCKERS → COMBAT_DAMAGE → COMBAT_END → MAIN_2 → END_STEP → CLEANUP
```

Game state quadrants (matching existing UserCardRating):

```
DEVELOPING | AHEAD | BEHIND | PARITY
```

Turn ranges:

```
EARLY (turns 1-3) | MID (turns 4-7) | LATE (turns 8+)
```

### A5. ClassifierRun (Audit Trail)

| Field | Type | Notes |
|---|---|---|
| `id` | `int` | PK |
| `classifier_name` | `str` | indexed — "keyword_synergy_v1", "tribal_v1", "17lands_co_occurrence" |
| `classifier_version` | `str` | |
| `set_code` | `str \| None` | if scoped to a set |
| `card_count_processed` | `int` | |
| `edges_created` | `int` | |
| `patterns_created` | `int` | |
| `config` | `dict` (JSON) | classifier parameters |
| `started_at` | `datetime` | |
| `completed_at` | `datetime \| None` | |
| `status` | `str` | "running", "completed", "failed" |

---

## B. Classification Taxonomy

### Interaction Types (top-level)

| Type | Direction | Example |
|---|---|---|
| `combo` | Bidirectional | Splinter Twin + Deceiver Exarch |
| `synergy` | Bidirectional | Cards that are better together |
| `enables` | A → B | Mana dork → expensive spell |
| `counters` | A → B | Removal → threat |
| `anti_synergy` | Bidirectional | Cards that are worse together (nonbo) |
| `payoff` | A → B | Lord → tribal creature |

### Interaction Subtypes (extensible)

- **combo:** infinite_loop, lock, one_shot_kill, value_engine, mana_combo
- **synergy:** tribal, keyword_matters, counter_synergy, sacrifice_synergy, etb_trigger, graveyard_synergy, artifact_matters, token_synergy, lifegain_synergy, spell_matters
- **enables:** mana_ramp, card_draw, tutor, cost_reduction, protection, evasion_grant
- **counters:** removal, counterspell, exile, wrath, hate_piece, graveyard_hate
- **payoff:** lord_effect, anthem, aristocrats_payoff, spellslinger_payoff

### Selectivity Spectrum

```
Most Generic ←─────────────────────────────────→ Most Specific

"Target creature"      "Target Elf"        "Deceiver Exarch"
(matches ~60K cards)   (matches ~500)      (matches 1 card)

     Tier 1:                Tier 1:              Tier 2:
  InteractionPattern    InteractionPattern    InteractionEdge
  target_selector:      target_selector:      source → target
  {types:["Creature"]}  {subtypes:["Elf"]}    (explicit edge)
```

### Pattern Resolution

A `matches_selector(card, selector) -> bool` function evaluates a card against a target_selector dict. At query time:
- For a set (300 cards): evaluate all patterns x all cards — ~1.5M checks, trivial
- For a format (15K cards): cache results or materialize into a `interaction_pattern_match` table

---

## C. Adversarial Critique

### C1. The Phase/Timing Gap Is Severe

17Lands `MJ17LReplayTurn` records what happened on a *turn number*, not within which *phase* or *step*. You know "Murder was cast on turn 5" but not whether it was during Main Phase or in response to Declare Attackers. **Tier 3 phase-level analysis cannot be data-driven from 17Lands.** Phase context must be rules-inferred ("Murder is an instant, so it CAN be cast during combat") not data-validated ("Murder IS cast during combat X% of the time"). The UI should label this distinction clearly.

**What 17Lands CAN validate:** Turn-range effectiveness (early/mid/late), game-state correlation (win rate when drawn while ahead/behind via life-total differentials), and card co-occurrence in winning decks.

### C2. 109K Cards Is Misleading

For interaction analysis, you care about unique oracle names (~30K), not total printings (109K). And you almost never need cross-set interactions:
- **Limited/Draft:** 250-300 cards per set. 300 x 300 = 90K potential edges, maybe 500-2000 meaningful.
- **Standard:** ~1500 cards. Tractable.
- **Modern:** ~15K cards. Needs caching but still feasible.

Scope interactions to a format or set. Don't try to build a universal 30K x 30K graph.

### C3. "Target Creature" Doesn't Mean "Interacts With Every Creature"

A card that says "destroy target creature" *can* target any creature, but that's a removal spell, not an "interaction" in the combo/synergy sense. The pattern system needs to distinguish between:
- **Mechanical targeting** — "this can legally target that" (removal, buffs)
- **Strategic synergy** — "these are better together than apart" (actual deck-building signal)

Most mechanical targeting creates *obvious* interactions that don't need to be stored. The interesting patterns are the non-obvious ones: "+1/+1 counters matter" cards that pair with proliferate, or sacrifice outlets that pair with death triggers.

### C4. Automatic Combo Detection Is Very Hard

"Goes infinite" is an emergent property of card combinations, not readable from individual cards. Kiki-Jiki + any creature with "untap target creature" goes infinite — but detecting this requires understanding that the loop terminates only when one of the pieces is removed. This is closer to formal verification than text parsing.

**Realistic approach:** Curate known combos manually or via LLM assistance, use classifiers for synergies and patterns, use 17Lands data for validation signals.

### C5. Graph Visualization at Scale

Displaying 1000+ nodes in a web graph is a UX problem. The 100-node BFS cap is good. For Tier 1 patterns, **don't expand to individual card nodes** — show the pattern as a single hub node labeled "All Creatures with Flying" rather than fanning out to 60 creature nodes. Pattern expansion should be optional at the API level.

### C6. Confidence Decay

Classifier-generated interactions become stale as new sets release and metagames shift. A "strong synergy" detected from 17Lands data in one set's draft format may not generalize. Consider: confidence scores should include a `valid_for` scope (set code, format, date range) rather than being universal.

### C7. What You're Not Modeling (and Might Want To)

- **Multi-card combos**: A+B might synergize, but only if you also have C. Three-card combos are common. The edge model is pairwise. Consider a `combo_group` concept for multi-card interactions.
- **Mana requirements**: Two cards that synergize but require WWWW and BBBB are never in the same deck. Color feasibility is a real-world filter on interactions.
- **Sideboard dynamics**: Some interactions only matter post-board (hate pieces).

---

## D. Implementation Phases

### Phase 1: Schema Foundation
- Add new columns to `user_card_interaction` (subtype, detected_by, confidence, win_rate_correlation, co_occurrence_count)
- Create `interaction_pattern` table
- Create `interaction_context` table
- Create `classifier_run` table
- Add MTGPhase, MTGGameState, MTGTurnRange enums
- Update API models and endpoints
- Add `matches_selector()` function
- Tests for all new models and the selector matcher

### Phase 2: Automated Classifiers
- Classifier base class in `src/mtgsim/classifiers/`
- Keyword synergy classifier
- Tribal classifier
- Removal/text-parse classifier
- Oracle text pattern classifier (ETB, death triggers, etc.)

### Phase 3: 17Lands Integration
- Co-occurrence analysis (cards appearing together in winning decks)
- Turn-range effectiveness mapping
- Game-state inference from life-total differentials
- Write validation signals back to edges

### Phase 4: Graph & Visualization API
- Pattern expansion endpoint for a given card pool
- Hub-node rendering for patterns
- Confidence/context filtering
- Cluster visualization

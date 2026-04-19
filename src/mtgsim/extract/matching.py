"""Pluggable text matching strategies for card identification.

Given raw OCR text from a card image, match it against known cards in the database.
Strategies are parameterized — preprocessing, scoring weights, and thresholds are
all configurable to support tuning as we gather real-world data.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel
from rapidfuzz import fuzz, process


class TextMatchResult(BaseModel):
    """A single candidate match with confidence breakdown."""

    card_name: str
    card_uuid: str
    score: float  # 0-100 overall confidence
    component_scores: dict[str, float] = {}  # per-field scores for debugging


class TextMatchParams(BaseModel):
    """Parameters for text matching — all configurable."""

    # Minimum overall score to consider a match
    threshold: float = 55.0

    # Weights for different card fields when computing overall score.
    # Oracle text is the most reliable OCR signal (card names are often
    # unreadable due to styled fonts over artwork).
    name_weight: float = 1.5
    type_line_weight: float = 1.5
    oracle_text_weight: float = 4.0
    combined_weight: float = 3.0  # full text vs concatenated card fields

    # Max candidates to return
    max_results: int = 5

    # Fuzzy scorer for name matching. partial_ratio works best for OCR
    # because card names appear as substrings in noisy text.
    name_scorer: str = "partial_ratio"

    # Fuzzy scorer for type line, oracle text, and combined matching.
    # token_set_ratio handles word-level overlap well.
    text_scorer: str = "token_set_ratio"


class CardRecord(BaseModel):
    """Flattened card data for matching. Built from DB once, reused across scans."""

    uuid: str
    name: str
    type_line: str = ""
    oracle_text: str = ""

    @property
    def combined_text(self) -> str:
        """All card text concatenated for full-text matching."""
        return f"{self.name} {self.type_line} {self.oracle_text}".strip()


class TextMatchStrategy(ABC):
    """Abstract base for text matching strategies."""

    @abstractmethod
    def match(
        self,
        ocr_text: str,
        cards: list[CardRecord],
        params: TextMatchParams | None = None,
    ) -> list[TextMatchResult]:
        """Match OCR text against a list of known cards.

        Args:
            ocr_text: Raw text extracted from card image.
            cards: Known cards to match against.
            params: Matching parameters. Uses defaults if None.

        Returns:
            Ranked list of matches (best first), filtered by threshold.
        """
        pass


# Map scorer names to rapidfuzz functions
_SCORERS = {
    "WRatio": fuzz.WRatio,
    "ratio": fuzz.ratio,
    "partial_ratio": fuzz.partial_ratio,
    "token_sort_ratio": fuzz.token_sort_ratio,
    "token_set_ratio": fuzz.token_set_ratio,
}


class FuzzyTextMatch(TextMatchStrategy):
    """Match OCR text against cards using rapidfuzz string similarity.

    Two-phase approach:
    1. Candidate generation — find cards whose oracle text or name partially
       matches any line of OCR text. This catches cards even when the name
       is unreadable (oracle text is the most reliable OCR signal).
    2. Multi-field scoring — score each candidate on name, type line, oracle
       text, and combined text. Weighted average determines the winner.
    """

    def match(
        self,
        ocr_text: str,
        cards: list[CardRecord],
        params: TextMatchParams | None = None,
    ) -> list[TextMatchResult]:
        params = params or TextMatchParams()
        name_scorer = _SCORERS.get(params.name_scorer, fuzz.partial_ratio)
        text_scorer = _SCORERS.get(params.text_scorer, fuzz.token_set_ratio)

        full_text = ocr_text
        lines = [ln.strip() for ln in ocr_text.strip().splitlines() if ln.strip()]

        # Phase 1: Candidate generation from multiple signals
        # Build lookup structures
        name_to_cards: dict[str, list[CardRecord]] = {}
        for c in cards:
            name_to_cards.setdefault(c.name, []).append(c)

        candidate_uuids: set[str] = set()

        # 1a. Name matching — try each OCR line as a potential card name
        name_list = [c.name for c in cards]
        candidate_lines = lines + [full_text] if lines else [full_text]
        for line in candidate_lines:
            if len(line) < 3:
                continue
            hits = process.extract(line, name_list, scorer=name_scorer, limit=params.max_results)
            for cand_name, score, _ in hits:
                if score >= 70:
                    for c in name_to_cards.get(cand_name, []):
                        candidate_uuids.add(c.uuid)

        # 1b. Oracle text matching — compare full OCR text against oracle texts
        oracle_list = [c.oracle_text for c in cards if c.oracle_text]
        oracle_to_cards: dict[str, list[CardRecord]] = {}
        for c in cards:
            if c.oracle_text:
                oracle_to_cards.setdefault(c.oracle_text, []).append(c)

        oracle_hits = process.extract(full_text, oracle_list, scorer=text_scorer, limit=params.max_results * 3)
        for oracle_text_hit, score, _ in oracle_hits:
            if score >= 50:
                for c in oracle_to_cards.get(oracle_text_hit, []):
                    candidate_uuids.add(c.uuid)

        # Phase 2: Multi-field scoring of all candidates
        card_by_uuid = {c.uuid: c for c in cards}
        results = []

        for uuid in candidate_uuids:
            card = card_by_uuid.get(uuid)
            if not card:
                continue

            component_scores: dict[str, float] = {}
            total_weight = 0.0
            weighted_sum = 0.0

            # Name score — best across all OCR lines
            best_name = 0.0
            for line in candidate_lines:
                if len(line) >= 3:
                    s = name_scorer(line, card.name)
                    if s > best_name:
                        best_name = s
            component_scores["name"] = best_name
            weighted_sum += best_name * params.name_weight
            total_weight += params.name_weight

            # Type line score
            if card.type_line:
                type_score = text_scorer(full_text, card.type_line)
                component_scores["type_line"] = type_score
                weighted_sum += type_score * params.type_line_weight
                total_weight += params.type_line_weight

            # Oracle text score — strongest signal
            if card.oracle_text:
                oracle_score = text_scorer(full_text, card.oracle_text)
                component_scores["oracle_text"] = oracle_score
                weighted_sum += oracle_score * params.oracle_text_weight
                total_weight += params.oracle_text_weight

            # Combined text score — full OCR vs all card text concatenated
            combined_score = text_scorer(full_text, card.combined_text)
            component_scores["combined"] = combined_score
            weighted_sum += combined_score * params.combined_weight
            total_weight += params.combined_weight

            overall = weighted_sum / total_weight if total_weight > 0 else 0

            if overall >= params.threshold:
                results.append(
                    TextMatchResult(
                        card_name=card.name,
                        card_uuid=card.uuid,
                        score=round(overall, 2),
                        component_scores={k: round(v, 2) for k, v in component_scores.items()},
                    )
                )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[: params.max_results]

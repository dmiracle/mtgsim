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
    threshold: float = 60.0

    # Weights for different card fields when computing overall score.
    # Higher weight = more influence on final score.
    name_weight: float = 3.0
    type_line_weight: float = 1.0
    oracle_text_weight: float = 2.0

    # Max candidates to return
    max_results: int = 5

    # Fuzzy scorer for name matching. partial_ratio works best for OCR
    # because card names appear as substrings in noisy text.
    name_scorer: str = "partial_ratio"

    # Fuzzy scorer for type line and oracle text matching.
    # token_set_ratio handles word-level overlap well.
    text_scorer: str = "token_set_ratio"


class CardRecord(BaseModel):
    """Flattened card data for matching. Built from DB once, reused across scans."""

    uuid: str
    name: str
    type_line: str = ""
    oracle_text: str = ""


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

    Scores each card field independently, then computes a weighted average.
    The OCR text is compared against card name, type line, and oracle text —
    whichever fields are available.
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

        # Try every OCR line as a potential card name — the name could be
        # on any line due to OCR noise, headers, or partial reads.
        lines = [ln.strip() for ln in ocr_text.strip().splitlines() if ln.strip()]
        # Also try the full text (for single-line OCR results)
        candidate_lines = lines + [full_text] if lines else [full_text]

        # Build lookup structures once
        name_list = [c.name for c in cards]
        name_to_cards: dict[str, list[CardRecord]] = {}
        for c in cards:
            name_to_cards.setdefault(c.name, []).append(c)

        # For each line, get the best name matches from rapidfuzz.
        # Track the best name score per card across all lines.
        best_name_scores: dict[str, float] = {}  # card_name -> best score
        for line in candidate_lines:
            if len(line) < 3:
                continue
            candidates = process.extract(
                line,
                name_list,
                scorer=name_scorer,
                limit=params.max_results * 2,
            )
            for cand_name, score, _ in candidates:
                if score > best_name_scores.get(cand_name, 0):
                    best_name_scores[cand_name] = score

        # Score and rank candidates using weighted multi-field matching
        results = []
        seen_uuids = set()

        for cand_name, name_score in sorted(best_name_scores.items(), key=lambda x: x[1], reverse=True):
            for card in name_to_cards.get(cand_name, []):
                if card.uuid in seen_uuids:
                    continue
                seen_uuids.add(card.uuid)

                component_scores = {"name": name_score}
                total_weight = params.name_weight
                weighted_sum = name_score * params.name_weight

                # Score type line match against full OCR text
                if card.type_line:
                    type_score = text_scorer(full_text, card.type_line)
                    component_scores["type_line"] = type_score
                    weighted_sum += type_score * params.type_line_weight
                    total_weight += params.type_line_weight

                # Score oracle text match against full OCR text
                if card.oracle_text:
                    oracle_score = text_scorer(full_text, card.oracle_text)
                    component_scores["oracle_text"] = oracle_score
                    weighted_sum += oracle_score * params.oracle_text_weight
                    total_weight += params.oracle_text_weight

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

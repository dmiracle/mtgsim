import { SITUATIONS, type Scores, type Situation } from "../types";

interface EvaluationPanelProps {
  scores: Scores;
  onRate: (situation: Situation, stars: number | null) => void;
}

const STARS = [1, 2, 3, 4, 5];

// One row of 1-5 stars per game state. Tapping the current rating clears it.
export function EvaluationPanel({ scores, onRate }: EvaluationPanelProps) {
  return (
    <div className="space-y-1">
      {SITUATIONS.map(({ key, label }) => (
        <div key={key} className="flex items-center gap-2">
          <span className="w-24 shrink-0 text-sm text-muted">{label}</span>
          <div className="grid flex-1 grid-cols-5 gap-1">
            {STARS.map((n) => (
              <button
                key={n}
                aria-label={`${label} ${n} star${n > 1 ? "s" : ""}`}
                onClick={() => onRate(key, scores[key] === n ? null : n)}
                className={`min-h-9 rounded-lg text-xl leading-none ${
                  (scores[key] ?? 0) >= n ? "text-accent" : "text-line"
                }`}
              >
                ★
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

import { useRef } from "react";
import type { Card, Scores, Situation } from "../types";
import { CardView } from "./CardView";
import { EvaluationPanel } from "./EvaluationPanel";
import { GradeBar } from "./GradeBar";

interface ReviewScreenProps {
  card: Card | undefined;
  index: number;
  total: number;
  summary: string;
  onSeek: (index: number) => void;
  onExit: () => void;
  grading?: { listName: string; grade: string | undefined; onGrade: (tier: string | null) => void };
  evaluating?: { setName: string; scores: Scores; onRate: (situation: Situation, stars: number | null) => void };
}

const SWIPE_PX = 50;

export function ReviewScreen({ card, index, total, summary, onSeek, onExit, grading, evaluating }: ReviewScreenProps) {
  const touchStart = useRef<{ x: number; y: number } | null>(null);
  const prev = () => index > 0 && onSeek(index - 1);
  const next = () => index < total - 1 && onSeek(index + 1);

  const onTouchEnd = (e: React.TouchEvent) => {
    if (!touchStart.current) return;
    const dx = e.changedTouches[0].clientX - touchStart.current.x;
    const dy = e.changedTouches[0].clientY - touchStart.current.y;
    touchStart.current = null;
    if (Math.abs(dx) < SWIPE_PX || Math.abs(dx) < Math.abs(dy)) return;
    if (dx < 0) next();
    else prev();
  };

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-10 space-y-2 border-b border-line bg-bg/95 px-4 pt-[max(0.75rem,env(safe-area-inset-top))] pb-2 backdrop-blur">
        <div className="flex items-center gap-3">
          <button onClick={onExit} className="min-h-10 rounded-lg border border-line px-3 text-sm">
            ‹ Filters
          </button>
          <p className="flex-1 truncate text-xs text-muted">{summary}</p>
          <span className="font-mono text-sm tabular-nums">
            {total ? index + 1 : 0} / {total}
          </span>
        </div>
        <input
          type="range"
          aria-label="Position"
          min={0}
          max={Math.max(total - 1, 0)}
          value={index}
          onChange={(e) => onSeek(Number(e.target.value))}
          className="w-full accent-accent"
        />
      </header>

      <main
        className={`flex-1 px-4 pt-4 ${grading && evaluating ? "pb-[30rem]" : evaluating ? "pb-80" : grading ? "pb-60" : "pb-28"}`}
        onTouchStart={(e) => (touchStart.current = { x: e.touches[0].clientX, y: e.touches[0].clientY })}
        onTouchEnd={onTouchEnd}
      >
        {card ? (
          <CardView card={card} />
        ) : (
          <p className="pt-20 text-center text-muted">{total === 0 ? "No cards match these filters." : "Loading…"}</p>
        )}
      </main>

      <nav className="fixed inset-x-0 bottom-0 space-y-2 border-t border-line bg-bg/95 px-4 pt-2 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur">
        {evaluating && card && (
          <>
            <p className="truncate text-xs text-muted">Evaluating into {evaluating.setName}</p>
            <EvaluationPanel scores={evaluating.scores} onRate={evaluating.onRate} />
          </>
        )}
        {grading && card && (
          <>
            <p className="truncate text-xs text-muted">Grading into {grading.listName}</p>
            <GradeBar grade={grading.grade} onGrade={grading.onGrade} />
          </>
        )}
        <div className="flex gap-3">
          <button
            onClick={prev}
            disabled={index <= 0}
            className="min-h-12 flex-1 rounded-xl border border-line text-lg disabled:opacity-30"
          >
            ‹ Prev
          </button>
          <button
            onClick={next}
            disabled={index >= total - 1}
            className="min-h-12 flex-1 rounded-xl bg-accent text-lg font-semibold text-bg disabled:opacity-30"
          >
            Next ›
          </button>
        </div>
      </nav>
    </div>
  );
}

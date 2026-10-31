import { TIERS } from "../filters";

const LETTER_COLOR: Record<string, string> = {
  A: "bg-grade-a",
  B: "bg-grade-b",
  C: "bg-grade-c",
  D: "bg-grade-d",
  F: "bg-grade-f",
};

interface GradeBarProps {
  grade: string | undefined;
  onGrade: (tier: string | null) => void;
}

export function GradeBar({ grade, onGrade }: GradeBarProps) {
  return (
    <div className="grid grid-cols-7 gap-1.5">
      {TIERS.map((t) => (
        <button
          key={t}
          onClick={() => onGrade(t)}
          className={`min-h-10 rounded-lg text-sm font-bold ${
            grade === t ? `${LETTER_COLOR[t[0]]} text-bg` : "bg-surface text-fg"
          }`}
        >
          {t}
        </button>
      ))}
      <button
        onClick={() => onGrade(null)}
        disabled={!grade}
        aria-label="Clear grade"
        className="min-h-10 rounded-lg bg-surface text-muted disabled:opacity-30"
      >
        ✕
      </button>
    </div>
  );
}

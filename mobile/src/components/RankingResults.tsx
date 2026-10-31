import type { Card } from "../types";

export interface RankingRow {
  card: Card;
  inCycle: boolean;
  // true when nothing ranked so far separates this card from the next one
  undetermined: boolean;
}

export function RankingResults({ rows }: { rows: RankingRow[] }) {
  return (
    <ol className="divide-y divide-line">
      {rows.map((row, i) => (
        <li key={row.card.uuid} className="flex items-center gap-3 py-2">
          <span className="w-8 text-right font-mono text-sm text-muted tabular-nums">{i + 1}</span>
          <img src={row.card.image_url ?? ""} alt="" className="h-14 w-10 rounded bg-surface object-cover" />
          <div className="min-w-0 flex-1">
            <p className="truncate">{row.card.name}</p>
            <p className="text-xs text-muted">
              {row.inCycle && <span className="text-grade-f">in a conflict · </span>}
              {row.undetermined && "≈ next card not decided yet"}
            </p>
          </div>
        </li>
      ))}
    </ol>
  );
}

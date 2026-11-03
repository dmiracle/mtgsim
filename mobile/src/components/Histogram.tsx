import type { Bucket } from "../stats";

const PLOT_PX = 120;

// Vertical bars, one per bucket, count above each bar and the value below.
export function Histogram({ title, buckets }: { title: string; buckets: Bucket[] }) {
  const max = Math.max(1, ...buckets.map((b) => b.count));
  return (
    <section className="space-y-2">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">{title}</h2>
      {buckets.length === 0 ? (
        <p className="text-sm text-muted">None</p>
      ) : (
        <div className="flex gap-0.5 border-b border-line">
          {buckets.map((b) => (
            <div key={b.label} className="flex min-w-0 flex-1 flex-col items-center justify-end">
              <span className="text-xs tabular-nums text-muted">{b.count || ""}</span>
              <div
                className="w-full max-w-10 rounded-t bg-accent"
                style={{ height: (b.count / max) * PLOT_PX }}
              />
            </div>
          ))}
        </div>
      )}
      <div className="flex gap-0.5">
        {buckets.map((b) => (
          <span key={b.label} className="min-w-0 flex-1 truncate text-center text-xs tabular-nums">
            {b.label}
          </span>
        ))}
      </div>
    </section>
  );
}

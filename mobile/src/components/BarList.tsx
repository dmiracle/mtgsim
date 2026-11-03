import type { Bucket } from "../stats";

// Horizontal bars for categories: label left, bar scaled to the largest, count right.
export function BarList({ title, buckets }: { title: string; buckets: Bucket[] }) {
  const max = Math.max(1, ...buckets.map((b) => b.count));
  return (
    <section className="space-y-2">
      <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">{title}</h2>
      {buckets.length === 0 && <p className="text-sm text-muted">None</p>}
      <div className="space-y-0.5">
        {buckets.map((b) => (
          <div key={b.label} className="flex items-center gap-2 text-sm">
            <span className="w-24 shrink-0 truncate">{b.label}</span>
            <div className="flex-1">
              <div className="h-5 rounded-r bg-accent" style={{ width: `${(b.count / max) * 100}%` }} />
            </div>
            <span className="w-10 shrink-0 text-right tabular-nums text-muted">{b.count}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

import { Link } from "react-router-dom"
import HistogramChart from "../components/shared/HistogramChart"
import SetIcon from "../components/shared/SetIcon"
import { useHomeStats } from "../hooks/useStats"

export default function HomePage() {
  const { data, isLoading } = useHomeStats()

  if (isLoading) return <div className="text-[var(--color-text-muted)]">Loading...</div>
  if (!data) return <div className="text-[var(--color-text-muted)]">Failed to load stats</div>

  return (
    <div className="space-y-6 max-w-5xl">
      <h1 className="text-2xl font-bold">MTG Deck Viewer</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Decks", value: data.total_decks, to: "/decks" },
          { label: "Sets", value: data.total_sets, to: "/sets" },
          { label: "Cards", value: data.total_cards, to: "/cards" },
          { label: "Priced Cards", value: data.total_cards_with_prices, to: "/prices" },
        ].map((s) => (
          <Link
            key={s.label}
            to={s.to}
            className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4 hover:border-[var(--color-accent)] transition-colors"
          >
            <div className="text-2xl font-bold text-[var(--color-accent)]">{s.value.toLocaleString()}</div>
            <div className="text-sm text-[var(--color-text-secondary)]">{s.label}</div>
          </Link>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-3">Format Distribution</h2>
          <div className="space-y-1">
            {Object.entries(data.format_distribution)
              .sort(([, a], [, b]) => b - a)
              .map(([format, count]) => (
                <div key={format} className="flex items-center gap-2 text-sm">
                  <span className="w-24 text-[var(--color-text-secondary)] capitalize">{format}</span>
                  <div className="flex-1 h-4 bg-[var(--color-bg-primary)] rounded overflow-hidden">
                    <div
                      className="h-full bg-[var(--color-accent)] rounded"
                      style={{ width: `${(count / Math.max(...Object.values(data.format_distribution))) * 100}%` }}
                    />
                  </div>
                  <span className="w-8 text-right text-xs text-[var(--color-text-muted)]">{count}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-3">Price Distribution</h2>
          <HistogramChart data={data.price_histogram} />
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-3">Recent Sets</h2>
          <div className="space-y-2">
            {data.recent_sets.map((s) => (
              <Link
                key={s.code}
                to={`/sets/${s.code}`}
                className="flex items-center gap-2 text-sm hover:text-[var(--color-accent)]"
              >
                <SetIcon code={s.code} />
                <span>{s.name}</span>
                <span className="ml-auto text-xs text-[var(--color-text-muted)]">{s.release_date}</span>
              </Link>
            ))}
          </div>
        </div>

        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-3">Most Expensive Cards</h2>
          <div className="space-y-2">
            {data.most_expensive_cards.map((c, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="text-[var(--color-text-muted)] w-5">{i + 1}.</span>
                <SetIcon code={c.set_code} />
                <span className="flex-1 truncate">{c.name}</span>
                <span className="text-green-400">${c.price.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

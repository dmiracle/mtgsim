import type { HomeStats } from "@/types/api";
import { StatCard } from "@/components/StatCard/StatCard";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";
import { VBarChart } from "@/components/charts/VBarChart/VBarChart";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type HomePageProps = {
  stats: HomeStats;
  onSetClick: (code: string) => void;
};

export function HomePage({ stats, onSetClick }: HomePageProps) {
  const formatData = Object.entries(stats.format_distribution)
    .sort(([, a], [, b]) => b - a)
    .map(([label, value]) => ({ label, value }));

  const priceData = stats.price_histogram.map((h) => ({
    label: h.range,
    value: h.count,
  }));

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-text-primary">Dashboard</h2>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Decks" value={stats.total_decks} />
        <StatCard label="Total Sets" value={stats.total_sets} />
        <StatCard label="Total Cards" value={stats.total_cards.toLocaleString()} />
        <StatCard label="Cards with Prices" value={stats.total_cards_with_prices.toLocaleString()} />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <HBarChart title="Format Distribution" data={formatData} color="accent" animate={false} />
        <VBarChart title="Deck Price Distribution" data={priceData} color="success" height={220} animate={false} />
      </div>

      {/* Recent sets */}
      <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-medium text-text-secondary">Recent Sets</h3>
        <div className="space-y-1.5">
          {stats.recent_sets.map((s) => (
            <button
              key={s.code}
              onClick={() => onSetClick(s.code)}
              className="w-full flex items-center justify-between px-3 py-2 rounded hover:bg-bg-hover transition-colors"
            >
              <SetBadge code={s.code} name={s.name} size="sm" navigable />
              <span className="text-xs text-text-muted">{s.release_date}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

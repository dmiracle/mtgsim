import type { HomeStats } from "@/types/api";
import { StatCard } from "@/components/StatCard/StatCard";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";

type PriceExplorerProps = {
  stats: HomeStats;
  onCardClick: (name: string) => void;
};

export function PriceExplorer({ stats, onCardClick }: PriceExplorerProps) {
  const topCards = stats.most_expensive_cards.map((c) => ({
    label: c.name,
    value: c.price,
  }));

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <StatCard label="Cards with Prices" value={stats.total_cards_with_prices.toLocaleString()} />
        <StatCard label="Total Decks" value={stats.total_decks} />
        <StatCard label="Total Sets" value={stats.total_sets} />
      </div>

      {topCards.length > 0 && (
        <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
          <h3 className="text-sm font-medium text-text-secondary">Most Expensive Cards</h3>
          <HBarChart
            data={topCards}
            color="success"
            animate={false}
          />
          <div className="flex flex-wrap gap-1.5 pt-2 border-t border-border">
            {stats.most_expensive_cards.map((c) => (
              <button
                key={c.name}
                onClick={() => onCardClick(c.name)}
                className="text-xs px-2 py-1 rounded bg-bg-tertiary text-text-secondary hover:text-accent hover:border-accent border border-border transition-colors"
              >
                {c.name} · ${c.price}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

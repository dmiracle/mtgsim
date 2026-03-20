import type { DeckStats as DeckStatsType } from "@/types/api";
import { StatCard } from "@/components/StatCard/StatCard";
import { VBarChart } from "@/components/charts/VBarChart/VBarChart";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";
import { DonutChart } from "@/components/charts/DonutChart/DonutChart";
import { FormatLegalityBadges } from "@/components/FormatLegalityBadges/FormatLegalityBadges";

type DeckStatsProps = {
  stats: DeckStatsType;
  legality: Record<string, boolean>;
  price: { total: number; tcgplayer: number; cardkingdom: number; cardsphere: number; cardmarket: number; mtgo: number };
};

export function DeckStats({ stats, legality, price }: DeckStatsProps) {
  const manaCurveData = Object.entries(stats.mana_curve)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([label, value]) => ({ label, value }));

  const typeData = Object.entries(stats.type_distribution)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 6)
    .map(([label, value]) => ({ label, value }));

  const rarityData = Object.entries(stats.rarity_distribution)
    .map(([label, value]) => ({ label, value }));

  const colorData = Object.entries(stats.color_distribution)
    .map(([label, value]) => ({ label, value }));

  const colorMap: Record<string, string> = {
    W: "#f9faf4", U: "#0e68ab", B: "#150b00", R: "#d3202a", G: "#00733e", C: "#9ca3af",
  };

  const priceRows = [
    { label: "TCGplayer", value: price.tcgplayer },
    { label: "Card Kingdom", value: price.cardkingdom },
    { label: "Cardsphere", value: price.cardsphere },
    { label: "Cardmarket", value: price.cardmarket },
    { label: "MTGO", value: price.mtgo },
  ].filter((r) => r.value > 0);

  const legalityStrings = Object.fromEntries(
    Object.entries(legality).map(([k, v]) => [k, v ? "legal" : "not_legal"])
  );

  // Keyword data for horizontal bars
  const allKeywords = [
    ...Object.entries(stats.keywords.keyword_abilities).map(([k, v]) => ({ label: k, value: v })),
    ...Object.entries(stats.keywords.keyword_actions).map(([k, v]) => ({ label: k, value: v })),
    ...Object.entries(stats.keywords.ability_words).map(([k, v]) => ({ label: k, value: v })),
  ].sort((a, b) => b.value - a.value).slice(0, 10);

  return (
    <div className="space-y-4">
      {/* Summary cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Cards" value={stats.total_cards} />
        <StatCard label="Unique Cards" value={stats.unique_cards} />
        <StatCard label="Total Price" value={`$${price.total.toFixed(2)}`} />
        <StatCard label="Avg per Card" value={`$${(price.total / (stats.total_cards || 1)).toFixed(2)}`} />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <VBarChart title="Mana Curve" data={manaCurveData} color="accent" height={200} animate={false} />
        <DonutChart
          title="Color Distribution"
          data={colorData.map((d) => ({ ...d, color: colorMap[d.label] }))}
          size={180}
          showLegend
        />
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <HBarChart title="Card Types" data={typeData} color="success" maxBars={6} animate={false} />
        <DonutChart title="Rarity Breakdown" data={rarityData} size={180} showLegend />
      </div>

      {/* Price breakdown */}
      {priceRows.length > 0 && (
        <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-2">
          <h3 className="text-sm font-medium text-text-secondary">Price Breakdown</h3>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1">
            {priceRows.map((r) => (
              <div key={r.label} className="contents">
                <dt className="text-xs text-text-muted text-right">{r.label}</dt>
                <dd className="text-xs text-success font-medium">${r.value.toFixed(2)}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}

      {/* Keywords */}
      {allKeywords.length > 0 && (
        <HBarChart title="Top Keywords" data={allKeywords} color="warning" animate={false} />
      )}

      {/* Legality */}
      <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-medium text-text-secondary">Format Legality</h3>
        <FormatLegalityBadges legalities={legalityStrings} />
      </div>
    </div>
  );
}

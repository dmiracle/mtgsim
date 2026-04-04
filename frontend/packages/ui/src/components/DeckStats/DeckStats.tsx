import type { DeckStats as DeckStatsType, TagCount } from "@/types/api";
import { StatCard } from "@/components/StatCard/StatCard";
import { VBarChart } from "@/components/charts/VBarChart/VBarChart";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";
import { DonutChart } from "@/components/charts/DonutChart/DonutChart";
import { FormatLegalityBadges } from "@/components/FormatLegalityBadges/FormatLegalityBadges";

type DeckStatsProps = {
  stats: DeckStatsType;
  legality: Record<string, boolean>;
  price: { total: number; tcgplayer: number; cardkingdom: number; cardsphere: number; cardmarket: number; mtgo: number };
  tags?: TagCount[];
};

export function DeckStats({ stats, legality, price, tags = [] }: DeckStatsProps) {
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

  const keywordAbilities = Object.entries(stats.keywords.keyword_abilities)
    .sort(([, a], [, b]) => b - a).map(([label, value]) => ({ label, value }));
  const keywordActions = Object.entries(stats.keywords.keyword_actions)
    .sort(([, a], [, b]) => b - a).map(([label, value]) => ({ label, value }));
  const abilityWords = Object.entries(stats.keywords.ability_words)
    .sort(([, a], [, b]) => b - a).map(([label, value]) => ({ label, value }));

  const tagData = tags.slice(0, 20).map((t) => ({ label: t.tag, value: t.count }));

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

      {(keywordAbilities.length > 0 || keywordActions.length > 0 || abilityWords.length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {keywordAbilities.length > 0 && (
            <HBarChart title="Keyword Abilities" data={keywordAbilities} color="accent" maxBars={10} animate={false} />
          )}
          {keywordActions.length > 0 && (
            <HBarChart title="Keyword Actions" data={keywordActions} color="success" maxBars={10} animate={false} />
          )}
          {abilityWords.length > 0 && (
            <HBarChart title="Ability Words" data={abilityWords} color="danger" maxBars={10} animate={false} />
          )}
        </div>
      )}

      {/* Tags */}
      {tagData.length > 0 && (
        <HBarChart title="Oracle Tags" data={tagData} color="accent" maxBars={20} animate={false} />
      )}

      {/* Legality */}
      <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-medium text-text-secondary">Format Legality</h3>
        <FormatLegalityBadges legalities={legalityStrings} />
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import type { SetDetail, TagCount, CardSummary, Pagination as PaginationType } from "@/types/api";
import { StatCard } from "@/components/StatCard/StatCard";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";
import { DonutChart } from "@/components/charts/DonutChart/DonutChart";
import { CardFilterBar } from "@/components/CardFilterBar/CardFilterBar";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import { SetBadge } from "@/components/SetBadge/SetBadge";
import { RawJsonViewer } from "@/components/RawJsonViewer/RawJsonViewer";

export type SetCardSearchParams = {
  rarity?: string;
  colors?: string;
  type?: string;
  text?: string;
  tags?: string;
  format?: string;
  owns?: boolean;
  unique?: boolean;
  sort?: string;
  order?: string;
  price_mode?: string;
};

type SetDetailPageProps = {
  set: SetDetail;
  cards: CardSummary[];
  cardPagination: PaginationType;
  availableTags?: TagCount[];
  onBack: () => void;
  onCardClick: (uuid: string) => void;
  onSetClick: (code: string) => void;
  onCardPageChange: (page: number) => void;
  onCardFiltersChange?: (params: SetCardSearchParams) => void;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [],
  ownership: "all", sort: "number", order: "asc", unique: true, priceMode: "min",
};

export function SetDetailPage({ set, cards, cardPagination, availableTags = [], onBack, onCardClick, onSetClick, onCardPageChange, onCardFiltersChange }: SetDetailPageProps) {
  const [tab, setTab] = useState<"stats" | "cards">("stats");
  const [filters, setFilters] = useState(emptyFilters);
  const [formatFilter, setFormatFilter] = useState("");

  // Push filter changes to the route for server-side filtering
  useEffect(() => {
    if (!onCardFiltersChange) return;
    const params: SetCardSearchParams = {};
    if (filters.text) params.text = filters.text;
    if (filters.colors.length) params.colors = filters.colors.join("");
    if (filters.rarities.length) params.rarity = filters.rarities.join(",");
    if (filters.types.length) params.type = filters.types.join(",");
    if (filters.tags.length) params.tags = filters.tags.join(",");
    if (formatFilter) params.format = formatFilter;
    if (filters.ownership === "owned") params.owns = true;
    if (filters.ownership === "not_owned") params.owns = false;
    if (filters.unique) params.unique = true;
    if (filters.sort !== "number") params.sort = filters.sort;
    if (filters.order !== "asc") params.order = filters.order;
    if (filters.priceMode !== "min") params.price_mode = filters.priceMode;
    onCardFiltersChange(params);
  }, [filters, formatFilter, onCardFiltersChange]);

  const rarityData = Object.entries(set.stats.rarity_count).map(([label, value]) => ({ label, value }));

  const allKeywords = [
    ...Object.entries(set.stats.keywords.keyword_abilities),
    ...Object.entries(set.stats.keywords.keyword_actions),
    ...Object.entries(set.stats.keywords.ability_words),
  ].sort(([, a], [, b]) => b - a).slice(0, 10).map(([label, value]) => ({ label, value }));

  const tabs = [
    { id: "stats" as const, label: "Statistics" },
    { id: "cards" as const, label: `Cards (${cardPagination.total})` },
  ];

  return (
    <div className="space-y-4">
      <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>

      {/* Header */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <SetBadge code={set.meta.code} name={set.meta.name} size="lg" />
        <div className="min-w-0">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary truncate">{set.meta.name}</h2>
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 text-xs text-text-muted mt-0.5">
            <span className="capitalize">{set.meta.type}</span>
            <span>·</span>
            <span>{set.meta.release_date}</span>
            {set.meta.block && <><span>·</span><span>{set.meta.block}</span></>}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
              tab === t.id ? "border-accent text-accent" : "border-transparent text-text-muted hover:text-text-secondary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "stats" && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <StatCard label="Base Size" value={set.meta.base_set_size} />
            <StatCard label="Total Size" value={set.meta.total_set_size} subtitle={`${set.meta.total_set_size - set.meta.base_set_size} variants`} />
            <StatCard label="Total Price" value={`$${set.stats.price.total.toFixed(0)}`} />
            <StatCard label="Avg per Card" value={`$${(set.stats.price.total / (set.meta.base_set_size || 1)).toFixed(2)}`} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <DonutChart title="Rarity Breakdown" data={rarityData} size={180} showLegend />
            {allKeywords.length > 0 && (
              <HBarChart title="Top Keywords" data={allKeywords} color="warning" animate={false} />
            )}
          </div>

          <RawJsonViewer data={set} title="Set JSON" />
        </div>
      )}

      {tab === "cards" && (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={formatFilter}
              onChange={(e) => setFormatFilter(e.target.value)}
              className="bg-bg-secondary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
            >
              <option value="">All Formats</option>
              {["standard", "pioneer", "modern", "legacy", "vintage", "commander", "brawl", "historic", "pauper"].map((f) => (
                <option key={f} value={f} className="capitalize">{f}</option>
              ))}
            </select>
            {formatFilter && (
              <span className="text-xs text-text-muted">
                {cardPagination.total} cards legal in <span className="capitalize text-text-secondary">{formatFilter}</span>
              </span>
            )}
          </div>
          <CardFilterBar
            filters={filters}
            onChange={setFilters}
            availableTags={availableTags}
            resultCount={cardPagination.total}
            showUnique
            sortOptions={[
              { value: "number", label: "Collector #" },
              { value: "name", label: "Name" },
              { value: "mana_value", label: "Mana Value" },
              { value: "rarity", label: "Rarity" },
              { value: "price", label: "Price" },
            ]}
          />
          <CardGrid
            cards={cards}
            pagination={cardPagination}
            onCardClick={onCardClick}
            onSetClick={onSetClick}
            onPageChange={onCardPageChange}
          />
        </div>
      )}
    </div>
  );
}

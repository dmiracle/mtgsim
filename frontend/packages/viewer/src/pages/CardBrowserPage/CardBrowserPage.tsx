import { useState, useEffect, useMemo } from "react";
import type { CardSummary, Pagination as PaginationType, TagCount, SetSummary, KeywordFrequencies, CardStatsResponse, AggregateVectorResponse } from "@/types/api";
import { VectorHeatmap } from "@/components/VectorHeatmap/VectorHeatmap";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { CardFilterBar } from "@/components/CardFilterBar/CardFilterBar";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import { CardTable } from "@/components/CardTable/CardTable";
import { KeywordCloud } from "@/components/KeywordCloud/KeywordCloud";
import { VBarChart } from "@/components/charts/VBarChart/VBarChart";
import { DonutChart } from "@/components/charts/DonutChart/DonutChart";
import { StatCard } from "@/components/StatCard/StatCard";

export type CardSearchParams = {
  q?: string;
  text?: string;
  format?: string;
  sets?: string;
  colors?: string;
  rarity?: string;
  type?: string;
  tags?: string;
  keywords?: string;
  mana_value?: string;
  owns?: boolean;
  unique?: boolean;
  sort?: string;
  order?: string;
  price_mode?: string;
};

type CardBrowserPageProps = {
  cards: CardSummary[];
  cardStats?: CardStatsResponse;
  pagination: PaginationType;
  availableTags: TagCount[];
  availableSets?: SetSummary[];
  onSetSearch?: (query: string) => void;
  keywordFrequencies: KeywordFrequencies;
  pinnedIds: Set<string>;
  onCardClick: (uuid: string) => void;
  onSetClick: (code: string) => void;
  onPin: (uuid: string) => void;
  onAddToDeck: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onPageChange: (page: number) => void;
  onSearch: (params: CardSearchParams) => void;
  aggregateVector?: AggregateVectorResponse;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [], manaValue: [],
  ownership: "all", sort: "name", order: "asc", unique: false, priceMode: "min", subtype: "", sets: [], formats: [],
};

export function CardBrowserPage({
  cards,
  cardStats,
  pagination,
  availableTags,
  availableSets,
  onSetSearch,
  keywordFrequencies,
  pinnedIds,
  onCardClick,
  onSetClick,
  onPin,
  onAddToDeck,
  onAddToCollection,
  onPageChange,
  onSearch,
  aggregateVector,
}: CardBrowserPageProps) {
  const [nameSearch, setNameSearch] = useState("");
  const [formatFilter, setFormatFilter] = useState("");
  const [setFilter, setSetFilter] = useState("");
  const [filters, setFilters] = useState(emptyFilters);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

  const hasActiveFilter = !!(nameSearch || formatFilter || setFilter || filters.text || filters.colors.length || filters.rarities.length || filters.types.length || filters.subtype || filters.sets.length || filters.formats.length || filters.tags.length || filters.manaValue.length || selectedKeywords.length);

  // Build and emit search params whenever any filter changes
  useEffect(() => {
    const params: CardSearchParams = {};
    if (nameSearch) params.q = nameSearch;
    if (filters.text) params.text = filters.text;
    if (formatFilter) params.format = formatFilter;
    if (setFilter) params.sets = setFilter;
    if (filters.colors.length) params.colors = filters.colors.join("");
    if (filters.rarities.length) params.rarity = filters.rarities.join(",");
    if (filters.types.length) params.type = filters.types.join(",");
    if (filters.subtype) params.type = [filters.types.join(","), filters.subtype].filter(Boolean).join(",");
    if (filters.sets.length) params.sets = filters.sets.join(",");
    if (filters.formats.length) params.format = filters.formats.join(",");
    if (filters.tags.length) params.tags = filters.tags.join(",");
    if (selectedKeywords.length) params.keywords = selectedKeywords.join(",");
    if (filters.manaValue.length) params.mana_value = filters.manaValue.join(",");
    if (filters.ownership === "owned") params.owns = true;
    if (filters.ownership === "not_owned") params.owns = false;
    if (filters.unique) params.unique = true;
    if (filters.sort !== "name") params.sort = filters.sort;
    if (filters.order !== "asc") params.order = filters.order;
    if (filters.priceMode !== "min") params.price_mode = filters.priceMode;
    onSearch(params);
  }, [nameSearch, formatFilter, setFilter, filters, selectedKeywords, onSearch]);

  function toggleKeyword(kw: string) {
    setSelectedKeywords((prev) =>
      prev.includes(kw) ? prev.filter((k) => k !== kw) : [...prev, kw]
    );
  }

  // Secondary sort by name — only breaks ties within identical primary sort values
  const sortedCards = useMemo(() => {
    if (filters.sort === "name") return cards;
    const key = filters.sort as keyof CardSummary;
    const dir = filters.order === "desc" ? -1 : 1;
    return [...cards].sort((a, b) => {
      const av = a[key], bv = b[key];
      if (av !== bv) {
        if (typeof av === "number" && typeof bv === "number") return (av - bv) * dir;
        return String(av).localeCompare(String(bv)) * dir;
      }
      return a.name.localeCompare(b.name);
    });
  }, [cards, filters.sort, filters.order]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-text-primary">Cards</h2>

      {/* Top search bar */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <div className="flex-1 min-w-[150px]">
          <SearchInput value={nameSearch} placeholder="Search cards by name..." onChange={setNameSearch} />
        </div>
        <select
          value={formatFilter}
          onChange={(e) => setFormatFilter(e.target.value)}
          className="bg-bg-secondary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
        >
          <option value="">All Formats</option>
          {["standard", "pioneer", "modern", "legacy", "vintage", "commander", "pauper"].map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <input
          type="text"
          value={setFilter}
          onChange={(e) => setSetFilter(e.target.value)}
          placeholder="Set codes"
          className="w-24 sm:w-28 bg-bg-secondary border border-border rounded px-2 py-1.5 text-xs text-text-secondary placeholder-text-muted focus:outline-none focus:border-accent"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-4">
        {/* Main content */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <CardFilterBar
                filters={filters}
                onChange={setFilters}
                availableTags={availableTags}
                availableSets={availableSets}
                onSetSearch={onSetSearch}
                resultCount={pagination.total}
                showUnique
              />
            </div>
          </div>

          {/* View toggle */}
          <div className="flex items-center justify-end gap-1">
            <button
              onClick={() => setViewMode("grid")}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                viewMode === "grid"
                  ? "bg-accent text-white"
                  : "bg-bg-secondary border border-border text-text-muted hover:text-text-secondary"
              }`}
              title="Grid view"
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode("table")}
              className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                viewMode === "table"
                  ? "bg-accent text-white"
                  : "bg-bg-secondary border border-border text-text-muted hover:text-text-secondary"
              }`}
              title="Table view"
            >
              Table
            </button>
          </div>

          {!hasActiveFilter ? (
            <div className="flex items-center justify-center py-16 text-text-muted">
              Enter a search term or select a filter to browse cards
            </div>
          ) : viewMode === "grid" ? (
            <CardGrid
              cards={sortedCards}
              pagination={pagination}
              pinnedIds={pinnedIds}
              onCardClick={onCardClick}
              onSetClick={onSetClick}
              onPin={onPin}
              onAddToDeck={onAddToDeck}
              onAddToCollection={onAddToCollection}
              onPageChange={onPageChange}
            />
          ) : (
            <CardTable
              cards={sortedCards}
              pagination={pagination}
              pinnedIds={pinnedIds}
              onCardClick={onCardClick}
              onSetClick={onSetClick}
              onPin={onPin}
              onPageChange={onPageChange}
            />
          )}
        </div>

        {/* Sidebar: stats + keywords */}
        <div className="space-y-4">
          {hasActiveFilter && aggregateVector && (
            <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-2">
              <h3 className="text-sm font-medium text-text-secondary">Collection Fingerprint</h3>
              <VectorHeatmap
                vector={aggregateVector.vector}
                featureNames={aggregateVector.dimension_names}
                label={`${aggregateVector.card_count} cards`}
                size="sm"
              />
            </div>
          )}
          {hasActiveFilter && cardStats && (
            <CardResultStats stats={cardStats} />
          )}
          <KeywordCloud
            frequencies={keywordFrequencies}
            selectedKeywords={selectedKeywords}
            onToggleKeyword={toggleKeyword}
          />
        </div>
      </div>
    </div>
  );
}

// --- Stats from /api/cards/stats endpoint ---

function CardResultStats({ stats }: { stats: CardStatsResponse }) {
  const manaCurveData = Object.entries(stats.mana_curve)
    .sort(([a], [b]) => Number(a) - Number(b))
    .map(([label, value]) => ({ label, value }));

  const typeData = Object.entries(stats.type_distribution)
    .sort(([, a], [, b]) => b - a)
    .map(([label, value]) => ({ label, value }));

  const rarityData = Object.entries(stats.rarity_distribution)
    .map(([label, value]) => ({ label, value }));

  const colorMap: Record<string, string> = {
    W: "#f9faf4", U: "#0e68ab", B: "#150b00", R: "#d3202a", G: "#00733e", C: "#9ca3af",
  };
  const colorData = Object.entries(stats.color_distribution)
    .map(([label, value]) => ({ label, value, color: colorMap[label] ?? "#9ca3af" }));

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <StatCard label="Total" value={stats.total.toLocaleString()} />
        <StatCard label="Avg Price" value={stats.price_stats.average > 0 ? `$${stats.price_stats.average.toFixed(2)}` : "—"} />
      </div>

      {manaCurveData.length > 0 && (
        <VBarChart title="Mana Curve" data={manaCurveData} color="accent" height={120} animate={false} />
      )}

      {colorData.length > 0 && (
        <DonutChart title="Colors" data={colorData} size={140} showLegend animate={false} />
      )}

      {rarityData.length > 0 && (
        <DonutChart title="Rarity" data={rarityData} size={140} showLegend animate={false} />
      )}

      {typeData.length > 0 && (
        <DonutChart title="Types" data={typeData} size={140} showLegend animate={false} />
      )}
    </div>
  );
}

import { useState, useEffect } from "react";
import type { CardSummary, Pagination as PaginationType, TagCount, KeywordFrequencies } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { CardFilterBar } from "@/components/CardFilterBar/CardFilterBar";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import { CardTable } from "@/components/CardTable/CardTable";
import { KeywordCloud } from "@/components/KeywordCloud/KeywordCloud";

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
  owns?: boolean;
  unique?: boolean;
  sort?: string;
  order?: string;
  price_mode?: string;
};

type CardBrowserPageProps = {
  cards: CardSummary[];
  pagination: PaginationType;
  availableTags: TagCount[];
  keywordFrequencies: KeywordFrequencies;
  pinnedIds: Set<string>;
  onCardClick: (uuid: string) => void;
  onSetClick: (code: string) => void;
  onPin: (uuid: string) => void;
  onAddToDeck: (uuid: string) => void;
  onPageChange: (page: number) => void;
  onSearch: (params: CardSearchParams) => void;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [],
  ownership: "all", sort: "name", order: "asc", unique: false, priceMode: "min",
};

export function CardBrowserPage({
  cards,
  pagination,
  availableTags,
  keywordFrequencies,
  pinnedIds,
  onCardClick,
  onSetClick,
  onPin,
  onAddToDeck,
  onPageChange,
  onSearch,
}: CardBrowserPageProps) {
  const [nameSearch, setNameSearch] = useState("");
  const [formatFilter, setFormatFilter] = useState("");
  const [setFilter, setSetFilter] = useState("");
  const [filters, setFilters] = useState(emptyFilters);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");

  const hasActiveFilter = !!(nameSearch || formatFilter || setFilter || filters.text || filters.colors.length || filters.rarities.length || filters.types.length || filters.tags.length || selectedKeywords.length);

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
    if (filters.tags.length) params.tags = filters.tags.join(",");
    if (selectedKeywords.length) params.keywords = selectedKeywords.join(",");
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
              cards={cards}
              pagination={pagination}
              pinnedIds={pinnedIds}
              onCardClick={onCardClick}
              onSetClick={onSetClick}
              onPin={onPin}
              onAddToDeck={onAddToDeck}
              onPageChange={onPageChange}
            />
          ) : (
            <CardTable
              cards={cards}
              pagination={pagination}
              pinnedIds={pinnedIds}
              onCardClick={onCardClick}
              onSetClick={onSetClick}
              onPin={onPin}
              onPageChange={onPageChange}
            />
          )}
        </div>

        {/* Keyword sidebar */}
        <div className="space-y-4">
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

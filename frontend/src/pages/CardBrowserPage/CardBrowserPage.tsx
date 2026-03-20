import { useState } from "react";
import type { CardSummary, Pagination as PaginationType, TagCount, KeywordFrequencies } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { CardFilterBar } from "@/components/CardFilterBar/CardFilterBar";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import { KeywordCloud } from "@/components/KeywordCloud/KeywordCloud";

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
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [],
  ownership: "all", sort: "name", order: "asc", unique: false,
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
}: CardBrowserPageProps) {
  const [nameSearch, setNameSearch] = useState("");
  const [formatFilter, setFormatFilter] = useState("");
  const [setFilter, setSetFilter] = useState("");
  const [filters, setFilters] = useState(emptyFilters);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);

  const hasActiveFilter = !!(nameSearch || formatFilter || setFilter || filters.text || filters.colors.length || filters.rarities.length || filters.types.length || filters.tags.length || selectedKeywords.length);

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
          <CardFilterBar
            filters={filters}
            onChange={setFilters}
            availableTags={availableTags}
            resultCount={pagination.total}
            showUnique
          />

          {!hasActiveFilter ? (
            <div className="flex items-center justify-center py-16 text-text-muted">
              Enter a search term or select a filter to browse cards
            </div>
          ) : (
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

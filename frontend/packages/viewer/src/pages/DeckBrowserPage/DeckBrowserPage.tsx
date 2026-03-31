import { useState } from "react";
import type { DeckSummary, Pagination as PaginationType } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { ColorIdentityPicker } from "@/components/ColorIdentityPicker/ColorIdentityPicker";
import { SortSelect } from "@/components/SortSelect/SortSelect";
import { Pagination } from "@/components/Pagination/Pagination";
import { DeckListItem } from "@/components/DeckListItem/DeckListItem";

type DeckBrowserPageProps = {
  decks: DeckSummary[];
  pagination: PaginationType;
  availableFormats: string[];
  availableSources: string[];
  onDeckClick: (file: string) => void;
  onPageChange: (page: number) => void;
  onCreateDeck: () => void;
  onImportDeck: () => void;
};

const SORT_OPTIONS = [
  { value: "name", label: "Name" },
  { value: "release_date", label: "Release Date" },
  { value: "card_count", label: "Card Count" },
];


export function DeckBrowserPage({
  decks,
  pagination,
  availableFormats,
  availableSources,
  onDeckClick,
  onPageChange,
  onCreateDeck,
  onImportDeck,
}: DeckBrowserPageProps) {
  const [search, setSearch] = useState("");
  const [format, setFormat] = useState("");
  const [source, setSource] = useState("");
  const [colors, setColors] = useState<string[]>([]);
  const [sort, setSort] = useState("name");
  const [order, setOrder] = useState<"asc" | "desc">("asc");

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-text-primary">Decks</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={onImportDeck}
            className="text-xs font-medium px-3 py-1.5 rounded border border-border text-text-secondary hover:border-accent hover:text-accent transition-colors"
          >
            Import
          </button>
          <button
            onClick={onCreateDeck}
            className="text-xs font-medium px-3 py-1.5 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
          >
            + New Deck
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-bg-secondary border border-border rounded-lg p-3 sm:p-4 space-y-3">
        <div className="flex flex-wrap items-center gap-2 sm:gap-3">
          <div className="flex-1 min-w-[150px]">
            <SearchInput value={search} placeholder="Search decks..." onChange={setSearch} />
          </div>
          <SortSelect options={SORT_OPTIONS} sort={sort} order={order} onSortChange={setSort} onOrderChange={setOrder} />
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Color</span>
            <ColorIdentityPicker selected={colors} onChange={setColors} size="sm" />
          </div>

          <select
            value={format}
            onChange={(e) => setFormat(e.target.value)}
            className="bg-bg-tertiary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
          >
            <option value="">All Formats</option>
            {availableFormats.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>

          <select
            value={source}
            onChange={(e) => setSource(e.target.value)}
            className="bg-bg-tertiary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
          >
            <option value="">All Sources</option>
            {availableSources.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* Deck list */}
      {decks.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-text-muted">No decks found</div>
      ) : (
        <div className="space-y-2">
          {decks.map((d) => (
            <DeckListItem key={d.file} deck={d} onClick={onDeckClick} />
          ))}
        </div>
      )}

      <Pagination
        page={pagination.page}
        pages={pagination.pages}
        total={pagination.total}
        limit={pagination.limit}
        onPageChange={onPageChange}
      />
    </div>
  );
}

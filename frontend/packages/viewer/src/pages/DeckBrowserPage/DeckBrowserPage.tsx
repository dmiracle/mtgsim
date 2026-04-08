import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import type { DeckSummary, Pagination as PaginationType, AggregateVectorResponse } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { ColorIdentityPicker } from "@/components/ColorIdentityPicker/ColorIdentityPicker";
import { SortSelect } from "@/components/SortSelect/SortSelect";
import { Pagination } from "@/components/Pagination/Pagination";
import { DeckListItem } from "@/components/DeckListItem/DeckListItem";

export type DeckSearchParams = {
  q?: string;
  format?: string;
  source?: string;
  colors?: string;
  sort?: string;
  order?: string;
};

type DeckBrowserPageProps = {
  decks: DeckSummary[];
  pinnedDecks: DeckSummary[];
  pagination: PaginationType;
  availableFormats: string[];
  availableSources: string[];
  pinnedIds: Set<string>;
  onTogglePin: (file: string) => void;
  onDuplicateDeck: (file: string) => void;
  onDeleteDeck: (file: string) => void;
  deckVectors?: Record<string, AggregateVectorResponse>;
  onDeckClick: (file: string) => void;
  onPageChange: (page: number) => void;
  onSearch: (params: DeckSearchParams) => void;
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
  pinnedDecks,
  pagination,
  availableFormats,
  availableSources,
  pinnedIds,
  onTogglePin,
  onDuplicateDeck,
  onDeleteDeck,
  deckVectors,
  onDeckClick,
  onPageChange,
  onSearch,
  onCreateDeck,
  onImportDeck,
}: DeckBrowserPageProps) {
  const [sp, setSp] = useSearchParams();
  const search = sp.get("q") ?? "";
  const format = sp.get("format") ?? "";
  const source = sp.get("source") ?? "";
  const colorsParam = sp.get("colors") ?? "";
  const colors = colorsParam ? colorsParam.split("") : [];
  const sort = sp.get("sort") ?? "name";
  const order = (sp.get("order") ?? "asc") as "asc" | "desc";

  function update(patch: Record<string, string>) {
    setSp((prev) => {
      const next = new URLSearchParams(prev);
      for (const [k, v] of Object.entries(patch)) {
        if (v) next.set(k, v); else next.delete(k);
      }
      return next;
    }, { replace: true });
  }

  useEffect(() => {
    const params: DeckSearchParams = {};
    if (search) params.q = search;
    if (format) params.format = format;
    if (source) params.source = source;
    if (colorsParam) params.colors = colorsParam;
    if (sort !== "name") params.sort = sort;
    if (order !== "asc") params.order = order;
    onSearch(params);
  }, [search, format, source, colorsParam, sort, order, onSearch]);

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
            <SearchInput value={search} placeholder="Search decks..." onChange={(q) => update({ q })} />
          </div>
          <SortSelect options={SORT_OPTIONS} sort={sort} order={order} onSortChange={(sort) => update({ sort: sort === "name" ? "" : sort })} onOrderChange={(order) => update({ order: order === "asc" ? "" : order })} />
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2">
            <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Color</span>
            <ColorIdentityPicker selected={colors} onChange={(c) => update({ colors: c.join("") })} size="sm" />
          </div>

          <select
            value={format}
            onChange={(e) => update({ format: e.target.value })}
            className="bg-bg-tertiary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
          >
            <option value="">All Formats</option>
            {availableFormats.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>

          <select
            value={source}
            onChange={(e) => update({ source: e.target.value })}
            className="bg-bg-tertiary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
          >
            <option value="">All Sources</option>
            {availableSources.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      {/* Pinned decks */}
      {pinnedDecks.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs uppercase tracking-widest text-text-muted font-semibold">Pinned</h3>
          {pinnedDecks.map((d) => (
            <DeckListItem
              key={`pinned-${d.file}`}
              deck={d}
              pinned
              vector={deckVectors?.[d.file]?.vector}
              featureNames={deckVectors?.[d.file]?.dimension_names}
              onTogglePin={onTogglePin}
              onDuplicate={onDuplicateDeck}
              onDelete={onDeleteDeck}
              onClick={onDeckClick}
            />
          ))}
        </div>
      )}

      {/* Deck list */}
      {decks.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-text-muted">No decks found</div>
      ) : (
        <div className="space-y-2">
          {decks.filter((d) => !pinnedIds.has(d.uuid)).map((d) => (
            <DeckListItem
              key={d.file}
              deck={d}
              vector={deckVectors?.[d.file]?.vector}
              featureNames={deckVectors?.[d.file]?.dimension_names}
              onTogglePin={onTogglePin}
              onDuplicate={onDuplicateDeck}
              onDelete={onDeleteDeck}
              onClick={onDeckClick}
            />
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

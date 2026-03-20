import { useState } from "react";
import type { SetSummary, Pagination as PaginationType } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SortSelect } from "@/components/SortSelect/SortSelect";
import { Pagination } from "@/components/Pagination/Pagination";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type SetBrowserPageProps = {
  sets: SetSummary[];
  pagination: PaginationType;
  availableTypes: string[];
  onSetClick: (code: string) => void;
  onPageChange: (page: number) => void;
};

const SORT_OPTIONS = [
  { value: "release_date", label: "Release Date" },
  { value: "name", label: "Name" },
];

export function SetBrowserPage({ sets, pagination, availableTypes, onSetClick, onPageChange }: SetBrowserPageProps) {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [sort, setSort] = useState("release_date");
  const [order, setOrder] = useState<"asc" | "desc">("desc");

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-text-primary">Sets</h2>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <SearchInput value={search} placeholder="Search sets..." onChange={setSearch} />
        </div>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="bg-bg-secondary border border-border rounded px-2 py-1.5 text-xs text-text-secondary focus:outline-none focus:border-accent"
        >
          <option value="">All Types</option>
          {availableTypes.map((t) => <option key={t} value={t}>{t}</option>)}
        </select>
        <SortSelect options={SORT_OPTIONS} sort={sort} order={order} onSortChange={setSort} onOrderChange={setOrder} />
      </div>

      {/* Set list */}
      {sets.length === 0 ? (
        <div className="flex items-center justify-center py-16 text-text-muted">No sets found</div>
      ) : (
        <div className="space-y-1.5">
          {sets.map((s) => (
            <button
              key={s.code}
              onClick={() => onSetClick(s.code)}
              className="w-full flex items-center gap-4 px-4 py-3 rounded-lg border border-border bg-bg-secondary hover:bg-bg-hover hover:border-border-hover transition-colors text-left group"
            >
              <SetBadge code={s.code} name={s.name} size="md" />
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors truncate">
                  {s.name}
                </h3>
                <div className="flex items-center gap-2 mt-0.5 text-xs text-text-muted">
                  <span className="capitalize">{s.type}</span>
                  <span>·</span>
                  <span>{s.release_date}</span>
                  <span>·</span>
                  <span>{s.base_set_size} cards</span>
                  {s.total_set_size > s.base_set_size && (
                    <span className="text-text-muted">({s.total_set_size} total)</span>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      <Pagination page={pagination.page} pages={pagination.pages} total={pagination.total} limit={pagination.limit} onPageChange={onPageChange} />
    </div>
  );
}

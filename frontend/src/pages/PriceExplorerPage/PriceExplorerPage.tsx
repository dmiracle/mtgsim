import { useState } from "react";
import type { HomeStats, PriceSummary, Pagination as PaginationType } from "@/types/api";
import { PriceExplorer } from "@/components/PriceExplorer/PriceExplorer";
import { PriceListItem } from "@/components/PriceListItem/PriceListItem";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SortSelect } from "@/components/SortSelect/SortSelect";
import { Pagination } from "@/components/Pagination/Pagination";

type PriceExplorerPageProps = {
  stats: HomeStats;
  prices: PriceSummary[];
  pagination: PaginationType;
  onCardClick: (uuid: string) => void;
  onPageChange: (page: number) => void;
};

const SORT_OPTIONS = [
  { value: "average_usd", label: "Price (High)" },
  { value: "name", label: "Name" },
];

const PRICE_RANGES = [
  { label: "All", min: 0, max: 99999 },
  { label: "Under $1", min: 0, max: 1 },
  { label: "$1-$5", min: 1, max: 5 },
  { label: "$5-$20", min: 5, max: 20 },
  { label: "$20-$50", min: 20, max: 50 },
  { label: "$50+", min: 50, max: 99999 },
];

export function PriceExplorerPage({ stats, prices, pagination, onCardClick, onPageChange }: PriceExplorerPageProps) {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState("average_usd");
  const [order, setOrder] = useState<"asc" | "desc">("desc");
  const [priceRange, setPriceRange] = useState(0);

  const hasSearch = !!search;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-text-primary">Prices</h2>

      {/* Search bar */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <div className="flex-1 min-w-[150px]">
          <SearchInput value={search} placeholder="Search cards by name..." onChange={setSearch} />
        </div>
        <SortSelect options={SORT_OPTIONS} sort={sort} order={order} onSortChange={setSort} onOrderChange={setOrder} />
      </div>

      {/* Price range filters */}
      <div className="flex flex-wrap gap-1">
        {PRICE_RANGES.map((r, i) => (
          <button
            key={r.label}
            onClick={() => setPriceRange(i)}
            className={`px-3 py-1.5 text-xs font-medium rounded border transition-all ${
              priceRange === i
                ? "bg-accent text-white border-accent"
                : "bg-bg-secondary border-border text-text-muted hover:border-border-hover"
            }`}
          >
            {r.label}
          </button>
        ))}
      </div>

      {!hasSearch ? (
        <PriceExplorer stats={stats} onCardClick={() => {}} />
      ) : (
        <div className="space-y-4">
          {prices.length === 0 ? (
            <div className="flex items-center justify-center py-16 text-text-muted">No results</div>
          ) : (
            <div className="space-y-2">
              {prices.map((p) => (
                <PriceListItem key={p.uuid} price={p} onClick={onCardClick} />
              ))}
            </div>
          )}
          <Pagination page={pagination.page} pages={pagination.pages} total={pagination.total} limit={pagination.limit} onPageChange={onPageChange} />
        </div>
      )}
    </div>
  );
}

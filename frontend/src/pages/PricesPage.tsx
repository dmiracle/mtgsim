import { Link, useSearchParams } from "react-router-dom"
import PaginationBar from "../components/shared/PaginationBar"
import PriceDisplay from "../components/shared/PriceDisplay"
import SetIcon from "../components/shared/SetIcon"
import { useDebounce } from "../hooks/useDebounce"
import { usePrices } from "../hooks/usePrices"
import { useAllSets } from "../hooks/useSets"
import { useHomeStats } from "../hooks/useStats"
import type { PriceFilters } from "../types/filters"

const PRICE_RANGES = [
  { label: "Under $1", min: 0, max: 1 },
  { label: "$1-$5", min: 1, max: 5 },
  { label: "$5-$20", min: 5, max: 20 },
  { label: "$20-$50", min: 20, max: 50 },
  { label: "$50-$100", min: 50, max: 100 },
  { label: "$100-$500", min: 100, max: 500 },
  { label: "$500-$1000", min: 500, max: 1000 },
  { label: "$1000+", min: 1000, max: 999999 },
]

export default function PricesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { data: stats } = useHomeStats()
  const { data: allSets } = useAllSets()

  const filters: PriceFilters = {
    q: searchParams.get("q") || undefined,
    set: searchParams.get("set") || undefined,
    price_min: searchParams.get("price_min") ? Number(searchParams.get("price_min")) : undefined,
    price_max: searchParams.get("price_max") ? Number(searchParams.get("price_max")) : undefined,
    sort: searchParams.get("sort") || "average_usd",
    order: searchParams.get("order") || "desc",
    page: searchParams.get("page") ? Number(searchParams.get("page")) : undefined,
  }

  const debouncedQ = useDebounce(filters.q || "", 300)
  const { data, isLoading } = usePrices({ ...filters, q: debouncedQ || undefined })

  function setFilter(key: string, value: unknown) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === undefined || value === null || value === "") next.delete(key)
      else next.set(key, String(value))
      if (key !== "page") next.delete("page")
      return next
    })
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Prices</h1>

      {stats && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-[var(--color-accent)]">{stats.total_cards_with_prices.toLocaleString()}</div>
            <div className="text-xs text-[var(--color-text-secondary)]">Cards with Prices</div>
          </div>
          <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-[var(--color-accent)]">{stats.total_decks.toLocaleString()}</div>
            <div className="text-xs text-[var(--color-text-secondary)]">Decks</div>
          </div>
          <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-[var(--color-accent)]">{stats.total_sets.toLocaleString()}</div>
            <div className="text-xs text-[var(--color-text-secondary)]">Sets</div>
          </div>
        </div>
      )}

      {stats && stats.most_expensive_cards.length > 0 && (
        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-2">Top 10 Most Expensive</h2>
          <div className="space-y-1">
            {stats.most_expensive_cards.slice(0, 10).map((c, i) => (
              <div key={i} className="flex items-center gap-2 text-sm">
                <span className="text-[var(--color-text-muted)] w-5">{i + 1}.</span>
                <SetIcon code={c.set_code} />
                <span className="flex-1 truncate">{c.name}</span>
                <span className="text-green-400">${c.price.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-2 items-center">
        <input
          type="text"
          placeholder="Search cards..."
          value={filters.q || ""}
          onChange={(e) => setFilter("q", e.target.value || undefined)}
          className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-48"
        />
        <select
          value={filters.set || ""}
          onChange={(e) => setFilter("set", e.target.value || undefined)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Sets</option>
          {allSets?.map((s) => (
            <option key={s.code} value={s.code}>{s.name} ({s.code.toUpperCase()})</option>
          ))}
        </select>
        <select
          value={filters.price_min != null && filters.price_max != null ? `${filters.price_min}-${filters.price_max}` : ""}
          onChange={(e) => {
            if (!e.target.value) {
              setFilter("price_min", undefined)
              setFilter("price_max", undefined)
            } else {
              const range = PRICE_RANGES.find((r) => `${r.min}-${r.max}` === e.target.value)
              if (range) {
                setSearchParams((prev) => {
                  const next = new URLSearchParams(prev)
                  next.set("price_min", String(range.min))
                  next.set("price_max", String(range.max))
                  next.delete("page")
                  return next
                })
              }
            }
          }}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Prices</option>
          {PRICE_RANGES.map((r) => (
            <option key={r.label} value={`${r.min}-${r.max}`}>{r.label}</option>
          ))}
        </select>
        <select
          value={filters.sort || "average_usd"}
          onChange={(e) => setFilter("sort", e.target.value)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="average_usd">Price</option>
          <option value="name">Name</option>
        </select>
        <button
          onClick={() => setFilter("order", filters.order === "desc" ? "asc" : "desc")}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]"
        >
          {filters.order === "desc" ? "↓" : "↑"}
        </button>
      </div>

      {isLoading && <div className="text-[var(--color-text-muted)]">Loading...</div>}

      {data && (
        <>
          <div className="space-y-1">
            {data.data.map((p) => (
              <Link
                key={p.uuid}
                to={`/cards/${p.uuid}`}
                className="flex items-center gap-3 px-4 py-2.5 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] hover:border-[var(--color-accent)] transition-colors"
              >
                <SetIcon code={p.set_code} rarity={p.rarity} />
                <span className="flex-1 truncate text-sm">{p.name}</span>
                <span className="text-xs text-[var(--color-text-muted)] capitalize">{p.rarity}</span>
                <PriceDisplay price={p.average_usd} />
              </Link>
            ))}
          </div>
          <PaginationBar pagination={data.pagination} onPageChange={(pg) => setFilter("page", pg)} />
        </>
      )}
    </div>
  )
}

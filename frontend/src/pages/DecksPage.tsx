import { Link, useSearchParams } from "react-router-dom"
import PaginationBar from "../components/shared/PaginationBar"
import PriceDisplay from "../components/shared/PriceDisplay"
import { useDebounce } from "../hooks/useDebounce"
import { useDecks } from "../hooks/useDecks"
import type { DeckFilters } from "../types/filters"

const SOURCES = ["precon", "user", "import", "test"]
const SIZES = [
  { label: "Land Pack", min: 1, max: 20 },
  { label: "Sample", min: 21, max: 39 },
  { label: "Limited", min: 40, max: 59 },
  { label: "Constructed", min: 60, max: 99 },
  { label: "Commander", min: 100, max: 100 },
  { label: "Large", min: 101, max: 599 },
  { label: "Cube", min: 600, max: 99999 },
]

export default function DecksPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: DeckFilters = {
    q: searchParams.get("q") || undefined,
    format: searchParams.get("format") || undefined,
    source: searchParams.get("source") || undefined,
    set: searchParams.get("set") || undefined,
    colors: searchParams.get("colors") || undefined,
    card_count_min: searchParams.get("card_count_min") ? Number(searchParams.get("card_count_min")) : undefined,
    card_count_max: searchParams.get("card_count_max") ? Number(searchParams.get("card_count_max")) : undefined,
    price_min: searchParams.get("price_min") ? Number(searchParams.get("price_min")) : undefined,
    price_max: searchParams.get("price_max") ? Number(searchParams.get("price_max")) : undefined,
    sort: searchParams.get("sort") || undefined,
    order: searchParams.get("order") || undefined,
    page: searchParams.get("page") ? Number(searchParams.get("page")) : undefined,
  }

  const debouncedQ = useDebounce(filters.q || "", 300)
  const queryFilters = { ...filters, q: debouncedQ || undefined }
  const { data, isLoading } = useDecks(queryFilters)

  function setFilter(key: string, value: unknown) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === undefined || value === null || value === "") next.delete(key)
      else next.set(key, String(value))
      if (key !== "page") next.delete("page")
      return next
    })
  }

  const COLORS = ["W", "U", "B", "R", "G"]
  const currentColors = (filters.colors || "").split("").filter(Boolean)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Decks</h1>
        <div className="flex gap-2">
          <Link to="/decks/create" className="px-3 py-1.5 text-sm rounded bg-[var(--color-accent)] text-white">
            New Deck
          </Link>
          <Link to="/decks/import" className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]">
            Import
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 items-center">
        <input
          type="text"
          placeholder="Search decks..."
          value={filters.q || ""}
          onChange={(e) => setFilter("q", e.target.value || undefined)}
          className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-48"
        />
        <select
          value={filters.format || ""}
          onChange={(e) => setFilter("format", e.target.value || undefined)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Formats</option>
          {(data?.filters.formats || []).map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <select
          value={filters.source || ""}
          onChange={(e) => setFilter("source", e.target.value || undefined)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Sources</option>
          {SOURCES.map((s) => (
            <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
          ))}
        </select>
        <select
          value={filters.set || ""}
          onChange={(e) => setFilter("set", e.target.value || undefined)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Sets</option>
          {(data?.filters.sets || []).map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={filters.card_count_min && filters.card_count_max ? `${filters.card_count_min}-${filters.card_count_max}` : ""}
          onChange={(e) => {
            if (!e.target.value) {
              setFilter("card_count_min", undefined)
              setFilter("card_count_max", undefined)
            } else {
              const size = SIZES.find((s) => `${s.min}-${s.max}` === e.target.value)
              if (size) {
                setSearchParams((prev) => {
                  const next = new URLSearchParams(prev)
                  next.set("card_count_min", String(size.min))
                  next.set("card_count_max", String(size.max))
                  next.delete("page")
                  return next
                })
              }
            }
          }}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Sizes</option>
          {SIZES.map((s) => (
            <option key={s.label} value={`${s.min}-${s.max}`}>{s.label}</option>
          ))}
        </select>
        <div className="flex gap-0.5">
          {COLORS.map((c) => (
            <button
              key={c}
              onClick={() => {
                const next = currentColors.includes(c)
                  ? currentColors.filter((x) => x !== c)
                  : [...currentColors, c]
                setFilter("colors", next.join("") || undefined)
              }}
              className={`w-7 h-7 rounded text-xs font-bold ${
                currentColors.includes(c)
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
        <select
          value={filters.sort || "name"}
          onChange={(e) => setFilter("sort", e.target.value)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="name">Name</option>
          <option value="release_date">Release Date</option>
          <option value="card_count">Card Count</option>
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
            {data.data.map((deck) => (
              <Link
                key={deck.file}
                to={`/decks/${deck.file}`}
                className="flex items-center gap-3 px-4 py-2.5 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] hover:border-[var(--color-accent)] transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">{deck.name}</div>
                  <div className="text-xs text-[var(--color-text-muted)]">
                    {deck.card_count} cards · {deck.source}
                    {deck.release_date && ` · ${deck.release_date}`}
                  </div>
                </div>
                <div className="flex gap-0.5">
                  {deck.colors.map((c) => (
                    <i key={c} className={`ms ms-${c.toLowerCase()} ms-cost`} />
                  ))}
                </div>
                <PriceDisplay price={deck.price} />
              </Link>
            ))}
          </div>
          <PaginationBar pagination={data.pagination} onPageChange={(p) => setFilter("page", p)} />
        </>
      )}
    </div>
  )
}

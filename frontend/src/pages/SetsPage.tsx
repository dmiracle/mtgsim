import { Link, useSearchParams } from "react-router-dom"
import PaginationBar from "../components/shared/PaginationBar"
import SetIcon from "../components/shared/SetIcon"
import { useDebounce } from "../hooks/useDebounce"
import { useSets } from "../hooks/useSets"
import type { SetFilters } from "../types/filters"

export default function SetsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: SetFilters = {
    q: searchParams.get("q") || undefined,
    type: searchParams.get("type") || undefined,
    sort: searchParams.get("sort") || "release_date",
    order: searchParams.get("order") || "desc",
    page: searchParams.get("page") ? Number(searchParams.get("page")) : undefined,
  }

  const debouncedQ = useDebounce(filters.q || "", 300)
  const { data, isLoading } = useSets({ ...filters, q: debouncedQ || undefined })

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
      <h1 className="text-xl font-bold">Sets</h1>

      <div className="flex flex-wrap gap-2 items-center">
        <input
          type="text"
          placeholder="Search sets..."
          value={filters.q || ""}
          onChange={(e) => setFilter("q", e.target.value || undefined)}
          className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-48"
        />
        <select
          value={filters.type || ""}
          onChange={(e) => setFilter("type", e.target.value || undefined)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="">All Types</option>
          {(data?.filters.types || []).map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <select
          value={filters.sort || "release_date"}
          onChange={(e) => setFilter("sort", e.target.value)}
          className="px-2 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)]"
        >
          <option value="release_date">Release Date</option>
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
            {data.data.map((set) => (
              <Link
                key={set.code}
                to={`/sets/${set.code}`}
                className="flex items-center gap-3 px-4 py-2.5 rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] hover:border-[var(--color-accent)] transition-colors"
              >
                <SetIcon code={set.keyrune_code || set.code} name={set.name} />
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{set.name}</div>
                  <div className="text-xs text-[var(--color-text-muted)]">
                    {set.code.toUpperCase()} · {set.type} · {set.base_set_size} cards
                    {set.release_date && ` · ${set.release_date}`}
                  </div>
                </div>
              </Link>
            ))}
          </div>
          <PaginationBar pagination={data.pagination} onPageChange={(p) => setFilter("page", p)} />
        </>
      )}
    </div>
  )
}

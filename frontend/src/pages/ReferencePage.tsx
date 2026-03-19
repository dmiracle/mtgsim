import { useMemo, useState } from "react"
import { useKeywords } from "../hooks/useKeywords"
import { useDebounce } from "../hooks/useDebounce"

const CATEGORIES = ["All", "Keyword Abilities", "Keyword Actions", "Ability Words"]

export default function ReferencePage() {
  const { data, isLoading } = useKeywords()
  const [search, setSearch] = useState("")
  const [category, setCategory] = useState("All")
  const debouncedSearch = useDebounce(search)

  const allKeywords = useMemo(() => {
    if (!data) return []
    return [
      ...data.keyword_abilities.map((k) => ({ ...k, category: "Keyword Abilities" })),
      ...data.keyword_actions.map((k) => ({ ...k, category: "Keyword Actions" })),
      ...data.ability_words.map((k) => ({ ...k, category: "Ability Words" })),
    ]
  }, [data])

  const filtered = useMemo(() => {
    let result = allKeywords
    if (category !== "All") {
      result = result.filter((k) => k.category === category)
    }
    if (debouncedSearch) {
      const q = debouncedSearch.toLowerCase()
      result = result.filter(
        (k) => k.term.toLowerCase().includes(q) || k.definition.toLowerCase().includes(q),
      )
    }
    return result
  }, [allKeywords, category, debouncedSearch])

  return (
    <div className="space-y-4 max-w-3xl">
      <h1 className="text-xl font-bold">Keyword Reference</h1>

      <div className="flex flex-wrap gap-2 items-center">
        <input
          type="text"
          placeholder="Search keywords..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-56"
        />
        <div className="flex gap-1">
          {CATEGORIES.map((c) => (
            <button
              key={c}
              onClick={() => setCategory(c)}
              className={`px-2 py-1 text-xs rounded ${
                category === c
                  ? "bg-[var(--color-accent)] text-white"
                  : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
        <span className="text-sm text-[var(--color-text-muted)]">{filtered.length} keywords</span>
      </div>

      {isLoading && <div className="text-[var(--color-text-muted)]">Loading...</div>}

      <div className="space-y-2">
        {filtered.map((k) => (
          <div
            key={k.term + k.category}
            className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-3"
          >
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">{k.term}</span>
              <span className="text-xs text-[var(--color-accent)]">{k.category}</span>
            </div>
            <p className="text-sm text-[var(--color-text-secondary)] mt-1">{k.definition}</p>
          </div>
        ))}
        {filtered.length === 0 && !isLoading && (
          <div className="text-center py-8 text-[var(--color-text-muted)]">No keywords found</div>
        )}
      </div>
    </div>
  )
}

import { useEffect, useMemo, useState } from "react"
import { useGlossary } from "../../GlossaryContext"
import { useKeywords } from "../../hooks/useKeywords"

export default function GlossaryOverlay() {
  const { isOpen, close } = useGlossary()
  const { data } = useKeywords()
  const [search, setSearch] = useState("")

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape" && isOpen) close()
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [isOpen, close])

  const allTerms = useMemo(() => {
    if (!data) return []
    return [
      ...data.keyword_abilities.map((k) => ({ ...k, category: "Keyword Ability" })),
      ...data.keyword_actions.map((k) => ({ ...k, category: "Keyword Action" })),
      ...data.ability_words.map((k) => ({ ...k, category: "Ability Word" })),
    ]
  }, [data])

  const filtered = useMemo(() => {
    if (!search) return allTerms
    const q = search.toLowerCase()
    return allTerms.filter(
      (t) => t.term.toLowerCase().includes(q) || t.definition.toLowerCase().includes(q) || t.category.toLowerCase().includes(q),
    )
  }, [allTerms, search])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/60 flex items-start justify-center z-50 pt-16" onClick={close}>
      <div
        className="bg-[var(--color-bg-secondary)] rounded-lg border border-[var(--color-border)] w-[600px] max-h-[70vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-[var(--color-border)]">
          <input
            type="text"
            placeholder="Search glossary..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            autoFocus
            className="w-full px-3 py-2 rounded bg-[var(--color-bg-primary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]"
          />
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filtered.length === 0 && (
            <div className="text-center text-[var(--color-text-muted)] py-8">No results</div>
          )}
          {filtered.map((t) => (
            <div key={t.term + t.category} className="py-2 border-b border-[var(--color-border)]/30">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm">{t.term}</span>
                <span className="text-xs text-[var(--color-accent)]">{t.category}</span>
              </div>
              <p className="text-xs text-[var(--color-text-secondary)] mt-1">{t.definition}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

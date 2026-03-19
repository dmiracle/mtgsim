import { useCallback, useState } from "react"
import CardFilterBar from "../components/shared/CardFilterBar"
import CardGrid from "../components/shared/CardGrid"
import DeckPickerDialog from "../components/shared/DeckPickerDialog"
import PaginationBar from "../components/shared/PaginationBar"
import WordCloud from "../components/shared/WordCloud"
import { useCardFilters } from "../hooks/useCardFilters"
import { useCards, useCardTags, useKeywordFrequencies } from "../hooks/useCards"
import { useDebounce } from "../hooks/useDebounce"
import { usePinnedCards } from "../hooks/usePinnedCards"

export default function CardsPage() {
  const { filters, setFilter, resetFilters } = useCardFilters()
  const debouncedQ = useDebounce(filters.q || "", 300)
  const queryFilters = { ...filters, q: debouncedQ }

  const hasFilters = !!(debouncedQ || filters.text || filters.rarity || filters.colors || filters.type || filters.tags || filters.keywords || filters.format || filters.sets || filters.owns !== undefined)
  const { data, isLoading } = useCards(queryFilters, hasFilters)

  const freqParams: Record<string, string> = {}
  if (filters.format) freqParams.format = filters.format
  if (filters.sets) freqParams.sets = filters.sets
  if (filters.rarity) freqParams.rarity = filters.rarity
  if (filters.colors) freqParams.colors = filters.colors
  if (filters.type) freqParams.type = filters.type
  const { data: freqData } = useKeywordFrequencies(freqParams, hasFilters)

  const tagParams: Record<string, string> = {}
  if (filters.format) tagParams.format = filters.format
  if (filters.colors) tagParams.colors = filters.colors
  if (filters.rarity) tagParams.rarity = filters.rarity
  if (filters.type) tagParams.type = filters.type
  const { data: tags } = useCardTags(tagParams)

  const { isPinned, togglePin, pinnedSet } = usePinnedCards()
  const [deckPickerUuid, setDeckPickerUuid] = useState<string | null>(null)

  const selectedKeywords = (filters.keywords || "").split(",").filter(Boolean)

  const handleKeywordClick = useCallback(
    (word: string) => {
      const current = selectedKeywords.includes(word)
        ? selectedKeywords.filter((w) => w !== word)
        : [...selectedKeywords, word]
      setFilter("keywords", current.join(",") || undefined)
    },
    [selectedKeywords, setFilter],
  )

  const sortedCards = data?.data
    ? [...data.data].sort((a, b) => {
        const aPin = pinnedSet.has(a.uuid) ? -1 : 0
        const bPin = pinnedSet.has(b.uuid) ? -1 : 0
        return aPin - bPin
      })
    : []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Cards</h1>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Format (e.g. standard)..."
            value={filters.format || ""}
            onChange={(e) => setFilter("format", e.target.value || undefined)}
            className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-40"
          />
          <input
            type="text"
            placeholder="Sets (e.g. DSK,MH3)..."
            value={filters.sets || ""}
            onChange={(e) => setFilter("sets", e.target.value || undefined)}
            className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-secondary)] border border-[var(--color-border)] text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] w-40"
          />
          <button onClick={resetFilters} className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
            Reset
          </button>
        </div>
      </div>

      {freqData && (
        <div className="grid md:grid-cols-3 gap-3">
          {(["keyword_abilities", "keyword_actions", "ability_words"] as const).map((cat) => {
            const words = freqData[cat]
            if (!words || Object.keys(words).length === 0) return null
            return (
              <div key={cat} className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-3">
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] mb-1 capitalize">
                  {cat.replace(/_/g, " ")}
                </h3>
                <WordCloud words={words} onWordClick={handleKeywordClick} selectedWords={selectedKeywords} height={150} />
              </div>
            )
          })}
        </div>
      )}

      <CardFilterBar
        filters={filters as Record<string, unknown>}
        onFilterChange={setFilter as (key: string, value: unknown) => void}
        tags={tags || undefined}
        showUnique
      />

      {!hasFilters && (
        <div className="text-center py-12 text-[var(--color-text-muted)]">
          Enter a search term or select a filter to browse cards
        </div>
      )}

      {hasFilters && isLoading && <div className="text-[var(--color-text-muted)]">Loading...</div>}

      {hasFilters && data && (
        <>
          <CardGrid
            cards={sortedCards}
            isPinned={isPinned}
            onTogglePin={togglePin}
            onAddToDeck={setDeckPickerUuid}
          />
          <PaginationBar
            pagination={data.pagination}
            onPageChange={(p) => setFilter("page", p)}
          />
        </>
      )}

      {deckPickerUuid && (
        <DeckPickerDialog cardUuid={deckPickerUuid} onClose={() => setDeckPickerUuid(null)} />
      )}
    </div>
  )
}

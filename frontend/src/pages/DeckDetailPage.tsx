import { useMemo, useState } from "react"
import { useParams, useSearchParams } from "react-router-dom"
import CardFilterBar from "../components/shared/CardFilterBar"
import CardGrid from "../components/shared/CardGrid"
import DeckPickerDialog from "../components/shared/DeckPickerDialog"
import HistogramChart from "../components/shared/HistogramChart"
import ManaCurveChart from "../components/shared/ManaCurveChart"
import PriceDisplay from "../components/shared/PriceDisplay"
import RawJsonViewer from "../components/shared/RawJsonViewer"
import WordCloud from "../components/shared/WordCloud"
import { useDeck } from "../hooks/useDecks"
import { usePinnedCards } from "../hooks/usePinnedCards"
import type { DeckCard } from "../types/deck"

function filterCards(cards: DeckCard[], filters: Record<string, unknown>): DeckCard[] {
  let result = cards
  const text = (filters.text as string || "").toLowerCase()
  if (text) result = result.filter((c) => c.text?.toLowerCase().includes(text))
  if (filters.rarity) result = result.filter((c) => c.rarity === filters.rarity)
  if (filters.type) result = result.filter((c) => c.type.includes(filters.type as string))
  if (filters.colors) {
    const fc = (filters.colors as string).split("")
    result = result.filter((c) => fc.some((f) => c.colors.includes(f)))
  }
  if (filters.tags) result = result.filter((c) => c.tags.includes(filters.tags as string))
  if (filters.owns === true) result = result.filter((c) => c.owns_enough)
  if (filters.owns === false) result = result.filter((c) => !c.owns_enough)

  const sort = (filters.sort as string) || "name"
  const order = filters.order === "desc" ? -1 : 1
  result.sort((a, b) => {
    let cmp = 0
    if (sort === "mana_value") cmp = a.mana_value - b.mana_value
    else if (sort === "price") cmp = (a.price || 0) - (b.price || 0)
    else if (sort === "rarity") {
      const r = { common: 0, uncommon: 1, rare: 2, mythic: 3 }
      cmp = (r[a.rarity as keyof typeof r] ?? 0) - (r[b.rarity as keyof typeof r] ?? 0)
    } else cmp = a.name.localeCompare(b.name)
    return cmp * order
  })

  return result
}

export default function DeckDetailPage() {
  const { file } = useParams<{ file: string }>()
  const { data: deck, isLoading } = useDeck(file)
  const [searchParams, setSearchParams] = useSearchParams()
  const { isPinned, togglePin } = usePinnedCards()
  const [deckPickerUuid, setDeckPickerUuid] = useState<string | null>(null)

  const filters: Record<string, unknown> = {
    text: searchParams.get("text") || undefined,
    rarity: searchParams.get("rarity") || undefined,
    type: searchParams.get("type") || undefined,
    colors: searchParams.get("colors") || undefined,
    tags: searchParams.get("tags") || undefined,
    owns: searchParams.get("owns") === "true" ? true : searchParams.get("owns") === "false" ? false : undefined,
    sort: searchParams.get("sort") || undefined,
    order: searchParams.get("order") || undefined,
  }

  function setFilter(key: string, value: unknown) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === undefined || value === null || value === "") next.delete(key)
      else next.set(key, String(value))
      return next
    })
  }

  const allCards = useMemo(() => {
    if (!deck) return []
    return [...deck.commander, ...deck.main_board, ...deck.side_board]
  }, [deck])

  const tags = useMemo(() => {
    const counts = new Map<string, number>()
    for (const c of allCards) {
      for (const t of c.tags) counts.set(t, (counts.get(t) || 0) + 1)
    }
    return [...counts.entries()].map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count)
  }, [allCards])

  if (isLoading) return <div className="text-[var(--color-text-muted)]">Loading...</div>
  if (!deck) return <div className="text-[var(--color-text-muted)]">Deck not found</div>

  const priceProviders = (["tcgplayer", "cardkingdom", "cardsphere", "cardmarket", "mtgo"] as const).filter(
    (p) => deck.price[p] != null,
  )

  const sections = [
    { label: "Commander", cards: deck.commander },
    { label: "Main Board", cards: deck.main_board },
    { label: "Sideboard", cards: deck.side_board },
  ].filter((s) => s.cards.length > 0)

  return (
    <div className="space-y-6 max-w-6xl">
      <div>
        <h1 className="text-2xl font-bold">{deck.meta.name}</h1>
        <div className="text-sm text-[var(--color-text-secondary)]">
          {deck.meta.code && <span>{deck.meta.code} · </span>}
          {deck.meta.release_date && <span>{deck.meta.release_date} · </span>}
          {deck.meta.source && <span className="capitalize">{deck.meta.source}</span>}
          {deck.meta.format && <span> · {deck.meta.format}</span>}
        </div>
        {deck.meta.description && <p className="text-sm text-[var(--color-text-muted)] mt-1">{deck.meta.description}</p>}
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-2">Overview</h2>
          <div className="space-y-1 text-sm">
            <div>Total: {deck.stats.total_cards} ({deck.stats.unique_cards} unique)</div>
            <div className="flex gap-2">
              Total: <PriceDisplay price={deck.price.total} />
            </div>
            {priceProviders.map((p) => (
              <div key={p} className="flex justify-between text-xs text-[var(--color-text-muted)]">
                <span className="capitalize">{p}</span>
                <PriceDisplay price={deck.price[p]} />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-2">Mana Curve</h2>
          <ManaCurveChart data={deck.stats.mana_curve} />
        </div>

        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-2">Price Distribution</h2>
          <HistogramChart data={deck.stats.price_histogram} />
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {[
          { label: "Colors", data: deck.stats.color_distribution },
          { label: "Types", data: deck.stats.type_distribution },
          { label: "Rarities", data: deck.stats.rarity_distribution },
        ].map(({ label, data: dist }) => (
          <div key={label} className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
            <h2 className="text-sm font-bold mb-2">{label}</h2>
            <div className="space-y-1">
              {Object.entries(dist)
                .sort(([, a], [, b]) => b - a)
                .slice(0, 6)
                .map(([k, v]) => (
                  <div key={k} className="flex justify-between text-sm">
                    <span className="capitalize text-[var(--color-text-secondary)]">{k}</span>
                    <span>{v}</span>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* Legality */}
      <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
        <h2 className="text-sm font-bold mb-2">Format Legality</h2>
        <div className="flex flex-wrap gap-1">
          {Object.entries(deck.legality).map(([fmt, legal]) => (
            <span
              key={fmt}
              className={`px-2 py-0.5 text-xs rounded ${
                legal ? "bg-green-900/40 text-green-400" : "bg-red-900/40 text-red-400"
              }`}
            >
              {fmt}
            </span>
          ))}
        </div>
      </div>

      {/* Keywords */}
      {(Object.keys(deck.stats.keywords.keyword_abilities).length > 0 ||
        Object.keys(deck.stats.keywords.keyword_actions).length > 0 ||
        Object.keys(deck.stats.keywords.ability_words).length > 0) && (
        <div className="grid md:grid-cols-3 gap-3">
          {(["keyword_abilities", "keyword_actions", "ability_words"] as const).map((cat) => {
            const words = deck.stats.keywords[cat]
            if (Object.keys(words).length === 0) return null
            return (
              <div key={cat} className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-3">
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] mb-1 capitalize">
                  {cat.replace(/_/g, " ")}
                </h3>
                <WordCloud words={words} height={140} />
              </div>
            )
          })}
        </div>
      )}

      {/* Cards */}
      <CardFilterBar
        filters={filters}
        onFilterChange={setFilter}
        tags={tags}
        showSearch={false}
      />

      {sections.map(({ label, cards }) => {
        const filtered = filterCards(cards, filters)
        if (filtered.length === 0) return null
        return (
          <div key={label}>
            <h2 className="text-sm font-bold mb-2">{label} ({filtered.length})</h2>
            <CardGrid
              cards={filtered.map((c) => ({ ...c, set_code: deck.meta.code || "" }))}
              isPinned={isPinned}
              onTogglePin={togglePin}
              onAddToDeck={setDeckPickerUuid}
            />
          </div>
        )
      })}

      <RawJsonViewer data={deck} label="Deck JSON" />

      {deckPickerUuid && (
        <DeckPickerDialog cardUuid={deckPickerUuid} onClose={() => setDeckPickerUuid(null)} />
      )}
    </div>
  )
}

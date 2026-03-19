import { useState } from "react"
import { useParams, useSearchParams } from "react-router-dom"
import CardFilterBar from "../components/shared/CardFilterBar"
import CardGrid from "../components/shared/CardGrid"
import DeckPickerDialog from "../components/shared/DeckPickerDialog"
import PaginationBar from "../components/shared/PaginationBar"
import PriceDisplay from "../components/shared/PriceDisplay"
import RawJsonViewer from "../components/shared/RawJsonViewer"
import SetIcon from "../components/shared/SetIcon"
import WordCloud from "../components/shared/WordCloud"
import { useCardTags } from "../hooks/useCards"
import { usePinnedCards } from "../hooks/usePinnedCards"
import { useSet } from "../hooks/useSets"

export default function SetDetailPage() {
  const { code } = useParams<{ code: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const { isPinned, togglePin } = usePinnedCards()
  const [deckPickerUuid, setDeckPickerUuid] = useState<string | null>(null)

  const cardParams: Record<string, unknown> = {
    rarity: searchParams.get("rarity") || undefined,
    colors: searchParams.get("colors") || undefined,
    type: searchParams.get("type") || undefined,
    text: searchParams.get("text") || undefined,
    tags: searchParams.get("tags") || undefined,
    owns: searchParams.get("owns") === "true" ? true : searchParams.get("owns") === "false" ? false : undefined,
    unique: searchParams.get("unique") !== "false",
    sort: searchParams.get("sort") || "number",
    order: searchParams.get("order") || "asc",
    card_page: searchParams.get("card_page") ? Number(searchParams.get("card_page")) : undefined,
  }

  const { data: set, isLoading } = useSet(code, cardParams)

  const tagParams: Record<string, string> = {}
  if (code) tagParams.set = code
  if (cardParams.colors) tagParams.colors = cardParams.colors as string
  if (cardParams.rarity) tagParams.rarity = cardParams.rarity as string
  if (cardParams.type) tagParams.type = cardParams.type as string
  const { data: tags } = useCardTags(tagParams)

  function setFilter(key: string, value: unknown) {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev)
      if (value === undefined || value === null || value === "") next.delete(key)
      else next.set(key, String(value))
      if (key !== "card_page") next.delete("card_page")
      return next
    })
  }

  if (isLoading) return <div className="text-[var(--color-text-muted)]">Loading...</div>
  if (!set) return <div className="text-[var(--color-text-muted)]">Set not found</div>

  const priceProviders = (["tcgplayer", "cardkingdom", "cardsphere", "cardmarket", "mtgo"] as const).filter(
    (p) => set.stats.price[p] != null,
  )

  return (
    <div className="space-y-6 max-w-6xl">
      <div className="flex items-center gap-3">
        <SetIcon code={set.meta.code} name={set.meta.name} />
        <div>
          <h1 className="text-2xl font-bold">{set.meta.name}</h1>
          <div className="text-sm text-[var(--color-text-secondary)]">
            {set.meta.code.toUpperCase()} · {set.meta.type} · {set.meta.release_date}
            {set.meta.block && ` · ${set.meta.block}`}
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-2">Overview</h2>
          <div className="space-y-1 text-sm">
            <div>Base Size: {set.meta.base_set_size}</div>
            <div>Total Size: {set.meta.total_set_size}</div>
            <div className="flex gap-2">Total: <PriceDisplay price={set.stats.price.total} /></div>
            {priceProviders.map((p) => (
              <div key={p} className="flex justify-between text-xs text-[var(--color-text-muted)]">
                <span className="capitalize">{p}</span>
                <PriceDisplay price={set.stats.price[p]} />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
          <h2 className="text-sm font-bold mb-2">Rarity Breakdown</h2>
          <div className="space-y-1">
            {Object.entries(set.stats.rarity_count)
              .sort(([, a], [, b]) => b - a)
              .map(([r, c]) => (
                <div key={r} className="flex justify-between text-sm">
                  <span className="capitalize text-[var(--color-text-secondary)]">{r}</span>
                  <span>{c}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4 space-y-2">
          {(["keyword_abilities", "keyword_actions", "ability_words"] as const).map((cat) => {
            const words = set.stats.keywords[cat]
            if (Object.keys(words).length === 0) return null
            return (
              <div key={cat}>
                <h3 className="text-xs font-bold text-[var(--color-text-secondary)] capitalize">{cat.replace(/_/g, " ")}</h3>
                <WordCloud words={words} height={100} />
              </div>
            )
          })}
        </div>
      </div>

      <CardFilterBar
        filters={cardParams}
        onFilterChange={setFilter}
        tags={tags || undefined}
        showSearch={false}
        showUnique
      />

      <CardGrid
        cards={set.cards.data.map((c) => ({ ...c, set_code: set.meta.code }))}
        isPinned={isPinned}
        onTogglePin={togglePin}
        onAddToDeck={setDeckPickerUuid}
      />

      <PaginationBar
        pagination={set.cards.pagination}
        onPageChange={(p) => setFilter("card_page", p)}
      />

      <RawJsonViewer data={set} label="Set JSON" />

      {deckPickerUuid && (
        <DeckPickerDialog cardUuid={deckPickerUuid} onClose={() => setDeckPickerUuid(null)} />
      )}
    </div>
  )
}

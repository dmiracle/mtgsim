import { useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"
import DeckPickerDialog from "../components/shared/DeckPickerDialog"
import ManaSymbols from "../components/shared/ManaSymbols"
import PriceDisplay from "../components/shared/PriceDisplay"
import RawJsonViewer from "../components/shared/RawJsonViewer"
import SetIcon from "../components/shared/SetIcon"
import { useCard, useUpdateCollection, useUpdateRating } from "../hooks/useCards"
import { useKeywords } from "../hooks/useKeywords"

export default function CardDetailPage() {
  const { uuid } = useParams<{ uuid: string }>()
  const navigate = useNavigate()
  const { data: card, isLoading } = useCard(uuid)
  const { data: keywordsData } = useKeywords()
  const updateCollection = useUpdateCollection()
  const updateRating = useUpdateRating()
  const [deckPickerOpen, setDeckPickerOpen] = useState(false)
  const [ratingForm, setRatingForm] = useState<{
    developing: number; ahead: number; behind: number; parity: number; notes: string
  } | null>(null)
  const [ratingStatus, setRatingStatus] = useState("")

  if (isLoading) return <div className="text-[var(--color-text-muted)]">Loading...</div>
  if (!card) return <div className="text-[var(--color-text-muted)]">Card not found</div>

  const keywordTypeMap = new Map<string, string>()
  if (keywordsData) {
    for (const k of keywordsData.keyword_abilities) keywordTypeMap.set(k.term, "Keyword Ability")
    for (const k of keywordsData.keyword_actions) keywordTypeMap.set(k.term, "Keyword Action")
    for (const k of keywordsData.ability_words) keywordTypeMap.set(k.term, "Ability Word")
  }

  const rating = ratingForm ?? {
    developing: card.quadrant_rating?.developing ?? 0,
    ahead: card.quadrant_rating?.ahead ?? 0,
    behind: card.quadrant_rating?.behind ?? 0,
    parity: card.quadrant_rating?.parity ?? 0,
    notes: card.quadrant_rating?.notes ?? "",
  }

  async function saveRating() {
    if (!uuid) return
    setRatingStatus("Saving...")
    try {
      await updateRating.mutateAsync({
        uuid,
        rating: {
          developing: rating.developing || null,
          ahead: rating.ahead || null,
          behind: rating.behind || null,
          parity: rating.parity || null,
          notes: rating.notes || null,
        },
      })
      setRatingStatus("Saved")
      setRatingForm(null)
    } catch {
      setRatingStatus("Error")
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <button onClick={() => navigate(-1)} className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
        ← Back
      </button>

      <div className="flex gap-6">
        <div className="w-64 shrink-0">
          {card.image_url ? (
            <img src={card.image_url} alt={card.name} className="rounded-lg w-full" />
          ) : (
            <div className="w-full aspect-[488/680] bg-[var(--color-bg-tertiary)] rounded-lg flex items-center justify-center text-[var(--color-text-muted)]">
              No image
            </div>
          )}
          <div className="mt-3 flex gap-2">
            <button
              onClick={() => setDeckPickerOpen(true)}
              className="flex-1 px-3 py-1.5 text-sm rounded bg-[var(--color-accent)] text-white hover:opacity-90"
            >
              Add to Deck
            </button>
            <button
              onClick={() => navigator.clipboard.writeText(card.uuid)}
              className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:text-white"
              title="Copy UUID"
            >
              UUID
            </button>
          </div>
        </div>

        <div className="flex-1 space-y-4">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{card.name}</h1>
              <ManaSymbols cost={card.mana_cost} />
            </div>
            <div className="text-[var(--color-text-secondary)]">{card.type}</div>
            <div className="flex gap-3 text-sm text-[var(--color-text-muted)] mt-1">
              {card.power && <span>P/T: {card.power}/{card.toughness}</span>}
              {card.loyalty && <span>Loyalty: {card.loyalty}</span>}
              {card.defense && <span>Defense: {card.defense}</span>}
              <span>MV: {card.mana_value}</span>
            </div>
          </div>

          {card.text && (
            <div className="bg-[var(--color-bg-secondary)] rounded p-3">
              <p className="text-sm whitespace-pre-wrap">{card.text}</p>
            </div>
          )}
          {card.flavor_text && (
            <p className="text-sm italic text-[var(--color-text-muted)]">{card.flavor_text}</p>
          )}

          {/* Quadrant Rating */}
          <div className="bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4">
            <h2 className="text-sm font-bold mb-2">Quadrant Rating</h2>
            <div className="grid grid-cols-2 gap-3">
              {(["developing", "ahead", "behind", "parity"] as const).map((q) => (
                <div key={q}>
                  <label className="text-xs text-[var(--color-text-secondary)] capitalize">{q}</label>
                  <input
                    type="range"
                    min={0}
                    max={5}
                    step={0.5}
                    value={rating[q]}
                    onChange={(e) => setRatingForm({ ...rating, [q]: Number(e.target.value) })}
                    className="w-full accent-[var(--color-accent)]"
                  />
                  <span className="text-xs text-[var(--color-text-muted)]">{rating[q]}</span>
                </div>
              ))}
            </div>
            <textarea
              placeholder="Notes..."
              value={rating.notes}
              onChange={(e) => setRatingForm({ ...rating, notes: e.target.value })}
              className="w-full mt-2 px-2 py-1.5 text-sm rounded bg-[var(--color-bg-primary)] border border-[var(--color-border)] text-[var(--color-text-primary)] resize-none"
              rows={2}
            />
            <div className="flex items-center gap-2 mt-2">
              <button onClick={saveRating} className="px-3 py-1 text-sm rounded bg-[var(--color-accent)] text-white">
                Save Rating
              </button>
              {ratingStatus && <span className="text-xs text-[var(--color-text-secondary)]">{ratingStatus}</span>}
            </div>
          </div>

          {/* Keywords */}
          {card.keywords.length > 0 && (
            <div>
              <h2 className="text-sm font-bold mb-1">Keywords</h2>
              <div className="flex flex-wrap gap-1">
                {card.keywords.map((kw) => (
                  <span
                    key={kw}
                    className="px-2 py-0.5 text-xs rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]"
                    title={keywordTypeMap.get(kw) || ""}
                  >
                    {kw}
                    {keywordTypeMap.has(kw) && (
                      <span className="ml-1 text-[var(--color-accent)]">({keywordTypeMap.get(kw)})</span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Metadata */}
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-[var(--color-text-muted)]">Set: </span>
              <Link to={`/sets/${card.set_code}`} className="hover:text-[var(--color-accent)]">
                <SetIcon code={card.set_code} rarity={card.rarity} /> {card.set_name}
              </Link>
            </div>
            <div><span className="text-[var(--color-text-muted)]">Rarity: </span><span className="capitalize">{card.rarity}</span></div>
            {card.number && <div><span className="text-[var(--color-text-muted)]">Number: </span>{card.number}</div>}
            {card.artist && <div><span className="text-[var(--color-text-muted)]">Artist: </span>{card.artist}</div>}
            {card.layout && <div><span className="text-[var(--color-text-muted)]">Layout: </span>{card.layout}</div>}
            {card.frame_version && <div><span className="text-[var(--color-text-muted)]">Frame: </span>{card.frame_version}</div>}
            {card.border_color && <div><span className="text-[var(--color-text-muted)]">Border: </span>{card.border_color}</div>}
            {card.finishes.length > 0 && <div><span className="text-[var(--color-text-muted)]">Finishes: </span>{card.finishes.join(", ")}</div>}
            {card.is_reprint && <span className="text-xs px-1.5 py-0.5 bg-[var(--color-bg-tertiary)] rounded">Reprint</span>}
            {card.is_reserved && <span className="text-xs px-1.5 py-0.5 bg-[var(--color-bg-tertiary)] rounded">Reserved</span>}
            {card.is_promo && <span className="text-xs px-1.5 py-0.5 bg-[var(--color-bg-tertiary)] rounded">Promo</span>}
          </div>

          {/* Legalities */}
          <div>
            <h2 className="text-sm font-bold mb-1">Legalities</h2>
            <div className="flex flex-wrap gap-1">
              {Object.entries(card.legalities)
                .sort(([, a], [, b]) => (a === "Legal" ? -1 : b === "Legal" ? 1 : a.localeCompare(b)))
                .map(([fmt, status]) => (
                  <span
                    key={fmt}
                    className={`px-2 py-0.5 text-xs rounded ${
                      status === "Legal"
                        ? "bg-green-900/40 text-green-400"
                        : status === "Banned"
                          ? "bg-red-900/40 text-red-400"
                          : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)]"
                    }`}
                  >
                    {fmt}: {status}
                  </span>
                ))}
            </div>
          </div>

          {/* Prices */}
          {card.all_prices.length > 0 && (
            <div>
              <h2 className="text-sm font-bold mb-1">Prices</h2>
              <div className="grid grid-cols-2 gap-1 text-sm">
                {card.all_prices.map((p, i) => (
                  <div key={i} className="flex justify-between">
                    <span className="text-[var(--color-text-secondary)]">{p.provider} ({p.finish}, {p.listing_type})</span>
                    <PriceDisplay price={p.price} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Other Printings */}
          {card.other_printings.length > 0 && (
            <div>
              <h2 className="text-sm font-bold mb-1">Other Printings</h2>
              <div className="flex flex-wrap gap-2">
                {card.other_printings.map((p) => (
                  <Link
                    key={p.uuid}
                    to={`/cards/${p.uuid}`}
                    className="flex items-center gap-1 px-2 py-1 rounded bg-[var(--color-bg-tertiary)] text-sm hover:bg-[var(--color-accent)] transition-colors"
                  >
                    <SetIcon code={p.set_code} rarity={p.rarity} name={p.set_name} />
                    <span>{p.set_name}</span>
                    {p.owns && <span className="text-green-400 text-xs">✓</span>}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Deck Appearances */}
          {card.appears_in_decks.length > 0 && (
            <div>
              <h2 className="text-sm font-bold mb-1">Appears In</h2>
              <div className="space-y-1">
                {card.appears_in_decks.map((d) => (
                  <Link
                    key={d.file}
                    to={`/decks/${d.file}`}
                    className="flex justify-between text-sm hover:text-[var(--color-accent)]"
                  >
                    <span>{d.name}</span>
                    <span className="text-[var(--color-text-muted)]">×{d.count}</span>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Collection */}
          <div>
            <h2 className="text-sm font-bold mb-1">Collection</h2>
            {card.collection ? (
              <div className="grid grid-cols-2 gap-1 text-sm">
                <div>Owned: {card.collection.quantity_owned}</div>
                <div>Foil Owned: {card.collection.quantity_owned_foil}</div>
                <div>Wanted: {card.collection.quantity_wanted}</div>
                <div>Foil Wanted: {card.collection.quantity_wanted_foil}</div>
                {card.collection.condition && <div>Condition: {card.collection.condition}</div>}
                {card.collection.notes && <div className="col-span-2">Notes: {card.collection.notes}</div>}
              </div>
            ) : (
              <button
                onClick={() => uuid && updateCollection.mutate(uuid)}
                disabled={updateCollection.isPending}
                className="px-3 py-1.5 text-sm rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-accent)] hover:text-white"
              >
                {updateCollection.isPending ? "Adding..." : "Add to Collection"}
              </button>
            )}
          </div>

          <RawJsonViewer data={card} label="Card JSON" />
        </div>
      </div>

      {deckPickerOpen && uuid && (
        <DeckPickerDialog cardUuid={uuid} onClose={() => setDeckPickerOpen(false)} />
      )}
    </div>
  )
}

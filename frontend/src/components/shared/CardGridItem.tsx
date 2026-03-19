import { Link } from "react-router-dom"
import ManaSymbols from "./ManaSymbols"
import PriceDisplay from "./PriceDisplay"
import SetIcon from "./SetIcon"

interface Props {
  uuid: string
  name: string
  type: string
  mana_cost: string | null
  rarity: string
  set_code: string
  price: number | null
  image_url: string | null
  text?: string | null
  count?: number
  isPinned?: boolean
  onTogglePin?: (uuid: string) => void
  onAddToDeck?: (uuid: string) => void
}

export default function CardGridItem({
  uuid, name, type, mana_cost, rarity, set_code, price, image_url,
  text, count, isPinned, onTogglePin, onAddToDeck,
}: Props) {
  return (
    <div className="bg-[var(--color-bg-secondary)] rounded-lg border border-[var(--color-border)] overflow-hidden hover:border-[var(--color-accent)] transition-colors group">
      <Link to={`/cards/${uuid}`} className="block">
        {image_url ? (
          <img src={image_url} alt={name} loading="lazy" className="w-full aspect-[488/680] object-cover" />
        ) : (
          <div className="w-full aspect-[488/680] bg-[var(--color-bg-tertiary)] flex items-center justify-center text-[var(--color-text-muted)] text-xs p-2 text-center">
            {name}
          </div>
        )}
      </Link>
      <div className="p-2 space-y-1">
        <div className="flex items-center justify-between gap-1">
          <Link to={`/cards/${uuid}`} className="text-sm font-medium truncate hover:text-[var(--color-accent)]">
            {count && count > 1 && <span className="text-[var(--color-accent)] mr-1">{count}x</span>}
            {name}
          </Link>
          <ManaSymbols cost={mana_cost} />
        </div>
        <div className="text-xs text-[var(--color-text-secondary)] truncate">{type}</div>
        {text && <div className="text-xs text-[var(--color-text-muted)] line-clamp-2">{text}</div>}
        <div className="flex items-center justify-between text-xs">
          <span className="flex items-center gap-1">
            <SetIcon code={set_code} rarity={rarity} />
            <span className="text-[var(--color-text-muted)] capitalize">{rarity}</span>
          </span>
          <PriceDisplay price={price} />
        </div>
        <div className="flex items-center gap-1 pt-1">
          {onTogglePin && (
            <button
              onClick={() => onTogglePin(uuid)}
              className={`text-xs px-1.5 py-0.5 rounded ${isPinned ? "bg-[var(--color-accent)] text-white" : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)]"} hover:opacity-80`}
              title={isPinned ? "Unpin" : "Pin"}
            >
              {isPinned ? "Pinned" : "Pin"}
            </button>
          )}
          {onAddToDeck && (
            <button
              onClick={() => onAddToDeck(uuid)}
              className="text-xs px-1.5 py-0.5 rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-accent)] hover:text-white"
            >
              + Deck
            </button>
          )}
          <button
            onClick={() => navigator.clipboard.writeText(uuid)}
            className="text-xs px-1.5 py-0.5 rounded bg-[var(--color-bg-tertiary)] text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] ml-auto"
            title="Copy UUID"
          >
            UUID
          </button>
        </div>
      </div>
    </div>
  )
}

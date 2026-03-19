import CardGridItem from "./CardGridItem"

interface CardData {
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
}

interface Props {
  cards: CardData[]
  isPinned?: (uuid: string) => boolean
  onTogglePin?: (uuid: string) => void
  onAddToDeck?: (uuid: string) => void
}

export default function CardGrid({ cards, isPinned, onTogglePin, onAddToDeck }: Props) {
  if (cards.length === 0) {
    return <div className="text-center py-12 text-[var(--color-text-muted)]">No cards found</div>
  }

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
      {cards.map((card) => (
        <CardGridItem
          key={card.uuid}
          {...card}
          isPinned={isPinned?.(card.uuid)}
          onTogglePin={onTogglePin}
          onAddToDeck={onAddToDeck}
        />
      ))}
    </div>
  )
}

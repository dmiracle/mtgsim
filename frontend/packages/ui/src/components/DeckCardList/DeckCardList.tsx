import type { DeckCard } from "@/types/api";
import { DeckCardItem } from "@/components/DeckCardItem/DeckCardItem";

type DeckCardListProps = {
  title: string;
  cards: DeckCard[];
  onRemove?: (uuid: string) => void;
  onChangePrinting?: (uuid: string) => void;
  onCardClick?: (uuid: string) => void;
  onAddCard?: () => void;
};

export function DeckCardList({ title, cards, onRemove, onChangePrinting, onCardClick, onAddCard }: DeckCardListProps) {
  const total = cards.reduce((s, c) => s + c.count, 0);

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between px-3 py-1">
        <h3 className="text-xs font-semibold uppercase tracking-widest text-text-muted">
          {title} <span className="font-normal">({total})</span>
        </h3>
        {onAddCard && (
          <button
            onClick={onAddCard}
            className="flex items-center gap-1 text-[11px] text-text-muted hover:text-accent transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
              <path d="M8.75 3.75a.75.75 0 0 0-1.5 0v3.5h-3.5a.75.75 0 0 0 0 1.5h3.5v3.5a.75.75 0 0 0 1.5 0v-3.5h3.5a.75.75 0 0 0 0-1.5h-3.5v-3.5Z" />
            </svg>
            Add
          </button>
        )}
      </div>

      {cards.length === 0 ? (
        <p className="px-3 py-4 text-xs text-text-muted text-center">No cards</p>
      ) : (
        <div className="divide-y divide-border/50">
          {cards.map((card) => (
            <DeckCardItem
              key={card.uuid}
              card={card}
              onRemove={onRemove}
              onChangePrinting={onChangePrinting}
              onClick={onCardClick}
            />
          ))}
        </div>
      )}
    </div>
  );
}

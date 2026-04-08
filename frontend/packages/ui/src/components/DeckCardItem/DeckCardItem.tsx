import type { DeckCard } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type DeckCardItemProps = {
  card: DeckCard;
  onRemove?: (uuid: string) => void;
  onClick?: (uuid: string) => void;
};

const rarityDots: Record<string, string> = {
  common: "bg-text-muted",
  uncommon: "bg-text-secondary",
  rare: "bg-amber-400",
  mythic: "bg-orange-500",
};

export function DeckCardItem({ card, onRemove, onClick }: DeckCardItemProps) {
  return (
    <div className="group flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-bg-hover transition-colors">
      {/* Quantity */}
      <span className="shrink-0 w-6 text-center text-xs font-bold text-text-muted tabular-nums">
        {card.count}×
      </span>

      {/* Card info — clickable */}
      <button
        onClick={() => onClick?.(card.uuid)}
        className="flex-1 min-w-0 flex items-center gap-2 text-left"
      >
        <span
          className={`shrink-0 w-1.5 h-1.5 rounded-full ${rarityDots[card.rarity] ?? "bg-text-muted"}`}
        />
        <span className="text-sm text-text-primary truncate group-hover:text-accent transition-colors">
          {card.name}
        </span>
        <span className="text-[10px] text-text-muted truncate hidden sm:inline">
          {card.type}
        </span>
      </button>

      {/* Mana cost */}
      <div className="shrink-0">
        <ManaSymbols cost={card.mana_cost} size="sm" />
      </div>

      {/* Price */}
      {card.price > 0 && (
        <span className="shrink-0 text-[11px] text-text-muted tabular-nums w-12 text-right">
          ${card.price.toFixed(2)}
        </span>
      )}

      {/* Ownership indicator */}
      {!card.owns_enough && (
        <span className="shrink-0 text-[9px] px-1 py-0.5 rounded bg-warning/15 text-warning font-medium">
          −{card.missing_count}
        </span>
      )}

      {/* Remove button — subtle, appears on hover */}
      {onRemove && (
        <button
          onClick={(e) => { e.stopPropagation(); onRemove(card.uuid); }}
          className="shrink-0 w-5 h-5 flex items-center justify-center rounded text-transparent group-hover:text-text-muted/40 hover:!text-danger hover:!bg-danger/10 transition-all"
          title="Remove from deck"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3 h-3">
            <path d="M5.28 4.22a.75.75 0 0 0-1.06 1.06L6.94 8l-2.72 2.72a.75.75 0 1 0 1.06 1.06L8 9.06l2.72 2.72a.75.75 0 1 0 1.06-1.06L9.06 8l2.72-2.72a.75.75 0 0 0-1.06-1.06L8 6.94 5.28 4.22Z" />
          </svg>
        </button>
      )}
    </div>
  );
}

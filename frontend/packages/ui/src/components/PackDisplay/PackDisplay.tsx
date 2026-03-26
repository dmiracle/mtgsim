import type { BoosterCard } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type PackDisplayProps = {
  cards: BoosterCard[];
  setName?: string;
  boosterType?: string;
  onCardClick?: (uuid: string) => void;
};

const rarityBorders: Record<string, string> = {
  common: "border-border",
  uncommon: "border-text-muted",
  rare: "border-amber-500",
  mythic: "border-orange-500",
};

export function PackDisplay({ cards, setName, boosterType, onCardClick }: PackDisplayProps) {
  if (cards.length === 0) {
    return (
      <div className="flex items-center justify-center py-16 text-text-muted">
        Open a pack to see cards
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {setName && (
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-text-secondary">{setName}</h3>
          {boosterType && (
            <span className="text-[10px] uppercase tracking-wide text-text-muted bg-bg-tertiary px-2 py-0.5 rounded">
              {boosterType}
            </span>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
        {cards.map((card, i) => (
          <button
            key={`${card.uuid}-${i}`}
            onClick={() => onCardClick?.(card.uuid)}
            className={`bg-bg-secondary border-2 ${rarityBorders[card.rarity] ?? "border-border"} rounded-lg overflow-hidden hover:border-accent transition-colors text-left group`}
          >
            {/* Image area */}
            <div className="aspect-[5/7] bg-bg-tertiary flex items-center justify-center relative">
              {card.image_url ? (
                <img src={card.image_url} alt={card.name} className="w-full h-full object-cover" loading="lazy" />
              ) : (
                <div className="text-center p-2">
                  <p className="text-text-muted text-xs font-medium">{card.name}</p>
                </div>
              )}
              {card.is_foil && (
                <span className="absolute top-1.5 right-1.5 text-[9px] font-bold uppercase tracking-wide bg-amber-500/90 text-amber-950 px-1.5 py-0.5 rounded">
                  Foil
                </span>
              )}
            </div>

            {/* Card info */}
            <div className="p-2 space-y-1">
              <div className="flex items-start justify-between gap-1">
                <h4 className="text-xs font-medium text-text-primary leading-tight group-hover:text-accent transition-colors truncate">
                  {card.name}
                </h4>
                <ManaSymbols cost={card.mana_cost} size="sm" shadow={false} />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-text-muted truncate">{card.type_line}</span>
                <span className="text-[10px] text-text-muted capitalize">{card.rarity}</span>
              </div>
              <div className="flex items-center justify-between">
                <SetBadge code={card.set_code} rarity={card.rarity as "common" | "uncommon" | "rare" | "mythic"} size="sm" />
                <span className="text-[10px] text-text-muted">{card.slot}</span>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

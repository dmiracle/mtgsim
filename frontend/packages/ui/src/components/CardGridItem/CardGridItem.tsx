import type { CardSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SetBadge } from "@/components/SetBadge/SetBadge";
import { CardHoverLarge } from "@/components/CardHoverLarge/CardHoverLarge";
import { PinnedBadge } from "@/components/PinnedBadge/PinnedBadge";

type CardGridItemProps = {
  card: CardSummary;
  pinned?: boolean;
  quantity?: number;
  onPin?: (uuid: string) => void;
  onAddToDeck?: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

const rarityBorders: Record<string, string> = {
  common: "border-border",
  uncommon: "border-text-muted",
  rare: "border-amber-500",
  mythic: "border-orange-500",
};

const rarityDots: Record<string, string> = {
  common: "bg-text-muted",
  uncommon: "bg-text-secondary",
  rare: "bg-amber-400",
  mythic: "bg-orange-500",
};

const colorBadges: Record<string, string> = {
  W: "bg-amber-100 text-amber-900",
  U: "bg-blue-200 text-blue-900",
  B: "bg-gray-400 text-gray-900",
  R: "bg-red-300 text-red-900",
  G: "bg-green-300 text-green-900",
  C: "bg-gray-300 text-gray-700",
};

export function CardGridItem({
  card,
  pinned = false,
  quantity,
  onPin,
  onAddToDeck,
  onAddToCollection,
  onClick,
  onSetClick,
}: CardGridItemProps) {
  return (
    <CardHoverLarge
      uuid={card.uuid}
      pinned={pinned}
      quantity={quantity}
      onPin={onPin}
      onAddToDeck={onAddToDeck}
      onClick={onClick}
      onSetClick={onSetClick}
    >
      <div
        className={`bg-bg-secondary border ${rarityBorders[card.rarity] ?? "border-border"} rounded-lg overflow-hidden hover:border-accent transition-colors group`}
      >
      {/* Image area */}
      <div
        className="aspect-[5/7] bg-bg-tertiary flex items-center justify-center cursor-pointer relative"
        onClick={() => onClick?.(card.uuid)}
      >
        {card.image_url ? (
          <img
            src={card.image_url}
            alt={card.name}
            className="w-full h-full object-cover"
            loading="lazy"
          />
        ) : (
          <div className="text-center p-4">
            <p className="text-text-muted text-sm font-medium">{card.name}</p>
            <p className="text-text-muted text-xs mt-1">{card.type}</p>
          </div>
        )}
        <div className="absolute top-2 left-2">
          <PinnedBadge pinned={pinned} onToggle={onPin ? () => onPin(card.uuid) : undefined} />
        </div>
        {quantity && quantity > 1 && (
          <span className="absolute top-2 right-2 bg-accent text-white text-xs font-bold w-6 h-6 rounded-full flex items-center justify-center">
            {quantity}
          </span>
        )}
      </div>

      {/* Card info */}
      <div className="p-3 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <h3
            className="text-sm font-medium text-text-primary leading-tight cursor-pointer hover:text-accent truncate"
            onClick={() => onClick?.(card.uuid)}
            title={card.name}
          >
            {card.name}
          </h3>
          <ManaSymbols cost={card.mana_cost} size="sm" />
        </div>

        <p className="text-xs text-text-muted truncate">{card.type}</p>

        {card.text && (
          <p className="text-xs text-text-muted line-clamp-2" title={card.text}>
            {card.text}
          </p>
        )}

        <div className="flex items-center justify-between pt-1 border-t border-border">
          <div className="flex items-center gap-2">
            <SetBadge
              code={card.set_code}
              rarity={card.rarity as "common" | "uncommon" | "rare" | "mythic"}
              size="sm"
              navigable
              onClick={() => onSetClick?.(card.set_code)}
            />
            <span className={`w-2 h-2 rounded-full ${rarityDots[card.rarity] ?? "bg-text-muted"}`} title={card.rarity} />
            {card.color_identity.map((c) => (
              <span
                key={c}
                className={`w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center ${colorBadges[c] ?? "bg-gray-500 text-white"}`}
              >
                {c}
              </span>
            ))}
          </div>
          {card.price > 0 && (
            <span className="text-xs text-success font-medium">
              ${card.price.toFixed(2)}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1 pt-1">
          <button
            onClick={() => onAddToDeck?.(card.uuid)}
            className="text-xs px-2 py-1 rounded bg-bg-tertiary text-text-muted hover:text-accent transition-colors"
            title="Add to active deck"
          >
            + Deck
          </button>
          {!card.owns && onAddToCollection && (
            <button
              onClick={() => onAddToCollection(card.uuid)}
              className="text-xs px-2 py-1 rounded bg-bg-tertiary text-text-muted hover:text-success transition-colors"
              title="Add to collection"
            >
              Own
            </button>
          )}
          {card.owns && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-success/15 text-success font-medium">
              ✓
            </span>
          )}
          <button
            onClick={() => navigator.clipboard.writeText(card.uuid)}
            className="text-xs px-2 py-1 rounded bg-bg-tertiary text-text-muted hover:text-text-secondary transition-colors ml-auto"
            title="Copy UUID"
          >
            UUID
          </button>
        </div>
      </div>
    </div>
    </CardHoverLarge>
  );
}

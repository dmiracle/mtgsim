import type { CardDetail } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SetBadge } from "@/components/SetBadge/SetBadge";
import { PinnedBadge } from "@/components/PinnedBadge/PinnedBadge";

type CardLargeViewProps = {
  card: CardDetail;
  pinned?: boolean;
  quantity?: number;
  onPin?: (uuid: string) => void;
  onAddToDeck?: (uuid: string) => void;
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

export function CardLargeView({
  card,
  pinned = false,
  quantity,
  onPin,
  onAddToDeck,
  onClick,
  onSetClick,
}: CardLargeViewProps) {
  const statParts: string[] = [];
  if (card.power !== null && card.toughness !== null) statParts.push(`${card.power}/${card.toughness}`);
  if (card.loyalty !== null) statParts.push(`Loyalty: ${card.loyalty}`);
  if (card.defense !== null) statParts.push(`Defense: ${card.defense}`);

  return (
    <div
      className={`bg-bg-secondary border-2 ${rarityBorders[card.rarity] ?? "border-border"} rounded-xl overflow-hidden w-[400px]`}
    >
      {/* Large image */}
      <div
        className="aspect-[5/7] bg-bg-tertiary flex items-center justify-center cursor-pointer relative"
        onClick={() => onClick?.(card.uuid)}
      >
        {card.image_url ? (
          <img
            src={card.image_url}
            alt={card.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-center p-6">
            <p className="text-text-muted text-base font-medium">{card.name}</p>
            <p className="text-text-muted text-sm mt-1">{card.type}</p>
          </div>
        )}
        <div className="absolute top-3 left-3">
          <PinnedBadge pinned={pinned} onToggle={onPin ? () => onPin(card.uuid) : undefined} size="md" />
        </div>
        {quantity && quantity > 1 && (
          <span className="absolute top-3 right-3 bg-accent text-white text-sm font-bold w-8 h-8 rounded-full flex items-center justify-center">
            {quantity}
          </span>
        )}
      </div>

      {/* Card info */}
      <div className="p-4 space-y-3">
        {/* Name + mana cost */}
        <div className="flex items-start justify-between gap-3">
          <h3
            className="text-base font-bold text-text-primary leading-tight cursor-pointer hover:text-accent"
            onClick={() => onClick?.(card.uuid)}
          >
            {card.name}
          </h3>
          <div className="flex items-center gap-2 shrink-0">
            <ManaSymbols cost={card.mana_cost} size="md" />
            <span className="text-[10px] text-text-muted bg-bg-tertiary rounded px-1.5 py-0.5">
              MV {card.mana_value}
            </span>
          </div>
        </div>

        {/* Type line + stats */}
        <div className="flex items-center justify-between">
          <p className="text-sm text-text-secondary">{card.type}</p>
          {statParts.length > 0 && (
            <div className="flex items-center gap-1.5">
              {statParts.map((s) => (
                <span key={s} className="text-sm font-semibold text-text-primary bg-bg-tertiary rounded px-2 py-0.5">
                  {s}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Oracle text — full, untruncated */}
        {card.text && (
          <div className="bg-bg-tertiary rounded-lg p-3 space-y-1">
            {card.text.split("\n").map((line, i) => (
              <p key={i} className="text-sm text-text-primary leading-relaxed">
                {line}
              </p>
            ))}
          </div>
        )}

        {/* Flavor text */}
        {card.flavor_text && (
          <div className="border-l-2 border-border pl-3">
            <p className="text-xs text-text-muted italic leading-relaxed">{card.flavor_text}</p>
          </div>
        )}

        {/* Keywords */}
        {card.keywords.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {card.keywords.map((kw) => (
              <span
                key={kw}
                className="px-2 py-0.5 text-xs rounded bg-bg-tertiary text-text-secondary border border-border"
              >
                {kw}
              </span>
            ))}
          </div>
        )}

        {/* Set, rarity, colors, price */}
        <div className="flex items-center justify-between pt-2 border-t border-border">
          <div className="flex items-center gap-2">
            <SetBadge
              code={card.set_code}
              name={card.set_name}
              rarity={card.rarity as "common" | "uncommon" | "rare" | "mythic"}
              size="sm"
              navigable
              onClick={() => onSetClick?.(card.set_code)}
            />
            <span className={`w-2.5 h-2.5 rounded-full ${rarityDots[card.rarity] ?? "bg-text-muted"}`} title={card.rarity} />
            {card.color_identity.map((c) => (
              <span
                key={c}
                className={`w-5 h-5 rounded-full text-[10px] font-bold flex items-center justify-center ${colorBadges[c] ?? "bg-gray-500 text-white"}`}
              >
                {c}
              </span>
            ))}
          </div>
          {card.all_prices.length > 0 && (
            <span className="text-sm text-success font-semibold">
              ${card.all_prices[0].price.toFixed(2)}
            </span>
          )}
        </div>

        {/* Ownership */}
        {(card.owns || card.wants) && (
          <div className="flex items-center gap-2">
            {card.owns && (
              <span className="text-[11px] text-success bg-success/15 px-2 py-0.5 rounded font-semibold">
                Owned ({card.total_owned})
              </span>
            )}
            {card.wants && (
              <span className="text-[11px] text-warning bg-warning/15 px-2 py-0.5 rounded font-semibold">
                Wanted ({card.total_wanted})
              </span>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-1.5 pt-1">
          <button
            onClick={() => onAddToDeck?.(card.uuid)}
            className="text-xs px-2.5 py-1 rounded bg-bg-tertiary text-text-muted hover:text-accent transition-colors"
          >
            + Deck
          </button>
          <button
            onClick={() => navigator.clipboard.writeText(card.uuid)}
            className="text-xs px-2.5 py-1 rounded bg-bg-tertiary text-text-muted hover:text-text-secondary transition-colors ml-auto"
          >
            UUID
          </button>
        </div>
      </div>
    </div>
  );
}

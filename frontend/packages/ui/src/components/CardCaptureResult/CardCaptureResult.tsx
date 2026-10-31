import type { CardSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type CardCaptureResultProps = {
  card: CardSummary;
  confidence: number;
  onAddToDeck?: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onDismiss?: () => void;
  onSetClick?: (code: string) => void;
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

function confidenceLabel(c: number): { text: string; color: string } {
  if (c >= 0.9) return { text: "High match", color: "text-success" };
  if (c >= 0.7) return { text: "Likely match", color: "text-warning" };
  return { text: "Low confidence", color: "text-error" };
}

export function CardCaptureResult({
  card,
  confidence,
  onAddToDeck,
  onAddToCollection,
  onDismiss,
  onSetClick,
}: CardCaptureResultProps) {
  const { text: confText, color: confColor } = confidenceLabel(confidence);

  return (
    <div className="bg-bg-secondary border border-border rounded-xl overflow-hidden animate-in slide-in-from-bottom-4 duration-300">
      <div className="flex gap-4 p-4">
        {/* Card image thumbnail */}
        <div className="w-24 shrink-0">
          <div className="aspect-[5/7] bg-bg-tertiary rounded-lg overflow-hidden">
            {card.image_url ? (
              <img
                src={card.image_url}
                alt={card.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <span className="text-text-muted text-xs text-center px-1">
                  {card.name}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Card info */}
        <div className="flex-1 min-w-0 space-y-2">
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-base font-bold text-text-primary leading-tight truncate">
              {card.name}
            </h3>
            <ManaSymbols cost={card.mana_cost} size="sm" />
          </div>

          <p className="text-xs text-text-muted truncate">{card.type}</p>

          {/* Confidence */}
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-bg-tertiary rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  confidence >= 0.9
                    ? "bg-success"
                    : confidence >= 0.7
                      ? "bg-warning"
                      : "bg-error"
                }`}
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
            <span className={`text-xs font-medium ${confColor}`}>
              {confText}
            </span>
          </div>

          {/* Set + rarity + colors */}
          <div className="flex items-center gap-2">
            <SetBadge
              code={card.set_code}
              rarity={card.rarity as "common" | "uncommon" | "rare" | "mythic"}
              size="sm"
              navigable
              onClick={() => onSetClick?.(card.set_code)}
            />
            <span
              className={`w-2 h-2 rounded-full ${rarityDots[card.rarity] ?? "bg-text-muted"}`}
              title={card.rarity}
            />
            {card.color_identity.map((c) => (
              <span
                key={c}
                className={`w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center ${colorBadges[c] ?? "bg-gray-500 text-white"}`}
              >
                {c}
              </span>
            ))}
            {card.price > 0 && (
              <span className="text-xs text-success font-medium ml-auto">
                ${card.price.toFixed(2)}
              </span>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1.5 pt-1">
            {onAddToDeck && (
              <button
                onClick={() => onAddToDeck(card.uuid)}
                className="text-xs px-3 py-1.5 rounded bg-accent text-white hover:bg-accent/80 transition-colors"
              >
                + Deck
              </button>
            )}
            {onAddToCollection && !card.owns && (
              <button
                onClick={() => onAddToCollection(card.uuid)}
                className="text-xs px-3 py-1.5 rounded bg-bg-tertiary text-text-muted hover:text-success transition-colors"
              >
                Own
              </button>
            )}
            {card.owns && (
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-success/15 text-success font-medium">
                Owned ({card.total_owned})
              </span>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-xs px-3 py-1.5 rounded bg-bg-tertiary text-text-muted hover:text-text-secondary transition-colors ml-auto"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

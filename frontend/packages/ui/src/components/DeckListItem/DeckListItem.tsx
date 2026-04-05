import type { DeckSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { PinButton } from "@/components/PinButton/PinButton";

type DeckListItemProps = {
  deck: DeckSummary;
  pinned?: boolean;
  onTogglePin?: (file: string) => void;
  onDuplicate?: (file: string) => void;
  onDelete?: (file: string) => void;
  onClick: (file: string) => void;
};

const colorToCost: Record<string, string> = {
  W: "{W}", U: "{U}", B: "{B}", R: "{R}", G: "{G}", C: "{C}",
};

export function DeckListItem({ deck, pinned, onTogglePin, onDuplicate, onDelete, onClick }: DeckListItemProps) {
  const isUserDeck = deck.source === "user" || deck.source === "import";
  const legalFormats = Object.entries(deck.legality)
    .filter(([, v]) => v)
    .map(([k]) => k);

  const hasActions = onTogglePin || onDuplicate || (isUserDeck && onDelete);

  return (
    <div
      className="flex items-center gap-4 px-4 py-3 border border-border bg-bg-secondary rounded-lg hover:bg-bg-hover hover:border-border-hover transition-colors cursor-pointer group"
      onClick={() => onClick(deck.file)}
    >
      {/* Color identity */}
      <div className="shrink-0">
        <ManaSymbols
          cost={deck.colors.map((c) => colorToCost[c] ?? "").join("")}
          size="sm"
          shadow={false}
        />
      </div>

      {/* Name + meta */}
      <div className="flex-1 min-w-0">
        <h3 className="text-sm font-medium text-text-primary group-hover:text-accent transition-colors truncate">
          {deck.name}
        </h3>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-[10px] uppercase tracking-wide text-text-muted">{deck.source}</span>
          <span className="text-text-muted">·</span>
          <span className="text-xs text-text-muted">{deck.card_count} cards</span>
          {legalFormats.length > 0 && (
            <>
              <span className="text-text-muted">·</span>
              <span className="text-xs text-text-muted truncate">
                {legalFormats.slice(0, 3).join(", ")}
                {legalFormats.length > 3 && ` +${legalFormats.length - 3}`}
              </span>
            </>
          )}
        </div>
      </div>

      {/* Price */}
      {deck.price > 0 && (
        <span className="text-sm font-medium text-success shrink-0">
          ${deck.price.toFixed(0)}
        </span>
      )}

      {/* Actions */}
      {hasActions && (
        <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
          {onTogglePin && (
            <PinButton
              pinned={!!pinned}
              onToggle={() => onTogglePin(deck.file)}
              size="sm"
            />
          )}
          {onDuplicate && (
            <button
              onClick={() => onDuplicate(deck.file)}
              title="Duplicate deck"
              className="text-xs px-2 py-1 rounded font-medium border transition-colors bg-bg-tertiary text-text-muted border-border hover:text-accent hover:border-accent/40"
            >
              Copy
            </button>
          )}
          {isUserDeck && onDelete && (
            <button
              onClick={() => onDelete(deck.file)}
              title="Delete deck"
              className="text-xs px-2 py-1 rounded font-medium border transition-colors bg-bg-tertiary text-text-muted border-border hover:text-danger hover:border-danger/40"
            >
              Del
            </button>
          )}
        </div>
      )}
    </div>
  );
}

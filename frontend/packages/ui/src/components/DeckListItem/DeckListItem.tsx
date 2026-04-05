import type { DeckSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { PinnedBadge } from "@/components/PinnedBadge/PinnedBadge";

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

const iconBtn = "text-xs w-7 h-7 rounded flex items-center justify-center border transition-colors";
const iconBtnEnabled = "bg-bg-tertiary text-text-muted border-border";
const iconBtnDisabled = "bg-bg-tertiary text-text-muted/20 border-border/50 cursor-default";

export function DeckListItem({ deck, pinned, onTogglePin, onDuplicate, onDelete, onClick }: DeckListItemProps) {
  const isUserDeck = deck.source === "user" || deck.source === "import";
  const legalFormats = Object.entries(deck.legality)
    .filter(([, v]) => v)
    .map(([k]) => k);

  return (
    <div
      className="relative flex items-center gap-3 px-4 py-3 border border-border bg-bg-secondary rounded-lg hover:bg-bg-hover hover:border-border-hover transition-colors cursor-pointer group"
      onClick={() => onClick(deck.file)}
    >
      {/* Pinned badge — floating top-left */}
      <div className="absolute -top-2 -left-2 z-10" onClick={(e) => e.stopPropagation()}>
        <PinnedBadge
          pinned={!!pinned}
          onToggle={onTogglePin ? () => onTogglePin(deck.file) : undefined}
        />
      </div>

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

      {/* Actions — always visible */}
      <div className="flex items-center gap-1 shrink-0" onClick={(e) => e.stopPropagation()}>
        <button
          onClick={onDuplicate ? () => onDuplicate(deck.file) : undefined}
          title="Duplicate deck"
          disabled={!onDuplicate}
          className={`${iconBtn} ${onDuplicate ? `${iconBtnEnabled} hover:text-accent hover:border-accent/40` : iconBtnDisabled}`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
            <path d="M5.5 3.5A1.5 1.5 0 0 1 7 2h5.5A1.5 1.5 0 0 1 14 3.5V9a1.5 1.5 0 0 1-1.5 1.5H7A1.5 1.5 0 0 1 5.5 9V3.5Z" />
            <path d="M3 5a1.5 1.5 0 0 0-1.5 1.5v6A1.5 1.5 0 0 0 3 14h6a1.5 1.5 0 0 0 1.5-1.5v-.5H7A2.5 2.5 0 0 1 4.5 9.5V5H3Z" />
          </svg>
        </button>
        <button
          onClick={isUserDeck && onDelete ? () => onDelete(deck.file) : undefined}
          title="Delete deck"
          disabled={!isUserDeck || !onDelete}
          className={`${iconBtn} ${isUserDeck && onDelete ? `${iconBtnEnabled} hover:text-danger hover:border-danger/40` : iconBtnDisabled}`}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
            <path fillRule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z" clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
}

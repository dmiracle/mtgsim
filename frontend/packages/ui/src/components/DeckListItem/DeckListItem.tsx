import type { DeckSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type DeckListItemProps = {
  deck: DeckSummary;
  pinned?: boolean;
  onTogglePin?: (file: string) => void;
  onDelete?: (file: string) => void;
  onClick: (file: string) => void;
};

const colorToCost: Record<string, string> = {
  W: "{W}", U: "{U}", B: "{B}", R: "{R}", G: "{G}", C: "{C}",
};

export function DeckListItem({ deck, pinned, onTogglePin, onDelete, onClick }: DeckListItemProps) {
  const isUserDeck = deck.source === "user" || deck.source === "import";
  const legalFormats = Object.entries(deck.legality)
    .filter(([, v]) => v)
    .map(([k]) => k);

  return (
    <div className="relative flex items-center gap-0">
      {onTogglePin && (
        <button
          onClick={(e) => { e.stopPropagation(); onTogglePin(deck.file); }}
          className={`shrink-0 w-8 h-full flex items-center justify-center rounded-l-lg border border-r-0 border-border transition-colors ${
            pinned
              ? "text-accent bg-bg-secondary"
              : "text-text-muted/30 hover:text-text-muted bg-bg-secondary"
          }`}
          title={pinned ? "Unpin deck" : "Pin deck"}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
            <path d="M10.97 2.22a.75.75 0 0 1 1.06 0l1.75 1.75a.75.75 0 0 1-.177 1.2l-2.28 1.14-.876 1.753a.75.75 0 0 1-.156.222L8.854 9.69l2.478 2.478a.75.75 0 1 1-1.06 1.06L7.793 10.75l-1.384 1.384a.75.75 0 0 1-.222.156l-1.753.876-1.14 2.28a.75.75 0 0 1-1.2.177L.22 13.75a.75.75 0 0 1 .177-1.2l2.28-1.14.876-1.753a.75.75 0 0 1 .156-.222L5.31 7.854 2.832 5.375a.75.75 0 1 1 1.061-1.06L6.37 6.793l1.584-1.584a.75.75 0 0 1 .222-.156l1.753-.876 1.14-2.28a.75.75 0 0 1 .1-.136Z" />
          </svg>
        </button>
      )}
      <button
        onClick={() => onClick(deck.file)}
        className={`w-full flex items-center gap-4 px-4 py-3 border border-border bg-bg-secondary hover:bg-bg-hover hover:border-border-hover transition-colors text-left group ${
          !onTogglePin && !(isUserDeck && onDelete) ? "rounded-lg" : ""
        } ${!onTogglePin ? "rounded-l-lg" : ""} ${!(isUserDeck && onDelete) ? "rounded-r-lg" : ""}`}
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
      </button>

      {/* Delete */}
      {isUserDeck && onDelete && (
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(deck.file); }}
          className="shrink-0 w-8 h-full flex items-center justify-center rounded-r-lg border border-l-0 border-border bg-bg-secondary text-text-muted/30 hover:text-danger hover:bg-danger/10 transition-colors"
          title="Delete deck"
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
            <path fillRule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z" clipRule="evenodd" />
          </svg>
        </button>
      )}
    </div>
  );
}

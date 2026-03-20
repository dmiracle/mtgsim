import type { DeckSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type DeckListItemProps = {
  deck: DeckSummary;
  onClick: (file: string) => void;
};

const colorToCost: Record<string, string> = {
  W: "{W}", U: "{U}", B: "{B}", R: "{R}", G: "{G}", C: "{C}",
};

export function DeckListItem({ deck, onClick }: DeckListItemProps) {
  const legalFormats = Object.entries(deck.legality)
    .filter(([, v]) => v)
    .map(([k]) => k);

  return (
    <button
      onClick={() => onClick(deck.file)}
      className="w-full flex items-center gap-4 px-4 py-3 rounded-lg border border-border bg-bg-secondary hover:bg-bg-hover hover:border-border-hover transition-colors text-left group"
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
  );
}

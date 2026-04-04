import { useState } from "react";
import type { DeckDetail, TagCount } from "@/types/api";
import { DeckStats } from "@/components/DeckStats/DeckStats";
import { DeckCards } from "@/components/DeckCards/DeckCards";
import { RawJsonViewer } from "@/components/RawJsonViewer/RawJsonViewer";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";

type DeckDetailPageProps = {
  deck: DeckDetail;
  availableTags?: TagCount[];
  pinned?: boolean;
  onTogglePin?: () => void;
  onDelete?: () => void;
  onBack: () => void;
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [], manaValue: [],
  ownership: "all", sort: "name", order: "asc", unique: false, priceMode: "min", subtype: "", sets: [], formats: [],
};

export function DeckDetailPage({ deck, availableTags = [], pinned, onTogglePin, onDelete, onBack, onCardClick, onSetClick }: DeckDetailPageProps) {
  const [tab, setTab] = useState<"stats" | "cards">("stats");
  const [filters, setFilters] = useState(emptyFilters);

  const tabs = [
    { id: "stats" as const, label: "Statistics" },
    { id: "cards" as const, label: "Cards" },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>
        {onTogglePin && (
          <button
            onClick={onTogglePin}
            className={`transition-colors ${pinned ? "text-accent" : "text-text-muted/40 hover:text-text-muted"}`}
            title={pinned ? "Unpin deck" : "Pin deck"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
              <path d="M10.97 2.22a.75.75 0 0 1 1.06 0l1.75 1.75a.75.75 0 0 1-.177 1.2l-2.28 1.14-.876 1.753a.75.75 0 0 1-.156.222L8.854 9.69l2.478 2.478a.75.75 0 1 1-1.06 1.06L7.793 10.75l-1.384 1.384a.75.75 0 0 1-.222.156l-1.753.876-1.14 2.28a.75.75 0 0 1-1.2.177L.22 13.75a.75.75 0 0 1 .177-1.2l2.28-1.14.876-1.753a.75.75 0 0 1 .156-.222L5.31 7.854 2.832 5.375a.75.75 0 1 1 1.061-1.06L6.37 6.793l1.584-1.584a.75.75 0 0 1 .222-.156l1.753-.876 1.14-2.28a.75.75 0 0 1 .1-.136Z" />
            </svg>
          </button>
        )}
        {onDelete && (
          <button
            onClick={onDelete}
            className="text-text-muted/40 hover:text-danger transition-colors"
            title="Delete deck"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-4 h-4">
              <path fillRule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z" clipRule="evenodd" />
            </svg>
          </button>
        )}
        <div className="min-w-0">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary truncate">{deck.meta.name}</h2>
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-0.5">
            {deck.meta.format && <span className="text-xs text-text-muted capitalize">{deck.meta.format}</span>}
            <span className="text-xs text-text-muted">{deck.meta.source}</span>
            {deck.meta.release_date && <span className="text-xs text-text-muted">{deck.meta.release_date}</span>}
          </div>
        </div>
      </div>

      {deck.meta.description && (
        <p className="text-sm text-text-secondary">{deck.meta.description}</p>
      )}

      {/* Tabs */}
      <div className="flex items-center gap-1 border-b border-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
              tab === t.id
                ? "border-accent text-accent"
                : "border-transparent text-text-muted hover:text-text-secondary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === "stats" && (
        <DeckStats stats={deck.stats} legality={deck.legality} price={deck.price} tags={availableTags} />
      )}
      {tab === "cards" && (
        <DeckCards
          commander={deck.commander}
          main_board={deck.main_board}
          side_board={deck.side_board}
          filters={filters}
          onFiltersChange={setFilters}
          availableTags={availableTags}
          onCardClick={onCardClick}
          onSetClick={onSetClick}
        />
      )}

      <RawJsonViewer data={deck} title="Deck JSON" />
    </div>
  );
}

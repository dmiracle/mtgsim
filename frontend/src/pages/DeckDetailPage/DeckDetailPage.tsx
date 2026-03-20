import { useState } from "react";
import type { DeckDetail, TagCount } from "@/types/api";
import { DeckStats } from "@/components/DeckStats/DeckStats";
import { DeckCards } from "@/components/DeckCards/DeckCards";
import { RawJsonViewer } from "@/components/RawJsonViewer/RawJsonViewer";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";

type DeckDetailPageProps = {
  deck: DeckDetail;
  availableTags?: TagCount[];
  onBack: () => void;
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [],
  ownership: "all", sort: "name", order: "asc", unique: false,
};

export function DeckDetailPage({ deck, availableTags = [], onBack, onCardClick, onSetClick }: DeckDetailPageProps) {
  const [tab, setTab] = useState<"stats" | "cards">("stats");
  const [filters, setFilters] = useState(emptyFilters);

  const tabs = [
    { id: "stats" as const, label: "Statistics" },
    { id: "cards" as const, label: "Cards" },
  ];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>
        <div>
          <h2 className="text-xl font-bold text-text-primary">{deck.meta.name}</h2>
          <div className="flex items-center gap-2 mt-0.5">
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
        <DeckStats stats={deck.stats} legality={deck.legality} price={deck.price} />
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

import { useState } from "react";
import type { CardSummary, DeckDetail, TagCount } from "@/types/api";
import { DeckStats } from "@/components/DeckStats/DeckStats";
import { DeckCards } from "@/components/DeckCards/DeckCards";
import { DeckCardList } from "@/components/DeckCardList/DeckCardList";
import { AddCardToDeckModal } from "@/components/AddCardToDeckModal/AddCardToDeckModal";
import { PinButton } from "@/components/PinButton/PinButton";
import { RawJsonViewer } from "@/components/RawJsonViewer/RawJsonViewer";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";

type DeckDetailPageProps = {
  deck: DeckDetail;
  availableTags?: TagCount[];
  pinned?: boolean;
  editable?: boolean;
  searchResults?: CardSummary[];
  searching?: boolean;
  onTogglePin?: () => void;
  onDuplicate?: () => void;
  onDelete?: () => void;
  onBack: () => void;
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
  onAddCard?: (uuid: string, board: string, count: number) => void;
  onRemoveCard?: (uuid: string) => void;
  onSearchCards?: (query: string) => void;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [], manaValue: [],
  ownership: "all", sort: "name", order: "asc", unique: false, priceMode: "min", subtype: "", sets: [], formats: [],
};

export function DeckDetailPage({
  deck,
  availableTags = [],
  pinned,
  editable = false,
  searchResults = [],
  searching = false,
  onTogglePin,
  onDuplicate,
  onDelete,
  onBack,
  onCardClick,
  onSetClick,
  onAddCard,
  onRemoveCard,
  onSearchCards,
}: DeckDetailPageProps) {
  const [tab, setTab] = useState<"stats" | "cards" | "edit">("stats");
  const [filters, setFilters] = useState(emptyFilters);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [addBoard, setAddBoard] = useState("main");

  const tabs = [
    { id: "stats" as const, label: "Statistics" },
    { id: "cards" as const, label: "Cards" },
    ...(editable ? [{ id: "edit" as const, label: "Edit" }] : []),
  ];

  function openAddModal(board?: string) {
    if (board) setAddBoard(board);
    setAddModalOpen(true);
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3">
        <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>
        <div className="min-w-0">
          <h2 className="text-lg sm:text-xl font-bold text-text-primary truncate">{deck.meta.name}</h2>
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-0.5">
            {deck.meta.format && <span className="text-xs text-text-muted capitalize">{deck.meta.format}</span>}
            <span className="text-xs text-text-muted">{deck.meta.source}</span>
            {deck.meta.release_date && <span className="text-xs text-text-muted">{deck.meta.release_date}</span>}
          </div>
        </div>
        <div className="flex items-center gap-1 ml-auto shrink-0">
          {onTogglePin && (
            <PinButton pinned={!!pinned} onToggle={onTogglePin} size="sm" />
          )}
          {onDuplicate && (
            <button
              onClick={onDuplicate}
              title="Duplicate deck"
              className="text-xs px-2 py-1 rounded font-medium border transition-colors bg-bg-tertiary text-text-muted border-border hover:text-accent hover:border-accent/40"
            >
              Copy
            </button>
          )}
          {onDelete && (
            <button
              onClick={onDelete}
              title="Delete deck"
              className="text-xs px-2 py-1 rounded font-medium border transition-colors bg-bg-tertiary text-text-muted border-border hover:text-danger hover:border-danger/40"
            >
              Del
            </button>
          )}
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
      {tab === "edit" && editable && (
        <div className="space-y-4">
          {deck.commander.length > 0 && (
            <DeckCardList
              title="Commander"
              cards={deck.commander}
              onRemove={onRemoveCard}
              onCardClick={onCardClick}
              onAddCard={() => openAddModal("commander")}
            />
          )}
          <DeckCardList
            title="Main Board"
            cards={deck.main_board}
            onRemove={onRemoveCard}
            onCardClick={onCardClick}
            onAddCard={() => openAddModal("main")}
          />
          <DeckCardList
            title="Sideboard"
            cards={deck.side_board}
            onRemove={onRemoveCard}
            onCardClick={onCardClick}
            onAddCard={() => openAddModal("side")}
          />
        </div>
      )}

      <RawJsonViewer data={deck} title="Deck JSON" />

      {/* Add card modal */}
      {onAddCard && onSearchCards && (
        <AddCardToDeckModal
          open={addModalOpen}
          deckName={deck.meta.name}
          defaultBoard={addBoard}
          searchResults={searchResults}
          searching={searching}
          onSearch={onSearchCards}
          onAdd={(uuid, board, count) => {
            onAddCard(uuid, board, count);
          }}
          onClose={() => setAddModalOpen(false)}
        />
      )}
    </div>
  );
}

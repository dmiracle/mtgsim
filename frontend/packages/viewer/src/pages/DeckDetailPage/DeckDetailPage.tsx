import { useState } from "react";
import type { CardSummary, DeckDetail, TagCount } from "@/types/api";
import { DeckStats } from "@/components/DeckStats/DeckStats";
import { DeckCards } from "@/components/DeckCards/DeckCards";
import { DeckCardList } from "@/components/DeckCardList/DeckCardList";
import { AddCardToDeckModal } from "@/components/AddCardToDeckModal/AddCardToDeckModal";
import { PinnedBadge } from "@/components/PinnedBadge/PinnedBadge";
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
  onRename?: (name: string) => void;
};

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [], manaValue: [],
  ownership: "all", platform: "any", sort: "name", order: "asc", unique: false, priceMode: "min", subtype: "", sets: [], formats: [],
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
  onRename,
}: DeckDetailPageProps) {
  const [tab, setTab] = useState<"stats" | "cards" | "edit">("stats");
  const [filters, setFilters] = useState(emptyFilters);
  const [addModalOpen, setAddModalOpen] = useState(false);
  const [addBoard, setAddBoard] = useState("main");
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState(deck.meta.name);

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
      <div className="relative flex flex-wrap items-center gap-2 sm:gap-3">
        <div className="absolute -top-2 -left-2 z-10">
          <PinnedBadge pinned={!!pinned} onToggle={onTogglePin} size="md" />
        </div>
        <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            {editing ? (
              <input
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && editName.trim()) {
                    onRename?.(editName.trim());
                    setEditing(false);
                  }
                  if (e.key === "Escape") {
                    setEditName(deck.meta.name);
                    setEditing(false);
                  }
                }}
                onBlur={() => {
                  if (editName.trim() && editName.trim() !== deck.meta.name) {
                    onRename?.(editName.trim());
                  } else {
                    setEditName(deck.meta.name);
                  }
                  setEditing(false);
                }}
                autoFocus
                className="text-lg sm:text-xl font-bold text-text-primary bg-bg-tertiary border border-accent rounded px-2 py-0.5 -ml-2 focus:outline-none"
              />
            ) : (
              <h2 className="text-lg sm:text-xl font-bold text-text-primary truncate">{deck.meta.name}</h2>
            )}
            <button
              onClick={() => { if (onRename) { setEditName(deck.meta.name); setEditing(true); } }}
              disabled={!onRename}
              title={onRename ? "Rename deck" : "Cannot rename precon decks"}
              className={`shrink-0 w-6 h-6 rounded flex items-center justify-center transition-colors ${onRename ? "text-text-muted hover:text-accent" : "text-text-muted/20 cursor-default"}`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
                <path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z" />
                <path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z" />
              </svg>
            </button>
          </div>
          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-0.5">
            {deck.meta.format && <span className="text-xs text-text-muted capitalize">{deck.meta.format}</span>}
            <span className="text-xs text-text-muted">{deck.meta.source}</span>
            {deck.meta.release_date && <span className="text-xs text-text-muted">{deck.meta.release_date}</span>}
          </div>
        </div>
        <div className="flex items-center gap-1 ml-auto shrink-0">
          <button
            onClick={onDuplicate}
            title="Duplicate deck"
            disabled={!onDuplicate}
            className={`text-xs w-7 h-7 rounded flex items-center justify-center border transition-colors ${onDuplicate ? "bg-bg-tertiary text-text-muted border-border hover:text-accent hover:border-accent/40" : "bg-bg-tertiary text-text-muted/20 border-border/50 cursor-default"}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
              <path d="M5.5 3.5A1.5 1.5 0 0 1 7 2h5.5A1.5 1.5 0 0 1 14 3.5V9a1.5 1.5 0 0 1-1.5 1.5H7A1.5 1.5 0 0 1 5.5 9V3.5Z" />
              <path d="M3 5a1.5 1.5 0 0 0-1.5 1.5v6A1.5 1.5 0 0 0 3 14h6a1.5 1.5 0 0 0 1.5-1.5v-.5H7A2.5 2.5 0 0 1 4.5 9.5V5H3Z" />
            </svg>
          </button>
          <button
            onClick={onDelete}
            title="Delete deck"
            disabled={!onDelete}
            className={`text-xs w-7 h-7 rounded flex items-center justify-center border transition-colors ${onDelete ? "bg-bg-tertiary text-text-muted border-border hover:text-danger hover:border-danger/40" : "bg-bg-tertiary text-text-muted/20 border-border/50 cursor-default"}`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" className="w-3.5 h-3.5">
              <path fillRule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5A.75.75 0 0 1 9.95 6Z" clipRule="evenodd" />
            </svg>
          </button>
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

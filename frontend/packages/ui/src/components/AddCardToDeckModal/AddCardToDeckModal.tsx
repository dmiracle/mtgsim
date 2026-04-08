import { useState, useEffect } from "react";
import type { CardSummary } from "@/types/api";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type AddCardToDeckModalProps = {
  open: boolean;
  deckName: string;
  defaultBoard?: string;
  searchResults: CardSummary[];
  searching?: boolean;
  onSearch: (query: string) => void;
  onAdd: (uuid: string, board: string, count: number) => void;
  onClose: () => void;
};

const BOARDS = [
  { id: "main", label: "Main" },
  { id: "side", label: "Side" },
  { id: "commander", label: "Cmdr" },
];

export function AddCardToDeckModal({
  open,
  deckName,
  defaultBoard = "main",
  searchResults,
  searching = false,
  onSearch,
  onAdd,
  onClose,
}: AddCardToDeckModalProps) {
  const [query, setQuery] = useState("");
  const [board, setBoard] = useState(defaultBoard);
  const [count, setCount] = useState(1);

  useEffect(() => {
    setBoard(defaultBoard);
  }, [defaultBoard]);

  if (!open) return null;

  function handleSearch(val: string) {
    setQuery(val);
    if (val.length >= 2) onSearch(val);
  }

  function handleAdd(card: CardSummary) {
    onAdd(card.uuid, board, count);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50" onClick={onClose}>
      <div
        className="bg-bg-secondary border border-border rounded-t-xl sm:rounded-xl w-full sm:max-w-md shadow-xl max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <div className="min-w-0">
            <h2 className="text-sm font-semibold text-text-primary">Add Card</h2>
            <p className="text-[11px] text-text-muted truncate">to {deckName}</p>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg leading-none">&times;</button>
        </div>

        {/* Search + options */}
        <div className="px-4 pt-3 pb-2 space-y-2 shrink-0">
          <input
            type="text"
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="Search by name or oracle text..."
            autoFocus
            className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent"
          />

          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 bg-bg-tertiary rounded-lg p-0.5">
              {BOARDS.map((b) => (
                <button
                  key={b.id}
                  onClick={() => setBoard(b.id)}
                  className={`text-[11px] px-2 py-1 rounded-md transition-colors ${
                    board === b.id
                      ? "bg-accent text-white"
                      : "text-text-muted hover:text-text-secondary"
                  }`}
                >
                  {b.label}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1 ml-auto">
              <button
                onClick={() => setCount(Math.max(1, count - 1))}
                className="w-6 h-6 flex items-center justify-center rounded bg-bg-tertiary text-text-muted hover:text-text-primary text-xs"
              >
                −
              </button>
              <span className="w-6 text-center text-xs font-medium text-text-primary tabular-nums">{count}</span>
              <button
                onClick={() => setCount(Math.min(99, count + 1))}
                className="w-6 h-6 flex items-center justify-center rounded bg-bg-tertiary text-text-muted hover:text-text-primary text-xs"
              >
                +
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto px-2 pb-3">
          {searching && (
            <p className="text-xs text-text-muted text-center py-6">Searching...</p>
          )}

          {!searching && query.length >= 2 && searchResults.length === 0 && (
            <p className="text-xs text-text-muted text-center py-6">No cards found</p>
          )}

          {!searching && query.length < 2 && (
            <p className="text-xs text-text-muted text-center py-6">Type at least 2 characters</p>
          )}

          {searchResults.map((card) => (
            <button
              key={card.uuid}
              onClick={() => handleAdd(card)}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-bg-hover transition-colors text-left group"
            >
              {/* Thumbnail */}
              <div className="shrink-0 w-8 h-11 rounded bg-bg-tertiary overflow-hidden">
                {card.image_url ? (
                  <img src={card.image_url} alt="" className="w-full h-full object-cover" loading="lazy" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-[8px] text-text-muted">?</div>
                )}
              </div>

              {/* Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-text-primary truncate group-hover:text-accent transition-colors">
                    {card.name}
                  </span>
                  <ManaSymbols cost={card.mana_cost} size="sm" />
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-text-muted truncate">{card.type}</span>
                  {card.price > 0 && (
                    <span className="text-[10px] text-success">${card.price.toFixed(2)}</span>
                  )}
                </div>
              </div>

              {/* Add indicator */}
              <span className="shrink-0 text-[10px] text-text-muted group-hover:text-accent transition-colors">
                +{count}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

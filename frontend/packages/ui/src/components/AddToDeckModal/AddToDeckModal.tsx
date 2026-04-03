import { useState } from "react";
import type { UserDeckResponse } from "@/types/api";

type AddToDeckModalProps = {
  open: boolean;
  cardName: string;
  cardUuid: string;
  decks: UserDeckResponse[];
  onClose: () => void;
  onAdd: (deckId: number, board: string, count: number) => void;
  onCreateDeck?: (name: string) => void;
  adding?: boolean;
};

const BOARDS = [
  { id: "main", label: "Main Board" },
  { id: "side", label: "Sideboard" },
  { id: "commander", label: "Commander" },
];

export function AddToDeckModal({
  open,
  cardName,
  decks,
  onClose,
  onAdd,
  onCreateDeck,
  adding = false,
}: AddToDeckModalProps) {
  const [selectedDeck, setSelectedDeck] = useState<number | null>(null);
  const [board, setBoard] = useState("main");
  const [count, setCount] = useState(1);
  const [quickName, setQuickName] = useState("");
  const [showQuickCreate, setShowQuickCreate] = useState(false);

  if (!open) return null;

  function handleAdd() {
    if (selectedDeck === null) return;
    onAdd(selectedDeck, board, count);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-lg w-full max-w-sm shadow-xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-sm font-semibold text-text-primary">Add to Deck</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg">&times;</button>
        </div>

        <div className="p-4 space-y-3">
          <p className="text-xs text-text-muted">Adding <span className="text-text-primary font-medium">{cardName}</span></p>

          {/* Deck picker */}
          <div className="space-y-1">
            <label className="text-xs font-medium text-text-secondary">Deck</label>
            <select
              value={selectedDeck ?? ""}
              onChange={(e) => setSelectedDeck(e.target.value ? Number(e.target.value) : null)}
              className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"
            >
              <option value="">Select a deck...</option>
              {decks.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.card_count} cards)
                </option>
              ))}
            </select>
          </div>

          {/* Quick create */}
          {onCreateDeck && (
            <div>
              {!showQuickCreate ? (
                <button
                  onClick={() => setShowQuickCreate(true)}
                  className="text-xs text-accent hover:underline"
                >
                  + Create new deck
                </button>
              ) : (
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={quickName}
                    onChange={(e) => setQuickName(e.target.value)}
                    placeholder="New deck name"
                    autoFocus
                    className="flex-1 bg-bg-tertiary border border-border rounded px-2 py-1.5 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
                  />
                  <button
                    onClick={() => { if (quickName.trim()) { onCreateDeck(quickName.trim()); setQuickName(""); setShowQuickCreate(false); } }}
                    className="text-xs px-2 py-1.5 rounded bg-accent text-white hover:bg-accent-hover"
                  >
                    Create
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Board + count */}
          <div className="flex gap-3">
            <div className="flex-1 space-y-1">
              <label className="text-xs font-medium text-text-secondary">Board</label>
              <select
                value={board}
                onChange={(e) => setBoard(e.target.value)}
                className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary focus:outline-none focus:border-accent"
              >
                {BOARDS.map((b) => (
                  <option key={b.id} value={b.id}>{b.label}</option>
                ))}
              </select>
            </div>
            <div className="w-20 space-y-1">
              <label className="text-xs font-medium text-text-secondary">Qty</label>
              <input
                type="number"
                min={1}
                max={99}
                value={count}
                onChange={(e) => setCount(Math.max(1, Math.min(99, Number(e.target.value))))}
                className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-sm text-text-primary text-center focus:outline-none focus:border-accent"
              />
            </div>
          </div>

          <button
            onClick={handleAdd}
            disabled={selectedDeck === null || adding}
            className="w-full text-sm font-medium px-4 py-2 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
          >
            {adding ? "Adding..." : "Add Card"}
          </button>
        </div>
      </div>
    </div>
  );
}

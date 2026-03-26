import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import type { UserDeckResponse } from "@/types/api";
import { useUserDecks, useCreateDeck, useAddCardToDeck } from "@/api/hooks";

type ActiveDeckContextType = {
  activeDeck: UserDeckResponse | null;
  setActiveDeck: (deck: UserDeckResponse | null) => void;
  decks: UserDeckResponse[];
  isPickerOpen: boolean;
  openPicker: (pendingCardUuid?: string) => void;
  closePicker: () => void;
  quickAddCard: (cardUuid: string) => void;
  addingCard: boolean;
  createDeck: (name: string) => void;
  creatingDeck: boolean;
};

const ActiveDeckContext = createContext<ActiveDeckContextType | null>(null);

export function ActiveDeckProvider({ children }: { children: ReactNode }) {
  const { data: decks = [] } = useUserDecks();
  const createDeckMutation = useCreateDeck();
  const addCardMutation = useAddCardToDeck();

  const [activeDeck, setActiveDeckState] = useState<UserDeckResponse | null>(null);
  const [isPickerOpen, setPickerOpen] = useState(false);
  const [pendingCardUuid, setPendingCardUuid] = useState<string | null>(null);

  // Restore active deck from localStorage
  useEffect(() => {
    const storedId = localStorage.getItem("activeDeckId");
    if (storedId && decks.length > 0) {
      const deck = decks.find((d) => d.id === Number(storedId));
      if (deck) setActiveDeckState(deck);
    }
  }, [decks]);

  function setActiveDeck(deck: UserDeckResponse | null) {
    setActiveDeckState(deck);
    if (deck) {
      localStorage.setItem("activeDeckId", String(deck.id));
    } else {
      localStorage.removeItem("activeDeckId");
    }
  }

  function openPicker(cardUuid?: string) {
    if (cardUuid) setPendingCardUuid(cardUuid);
    setPickerOpen(true);
  }

  function closePicker() {
    setPickerOpen(false);
    setPendingCardUuid(null);
  }

  function quickAddCard(cardUuid: string) {
    if (!activeDeck) {
      openPicker(cardUuid);
      return;
    }
    addCardMutation.mutate({
      deckId: activeDeck.id,
      card_uuid: cardUuid,
      count: 1,
      board: "main",
    });
  }

  function handleCreateDeck(name: string) {
    createDeckMutation.mutate(
      { name, format: null, description: null },
      {
        onSuccess: (newDeck) => {
          setActiveDeck(newDeck);
          if (pendingCardUuid) {
            addCardMutation.mutate({
              deckId: newDeck.id,
              card_uuid: pendingCardUuid,
              count: 1,
              board: "main",
            });
          }
          closePicker();
        },
      }
    );
  }

  // When picker selects a deck, set it active and add pending card
  function handleSelectDeck(deck: UserDeckResponse) {
    setActiveDeck(deck);
    if (pendingCardUuid) {
      addCardMutation.mutate({
        deckId: deck.id,
        card_uuid: pendingCardUuid,
        count: 1,
        board: "main",
      });
    }
    closePicker();
  }

  return (
    <ActiveDeckContext.Provider
      value={{
        activeDeck,
        setActiveDeck,
        decks,
        isPickerOpen,
        openPicker,
        closePicker,
        quickAddCard,
        addingCard: addCardMutation.isPending,
        createDeck: handleCreateDeck,
        creatingDeck: createDeckMutation.isPending,
      }}
    >
      {children}
      {/* Inline deck picker modal */}
      {isPickerOpen && (
        <DeckPickerModal
          decks={decks}
          onSelect={handleSelectDeck}
          onCreate={handleCreateDeck}
          onClose={closePicker}
          creating={createDeckMutation.isPending}
        />
      )}
    </ActiveDeckContext.Provider>
  );
}

export function useActiveDeck() {
  const ctx = useContext(ActiveDeckContext);
  if (!ctx) throw new Error("useActiveDeck must be used within ActiveDeckProvider");
  return ctx;
}

// --- Inline deck picker modal ---

function DeckPickerModal({
  decks,
  onSelect,
  onCreate,
  onClose,
  creating,
}: {
  decks: UserDeckResponse[];
  onSelect: (deck: UserDeckResponse) => void;
  onCreate: (name: string) => void;
  onClose: () => void;
  creating: boolean;
}) {
  const [newName, setNewName] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-bg-secondary border border-border rounded-lg w-full max-w-sm shadow-xl max-h-[80vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-border">
          <h2 className="text-sm font-semibold text-text-primary">Select Active Deck</h2>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg">&times;</button>
        </div>

        <div className="max-h-60 overflow-y-auto">
          {decks.length === 0 && !showCreate && (
            <p className="text-sm text-text-muted p-4 text-center">No decks yet</p>
          )}
          {decks.map((d) => (
            <button
              key={d.id}
              onClick={() => onSelect(d)}
              className="w-full text-left px-4 py-2.5 text-sm hover:bg-bg-hover transition-colors border-b border-border/50 last:border-none"
            >
              <span className="text-text-primary font-medium">{d.name}</span>
              <span className="text-text-muted text-xs ml-2">{d.card_count} cards</span>
            </button>
          ))}
        </div>

        <div className="p-3 border-t border-border">
          {showCreate ? (
            <div className="flex gap-2">
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="New deck name"
                autoFocus
                className="flex-1 bg-bg-tertiary border border-border rounded px-2 py-1.5 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
              />
              <button
                onClick={() => { if (newName.trim()) onCreate(newName.trim()); }}
                disabled={!newName.trim() || creating}
                className="text-xs px-3 py-1.5 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50"
              >
                {creating ? "..." : "Create"}
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowCreate(true)}
              className="text-xs text-accent hover:underline"
            >
              + Create new deck
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

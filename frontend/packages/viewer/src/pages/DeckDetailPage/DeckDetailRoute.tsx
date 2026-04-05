import { useMemo, useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useDeck, useDeleteDeck, useDuplicateDeck, useRenameDeck, useAddCardToDeck, useRemoveCardFromDeck, useCards } from "@/api/hooks";
import { usePinnedDecks } from "@/hooks/usePinnedDecks";
import type { TagCount } from "@/types/api";
import { DeckDetailPage } from "./DeckDetailPage";

export function DeckDetailRoute() {
  const { file } = useParams<{ file: string }>();
  const navigate = useNavigate();
  const { data: deck } = useDeck(file ?? "");
  const { pinnedIds, togglePin } = usePinnedDecks();
  const deleteDeck = useDeleteDeck();
  const duplicateDeck = useDuplicateDeck();
  const renameDeck = useRenameDeck();
  const addCard = useAddCardToDeck();
  const removeCard = useRemoveCardFromDeck();

  const [searchQuery, setSearchQuery] = useState("");
  const { data: searchData, isFetching: searching } = useCards(
    searchQuery.length >= 2 ? { text: searchQuery, limit: 20 } : {},
  );

  const isEditable = deck?.meta.source === "user" || deck?.meta.source === "import";
  const deckId = Number(file);

  const availableTags: TagCount[] = useMemo(() => {
    if (!deck) return [];
    const counts = new Map<string, number>();
    for (const card of [...deck.commander, ...deck.main_board, ...deck.side_board]) {
      for (const tag of card.tags ?? []) {
        counts.set(tag, (counts.get(tag) ?? 0) + 1);
      }
    }
    return Array.from(counts, ([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count);
  }, [deck]);

  const handleSearchCards = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  if (!deck) {
    return <div className="flex items-center justify-center h-64 text-text-muted">Loading deck...</div>;
  }

  return (
    <DeckDetailPage
      deck={deck}
      availableTags={availableTags}
      pinned={pinnedIds.has(file ?? "")}
      editable={isEditable}
      searchResults={searchData?.data ?? []}
      searching={searching}
      onTogglePin={() => togglePin(file ?? "")}
      onDuplicate={() => {
        duplicateDeck.mutate(deckId, {
          onSuccess: (res) => navigate(`/decks/${res.id}`),
        });
      }}
      onDelete={() => {
        if (!confirm("Delete this deck?")) return;
        deleteDeck.mutate(deckId, { onSuccess: () => navigate("/decks") });
      }}
      onBack={() => navigate("/decks")}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onAddCard={(uuid, board, count) => {
        addCard.mutate({ deckId, card_uuid: uuid, count, board });
      }}
      onRemoveCard={(uuid) => {
        removeCard.mutate({ deckId, cardUuid: uuid, count: 1 });
      }}
      onSearchCards={handleSearchCards}
      onRename={isEditable ? (name) => renameDeck.mutate({ deckId, name }) : undefined}
    />
  );
}

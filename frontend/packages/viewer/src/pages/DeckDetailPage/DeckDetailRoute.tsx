import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useDeck, useDeleteDeck } from "@/api/hooks";
import { usePinnedDecks } from "@/hooks/usePinnedDecks";
import type { TagCount } from "@/types/api";
import { DeckDetailPage } from "./DeckDetailPage";

export function DeckDetailRoute() {
  const { file } = useParams<{ file: string }>();
  const navigate = useNavigate();
  const { data: deck } = useDeck(file ?? "");
  const { pinnedIds, togglePin } = usePinnedDecks();
  const deleteDeck = useDeleteDeck();

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

  if (!deck) {
    return <div className="flex items-center justify-center h-64 text-text-muted">Loading deck...</div>;
  }

  return (
    <DeckDetailPage
      deck={deck}
      availableTags={availableTags}
      pinned={pinnedIds.has(file ?? "")}
      onTogglePin={() => togglePin(file ?? "")}
      onDelete={() => {
        if (!confirm("Delete this deck?")) return;
        deleteDeck.mutate(Number(file), { onSuccess: () => navigate("/decks") });
      }}
      onBack={() => navigate("/decks")}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
    />
  );
}

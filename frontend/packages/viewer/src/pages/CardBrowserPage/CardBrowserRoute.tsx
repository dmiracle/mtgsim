import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useCards, useCardStats, useCardTags, useKeywordFrequencies, useSets, useAddToCollection } from "@/api/hooks";
import { buildParams } from "@/api/client";
import { useActiveDeck } from "@/context/ActiveDeckContext";
import { CardBrowserPage } from "./CardBrowserPage";
import type { CardSearchParams } from "./CardBrowserPage";

export function CardBrowserRoute() {
  const navigate = useNavigate();
  const { quickAddCard } = useActiveDeck();
  const addToCollection = useAddToCollection();
  const [pinnedIds, setPinnedIds] = useState(() => {
    const stored = localStorage.getItem("pinnedCards");
    return new Set<string>(stored ? JSON.parse(stored) : []);
  });
  const [page, setPage] = useState(1);
  const [searchParams, setSearchParams] = useState<CardSearchParams>({});
  const [setSearchQuery, setSetSearchQuery] = useState("");

  const { data: cardsData } = useCards({ ...searchParams, page, limit: 50 });
  const { data: cardStats } = useCardStats(searchParams);
  const { data: tags } = useCardTags({
    format: searchParams.format,
    colors: searchParams.colors,
    set: searchParams.sets,
  });
  const { data: setsData } = useSets(setSearchQuery ? { q: setSearchQuery, limit: 30 } : { limit: 30 });
  const { data: kwFreqs } = useKeywordFrequencies({
    format: searchParams.format,
    sets: searchParams.sets,
    colors: searchParams.colors,
  });

  function togglePin(uuid: string) {
    setPinnedIds((prev) => {
      const next = new Set(prev);
      if (next.has(uuid)) next.delete(uuid);
      else next.add(uuid);
      localStorage.setItem("pinnedCards", JSON.stringify([...next]));
      return next;
    });
  }

  const handleSearch = useCallback((params: CardSearchParams) => {
    setSearchParams(params);
    setPage(1);
  }, []);

  return (
    <CardBrowserPage
      cards={cardsData?.data ?? []}
      cardStats={cardStats ?? undefined}
      pagination={cardsData?.pagination ?? { page: 1, pages: 1, total: 0, limit: 50 }}
      availableTags={tags ?? []}
      availableSets={setsData?.data}
      onSetSearch={setSetSearchQuery}
      keywordFrequencies={kwFreqs ?? { keyword_abilities: {}, keyword_actions: {}, ability_words: {} }}
      pinnedIds={pinnedIds}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onPin={togglePin}
      onAddToDeck={quickAddCard}
      onAddToCollection={(uuid) => addToCollection.mutate(uuid)}
      onPageChange={setPage}
      onSearch={handleSearch}
      onDownload={() => {
        const base = import.meta.env.VITE_API_URL ?? "/api";
        window.location.href = `${base}/cards/download${buildParams(searchParams)}`;
      }}
    />
  );
}

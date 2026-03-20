import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { CardBrowserPage } from "./CardBrowserPage";
import { cardSummaries, keywordFrequencies } from "@/fixtures";

const sampleTags = [
  { tag: "removal", count: 245 },
  { tag: "burn", count: 128 },
  { tag: "counter", count: 89 },
  { tag: "draw", count: 312 },
];

export function CardBrowserRoute() {
  const navigate = useNavigate();
  const [pinnedIds, setPinnedIds] = useState(new Set<string>());

  function togglePin(uuid: string) {
    setPinnedIds((prev) => {
      const next = new Set(prev);
      if (next.has(uuid)) next.delete(uuid);
      else next.add(uuid);
      return next;
    });
  }

  return (
    <CardBrowserPage
      cards={cardSummaries}
      pagination={{ page: 1, pages: 5, total: 250, limit: 50 }}
      availableTags={sampleTags}
      keywordFrequencies={keywordFrequencies}
      pinnedIds={pinnedIds}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onPin={togglePin}
      onAddToDeck={() => {}}
      onPageChange={() => {}}
    />
  );
}

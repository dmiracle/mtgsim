import { useMemo } from "react";
import { usePinnedDecksQuery, usePinDeck, useUnpinDeck } from "@/api/hooks";

export function usePinnedDecks() {
  const { data: pinnedDecks = [] } = usePinnedDecksQuery();
  const pinDeck = usePinDeck();
  const unpinDeck = useUnpinDeck();

  const pinnedIds = useMemo(() => new Set(pinnedDecks.map((d) => d.file)), [pinnedDecks]);

  function togglePin(file: string) {
    if (pinnedIds.has(file)) {
      unpinDeck.mutate(file);
    } else {
      pinDeck.mutate(file);
    }
  }

  return { pinnedIds, pinnedDecks, togglePin };
}

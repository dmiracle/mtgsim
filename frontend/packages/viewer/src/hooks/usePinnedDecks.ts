import { useMemo } from "react";
import { usePinnedDecksQuery, usePinDeck, useUnpinDeck } from "@/api/hooks";

export function usePinnedDecks() {
  const { data: pinnedDecks = [] } = usePinnedDecksQuery();
  const pinDeck = usePinDeck();
  const unpinDeck = useUnpinDeck();

  const pinnedIds = useMemo(() => new Set(pinnedDecks.map((d) => d.uuid)), [pinnedDecks]);

  function togglePin(uuid: string) {
    if (pinnedIds.has(uuid)) {
      unpinDeck.mutate(uuid);
    } else {
      pinDeck.mutate(uuid);
    }
  }

  return { pinnedIds, pinnedDecks, togglePin };
}

import { useEffect, useMemo, useRef } from "react";
import { usePinnedDecksQuery, usePinDeck, useUnpinDeck } from "@/api/hooks";

const LEGACY_KEY = "pinnedDecks";
const LEGACY_SUMMARIES_KEY = "pinnedDeckSummaries";

export function usePinnedDecks() {
  const { data: pinnedDecks = [] } = usePinnedDecksQuery();
  const pinDeck = usePinDeck();
  const unpinDeck = useUnpinDeck();
  const migrated = useRef(false);

  // One-time migration from localStorage to backend
  useEffect(() => {
    if (migrated.current) return;
    migrated.current = true;
    const raw = localStorage.getItem(LEGACY_KEY);
    if (!raw) return;
    const ids: string[] = JSON.parse(raw);
    if (ids.length === 0) return;
    for (const id of ids) {
      pinDeck.mutate(id);
    }
    localStorage.removeItem(LEGACY_KEY);
    localStorage.removeItem(LEGACY_SUMMARIES_KEY);
  }, [pinDeck]);

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

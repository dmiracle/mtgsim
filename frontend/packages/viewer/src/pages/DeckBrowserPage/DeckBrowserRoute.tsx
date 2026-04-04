import { useState, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useDecks, useDeleteDeck, useCreateDeck, useImportDeck } from "@/api/hooks";
import { usePinnedDecks } from "@/hooks/usePinnedDecks";
import { DeckCreateModal } from "@/components/DeckCreateModal/DeckCreateModal";
import { DeckImportModal } from "@/components/DeckImportModal/DeckImportModal";
import { DeckBrowserPage } from "./DeckBrowserPage";
import type { DeckSearchParams } from "./DeckBrowserPage";

export function DeckBrowserRoute() {
  const navigate = useNavigate();
  const [sp, setSp] = useSearchParams();
  const page = Number(sp.get("page") ?? "1");
  const [searchParams, setSearchParams] = useState<DeckSearchParams>({});
  const [createOpen, setCreateOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const { pinnedIds, pinnedDecks, togglePin } = usePinnedDecks();
  const deleteDeck = useDeleteDeck();
  const createDeck = useCreateDeck();
  const importDeck = useImportDeck();

  const { data } = useDecks({ ...searchParams, page, limit: 50 });
  const allDecks = data?.data ?? [];

  function setPage(p: number) {
    setSp((prev) => {
      const next = new URLSearchParams(prev);
      if (p > 1) next.set("page", String(p)); else next.delete("page");
      return next;
    }, { replace: true });
  }

  const handleSearch = useCallback((params: DeckSearchParams) => {
    setSearchParams(params);
    setSp((prev) => { const next = new URLSearchParams(prev); next.delete("page"); return next; }, { replace: true });
  }, [setSp]);

  function handleDelete(file: string) {
    if (!confirm(`Delete this deck?`)) return;
    deleteDeck.mutate(Number(file));
  }

  return (
    <>
      <DeckBrowserPage
        decks={allDecks}
        pinnedDecks={pinnedDecks}
        pagination={data?.pagination ?? { page: 1, pages: 1, total: 0, limit: 50 }}
        availableFormats={data?.filters.formats ?? []}
        availableSources={["user", "import", "precon"]}
        pinnedIds={pinnedIds}
        onTogglePin={togglePin}
        onDeleteDeck={handleDelete}
        onDeckClick={(file) => navigate(`/decks/${file}`)}
        onPageChange={setPage}
        onSearch={handleSearch}
        onCreateDeck={() => setCreateOpen(true)}
        onImportDeck={() => setImportOpen(true)}
      />
      <DeckCreateModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        creating={createDeck.isPending}
        onCreate={(data) => {
          createDeck.mutate(data, {
            onSuccess: (res) => {
              setCreateOpen(false);
              navigate(`/decks/${res.id}`);
            },
          });
        }}
      />
      <DeckImportModal
        open={importOpen}
        onClose={() => { setImportOpen(false); importDeck.reset(); }}
        importing={importDeck.isPending}
        result={importDeck.data}
        onImport={(text, name) => importDeck.mutate({ text, name })}
        onViewDeck={(deckId) => { setImportOpen(false); importDeck.reset(); navigate(`/decks/${deckId}`); }}
      />
    </>
  );
}

import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDecks } from "@/api/hooks";
import { DeckBrowserPage } from "./DeckBrowserPage";
import type { DeckSearchParams } from "./DeckBrowserPage";

export function DeckBrowserRoute() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [searchParams, setSearchParams] = useState<DeckSearchParams>({});

  const { data } = useDecks({ ...searchParams, page, limit: 50 });

  const handleSearch = useCallback((params: DeckSearchParams) => {
    setSearchParams(params);
    setPage(1);
  }, []);

  return (
    <DeckBrowserPage
      decks={data?.data ?? []}
      pagination={data?.pagination ?? { page: 1, pages: 1, total: 0, limit: 50 }}
      availableFormats={data?.filters.formats ?? []}
      availableSources={["user", "import", "precon"]}
      onDeckClick={(file) => navigate(`/decks/${file}`)}
      onPageChange={setPage}
      onSearch={handleSearch}
      onCreateDeck={() => {}}
      onImportDeck={() => {}}
    />
  );
}

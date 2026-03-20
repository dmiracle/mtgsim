import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDecks } from "@/api/hooks";
import { DeckBrowserPage } from "./DeckBrowserPage";

export function DeckBrowserRoute() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data } = useDecks({ page, limit: 50 });

  return (
    <DeckBrowserPage
      decks={data?.data ?? []}
      pagination={data?.pagination ?? { page: 1, pages: 1, total: 0, limit: 50 }}
      availableFormats={data?.filters.formats ?? []}
      availableSources={["user", "import", "precon"]}
      onDeckClick={(file) => navigate(`/decks/${file}`)}
      onPageChange={setPage}
      onCreateDeck={() => {}}
      onImportDeck={() => {}}
    />
  );
}

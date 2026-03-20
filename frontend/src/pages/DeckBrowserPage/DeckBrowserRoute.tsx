import { useNavigate } from "react-router-dom";
import { DeckBrowserPage } from "./DeckBrowserPage";
import { deckSummaries } from "@/fixtures";

export function DeckBrowserRoute() {
  const navigate = useNavigate();
  return (
    <DeckBrowserPage
      decks={deckSummaries}
      pagination={{ page: 1, pages: 1, total: deckSummaries.length, limit: 50 }}
      availableFormats={["standard", "modern", "commander", "legacy", "pioneer"]}
      availableSources={["user", "import", "precon"]}
      onDeckClick={(file) => navigate(`/decks/${file}`)}
      onPageChange={() => {}}
      onCreateDeck={() => {}}
      onImportDeck={() => {}}
    />
  );
}

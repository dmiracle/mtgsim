import { useNavigate } from "react-router-dom";
import { DeckDetailPage } from "./DeckDetailPage";
import { deckDetail } from "@/fixtures";

export function DeckDetailRoute() {
  const navigate = useNavigate();
  return (
    <DeckDetailPage
      deck={deckDetail}
      onBack={() => navigate("/decks")}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
    />
  );
}

import { useNavigate, useParams } from "react-router-dom";
import { useDeck } from "@/api/hooks";
import { DeckDetailPage } from "./DeckDetailPage";

export function DeckDetailRoute() {
  const { file } = useParams<{ file: string }>();
  const navigate = useNavigate();
  const { data: deck } = useDeck(file ?? "");

  if (!deck) {
    return <div className="flex items-center justify-center h-64 text-text-muted">Loading deck...</div>;
  }

  return (
    <DeckDetailPage
      deck={deck}
      onBack={() => navigate("/decks")}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
    />
  );
}

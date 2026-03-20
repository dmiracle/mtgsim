import { useNavigate } from "react-router-dom";
import { CardDetailPage } from "./CardDetailPage";
import { cardDetail, keywordsResponse } from "@/fixtures";

export function CardDetailRoute() {
  const navigate = useNavigate();
  return (
    <CardDetailPage
      card={cardDetail}
      keywordTypes={keywordsResponse}
      onBack={() => navigate(-1)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onPrintingClick={(uuid) => navigate(`/cards/${uuid}`)}
      onDeckClick={(file) => navigate(`/decks/${file}`)}
      onAddToDeck={() => {}}
      onAddToCollection={() => {}}
      onSaveRating={() => {}}
    />
  );
}

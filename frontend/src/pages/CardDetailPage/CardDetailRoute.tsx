import { useNavigate, useParams } from "react-router-dom";
import { useCard, useKeywords, useAddToCollection, useSaveRating } from "@/api/hooks";
import { CardDetailPage } from "./CardDetailPage";

export function CardDetailRoute() {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const { data: card } = useCard(uuid ?? "");
  const { data: keywords } = useKeywords();
  const addToCollection = useAddToCollection();
  const saveRating = useSaveRating();

  if (!card) {
    return <div className="flex items-center justify-center h-64 text-text-muted">Loading card...</div>;
  }

  return (
    <CardDetailPage
      card={card}
      keywordTypes={keywords}
      onBack={() => navigate(-1)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onPrintingClick={(id) => navigate(`/cards/${id}`)}
      onDeckClick={(file) => navigate(`/decks/${file}`)}
      onAddToDeck={() => {}}
      onAddToCollection={() => addToCollection.mutate(card.uuid)}
      onSaveRating={(rating) => saveRating.mutate({ uuid: card.uuid, ...rating })}
    />
  );
}

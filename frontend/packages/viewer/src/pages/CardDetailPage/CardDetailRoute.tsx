import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useCard, useKeywords, useAddToCollection, useSaveRating, useStrategies, useSimilarCards } from "@/api/hooks";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardDetailPage } from "./CardDetailPage";

const emptyFilters: CardFilters = {
  text: "", colors: [], rarities: [], types: [], tags: [], manaValue: [],
  ownership: "all", platform: "any", sort: "score", order: "desc", unique: false, priceMode: "min", subtype: "", sets: [], formats: [],
};

function filtersToParams(f: CardFilters): Record<string, string | undefined> {
  return {
    text: f.text || undefined,
    colors: f.colors.length > 0 ? f.colors.join("") : undefined,
    rarity: f.rarities.length > 0 ? f.rarities.join(",") : undefined,
    type: f.types.length > 0 ? f.types.join(",") : undefined,
    mana_value: f.manaValue.length > 0 ? f.manaValue.join(",") : undefined,
    format: f.formats.length > 0 ? f.formats[0] : undefined,
  };
}

export function CardDetailRoute() {
  const { uuid } = useParams<{ uuid: string }>();
  const navigate = useNavigate();
  const { data: card } = useCard(uuid ?? "");
  const { data: keywords } = useKeywords();
  const addToCollection = useAddToCollection();
  const saveRating = useSaveRating();

  const { data: strategies } = useStrategies();
  const [selectedStrategies, setSelectedStrategies] = useState<string[]>([]);
  const [similarFilters, setSimilarFilters] = useState(emptyFilters);

  const filterParams = filtersToParams(similarFilters);
  const { data: similarData } = useSimilarCards(uuid ?? "", selectedStrategies, filterParams);

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
      strategies={strategies}
      selectedStrategies={selectedStrategies}
      onStrategiesChange={setSelectedStrategies}
      similarResults={similarData?.results}
      similarFilters={similarFilters}
      onSimilarFiltersChange={setSimilarFilters}
      onSimilarCardClick={(id) => navigate(`/cards/${id}`)}
    />
  );
}

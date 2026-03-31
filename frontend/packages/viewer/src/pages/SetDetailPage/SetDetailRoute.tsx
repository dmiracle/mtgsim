import { useState, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useSet } from "@/api/hooks";
import { SetDetailPage } from "./SetDetailPage";
import type { SetCardSearchParams } from "./SetDetailPage";
import type { CardSummary } from "@/types/api";

export function SetDetailRoute() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const [cardPage, setCardPage] = useState(1);
  const [cardFilters, setCardFilters] = useState<SetCardSearchParams>({});

  const { data: setData } = useSet(code ?? "", {
    card_page: cardPage,
    card_limit: 50,
    unique: true,
    ...cardFilters,
  });

  const handleFiltersChange = useCallback((params: SetCardSearchParams) => {
    setCardFilters(params);
    setCardPage(1);
  }, []);

  if (!setData) {
    return <div className="flex items-center justify-center h-64 text-text-muted">Loading set...</div>;
  }

  const cards: CardSummary[] = setData.cards.data.map((c) => ({
    uuid: c.uuid,
    name: c.name,
    type: c.type,
    mana_cost: c.mana_cost,
    mana_value: c.mana_value,
    rarity: c.rarity,
    set_code: setData.meta.code,
    color_identity: c.color_identity,
    tags: [],
    text: c.text,
    price: c.price,
    image_url: c.image_url,
    owns: c.owns,
    wants: c.wants,
    total_owned: c.total_owned,
    total_wanted: c.total_wanted,
  }));

  return (
    <SetDetailPage
      set={setData}
      cards={cards}
      cardPagination={setData.cards.pagination}
      onBack={() => navigate("/sets")}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(c) => navigate(`/sets/${c}`)}
      onCardPageChange={setCardPage}
      onCardFiltersChange={handleFiltersChange}
    />
  );
}

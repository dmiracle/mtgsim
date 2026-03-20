import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useHomeStats, usePrices } from "@/api/hooks";
import { PriceExplorerPage } from "./PriceExplorerPage";
import { homeStats as fallback } from "@/fixtures";

export function PriceExplorerRoute() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data: stats } = useHomeStats();
  const { data: pricesData } = usePrices({ page, limit: 50, sort: "average_usd", order: "desc" });

  return (
    <PriceExplorerPage
      stats={stats ?? fallback}
      prices={pricesData?.data ?? []}
      pagination={pricesData?.pagination ?? { page: 1, pages: 1, total: 0, limit: 50 }}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onPageChange={setPage}
    />
  );
}

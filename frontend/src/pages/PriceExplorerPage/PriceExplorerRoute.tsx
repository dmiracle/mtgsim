import { useNavigate } from "react-router-dom";
import { PriceExplorerPage } from "./PriceExplorerPage";
import { homeStats, priceSummaries } from "@/fixtures";

export function PriceExplorerRoute() {
  const navigate = useNavigate();
  return (
    <PriceExplorerPage
      stats={homeStats}
      prices={priceSummaries}
      pagination={{ page: 1, pages: 10, total: 500, limit: 50 }}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onPageChange={() => {}}
    />
  );
}

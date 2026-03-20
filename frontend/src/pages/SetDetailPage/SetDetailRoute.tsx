import { useNavigate } from "react-router-dom";
import { SetDetailPage } from "./SetDetailPage";
import { setDetail, cardSummaries } from "@/fixtures";

export function SetDetailRoute() {
  const navigate = useNavigate();
  return (
    <SetDetailPage
      set={setDetail}
      cards={cardSummaries}
      cardPagination={{ page: 1, pages: 7, total: 303, limit: 50 }}
      onBack={() => navigate("/sets")}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onCardPageChange={() => {}}
    />
  );
}

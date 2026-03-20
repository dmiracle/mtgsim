import { useNavigate } from "react-router-dom";
import { DraftSimulatorPage } from "./DraftSimulatorPage";
import { setSummaries } from "@/fixtures";

export function DraftSimulatorRoute() {
  const navigate = useNavigate();
  return (
    <DraftSimulatorPage
      sets={setSummaries}
      packs={[]}
      onOpenPacks={() => {}}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
    />
  );
}

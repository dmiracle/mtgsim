import { useNavigate } from "react-router-dom";
import { SetBrowserPage } from "./SetBrowserPage";
import { setSummaries } from "@/fixtures";

export function SetBrowserRoute() {
  const navigate = useNavigate();
  return (
    <SetBrowserPage
      sets={setSummaries}
      pagination={{ page: 1, pages: 4, total: 156, limit: 50 }}
      availableTypes={["core", "expansion", "masters", "draft_innovation", "commander"]}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onPageChange={() => {}}
    />
  );
}

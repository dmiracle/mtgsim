import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSets } from "@/api/hooks";
import { SetBrowserPage } from "./SetBrowserPage";

export function SetBrowserRoute() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const { data } = useSets({ page, limit: 50, sort: "release_date", order: "desc" });

  return (
    <SetBrowserPage
      sets={data?.data ?? []}
      pagination={data?.pagination ?? { page: 1, pages: 1, total: 0, limit: 50 }}
      availableTypes={data?.filters.types ?? []}
      onSetClick={(code) => navigate(`/sets/${code}`)}
      onPageChange={setPage}
    />
  );
}

import { useNavigate, useSearchParams } from "react-router-dom";
import { useCardStats } from "../api";
import { PageHeader } from "../components/PageHeader";
import { StatsView } from "../components/StatsView";
import { summarizeFilters, type Filters } from "../filters";

export function StatsPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const filters: Filters = Object.fromEntries(params);
  const stats = useCardStats(filters);

  return (
    <div className="pb-[max(1rem,env(safe-area-inset-bottom))]">
      <PageHeader title="Stats" backLabel="Filters" onBack={() => navigate("/")} />
      <div className="space-y-4 px-4 pt-3">
        <p className="text-xs text-muted">{summarizeFilters(filters)}</p>
        {stats.data ? <StatsView stats={stats.data} /> : <p className="text-muted">Loading…</p>}
      </div>
    </div>
  );
}

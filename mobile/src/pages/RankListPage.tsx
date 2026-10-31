import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  RANKING_POOL_MAX,
  rankingPoolFilters,
  useCardCount,
  useCreateRanking,
  useDeleteRanking,
  useRankings,
} from "../api";
import { PageHeader } from "../components/PageHeader";
import { loadFilters, summarizeFilters } from "../filters";

export function RankListPage() {
  const navigate = useNavigate();
  const filters = rankingPoolFilters(loadFilters());
  const count = useCardCount(filters);
  const rankings = useRankings();
  const createRanking = useCreateRanking();
  const deleteRanking = useDeleteRanking();
  const [name, setName] = useState("");
  const tooMany = (count.data ?? 0) > RANKING_POOL_MAX;

  const create = async () => {
    const ranking = await createRanking.mutateAsync({ name: name.trim(), filters });
    navigate(`/rank/${ranking.id}`);
  };

  return (
    <div className="pb-[max(1rem,env(safe-area-inset-bottom))]">
      <PageHeader title="Rankings" backLabel="Filters" onBack={() => navigate("/")} />
      <div className="space-y-6 px-4 pt-4">
        <section className="space-y-3 rounded-xl bg-surface p-4">
          <h2 className="font-semibold">New ranking from current filters</h2>
          <p className="text-sm text-muted">
            {summarizeFilters(filters)} · {count.data?.toLocaleString() ?? "…"} cards
          </p>
          {tooMany && (
            <p className="text-sm text-grade-f">
              Narrow your filters to {RANKING_POOL_MAX} cards or fewer to rank them.
            </p>
          )}
          <input
            className="w-full rounded-lg border border-line bg-bg px-3 py-2.5 text-base"
            placeholder="Ranking name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <button
            onClick={create}
            disabled={!name.trim() || tooMany || !count.data}
            className="min-h-12 w-full rounded-xl bg-accent font-semibold text-bg disabled:opacity-30"
          >
            Start ranking
          </button>
        </section>

        <section className="space-y-2">
          <h2 className="text-xs font-semibold tracking-wider text-muted uppercase">Your rankings</h2>
          {rankings.data?.length === 0 && <p className="text-sm text-muted">None yet.</p>}
          <ul className="divide-y divide-line rounded-xl border border-line">
            {rankings.data?.map((r) => (
              <li key={r.id} className="flex items-center gap-2">
                <button onClick={() => navigate(`/rank/${r.id}`)} className="min-w-0 flex-1 px-3 py-3 text-left">
                  <p className="truncate">{r.name}</p>
                  <p className="truncate text-xs text-muted">
                    {summarizeFilters(r.filters)} · {r.comparison_count} comparisons
                  </p>
                </button>
                <button
                  onClick={() => confirm(`Delete "${r.name}"?`) && deleteRanking.mutate(r.id)}
                  aria-label={`Delete ${r.name}`}
                  className="min-h-10 px-3 text-muted"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

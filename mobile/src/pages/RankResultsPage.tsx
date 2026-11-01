import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useExcludeCard, useRanking, useRankingPool } from "../api";
import { PageHeader } from "../components/PageHeader";
import { RankingResults } from "../components/RankingResults";
import { buildGraph, cycleMembers, rankOrder, reaches } from "../ranking";

export function RankResultsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const ranking = useRanking(id);
  const pool = useRankingPool(ranking.data?.filters);
  const excludeCard = useExcludeCard(id);
  const excludedNames = ranking.data?.excluded_names ?? [];

  const rows = useMemo(() => {
    const excluded = new Set(ranking.data?.excluded_names);
    const cards = (pool.data?.cards ?? []).filter((c) => !excluded.has(c.name));
    const byName = new Map(cards.map((c) => [c.name, c]));
    const graph = buildGraph(cards.map((c) => c.name), ranking.data?.comparisons ?? []);
    const inCycle = cycleMembers(graph);
    const order = rankOrder(graph);
    return order.map((name, i) => ({
      card: byName.get(name)!,
      inCycle: inCycle.has(name),
      undetermined: i + 1 < order.length && !reaches(graph, name, order[i + 1]),
    }));
  }, [pool.data, ranking.data]);

  return (
    <div className="pb-[max(1rem,env(safe-area-inset-bottom))]">
      <PageHeader
        title={ranking.data?.name ?? ""}
        backLabel="Rank"
        onBack={() => navigate(`/rank/${id}`)}
      />
      <div className="px-4">
        <RankingResults rows={rows} />
        {excludedNames.length > 0 && (
          <section className="space-y-2 pt-6">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-muted">
              Excluded ({excludedNames.length})
            </h2>
            <ul className="divide-y divide-line">
              {excludedNames.map((name) => (
                <li key={name} className="flex items-center gap-3 py-2">
                  <span className="min-w-0 flex-1 truncate text-muted">{name}</span>
                  <button
                    onClick={() => excludeCard.mutate({ cardName: name, exclude: false })}
                    className="min-h-10 rounded-lg border border-line px-3 text-sm"
                  >
                    Restore
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}

import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useRanking, useRankingPool } from "../api";
import { PageHeader } from "../components/PageHeader";
import { RankingResults } from "../components/RankingResults";
import { buildGraph, cycleMembers, rankOrder, reaches } from "../ranking";

export function RankResultsPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const ranking = useRanking(id);
  const pool = useRankingPool(ranking.data?.filters);

  const rows = useMemo(() => {
    const cards = pool.data?.cards ?? [];
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
      </div>
    </div>
  );
}

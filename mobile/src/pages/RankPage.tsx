import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { RANKING_POOL_MAX, useRanking, useRankingPool, useSubmitRound } from "../api";
import { PageHeader } from "../components/PageHeader";
import { RankRound } from "../components/RankRound";
import { buildGraph, nextRound, rankOrder, undeterminedPairs } from "../ranking";

export function RankPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const ranking = useRanking(id);
  const pool = useRankingPool(ranking.data?.filters);
  const submitRound = useSubmitRound(id);

  const cards = pool.data?.cards ?? [];
  const graph = useMemo(
    () => buildGraph(cards.map((c) => c.name), ranking.data?.comparisons ?? []),
    [cards, ranking.data?.comparisons],
  );
  // Recomputed only when the comparisons change, so the random draw stays put between renders.
  const round = useMemo(() => nextRound(graph), [graph]);
  const settled = cards.length > 1 ? 1 - undeterminedPairs(graph, rankOrder(graph)).length / (cards.length - 1) : 0;
  const byName = new Map(cards.map((c) => [c.name, c]));

  const header = (
    <PageHeader
      title={ranking.data?.name ?? ""}
      backLabel="Rankings"
      onBack={() => navigate("/rank")}
      action={
        <button onClick={() => navigate(`/rank/${id}/results`)} className="min-h-10 rounded-lg bg-raised px-3 text-sm">
          Results
        </button>
      }
    />
  );

  if (!pool.data) return <>{header}<p className="pt-20 text-center text-muted">Loading cards…</p></>;
  if (pool.data.total > RANKING_POOL_MAX) {
    return (
      <>
        {header}
        <p className="px-4 pt-20 text-center text-muted">
          This ranking's filters now match {pool.data.total.toLocaleString()} cards — more than {RANKING_POOL_MAX}.
        </p>
      </>
    );
  }

  return (
    <div className="pb-[max(1rem,env(safe-area-inset-bottom))]">
      {header}
      <div className="space-y-3 px-4 pt-3">
        <div className="space-y-1">
          <div className="h-2 overflow-hidden rounded-full bg-surface">
            <div className="h-full bg-accent" style={{ width: `${Math.round(settled * 100)}%` }} />
          </div>
          <p className="text-xs text-muted">
            {cards.length} cards · {ranking.data?.comparison_count ?? 0} comparisons · {Math.round(settled * 100)}%
            settled
          </p>
        </div>
        {round.kind === "done" ? (
          <div className="space-y-4 pt-16 text-center">
            <p className="text-lg">All {cards.length} cards are ranked.</p>
            <button
              onClick={() => navigate(`/rank/${id}/results`)}
              className="min-h-12 rounded-xl bg-accent px-6 font-semibold text-bg"
            >
              See the ranking
            </button>
          </div>
        ) : (
          <RankRound
            key={round.names.join("|")}
            cards={round.names.map((n) => byName.get(n)!)}
            kind={round.kind}
            submitting={submitRound.isPending}
            onSubmit={(names) => submitRound.mutate(names)}
          />
        )}
      </div>
    </div>
  );
}

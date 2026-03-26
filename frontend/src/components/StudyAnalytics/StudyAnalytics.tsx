import type {
  ReviewHistory,
  SessionAnalytics,
  RetentionAnalytics,
  KeywordAnalytics,
  CollectionAnalytics,
  CardDifficulty,
} from "@/types/flashcards";
import { LineChart } from "@/components/charts/LineChart/LineChart";
import { HBarChart } from "@/components/charts/HBarChart/HBarChart";
import { DonutChart } from "@/components/charts/DonutChart/DonutChart";
import { StatCard } from "@/components/StatCard/StatCard";

type StudyAnalyticsProps = {
  reviewHistory?: ReviewHistory | null;
  session?: SessionAnalytics | null;
  retention?: RetentionAnalytics | null;
  keywords?: KeywordAnalytics | null;
  collections?: CollectionAnalytics[] | null;
  cardDifficulty?: CardDifficulty | null;
};

function formatMs(ms: number): string {
  const minutes = Math.floor(ms / 60000);
  const hours = Math.floor(minutes / 60);
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  return `${minutes}m`;
}

function getCardLabel(q: Record<string, unknown>): string {
  if (q.card_name) return String(q.card_name);
  if (q.keyword) return String(q.keyword);
  return `#${q.flashcard_id}`;
}

export function StudyAnalytics({ reviewHistory, session, retention, keywords, collections, cardDifficulty }: StudyAnalyticsProps) {
  // --- Review History: line chart ---
  const allBuckets = reviewHistory?.buckets ?? [];
  const activeBuckets = allBuckets.filter((d) => d.reviews > 0);
  const recentEntries = activeBuckets.slice(-48);
  const isHourly = reviewHistory?.granularity === "hourly";

  function entryLabel(e: { date: string }): string {
    if (isHourly) {
      const dt = new Date(e.date);
      return `${(dt.getMonth() + 1)}/${dt.getDate()} ${dt.getHours()}:00`;
    }
    return e.date.slice(5);
  }

  const reviewSeries = recentEntries.length > 0 ? [
    {
      label: "Reviews",
      color: "var(--color-accent)",
      data: recentEntries.map((d) => ({ x: entryLabel(d), y: d.reviews })),
    },
    {
      label: "New Learned",
      color: "var(--color-success)",
      data: recentEntries.map((d) => ({ x: entryLabel(d), y: d.new_cards_learned })),
    },
  ] : [];

  const ratingSeries = recentEntries.length > 0 ? [
    {
      label: "Avg Rating",
      color: "var(--color-warning)",
      data: recentEntries.filter((d) => d.average_rating !== null).map((d) => ({ x: entryLabel(d), y: d.average_rating! })),
    },
  ] : [];

  // --- Session: stat cards + accuracy donut ---
  const accuracyData = session?.accuracy_by_card_type
    ? Object.entries(session.accuracy_by_card_type).map(([label, value]) => ({
        label: label.replace("card_", "").replace("_", " "),
        value: Math.round(value),
      }))
    : [];

  // --- Retention curve ---
  const retentionData = retention?.buckets
    .map((b) => ({ label: b.interval_label, value: Math.round(b.pass_rate) })) ?? [];

  // --- Keywords: hardest + easiest ---
  const hardestKw = keywords?.hardest.slice(0, 10).map((k) => ({
    label: k.keyword,
    value: Math.round(100 - k.pass_rate),
  })) ?? [];

  const easiestKw = keywords?.easiest.slice(0, 10).map((k) => ({
    label: k.keyword,
    value: Math.round(k.pass_rate),
  })) ?? [];

  // --- Card difficulty: top 10 lists ---
  const hardestCards = cardDifficulty?.hardest.slice(0, 10) ?? [];
  const mostReviewed = cardDifficulty?.hardest
    .slice()
    .sort((a, b) => b.total_reviews - a.total_reviews)
    .slice(0, 10) ?? [];

  return (
    <div className="space-y-6">
      {/* Session stats */}
      {session && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <StatCard label="Total Study Time" value={formatMs(session.total_study_time_ms)} />
          <StatCard label="Cards / Min" value={session.avg_cards_per_minute.toFixed(1)} />
          <StatCard
            label="Overall Accuracy"
            value={`${Math.round(
              Object.values(session.accuracy_by_card_type).reduce((a, b) => a + b, 0) /
              Math.max(Object.keys(session.accuracy_by_card_type).length, 1)
            )}%`}
          />
        </div>
      )}

      {/* Review history line chart */}
      {reviewSeries.length > 0 && (
        <LineChart title={isHourly ? "Review Activity (Hourly)" : "Review Activity (Daily)"} series={reviewSeries} height={200} animate={false} />
      )}

      {ratingSeries[0]?.data.length > 0 && (
        <LineChart title="Average Rating Over Time" series={ratingSeries} height={160} yLabel="Rating" animate={false} />
      )}

      {/* Accuracy by type + Retention curve */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {accuracyData.length > 0 && (
          <DonutChart
            title="Accuracy by Card Type"
            data={accuracyData}
            size={180}
            showLegend
          />
        )}
        {retentionData.length > 0 && (
          <HBarChart title="Retention Curve (Pass %)" data={retentionData} color="accent" animate={false} />
        )}
      </div>

      {/* Keywords: hardest + easiest */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {hardestKw.length > 0 && (
          <HBarChart title="Hardest Keywords (% wrong)" data={hardestKw} color="danger" animate={false} />
        )}
        {easiestKw.length > 0 && (
          <HBarChart title="Easiest Keywords (% correct)" data={easiestKw} color="success" animate={false} />
        )}
      </div>

      {/* Card difficulty: top 10 lists */}
      {hardestCards.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-2">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-widest">Hardest Cards</h3>
            <div className="space-y-1">
              {hardestCards.map((c, i) => (
                <div key={c.flashcard_id} className="flex items-center justify-between text-xs">
                  <span className="text-text-primary truncate max-w-[180px]">
                    {i + 1}. {getCardLabel(c.question)}
                  </span>
                  <span className="text-text-muted tabular-nums shrink-0">
                    ease {c.ease_factor.toFixed(2)} · {c.total_reviews} reviews
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-2">
            <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-widest">Most Reviewed</h3>
            <div className="space-y-1">
              {mostReviewed.map((c, i) => (
                <div key={c.flashcard_id} className="flex items-center justify-between text-xs">
                  <span className="text-text-primary truncate max-w-[180px]">
                    {i + 1}. {getCardLabel(c.question)}
                  </span>
                  <span className="text-text-muted tabular-nums shrink-0">
                    {c.total_reviews} reviews · ease {c.ease_factor.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Collection progress */}
      {collections && collections.length > 0 && (
        <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
          <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-widest">Collection Progress</h3>
          <div className="space-y-3">
            {collections.map((c) => (
              <div key={c.id} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-text-primary truncate max-w-[200px]">
                    {c.name.replace(/_/g, " ")}
                  </span>
                  <span className="text-text-muted tabular-nums shrink-0">
                    {c.cards_reviewed}/{c.card_count} ({c.completion_pct.toFixed(0)}%)
                  </span>
                </div>
                <div className="w-full h-2 bg-bg-tertiary rounded-full overflow-hidden">
                  <div className="h-full bg-accent rounded-full" style={{ width: `${c.completion_pct}%` }} />
                </div>
                <div className="flex gap-3 text-[10px] text-text-muted">
                  <span>Win: {c.win_rate.toFixed(0)}%</span>
                  <span>Ease: {c.average_ease.toFixed(2)}</span>
                  <span>Due: {c.cards_due}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

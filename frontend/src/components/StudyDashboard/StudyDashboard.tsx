import { useState } from "react";
import type { StudyStats } from "@/types/flashcards";
import { StatCard } from "@/components/StatCard/StatCard";

type StudyDashboardProps = {
  stats: StudyStats;
  onStudyAll: () => void;
  onStudyCollections: (collections: string[]) => void;
  onDeleteCollection: (collectionId: number) => void;
  onGenerate: () => void;
  deleting?: number | null;
};

function formatCollectionName(name: string): string {
  return name
    .replace(/^keywords_/, "Keywords: ")
    .replace(/^card_oracle_/, "Oracle: ")
    .replace(/^card_mana_cost_/, "Mana Cost: ")
    .replace(/^card_stats_/, "Stats: ")
    .replace(/_/g, " ");
}

export function StudyDashboard({
  stats,
  onStudyAll,
  onStudyCollections,
  onDeleteCollection,
  onGenerate,
  deleting = null,
}: StudyDashboardProps) {
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);

  function toggleSelect(id: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  const selectedCollections = stats.collections.filter((c) => selectedIds.has(c.id));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl text-text-primary">Flashcards</h2>
        <button
          onClick={onGenerate}
          className="text-xs font-medium px-3 py-1.5 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
        >
          + Generate
        </button>
      </div>

      {/* Core stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Cards" value={stats.total_cards} />
        <StatCard label="Due Now" value={stats.cards_due} />
        <StatCard label="New" value={stats.cards_new} />
        <StatCard label="Reviewed Today" value={stats.reviews_today} />
      </div>

      {/* Mastery breakdown */}
      {(stats.cards_learning !== undefined || stats.cards_mature !== undefined) && (
        <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
          <h3 className="text-xs font-semibold text-text-secondary uppercase tracking-widest">Mastery</h3>
          <div className="w-full h-3 bg-bg-tertiary rounded-full overflow-hidden flex">
            {stats.cards_mature !== undefined && stats.total_cards > 0 && (
              <div
                className="h-full bg-success"
                style={{ width: `${(stats.cards_mature / stats.total_cards) * 100}%` }}
                title={`Mature: ${stats.cards_mature}`}
              />
            )}
            {stats.cards_young !== undefined && stats.total_cards > 0 && (
              <div
                className="h-full bg-accent"
                style={{ width: `${(stats.cards_young / stats.total_cards) * 100}%` }}
                title={`Young: ${stats.cards_young}`}
              />
            )}
            {stats.cards_learning !== undefined && stats.total_cards > 0 && (
              <div
                className="h-full bg-warning"
                style={{ width: `${(stats.cards_learning / stats.total_cards) * 100}%` }}
                title={`Learning: ${stats.cards_learning}`}
              />
            )}
            {stats.cards_new !== undefined && stats.total_cards > 0 && (
              <div
                className="h-full bg-border"
                style={{ width: `${(stats.cards_new / stats.total_cards) * 100}%` }}
                title={`New: ${stats.cards_new}`}
              />
            )}
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-text-muted">
            {stats.cards_mature !== undefined && (
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-success" />Mature: {stats.cards_mature}</span>
            )}
            {stats.cards_young !== undefined && (
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-accent" />Young: {stats.cards_young}</span>
            )}
            {stats.cards_learning !== undefined && (
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-warning" />Learning: {stats.cards_learning}</span>
            )}
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-border" />New: {stats.cards_new}</span>
          </div>
        </div>
      )}

      {/* Performance stats */}
      {(stats.total_reviews !== undefined || stats.streak_days !== undefined || stats.average_ease !== undefined) && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {stats.total_reviews !== undefined && (
            <StatCard label="Total Reviews" value={stats.total_reviews.toLocaleString()} />
          )}
          {stats.streak_days !== undefined && (
            <StatCard label="Study Streak" value={`${stats.streak_days}d`} />
          )}
          {stats.average_ease !== undefined && (
            <StatCard label="Avg Ease" value={stats.average_ease.toFixed(2)} />
          )}
          {stats.due_this_week !== undefined && (
            <StatCard label="Due This Week" value={stats.due_this_week} />
          )}
        </div>
      )}

      {/* Study buttons */}
      <div className="flex flex-wrap items-center gap-2">
        {stats.cards_due > 0 && (
          <button
            onClick={onStudyAll}
            className="text-sm font-semibold px-6 py-2.5 rounded-lg bg-accent text-white hover:bg-accent-hover transition-colors"
          >
            Study {stats.cards_due} Due Cards
          </button>
        )}
        {selectedCollections.length > 0 && (
          <button
            onClick={() => onStudyCollections(selectedCollections.map((c) => c.name))}
            className="text-sm font-medium px-4 py-2.5 rounded-lg border border-accent text-accent hover:bg-accent hover:text-white transition-colors"
          >
            Study {selectedCollections.length} Selected ({selectedCollections.reduce((s, c) => s + c.card_count, 0)} cards)
          </button>
        )}
      </div>

      {/* Collections */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-text-secondary">Collections</h3>
        {stats.collections.length === 0 ? (
          <p className="text-sm text-text-muted py-4">No collections yet. Generate flashcards to get started.</p>
        ) : (
          <div className="space-y-1.5">
            {stats.collections.map((col) => (
              <div
                key={col.id}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg border transition-colors ${
                  selectedIds.has(col.id)
                    ? "border-accent bg-accent-muted"
                    : "border-border bg-bg-secondary hover:bg-bg-hover hover:border-border-hover"
                }`}
              >
                {/* Select checkbox */}
                <input
                  type="checkbox"
                  checked={selectedIds.has(col.id)}
                  onChange={() => toggleSelect(col.id)}
                  className="accent-accent shrink-0"
                />

                {/* Collection info */}
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium text-text-primary">{formatCollectionName(col.name)}</h4>
                  <p className="text-xs text-text-muted mt-0.5">{col.card_count} cards</p>
                </div>

                {/* Delete button */}
                {confirmDelete === col.id ? (
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => { onDeleteCollection(col.id); setConfirmDelete(null); }}
                      disabled={deleting === col.id}
                      className="text-[10px] px-2 py-0.5 rounded bg-danger text-white hover:bg-danger/80 disabled:opacity-50"
                    >
                      {deleting === col.id ? "..." : "Confirm"}
                    </button>
                    <button
                      onClick={() => setConfirmDelete(null)}
                      className="text-[10px] px-2 py-0.5 rounded border border-border text-text-muted"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmDelete(col.id)}
                    className="text-xs text-text-muted hover:text-danger shrink-0 transition-colors"
                    title="Delete collection"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

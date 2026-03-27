import { useState, useCallback } from "react";
import { FlashcardCard } from "@/components/FlashcardCard/FlashcardCard";
import {
  useFlashcardStats,
  useNextFlashcard,
  useRecordReview,
} from "@/api/flashcard-hooks";
import type { CollectionInfo } from "@/types/flashcards";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

function formatName(name: string) {
  return name.replace(/_/g, " ");
}

export function StudyPage() {
  const [studying, setStudying] = useState(false);
  const [collection, setCollection] = useState<string | undefined>();

  const { data: stats } = useFlashcardStats(USER_ID);
  const { data: flashcard, refetch } = useNextFlashcard(
    studying ? USER_ID : "",
    collection
  );
  const reviewMutation = useRecordReview();

  const handleRate = useCallback(
    (rating: number, responseTimeMs: number) => {
      if (!flashcard) return;
      reviewMutation.mutate(
        {
          user_id: USER_ID,
          flashcard_id: flashcard.flashcard_id,
          rating,
          response_time_ms: responseTimeMs,
        },
        { onSuccess: () => refetch() }
      );
    },
    [flashcard, reviewMutation, refetch]
  );

  function startStudy(col?: string) {
    setCollection(col);
    setStudying(true);
  }

  function backToPicker() {
    setStudying(false);
    setCollection(undefined);
  }

  if (!studying) {
    return <Picker stats={stats} onStudyAll={() => startStudy()} onStudyCollection={(c) => startStudy(c)} />;
  }

  if (flashcard === null) {
    return (
      <div className="max-w-lg mx-auto px-4 min-h-screen flex flex-col items-center justify-center space-y-4">
        <i className="ms ms-ability-adventure text-5xl text-success" />
        <h2 className="text-xl font-bold text-text-primary">All caught up!</h2>
        <p className="text-sm text-text-muted">No more cards due for review.</p>
        <button
          onClick={backToPicker}
          className="text-sm font-medium px-4 py-2 rounded-lg bg-accent text-white hover:bg-accent/80 transition-colors"
        >
          Back to Collections
        </button>
      </div>
    );
  }

  if (!flashcard) {
    return (
      <div className="max-w-lg mx-auto px-4 min-h-screen flex items-center justify-center text-text-muted">
        Loading...
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-4 min-h-screen">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={backToPicker}
          className="text-xs text-text-muted hover:text-accent transition-colors"
        >
          <i className="ms ms-ability-transform mr-1" style={{ transform: "scaleX(-1)", display: "inline-block" }} />
          Collections
        </button>
        {collection && (
          <span className="text-[10px] uppercase tracking-widest text-text-muted">
            {formatName(collection)}
          </span>
        )}
      </div>
      <FlashcardCard flashcard={flashcard} onRate={handleRate} />
    </div>
  );
}

function Picker({
  stats,
  onStudyAll,
  onStudyCollection,
}: {
  stats: { cards_due: number; collections: CollectionInfo[] } | undefined;
  onStudyAll: () => void;
  onStudyCollection: (name: string) => void;
}) {
  const due = stats?.cards_due ?? 0;
  const collections = stats?.collections ?? [];

  return (
    <div className="max-w-lg mx-auto px-4 py-8 min-h-screen">
      <div className="flex items-center gap-3 mb-6">
        <i className="ms ms-planeswalker text-3xl text-accent" />
        <div>
          <h1 className="text-2xl font-bold text-text-primary">Study</h1>
          <p className="text-sm text-text-muted">{due} cards due</p>
        </div>
      </div>

      <button
        onClick={onStudyAll}
        disabled={due === 0}
        className="w-full py-3 mb-6 rounded-lg bg-accent text-white font-semibold text-sm hover:bg-accent/80 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Study All Due ({due})
      </button>

      {collections.length === 0 && (
        <p className="text-center text-text-muted text-sm py-8">No collections yet.</p>
      )}

      <div className="space-y-1">
        {collections.map((c) => (
          <button
            key={c.id}
            onClick={() => onStudyCollection(c.name)}
            className="w-full flex items-center justify-between px-4 py-4 rounded-lg bg-bg-secondary hover:bg-bg-tertiary border border-border transition-colors text-left"
          >
            <span className="text-sm font-medium text-text-primary">{formatName(c.name)}</span>
            <span className="text-xs text-text-muted">{c.card_count} cards</span>
          </button>
        ))}
      </div>
    </div>
  );
}

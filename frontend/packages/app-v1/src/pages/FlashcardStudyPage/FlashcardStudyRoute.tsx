import { useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useNextFlashcard, useRecordReview } from "@/api/flashcard-hooks";
import { FlashcardCard } from "@/components/FlashcardCard/FlashcardCard";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function FlashcardStudyRoute() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const collection = searchParams.get("collection") ?? undefined;

  const { data: flashcard, refetch } = useNextFlashcard(USER_ID, collection);
  const reviewMutation = useRecordReview();

  const handleRate = useCallback((rating: number, responseTimeMs: number) => {
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
  }, [flashcard, reviewMutation, refetch]);

  if (flashcard === null) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="text-4xl">🎉</div>
        <h2 className="text-xl text-text-primary">All caught up!</h2>
        <p className="text-sm text-text-muted">No more cards due for review.</p>
        <button
          onClick={() => navigate("/flashcards")}
          className="text-sm font-medium px-4 py-2 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
        >
          Back to Dashboard
        </button>
      </div>
    );
  }

  if (!flashcard) {
    return (
      <div className="flex items-center justify-center py-24 text-text-muted">
        Loading...
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-4">
      <div className="flex items-center justify-between mb-4">
        <button
          onClick={() => navigate("/flashcards")}
          className="text-xs text-text-muted hover:text-accent transition-colors"
        >
          &larr; Dashboard
        </button>
        {collection && (
          <span className="text-[10px] uppercase tracking-widest text-text-muted">
            {collection.replace(/_/g, " ")}
          </span>
        )}
      </div>

      <FlashcardCard flashcard={flashcard} onRate={handleRate} />
    </div>
  );
}

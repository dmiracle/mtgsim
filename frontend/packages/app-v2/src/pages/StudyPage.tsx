import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { FlashcardCard } from "@/components/FlashcardCard/FlashcardCard";
import { CollectionPicker } from "@/components/CollectionPicker/CollectionPicker";
import { StudyFeed, StudyFeedEmpty, StudyFeedLoading } from "@/components/StudyFeed/StudyFeed";
import {
  useFlashcardStats,
  useNextFlashcard,
  useRecordReview,
} from "@/api/flashcard-hooks";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function StudyPage() {
  const navigate = useNavigate();
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
    return (
      <CollectionPicker
        collections={stats?.collections ?? []}
        dueCount={stats?.cards_due ?? 0}
        onStudyAll={() => startStudy()}
        onStudyCollection={(c) => startStudy(c)}
        onBack={() => navigate("/")}
      />
    );
  }

  if (flashcard === null) {
    return <StudyFeedEmpty onBack={backToPicker} />;
  }

  if (!flashcard) {
    return <StudyFeedLoading />;
  }

  return (
    <StudyFeed collection={collection} onBack={backToPicker}>
      <FlashcardCard flashcard={flashcard} onRate={handleRate} />
    </StudyFeed>
  );
}

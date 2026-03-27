import { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { FlashcardCard } from "@/components/FlashcardCard/FlashcardCard";
import { CardRecallFlashcard } from "@/components/CardRecallFlashcard/CardRecallFlashcard";
import { CollectionPicker } from "@/components/CollectionPicker/CollectionPicker";
import { StudyFeed, StudyFeedEmpty, StudyFeedLoading } from "@/components/StudyFeed/StudyFeed";
import {
  useFlashcardStats,
  useNextFlashcard,
  useRecordReview,
} from "@/api/flashcard-hooks";
import type { AspectRating } from "@/types/flashcards";

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

  const handleRecallRate = useCallback(
    (ratings: Record<string, number | string>, responseTimeMs: number) => {
      if (!flashcard) return;
      const aspectRatings = ratings as Record<string, AspectRating>;
      reviewMutation.mutate(
        {
          user_id: USER_ID,
          flashcard_id: flashcard.flashcard_id,
          aspect_ratings: aspectRatings,
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

  const isRecall = flashcard.question.card_type === "card_recall";

  return (
    <StudyFeed collection={collection} onBack={backToPicker}>
      {isRecall ? (
        <CardRecallFlashcard
          card={{
            uuid: flashcard.question.card_type === "card_recall" ? flashcard.question.uuid : String(flashcard.flashcard_id),
            name: flashcard.question.card_type === "card_recall" ? flashcard.question.card_name : "",
            image_url: flashcard.answer?.image_url ?? (flashcard.question.card_type === "card_recall" ? flashcard.question.image_url : null),
            set_code: flashcard.question.card_type === "card_recall" ? flashcard.question.set_code : undefined,
            aspects: flashcard.question.card_type === "card_recall" ? flashcard.question.aspects : undefined,
            answer: flashcard.answer,
          }}
          onRate={handleRecallRate}
        />
      ) : (
        <FlashcardCard flashcard={flashcard} onRate={handleRate} />
      )}
    </StudyFeed>
  );
}

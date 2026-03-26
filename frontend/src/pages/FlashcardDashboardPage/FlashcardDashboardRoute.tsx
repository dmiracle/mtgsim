import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  useFlashcardStats,
  useDeleteCollection,
  useReviewHistory,
  useCardDifficulty,
  useSessionAnalytics,
  useRetentionAnalytics,
  useKeywordAnalytics,
  useCollectionAnalytics,
} from "@/api/flashcard-hooks";
import { StudyDashboard } from "@/components/StudyDashboard/StudyDashboard";
import { StudyAnalytics } from "@/components/StudyAnalytics/StudyAnalytics";
import { flashcardStats as fallback } from "@/fixtures/flashcards";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function FlashcardDashboardRoute() {
  const navigate = useNavigate();
  const { data: stats } = useFlashcardStats(USER_ID);
  const deleteMutation = useDeleteCollection();
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [tab, setTab] = useState<"study" | "analytics">("study");

  const { data: reviewHistory } = useReviewHistory(USER_ID);
  const { data: cardDifficulty } = useCardDifficulty(USER_ID);
  const { data: session } = useSessionAnalytics(USER_ID);
  const { data: retention } = useRetentionAnalytics(USER_ID);
  const { data: keywords } = useKeywordAnalytics(USER_ID);
  const { data: collections } = useCollectionAnalytics(USER_ID);

  function handleDelete(collectionId: number) {
    setDeletingId(collectionId);
    deleteMutation.mutate(
      { collectionId, userId: USER_ID },
      { onSettled: () => setDeletingId(null) }
    );
  }

  function handleStudyCollections(cols: string[]) {
    const params = cols.map((c) => `collection=${encodeURIComponent(c)}`).join("&");
    navigate(`/flashcards/study?${params}`);
  }

  const tabs = [
    { id: "study" as const, label: "Study" },
    { id: "analytics" as const, label: "Analytics" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-1 border-b border-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
              tab === t.id ? "border-accent text-accent" : "border-transparent text-text-muted hover:text-text-secondary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "study" && (
        <StudyDashboard
          stats={stats ?? fallback}
          onStudyAll={() => navigate("/flashcards/study")}
          onStudyCollections={handleStudyCollections}
          onDeleteCollection={handleDelete}
          onGenerate={() => navigate("/flashcards/generate")}
          deleting={deletingId}
        />
      )}

      {tab === "analytics" && (
        <StudyAnalytics
          reviewHistory={reviewHistory}
          cardDifficulty={cardDifficulty}
          session={session}
          retention={retention}
          keywords={keywords}
          collections={collections}
        />
      )}
    </div>
  );
}

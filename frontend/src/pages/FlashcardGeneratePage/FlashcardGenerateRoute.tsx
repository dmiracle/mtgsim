import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSets } from "@/api/hooks";
import { apiFetch } from "@/api/client";
import { SetFlashcardGenerator } from "@/components/SetFlashcardGenerator/SetFlashcardGenerator";
import { CardQuizGenerator } from "@/components/CardQuizGenerator/CardQuizGenerator";
import type { GenerateResponse } from "@/types/flashcards";

const USER_ID = localStorage.getItem("flashcard_user_id") || "default_user";

export function FlashcardGenerateRoute() {
  const navigate = useNavigate();
  const { data: setsData } = useSets({ limit: 100, sort: "release_date", order: "desc" });
  const [tab, setTab] = useState<"set" | "quiz">("quiz");

  async function handleGenerate(cardType: string, setCode?: string, collectionName?: string) {
    return apiFetch<GenerateResponse>("/flashcards/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: USER_ID,
        card_type: cardType,
        set_code: setCode || undefined,
        collection_name: collectionName || undefined,
      }),
    });
  }

  const tabs = [
    { id: "quiz" as const, label: "Card Quiz" },
    { id: "set" as const, label: "Full Set" },
  ];

  return (
    <div className="py-8 max-w-lg mx-auto">
      <button
        onClick={() => navigate("/flashcards")}
        className="text-xs text-text-muted hover:text-accent transition-colors mb-4"
      >
        &larr; Back to Dashboard
      </button>

      <div className="flex items-center gap-1 border-b border-border mb-6">
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

      {tab === "quiz" && (
        <CardQuizGenerator
          sets={setsData?.data ?? []}
          onGenerate={handleGenerate}
          onComplete={() => navigate("/flashcards/study")}
        />
      )}

      {tab === "set" && (
        <SetFlashcardGenerator
          sets={setsData?.data ?? []}
          onGenerate={handleGenerate}
          onComplete={() => navigate("/flashcards/study")}
        />
      )}
    </div>
  );
}

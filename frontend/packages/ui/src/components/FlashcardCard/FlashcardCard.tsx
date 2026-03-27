import { useState, useEffect, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import type { FlashcardQuestion, FlashcardAnswer } from "@/types/flashcards";
import type { CardListResponse } from "@/types/api";
import { apiFetch, buildParams } from "@/api/client";
import { FlipCard } from "@/components/FlipCard/FlipCard";
import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { RatingButtons } from "@/components/RatingButtons/RatingButtons";

type FlashcardCardProps = {
  flashcard: FlashcardQuestion;
  onRate: (rating: number, responseTimeMs: number) => void;
};

// --- Shared card shell ---

function CardShell({
  borderColor,
  imageUrl,
  children,
}: {
  borderColor: string;
  imageUrl?: string | null;
  children: ReactNode;
}) {
  return (
    <div className={`bg-bg-secondary border-2 ${borderColor} rounded-xl overflow-hidden`}>
      {imageUrl && (
        <div className="flex justify-center bg-bg-tertiary p-4">
          <img src={imageUrl} alt="" className="max-h-[420px] rounded-lg object-contain" />
        </div>
      )}
      <div className="p-5 space-y-2">
        {children}
      </div>
    </div>
  );
}

// --- Helpers to extract image/name from question ---

function getImageUrl(question: FlashcardQuestion["question"], answer?: FlashcardAnswer | null): string | null {
  if (answer?.image_url) return answer.image_url;
  if ("image_url" in question && question.image_url) return question.image_url as string;
  return null;
}

function getCardName(question: FlashcardQuestion["question"]): string {
  if ("card_name" in question) return question.card_name;
  if ("keyword" in question) return question.keyword;
  return "";
}

// --- Type-specific content ---

function QuestionContent({ question }: { question: FlashcardQuestion["question"] }) {
  switch (question.card_type) {
    case "keyword_definition":
      return (
        <div className="text-center">
          <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-3">
            {question.keyword_type.replace("_", " ")}
          </p>
          <h2 className="text-2xl sm:text-3xl text-text-primary">{question.keyword}</h2>
          <p className="text-text-muted text-sm mt-4">What does this keyword do?</p>
        </div>
      );

    case "card_oracle":
      return (
        <div className="text-center">
          <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-2">{question.set_code}</p>
          <h2 className="text-xl sm:text-2xl text-text-primary">{question.card_name}</h2>
          <p className="text-text-muted text-sm mt-4">What is the oracle text?</p>
        </div>
      );

    case "card_mana_cost":
      return (
        <div>
          <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-3 text-center">Mana Cost</p>
          <h2 className="text-xl sm:text-2xl text-text-primary text-center">{question.card_name}</h2>
          <p className="text-sm text-text-secondary mt-3">{question.type_line}</p>
          <OracleTextBlock text={question.oracle_text} />
          <p className="text-text-muted text-sm mt-4 text-center">What is the mana cost?</p>
        </div>
      );

    case "card_stats":
      return (
        <div>
          <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-3 text-center">Power / Toughness</p>
          <h2 className="text-xl sm:text-2xl text-text-primary text-center">{question.card_name}</h2>
          <p className="text-sm text-text-secondary mt-3">{question.type_line}</p>
          <OracleTextBlock text={question.oracle_text} />
          <p className="text-text-muted text-sm mt-4 text-center">What is the power/toughness?</p>
        </div>
      );

    case "card_recall":
      return (
        <div className="text-center space-y-3">
          <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Card Recall</p>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary">{question.card_name}</h2>
          <p className="text-text-muted text-sm mt-4">What is the mana cost, type, stats, and oracle text?</p>
        </div>
      );
  }
}

function AnswerContent({ question, answer }: { question: FlashcardQuestion["question"]; answer?: FlashcardAnswer | null }) {
  const name = getCardName(question);

  switch (question.card_type) {
    case "keyword_definition":
      return (
        <div className="text-center">
          <h3 className="text-lg text-text-primary mb-3">{question.keyword}</h3>
          <p className="text-sm text-text-primary leading-relaxed">{answer?.definition ?? "—"}</p>
        </div>
      );

    case "card_oracle":
      return (
        <div className="text-center space-y-2">
          <h3 className="text-base font-bold text-text-primary">{name}</h3>
          {answer?.type_line && <p className="text-xs text-text-secondary">{answer.type_line}</p>}
          {answer?.mana_cost && (
            <div className="flex justify-center"><ManaSymbols cost={answer.mana_cost} size="md" /></div>
          )}
          {answer?.oracle_text && <OracleTextBlock text={answer.oracle_text} />}
        </div>
      );

    case "card_mana_cost":
      return (
        <div className="text-center space-y-2">
          <h3 className="text-lg text-text-primary">{name}</h3>
          {answer?.mana_cost ? (
            <>
              <div className="flex justify-center"><ManaSymbols cost={answer.mana_cost} size="lg" /></div>
              {answer.mana_value !== undefined && <p className="text-sm text-text-muted">MV {answer.mana_value}</p>}
            </>
          ) : (
            <p className="text-sm text-text-muted">—</p>
          )}
        </div>
      );

    case "card_stats":
      return (
        <div className="text-center space-y-2">
          <h3 className="text-lg text-text-primary">{name}</h3>
          {answer?.power && answer?.toughness ? (
            <p className="text-3xl font-bold text-text-primary">{answer.power}/{answer.toughness}</p>
          ) : (
            <p className="text-sm text-text-muted">—</p>
          )}
        </div>
      );

    case "card_recall":
      return (
        <div className="text-center space-y-2">
          <h3 className="text-base font-bold text-text-primary">{name}</h3>
          {answer?.type_line && <p className="text-xs text-text-secondary">{answer.type_line}</p>}
          {answer?.mana_cost && (
            <div className="flex justify-center"><ManaSymbols cost={answer.mana_cost} size="md" /></div>
          )}
          {answer?.oracle_text && <OracleTextBlock text={answer.oracle_text} />}
          {answer?.power && answer?.toughness && (
            <p className="text-lg font-bold text-text-primary">{answer.power}/{answer.toughness}</p>
          )}
        </div>
      );
  }
}

function OracleTextBlock({ text }: { text: string }) {
  return (
    <div className="bg-bg-tertiary rounded-lg p-3 mt-3 text-left">
      {text.split("\n").map((line, i) => (
        <p key={i} className="text-sm text-text-primary leading-relaxed">{line}</p>
      ))}
    </div>
  );
}

// --- Main component ---

export function FlashcardCard({ flashcard, onRate }: FlashcardCardProps) {
  const [flipped, setFlipped] = useState(false);
  const [revealTime, setRevealTime] = useState<number | null>(null);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    setFlipped(false);
    setRevealTime(null);
  }, [flashcard.flashcard_id]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.code === "Space") {
        e.preventDefault();
        if (!flipped) {
          setFlipped(true);
          setRevealTime(Date.now());
        }
      }
      if (flipped && e.key >= "0" && e.key <= "5") {
        const rating = parseInt(e.key);
        const responseMs = revealTime ? Date.now() - revealTime : Date.now() - startTime;
        onRate(rating, responseMs);
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [flipped, revealTime, startTime, onRate]);

  function handleFlip() {
    if (!flipped) {
      setFlipped(true);
      setRevealTime(Date.now());
    }
  }

  function handleRate(rating: number) {
    const responseMs = revealTime ? Date.now() - revealTime : Date.now() - startTime;
    onRate(rating, responseMs);
  }

  // Try to get image from question/answer data first
  const directImageUrl = getImageUrl(flashcard.question, flashcard.answer);

  // Fallback: look up card image by name if not available
  const cardName = getCardName(flashcard.question);
  const needsLookup = !directImageUrl && !!cardName && flashcard.question.card_type !== "keyword_definition";
  const { data: lookupData } = useQuery({
    queryKey: ["flashcard-image-lookup", cardName],
    queryFn: () => apiFetch<CardListResponse>(`/cards${buildParams({ q: cardName!, limit: 5 })}`),
    enabled: needsLookup,
    staleTime: Infinity,
  });

  // Find exact name match from search results
  const exactMatch = lookupData?.data.find((c) => c.name === cardName);
  const answerImageUrl = directImageUrl ?? exactMatch?.image_url ?? null;

  return (
    <div className="w-full max-w-[400px] mx-auto space-y-4">
      {flashcard.collection && (
        <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold text-center">
          {flashcard.collection.replace(/_/g, " ")}
        </p>
      )}

      <FlipCard
        flipped={flipped}
        onFlip={handleFlip}
        front={
          <CardShell borderColor="border-accent">
            <QuestionContent question={flashcard.question} />
          </CardShell>
        }
        back={
          <CardShell borderColor="border-success" imageUrl={answerImageUrl}>
            <AnswerContent question={flashcard.question} answer={flashcard.answer} />
          </CardShell>
        }
      />

      {!flipped && (
        <p className="text-text-muted text-xs text-center">Click card or press Space to reveal</p>
      )}
      {flipped && (
        <div className="space-y-2">
          <p className="text-text-muted text-xs text-center">How well did you recall?</p>
          <RatingButtons onRate={handleRate} compact />
        </div>
      )}
    </div>
  );
}

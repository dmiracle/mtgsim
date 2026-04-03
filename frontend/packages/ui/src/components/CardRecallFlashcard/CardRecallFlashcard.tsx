import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import type { CardListResponse } from "@/types/api";
import type { RecallAspect, FlashcardAnswer } from "@/types/flashcards";
import { apiFetch, buildParams } from "@/api/client";
import { FlipCard } from "@/components/FlipCard/FlipCard";
import { TrafficLight } from "@/components/TrafficLight/TrafficLight";
import { ImageCarousel } from "@/components/ImageCarousel/ImageCarousel";
import { RecallGuessForm } from "@/components/RecallGuessForm/RecallGuessForm";
import type { RecallGuess } from "@/components/RecallGuessForm/RecallGuessForm";
import { scoreRecallGuess } from "@/components/RecallGuessForm/recallScorer";

const DEFAULT_ASPECTS: RecallAspect[] = [
  { key: "mana_cost", label: "MV", icon_class: "ms ms-x", enabled: true },
  { key: "type_line", label: "Type", icon_class: "ms ms-saga", enabled: true },
  { key: "power_toughness", label: "Stats", icon_class: "ms ms-creature", enabled: true },
  { key: "oracle_text", label: "Oracle", icon_class: "ms ms-ability-activated", enabled: true },
];

type RecallCard = {
  uuid: string;
  name: string;
  image_url: string | null;
  set_code?: string;
  aspects?: RecallAspect[];
  answer?: FlashcardAnswer | null;
};

type CardRecallFlashcardProps = {
  card: RecallCard;
  onRate: (ratings: Record<string, number | string>, responseTimeMs: number, guess?: RecallGuess) => void;
};

export function CardRecallFlashcard({ card, onRate }: CardRecallFlashcardProps) {
  const aspects = card.aspects ?? DEFAULT_ASPECTS;
  const [flipped, setFlipped] = useState(false);
  const [startTime] = useState(Date.now());
  const [revealTime, setRevealTime] = useState<number | null>(null);
  const [completed, setCompleted] = useState(false);
  const [guess, setGuess] = useState<RecallGuess | null>(null);
  const [suggestedScores, setSuggestedScores] = useState<Record<string, "green" | "yellow" | "red"> | null>(null);
  const [key, setKey] = useState(card.uuid);

  // Fetch other versions from the same set when revealed
  const { data: printingsData } = useQuery({
    queryKey: ["card-printings", card.name, card.set_code],
    queryFn: () => apiFetch<CardListResponse>(`/cards${buildParams({ q: card.name, sets: card.set_code, limit: 20 })}`),
    enabled: flipped && !!card.name && !!card.set_code,
    staleTime: Infinity,
  });

  const sameSetPrintings = printingsData?.data.filter(
    (c) => c.name === card.name && c.image_url
  ) ?? [];

  const images = sameSetPrintings.length > 1
    ? sameSetPrintings.map((c) => ({ url: c.image_url! }))
    : card.image_url
      ? [{ url: card.image_url }]
      : [];

  const trafficAspects = aspects.map((a) => ({
    key: a.key,
    label: a.label,
    iconClass: a.icon_class,
    disabled: !a.enabled,
  }));

  const activeCount = aspects.filter((a) => a.enabled).length;

  useEffect(() => {
    setFlipped(false);
    setRevealTime(null);
    setCompleted(false);
    setGuess(null);
    setSuggestedScores(null);
    setKey(card.uuid);
  }, [card.uuid]);

  function handleReveal(g: RecallGuess) {
    setGuess(g);
    setFlipped(true);
    setRevealTime(Date.now());

    // Auto-score if we have answer data
    if (card.answer) {
      const scores = scoreRecallGuess(g, card.answer);
      setSuggestedScores(scores);
    }
  }

  function handleComplete(ratings: Record<string, number | string>) {
    setCompleted(true);
    const responseMs = revealTime ? Date.now() - revealTime : Date.now() - startTime;
    onRate(ratings, responseMs, guess ?? undefined);
  }

  const front = (
    <RecallGuessForm
      cardName={card.name}
      showStats
      onReveal={handleReveal}
    />
  );

  const back = (
    <div className="bg-bg-secondary border-2 border-success rounded-xl overflow-hidden">
      {images.length > 0 && <ImageCarousel images={images} />}
      <div className="p-4">
        {!completed && (
          <TrafficLight
            key={key}
            aspects={trafficAspects}
            initialSignals={suggestedScores ?? undefined}
            onComplete={handleComplete}
          />
        )}
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-[400px] mx-auto space-y-4">
      <FlipCard flipped={flipped} onFlip={() => {}} front={front} back={back} />
      {flipped && !completed && (
        <p className="text-text-muted text-xs text-center">
          {suggestedScores
            ? "Scores auto-filled — adjust if needed, then submit"
            : `Rate each aspect — advances when all ${activeCount} are rated`}
        </p>
      )}
    </div>
  );
}

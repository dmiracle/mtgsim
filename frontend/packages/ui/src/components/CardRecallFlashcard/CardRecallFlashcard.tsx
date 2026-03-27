import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import type { CardListResponse } from "@/types/api";
import { apiFetch, buildParams } from "@/api/client";
import { FlipCard } from "@/components/FlipCard/FlipCard";
import { TrafficLight } from "@/components/TrafficLight/TrafficLight";
import { ImageCarousel } from "@/components/ImageCarousel/ImageCarousel";

const RECALL_ASPECTS = [
  { key: "mana_cost", label: "MV", iconClass: "ms ms-x" },
  { key: "type_line", label: "Type", iconClass: "ms ms-saga" },
  { key: "power_toughness", label: "Stats", iconClass: "ms ms-creature" },
  { key: "oracle_text", label: "Oracle", iconClass: "ms ms-ability-activated" },
];

type RecallCard = {
  uuid: string;
  name: string;
  image_url: string | null;
};

type CardRecallFlashcardProps = {
  card: RecallCard;
  onRate: (ratings: Record<string, number | string>, responseTimeMs: number) => void;
};

export function CardRecallFlashcard({ card, onRate }: CardRecallFlashcardProps) {
  const [flipped, setFlipped] = useState(false);
  const [startTime] = useState(Date.now());
  const [revealTime, setRevealTime] = useState<number | null>(null);
  const [completed, setCompleted] = useState(false);
  const [key, setKey] = useState(card.uuid);

  // Fetch all printings when revealed
  const { data: printingsData } = useQuery({
    queryKey: ["card-printings", card.name],
    queryFn: () => apiFetch<CardListResponse>(`/cards${buildParams({ q: card.name, limit: 20 })}`),
    enabled: flipped && !!card.name,
    staleTime: Infinity,
  });

  // Build carousel images: primary card first, then other printings
  const allPrintings = printingsData?.data.filter(
    (c) => c.name === card.name && c.image_url
  ) ?? [];

  const images = allPrintings.length > 1
    ? allPrintings.map((c) => ({ url: c.image_url!, label: c.set_code.toUpperCase() }))
    : card.image_url
      ? [{ url: card.image_url }]
      : [];

  useEffect(() => {
    setFlipped(false);
    setRevealTime(null);
    setCompleted(false);
    setKey(card.uuid);
  }, [card.uuid]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.code === "Space" && !flipped) {
        e.preventDefault();
        setFlipped(true);
        setRevealTime(Date.now());
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [flipped]);

  function handleFlip() {
    if (!flipped) {
      setFlipped(true);
      setRevealTime(Date.now());
    }
  }

  function handleComplete(ratings: Record<string, number | string>) {
    setCompleted(true);
    const responseMs = revealTime ? Date.now() - revealTime : Date.now() - startTime;
    onRate(ratings, responseMs);
  }

  const front = (
    <div className="bg-bg-secondary border-2 border-accent rounded-xl overflow-hidden p-8">
      <div className="text-center space-y-3">
        <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
          Card Recall
        </p>
        <h2 className="text-2xl sm:text-3xl font-bold text-text-primary">{card.name}</h2>
        <p className="text-text-muted text-sm mt-6">
          What is the mana cost, power/toughness, and oracle text?
        </p>
      </div>
    </div>
  );

  const back = (
    <div className="bg-bg-secondary border-2 border-success rounded-xl overflow-hidden">
      {images.length > 0 && <ImageCarousel images={images} />}
      <div className="p-4">
        {!completed && (
          <TrafficLight key={key} aspects={RECALL_ASPECTS} onComplete={handleComplete} />
        )}
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-[400px] mx-auto space-y-4">
      <FlipCard flipped={flipped} onFlip={handleFlip} front={front} back={back} />
      {!flipped && (
        <p className="text-text-muted text-xs text-center">Click card or press Space to reveal</p>
      )}
      {flipped && !completed && (
        <p className="text-text-muted text-xs text-center">
          Rate each aspect — advances when all four are rated
        </p>
      )}
    </div>
  );
}

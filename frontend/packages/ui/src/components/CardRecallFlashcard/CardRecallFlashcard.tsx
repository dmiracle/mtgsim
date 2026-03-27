import { useState, useEffect } from "react";
import type { CardDetail } from "@/types/api";
import { FlipCard } from "@/components/FlipCard/FlipCard";
import { TrafficLight } from "@/components/TrafficLight/TrafficLight";

const RECALL_ASPECTS = [
  { key: "manaValue", label: "MV", iconClass: "ms ms-x" },
  { key: "type", label: "Type", iconClass: "ms ms-saga" },
  { key: "stats", label: "Stats", iconClass: "ms ms-creature" },
  { key: "oracle", label: "Oracle", iconClass: "ms ms-ability-activated" },
];

type CardRecallFlashcardProps = {
  card: CardDetail;
  onRate: (ratings: Record<string, number | string>, responseTimeMs: number) => void;
};

export function CardRecallFlashcard({ card, onRate }: CardRecallFlashcardProps) {
  const [flipped, setFlipped] = useState(false);
  const [startTime] = useState(Date.now());
  const [revealTime, setRevealTime] = useState<number | null>(null);
  const [completed, setCompleted] = useState(false);
  const [key, setKey] = useState(card.uuid);

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
      {card.image_url && (
        <div className="flex justify-center bg-bg-tertiary p-4">
          <img src={card.image_url} alt={card.name} className="max-h-[480px] rounded-lg object-contain" />
        </div>
      )}
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

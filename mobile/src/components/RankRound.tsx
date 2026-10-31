import { useRef, useState } from "react";
import type { Round } from "../ranking";
import type { Card } from "../types";
import { CardZoom } from "./CardZoom";

interface RankRoundProps {
  cards: Card[];
  kind: Round["kind"];
  submitting: boolean;
  onSubmit: (orderedNames: string[]) => void;
}

const LONG_PRESS_MS = 400;

const PROMPT: Record<string, string> = {
  new: "Tap cards from best to worst. Hold a card to see it large.",
  refine: "Tap cards from best to worst — these are still too close to call.",
  cycle: "These conflict with each other (A over B over C over A). Re-rank them to resolve it.",
};

export function RankRound({ cards, kind, submitting, onSubmit }: RankRoundProps) {
  const [order, setOrder] = useState<string[]>([]);
  const [zoomed, setZoomed] = useState<Card | null>(null);
  const [peeked, setPeeked] = useState<Card | null>(null);
  const pressTimer = useRef(0);
  const longPressed = useRef(false);

  // Hold a card to peek at it full-size; releasing closes it and doesn't count as a tap.
  const startPress = (card: Card) => {
    longPressed.current = false;
    pressTimer.current = window.setTimeout(() => {
      longPressed.current = true;
      setPeeked(card);
    }, LONG_PRESS_MS);
  };
  const endPress = () => {
    clearTimeout(pressTimer.current);
    setPeeked(null);
  };
  const toggle = (name: string) =>
    setOrder((o) => (o.includes(name) ? o.filter((n) => n !== name) : [...o, name]));
  // The last card's place is implied once the others are picked.
  const complete = order.length >= cards.length - 1;
  const finalOrder = [...order, ...cards.map((c) => c.name).filter((n) => !order.includes(n))];

  return (
    <div className="space-y-3 pb-24">
      <p className={`rounded-lg px-3 py-2 text-sm ${kind === "cycle" ? "bg-grade-f/20 text-fg" : "text-muted"}`}>
        {PROMPT[kind]}
      </p>
      <div className="grid grid-cols-2 gap-3">
        {cards.map((card) => {
          const rank = order.indexOf(card.name) + 1;
          return (
            <div key={card.uuid} className="relative">
              <button
                onClick={() => !longPressed.current && toggle(card.name)}
                onPointerDown={() => startPress(card)}
                onPointerUp={endPress}
                onPointerCancel={endPress}
                onPointerLeave={endPress}
                onContextMenu={(e) => e.preventDefault()}
                className="block w-full select-none [-webkit-touch-callout:none]"
                aria-label={`Rank ${card.name}`}
              >
                <img
                  src={card.image_url ?? ""}
                  alt={card.name}
                  draggable={false}
                  className={`pointer-events-none aspect-[488/680] w-full rounded-[4.5%] bg-surface object-cover ${
                    rank ? "ring-4 ring-accent" : ""
                  }`}
                />
              </button>
              {rank > 0 && (
                <span className="pointer-events-none absolute top-1/3 left-1/2 flex size-14 -translate-x-1/2 items-center justify-center rounded-full bg-accent text-3xl font-bold text-bg shadow-lg">
                  {rank}
                </span>
              )}
              <button
                onClick={() => setZoomed(card)}
                aria-label={`Zoom ${card.name}`}
                className="absolute right-1 bottom-1 flex size-9 items-center justify-center rounded-full bg-bg/80 text-lg"
              >
                ⤢
              </button>
            </div>
          );
        })}
      </div>
      <div className="fixed inset-x-0 bottom-0 flex gap-3 border-t border-line bg-bg/95 px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur">
        <button
          onClick={() => setOrder([])}
          disabled={!order.length}
          className="min-h-12 rounded-xl border border-line px-4 disabled:opacity-30"
        >
          Clear
        </button>
        <button
          onClick={() => onSubmit(finalOrder)}
          disabled={!complete || submitting}
          className="min-h-12 flex-1 rounded-xl bg-accent font-semibold text-bg disabled:opacity-30"
        >
          Save ranking
        </button>
      </div>
      {zoomed && <CardZoom card={zoomed} onClose={() => setZoomed(null)} />}
      {peeked && <CardZoom card={peeked} />}
    </div>
  );
}

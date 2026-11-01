import { useRef, useState } from "react";
import type { Round } from "../ranking";
import type { Card } from "../types";
import { CardZoom } from "./CardZoom";

interface RankRoundProps {
  cards: Card[];
  kind: Round["kind"];
  submitting: boolean;
  onSubmit: (orderedNames: string[]) => void;
  onExclude: (name: string) => void;
}

const LONG_PRESS_MS = 500;
const MOVE_TOLERANCE_PX = 10;
// Lifting the finger after a hold can fire a click onto the sheet that just
// opened; taps this soon after it opens are ignored.
const SHEET_GUARD_MS = 400;

const PROMPT: Record<string, string> = {
  new: "Tap cards from best to worst. Tap ⤢ to see them large. Long-press a card to exclude it.",
  refine: "Tap cards from best to worst — these are still too close to call.",
  cycle: "These conflict with each other (A over B over C over A). Re-rank them to resolve it.",
};

export function RankRound({ cards, kind, submitting, onSubmit, onExclude }: RankRoundProps) {
  const [order, setOrder] = useState<string[]>([]);
  const [zoomIndex, setZoomIndex] = useState<number | null>(null);
  const [confirmExclude, setConfirmExclude] = useState<{ name: string; at: number } | null>(null);
  const pressTimer = useRef<number | undefined>(undefined);
  const pressStart = useRef({ x: 0, y: 0 });
  const longPressed = useRef(false);
  const toggle = (name: string) =>
    setOrder((o) => (o.includes(name) ? o.filter((n) => n !== name) : [...o, name]));

  // Holding a card asks to exclude it; the click that ends the hold must not also rank it.
  // Only real finger movement (a scroll) cancels a hold: iOS Safari can send
  // pointercancel mid-hold, so that event is deliberately not used.
  const startPress = (name: string, x: number, y: number) => {
    longPressed.current = false;
    pressStart.current = { x, y };
    pressTimer.current = window.setTimeout(() => {
      longPressed.current = true;
      setConfirmExclude({ name, at: Date.now() });
    }, LONG_PRESS_MS);
  };
  const endPress = () => window.clearTimeout(pressTimer.current);
  const movePress = (x: number, y: number) => {
    if (Math.hypot(x - pressStart.current.x, y - pressStart.current.y) > MOVE_TOLERANCE_PX) endPress();
  };
  const closeSheet = (exclude: string | null) => {
    if (Date.now() - confirmExclude!.at < SHEET_GUARD_MS) return;
    if (exclude) onExclude(exclude);
    setConfirmExclude(null);
  };
  const onCardClick = (name: string) => {
    if (longPressed.current) longPressed.current = false;
    else toggle(name);
  };
  // The last card's place is implied once the others are picked.
  const complete = order.length >= cards.length - 1;
  const finalOrder = [...order, ...cards.map((c) => c.name).filter((n) => !order.includes(n))];

  return (
    <div className="space-y-3 pb-24">
      <p className={`rounded-lg px-3 py-2 text-sm ${kind === "cycle" ? "bg-grade-f/20 text-fg" : "text-muted"}`}>
        {PROMPT[kind]}
      </p>
      <div className="grid grid-cols-2 gap-3">
        {cards.map((card, cardIndex) => {
          const rank = order.indexOf(card.name) + 1;
          return (
            <div key={card.uuid} className="relative">
              <button
                onClick={() => onCardClick(card.name)}
                onPointerDown={(e) => startPress(card.name, e.clientX, e.clientY)}
                onPointerMove={(e) => movePress(e.clientX, e.clientY)}
                onTouchMove={(e) => movePress(e.touches[0].clientX, e.touches[0].clientY)}
                onPointerUp={endPress}
                onTouchEnd={endPress}
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
                <span className="pointer-events-none absolute top-1 left-1 flex size-8 items-center justify-center rounded-full bg-accent text-lg font-bold text-bg shadow-lg">
                  {rank}
                </span>
              )}
              <button
                onClick={() => setZoomIndex(cardIndex)}
                aria-label={`Zoom ${card.name}`}
                className="absolute bottom-1 left-1 flex size-9 items-center justify-center rounded-full bg-bg/80 text-base"
              >
                ⤢
              </button>
            </div>
          );
        })}
      </div>
      <div className="fixed inset-x-0 bottom-0 flex gap-3 border-t border-line bg-bg px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))]">
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
      {confirmExclude && (
        <div className="fixed inset-0 z-30 flex items-end bg-bg/70" onClick={() => closeSheet(null)}>
          <div
            className="w-full space-y-3 rounded-t-2xl border-t border-line bg-surface px-4 pt-4 pb-[max(1rem,env(safe-area-inset-bottom))]"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="font-semibold">Exclude {confirmExclude.name}?</p>
            <p className="text-sm text-muted">
              It won't appear in rounds or results. You can restore it from Results.
            </p>
            <div className="flex gap-3">
              <button onClick={() => closeSheet(null)} className="min-h-12 flex-1 rounded-xl border border-line">
                Cancel
              </button>
              <button
                onClick={() => closeSheet(confirmExclude.name)}
                className="min-h-12 flex-1 rounded-xl bg-grade-f font-semibold text-bg"
              >
                Exclude
              </button>
            </div>
          </div>
        </div>
      )}
      {zoomIndex !== null && (
        <CardZoom
          cards={cards}
          startIndex={zoomIndex}
          rankOf={(name) => order.indexOf(name) + 1}
          onClose={() => setZoomIndex(null)}
        />
      )}
    </div>
  );
}

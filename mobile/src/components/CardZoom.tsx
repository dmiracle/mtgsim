import { useRef, useState } from "react";
import type { Card } from "../types";

interface CardZoomProps {
  cards: Card[];
  startIndex: number;
  // rank already assigned to a card in this round, shown as a badge
  rankOf?: (name: string) => number;
  onClose: () => void;
}

const SWIPE_PX = 50;

// Full-screen card carousel: swipe left/right through the cards, tap to close.
export function CardZoom({ cards, startIndex, rankOf, onClose }: CardZoomProps) {
  const [index, setIndex] = useState(startIndex);
  const [dragX, setDragX] = useState(0);
  const startX = useRef<number | null>(null);
  const tapped = useRef(false);
  const card = cards[index];
  const rank = rankOf?.(card.name) ?? 0;

  const onPointerUp = () => {
    if (startX.current === null) return;
    startX.current = null;
    setDragX(0);
    if (dragX < -SWIPE_PX) setIndex((i) => (i + 1) % cards.length);
    else if (dragX > SWIPE_PX) setIndex((i) => (i - 1 + cards.length) % cards.length);
    tapped.current = Math.abs(dragX) < 10;
  };

  return (
    <div
      role="dialog"
      aria-label={card.name}
      onPointerDown={(e) => (startX.current = e.clientX)}
      onPointerMove={(e) => startX.current !== null && setDragX(e.clientX - startX.current)}
      onPointerUp={onPointerUp}
      // Close on click (not pointerup) so the overlay absorbs the tap instead of
      // iOS re-dispatching it to the card underneath.
      onClick={() => tapped.current && onClose()}
      onPointerCancel={() => {
        startX.current = null;
        setDragX(0);
      }}
      className="fixed inset-0 z-50 flex touch-none flex-col items-center justify-center gap-3 bg-black/90 p-4 select-none"
    >
      <div className="relative w-full max-w-md" style={{ transform: `translateX(${dragX}px)` }}>
        <img
          src={card.image_url ?? ""}
          alt={card.name}
          draggable={false}
          className="pointer-events-none w-full rounded-[4.5%]"
        />
        {rank > 0 && (
          <span className="absolute top-2 left-2 flex size-10 items-center justify-center rounded-full bg-accent text-xl font-bold text-bg shadow-lg">
            {rank}
          </span>
        )}
      </div>
      {cards.length > 1 && (
        <div className="flex gap-2">
          {cards.map((c, i) => (
            <span key={c.uuid} className={`size-2 rounded-full ${i === index ? "bg-accent" : "bg-line"}`} />
          ))}
        </div>
      )}
    </div>
  );
}

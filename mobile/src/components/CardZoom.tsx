import type { Card } from "../types";

// Full-screen card image. With onClose it's tap-to-close; without, it's a
// non-interactive "peek" shown only while a card is held down.
export function CardZoom({ card, onClose }: { card: Card; onClose?: () => void }) {
  return (
    <button
      onClick={onClose}
      className={`fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 ${onClose ? "" : "pointer-events-none"}`}
    >
      <img src={card.image_url ?? ""} alt={card.name} className="max-h-full w-full max-w-md rounded-[4.5%]" />
    </button>
  );
}

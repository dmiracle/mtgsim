import type { Card } from "../types";
import { ManaCost } from "./ManaCost";

export function CardView({ card }: { card: Card }) {
  return (
    <div className="space-y-4">
      {card.image_url ? (
        <img
          src={card.image_url}
          alt={card.name}
          draggable={false}
          className="mx-auto aspect-[488/680] w-full max-w-sm rounded-[4.5%] bg-surface object-cover shadow-xl select-none"
        />
      ) : (
        <div className="mx-auto flex aspect-[488/680] w-full max-w-sm items-center justify-center rounded-[4.5%] bg-surface p-6 text-center text-xl">
          {card.name}
        </div>
      )}
      <div className="space-y-2 rounded-xl bg-surface p-4">
        <div className="flex items-start justify-between gap-3">
          <h2 className="text-lg font-semibold leading-tight">{card.name}</h2>
          <ManaCost cost={card.mana_cost} />
        </div>
        <p className="text-sm text-muted">{card.type}</p>
        {card.text && <p className="whitespace-pre-line text-sm leading-relaxed">{card.text}</p>}
        <div className="flex flex-wrap gap-x-4 gap-y-1 pt-1 text-xs text-muted">
          <span>
            {card.set_code} #{card.number}
          </span>
          <span className="capitalize">{card.rarity}</span>
          <span>{card.price != null ? `$${card.price.toFixed(2)}` : "no price"}</span>
          {card.owns && <span className="text-accent">owned</span>}
          {card.note_count > 0 && <span>{card.note_count} note(s)</span>}
        </div>
        {card.user_tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {card.user_tags.map((t) => (
              <span key={t} className="rounded-full bg-raised px-2 py-0.5 text-xs">
                {t}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

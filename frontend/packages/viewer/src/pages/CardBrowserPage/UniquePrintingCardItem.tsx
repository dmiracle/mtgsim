import { useEffect, useState } from "react";
import { usePrintings } from "@/api/hooks";
import type { CardSummary } from "@/types/api";
import { CardGridItem } from "@/components/CardGridItem/CardGridItem";
import type { GridSize } from "@/components/GridSizeToggle/GridSizeToggle";

type UniquePrintingCardItemProps = {
  card: CardSummary;
  overrideUuid?: string;
  onSelectPrinting: (name: string, uuid: string | null) => void;
  size?: GridSize;
  pinned?: boolean;
  onPin?: (uuid: string) => void;
  onAddToDeck?: (uuid: string) => void;
  onAddToCollection?: (uuid: string) => void;
  onClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

export function UniquePrintingCardItem({
  card,
  overrideUuid,
  onSelectPrinting,
  ...itemProps
}: UniquePrintingCardItemProps) {
  // Printings are fetched lazily: on first pointer interaction, or immediately
  // when a saved override needs its printing data to render.
  const [active, setActive] = useState(!!overrideUuid);
  const { data } = usePrintings(active ? card.uuid : "");

  const printings = data ? [...data].sort((a, b) => Number(b.is_default_printing) - Number(a.is_default_printing)) : undefined;
  const overrideIndex = printings && overrideUuid ? printings.findIndex((p) => p.uuid === overrideUuid) : -1;

  // Saved override no longer among the printings (data resync): drop it
  useEffect(() => {
    if (printings && overrideUuid && overrideIndex === -1) {
      onSelectPrinting(card.name, null);
    }
  });

  const override = overrideIndex >= 0 && printings ? printings[overrideIndex] : undefined;
  const index = override ? overrideIndex : Math.max(printings?.findIndex((p) => p.uuid === card.uuid) ?? 0, 0);

  const shown = override
    ? { ...card, uuid: override.uuid, set_code: override.set_code, image_url: override.image_url, price: 0 }
    : card;

  function step(delta: number) {
    if (!printings || printings.length < 2) return;
    const next = printings[(index + delta + printings.length) % printings.length];
    onSelectPrinting(card.name, next.uuid === card.uuid ? null : next.uuid);
  }

  return (
    <div onMouseEnter={() => setActive(true)} onTouchStart={() => setActive(true)}>
      <CardGridItem
        {...itemProps}
        card={shown}
        printingNav={
          printings && printings.length > 1
            ? { index, count: printings.length, onPrev: () => step(-1), onNext: () => step(1) }
            : undefined
        }
      />
    </div>
  );
}

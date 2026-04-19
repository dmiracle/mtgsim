import type { DeckCardPrinting } from "@/types/api";
import { SetBadge } from "@/components/SetBadge/SetBadge";

type PrintingPickerProps = {
  open: boolean;
  cardName: string;
  printings: DeckCardPrinting[];
  currentUuid?: string;
  onSelect: (uuid: string) => void;
  onClose: () => void;
};

export function PrintingPicker({ open, cardName, printings, currentUuid, onSelect, onClose }: PrintingPickerProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50" onClick={onClose}>
      <div
        className="bg-bg-secondary border border-border rounded-t-xl sm:rounded-xl w-full sm:max-w-lg shadow-xl max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <div className="min-w-0">
            <h2 className="text-sm font-semibold text-text-primary">Choose Printing</h2>
            <p className="text-[11px] text-text-muted truncate">{cardName}</p>
          </div>
          <button onClick={onClose} className="text-text-muted hover:text-text-primary text-lg leading-none">&times;</button>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          {printings.length === 0 ? (
            <p className="text-xs text-text-muted text-center py-8">Loading printings...</p>
          ) : (
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
              {printings.map((p) => {
                const selected = p.uuid === currentUuid;
                return (
                  <button
                    key={p.uuid}
                    onClick={() => onSelect(p.uuid)}
                    className={`rounded-lg overflow-hidden border-2 transition-colors text-left ${
                      selected
                        ? "border-accent shadow-[0_0_8px_var(--color-accent)]"
                        : "border-border hover:border-border-hover"
                    }`}
                  >
                    <div className="aspect-[5/7] bg-bg-tertiary">
                      {p.image_url ? (
                        <img src={p.image_url} alt={`${cardName} — ${p.set_name}`} className="w-full h-full object-cover" loading="lazy" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-[10px] text-text-muted">No image</div>
                      )}
                    </div>
                    <div className="px-1.5 py-1 space-y-0.5">
                      <SetBadge code={p.set_code} size="sm" />
                      <p className="text-[10px] text-text-muted">#{p.number}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

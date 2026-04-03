import { useRef, useState } from "react";
import type { QuadrantRating as QuadrantRatingType } from "@/types/api";
import { RadarChart } from "@/components/charts/RadarChart/RadarChart";

type QuadrantRatingProps = {
  rating: QuadrantRatingType | null;
  onSave: (rating: QuadrantRatingType) => void;
  saving?: boolean;
};

const AXES = ["Developing", "Ahead", "Behind", "Parity"] as const;

export function QuadrantRating({ rating, onSave, saving = false }: QuadrantRatingProps) {
  const [values, setValues] = useState<number[]>([
    rating?.developing ?? 0,
    rating?.ahead ?? 0,
    rating?.behind ?? 0,
    rating?.parity ?? 0,
  ]);
  const [notes, setNotes] = useState(rating?.notes ?? "");

  // Live display values updated during drag without triggering radar re-render
  const [displayValues, setDisplayValues] = useState(values);

  const data = AXES.map((axis, i) => ({ axis, value: values[i] }));

  // Ref-based display updates to avoid re-render lag
  const displayRef = useRef<(HTMLSpanElement | null)[]>([]);

  function handleDrag(index: number, value: number) {
    // Update display spans directly via ref for zero-lag feedback
    const el = displayRef.current[index];
    if (el) {
      el.textContent = value > 0 ? value.toFixed(1) : "—";
    }
  }

  function handleValueChange(index: number, value: number) {
    setValues((prev) => prev.map((v, i) => (i === index ? value : v)));
    setDisplayValues((prev) => prev.map((v, i) => (i === index ? value : v)));
  }

  function handleSave() {
    const result: QuadrantRatingType = {
      developing: values[0] || null,
      ahead: values[1] || null,
      behind: values[2] || null,
      parity: values[3] || null,
      notes: notes || null,
    };
    onSave(result);
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-lg overflow-hidden">
      <div className="p-4 pb-0">
        <RadarChart
          title="Quadrant Rating"
          data={data}
          maxValue={5}
          color="accent"
          interactive
          animate={false}
          onValueChange={handleValueChange}
          onDrag={handleDrag}
          size={220}
        />
      </div>

      {/* Values summary — uses refs for live updates during drag */}
      <div className="grid grid-cols-4 gap-px bg-border mx-4">
        {AXES.map((axis, i) => (
          <div key={axis} className="bg-bg-secondary py-2 text-center">
            <p className="text-[10px] uppercase tracking-wider text-text-muted font-medium">{axis}</p>
            <p className="text-lg font-bold text-text-primary tabular-nums">
              <span ref={(el) => { displayRef.current[i] = el; }}>
                {displayValues[i] > 0 ? displayValues[i].toFixed(1) : "—"}
              </span>
            </p>
          </div>
        ))}
      </div>

      <div className="p-4 space-y-3">
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Rating notes..."
          rows={2}
          className="w-full bg-bg-tertiary border border-border rounded px-3 py-2 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
        />
        <button
          onClick={handleSave}
          disabled={saving}
          className="w-full text-xs font-medium px-3 py-2 rounded bg-accent text-white hover:bg-accent-hover disabled:opacity-50 transition-colors"
        >
          {saving ? "Saving..." : "Save Rating"}
        </button>
      </div>
    </div>
  );
}

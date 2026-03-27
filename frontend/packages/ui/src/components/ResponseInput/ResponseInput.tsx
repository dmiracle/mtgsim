import { useState } from "react";
import { RatingButtons } from "@/components/RatingButtons/RatingButtons";
import { RatingSlider } from "@/components/RatingSlider/RatingSlider";
import { TrafficLight } from "@/components/TrafficLight/TrafficLight";

type Aspect = {
  key: string;
  label: string;
  /** CSS class for the icon (used in traffic-light mode), e.g. "ms ms-x" */
  iconClass?: string;
};

type Mode = "buttons" | "slider" | "slider-horizontal" | "traffic-light";

type ResponseInputProps = {
  /** Single aspect or array of aspects to rate */
  aspects: Aspect | Aspect[];
  /** buttons: discrete 0-5, slider: vertical, slider-horizontal, traffic-light: G/Y/R cycling icons */
  mode?: Mode;
  /** Compact layout */
  compact?: boolean;
  /** Called with { [key]: rating } when all aspects are rated. Values are numbers for buttons/slider, or strings for traffic-light. */
  onComplete: (ratings: Record<string, number | string>) => void;
};

function RatingControl({ mode, compact, onRate }: { mode: Mode; compact: boolean; onRate: (v: number) => void }) {
  if (mode === "buttons") return <RatingButtons onRate={onRate} compact={compact} />;
  if (mode === "slider-horizontal") return <RatingSlider onChange={onRate} compact={compact} orientation="horizontal" />;
  return <RatingSlider onChange={onRate} compact={compact} orientation="vertical" />;
}

function isSlider(mode: Mode) {
  return mode === "slider" || mode === "slider-horizontal";
}

export function ResponseInput({
  aspects,
  mode = "buttons",
  compact = false,
  onComplete,
}: ResponseInputProps) {
  const aspectList = Array.isArray(aspects) ? aspects : [aspects];

  // Traffic light mode — completely different layout, handles its own state
  if (mode === "traffic-light") {
    const tlAspects = aspectList.map((a) => ({
      key: a.key,
      label: a.label,
      iconClass: a.iconClass ?? "ms ms-planeswalker",
    }));
    return <TrafficLight aspects={tlAspects} onComplete={onComplete} />;
  }

  // Numeric modes (buttons, slider, slider-horizontal)
  const [ratings, setRatings] = useState<Record<string, number | null>>(
    () => Object.fromEntries(aspectList.map((a) => [a.key, null]))
  );

  function rate(key: string, value: number) {
    const next = { ...ratings, [key]: value };
    setRatings(next);
    if (aspectList.every((a) => next[a.key] !== null)) {
      onComplete(next as Record<string, number>);
    }
  }

  if (aspectList.length === 1) {
    const aspect = aspectList[0];
    const r = ratings[aspect.key];
    if (r !== null) {
      return (
        <div className="text-center">
          <span className="text-[10px] text-success font-semibold">
            {aspect.label}: {r}{isSlider(mode) ? "" : "/5"}
          </span>
        </div>
      );
    }
    return <RatingControl mode={mode} compact={compact} onRate={(v) => rate(aspect.key, v)} />;
  }

  return (
    <div className="space-y-2">
      {aspectList.map((aspect) => (
        <div key={aspect.key} className="border-t border-border pt-2">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
              {aspect.label}
            </span>
            {ratings[aspect.key] !== null && (
              <span className="text-[10px] text-success font-semibold">
                {ratings[aspect.key]}{isSlider(mode) ? "" : "/5"}
              </span>
            )}
          </div>
          {ratings[aspect.key] === null && (
            <RatingControl mode={mode} compact={compact} onRate={(v) => rate(aspect.key, v)} />
          )}
        </div>
      ))}
    </div>
  );
}

import { useRef, useState } from "react";

type RatingSliderProps = {
  value?: number | null;
  min?: number;
  max?: number;
  step?: number;
  onChange: (value: number) => void;
  compact?: boolean;
};

export function getColor(ratio: number): string {
  if (ratio <= 0.5) {
    const r = 239;
    const g = Math.round(68 + ratio * 2 * (180 - 68));
    return `rgb(${r}, ${g}, 68)`;
  }
  const r = Math.round(239 - (ratio - 0.5) * 2 * (239 - 34));
  const g = Math.round(180 + (ratio - 0.5) * 2 * (197 - 180));
  return `rgb(${r}, ${g}, 94)`;
}

export function RatingSlider({
  value = null,
  min = 0,
  max = 5,
  step = 0.1,
  onChange,
  compact = false,
}: RatingSliderProps) {
  const [localValue, setLocalValue] = useState(value ?? min);
  const displayValue = value ?? localValue;
  const ratio = (displayValue - min) / (max - min);
  const color = getColor(ratio);
  const scrollAccum = useRef(0);

  function adjust(delta: number) {
    const raw = displayValue + delta;
    const clamped = Math.max(min, Math.min(max, raw));
    const rounded = Math.round(clamped * 10) / 10;
    setLocalValue(rounded);
    onChange(rounded);
  }

  function handleWheel(e: React.WheelEvent) {
    e.preventDefault();
    scrollAccum.current += e.deltaY;
    if (Math.abs(scrollAccum.current) >= 20) {
      // Scroll down = decrease, scroll up = increase
      adjust(scrollAccum.current > 0 ? -step : step);
      scrollAccum.current = 0;
    }
  }

  const w = compact ? "w-8" : "w-10";
  const textSize = compact ? "text-xs" : "text-sm";
  const btnPad = compact ? "py-0.5" : "py-1";

  return (
    <div
      className={`inline-flex flex-col items-center rounded-lg border border-border overflow-hidden ${w}`}
      onWheel={handleWheel}
    >
      <button
        onClick={() => adjust(step)}
        className={`${btnPad} w-full bg-bg-tertiary text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors text-xs text-center`}
      >
        ▲
      </button>
      <div
        className={`${btnPad} w-full flex items-center justify-center ${textSize} font-bold tabular-nums`}
        style={{ backgroundColor: color, color: ratio > 0.35 && ratio < 0.65 ? "#000" : "#fff" }}
      >
        {displayValue.toFixed(1)}
      </div>
      <button
        onClick={() => adjust(-step)}
        className={`${btnPad} w-full bg-bg-tertiary text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors text-xs text-center`}
      >
        ▼
      </button>
    </div>
  );
}

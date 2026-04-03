import { useRef, useState } from "react";

type RatingSliderProps = {
  value?: number | null;
  min?: number;
  max?: number;
  step?: number;
  /** Called only on explicit confirm (click value or press Enter) */
  onChange: (value: number) => void;
  compact?: boolean;
  orientation?: "vertical" | "horizontal";
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
  orientation = "vertical",
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
  }

  function confirm() {
    onChange(displayValue);
  }

  function handleWheel(e: React.WheelEvent) {
    e.preventDefault();
    const delta = orientation === "horizontal" ? e.deltaX || e.deltaY : e.deltaY;
    scrollAccum.current += delta;
    if (Math.abs(scrollAccum.current) >= 20) {
      const dir = orientation === "horizontal"
        ? (scrollAccum.current > 0 ? step : -step)
        : (scrollAccum.current > 0 ? -step : step);
      adjust(dir);
      scrollAccum.current = 0;
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") {
      e.preventDefault();
      confirm();
    }
    const incKeys = orientation === "horizontal" ? ["ArrowRight", "ArrowUp"] : ["ArrowUp"];
    const decKeys = orientation === "horizontal" ? ["ArrowLeft", "ArrowDown"] : ["ArrowDown"];
    if (incKeys.includes(e.key)) { e.preventDefault(); adjust(step); }
    if (decKeys.includes(e.key)) { e.preventDefault(); adjust(-step); }
  }

  if (orientation === "horizontal") {
    const h = compact ? "h-8" : "h-10";
    const textSize = compact ? "text-sm" : "text-base";
    const arrowPad = compact ? "px-2" : "px-3";

    return (
      <div
        className={`inline-flex flex-row items-center rounded-lg border border-border overflow-hidden ${h} select-none`}
        onWheel={handleWheel}
        onKeyDown={handleKeyDown}
        tabIndex={0}
      >
        <button
          onClick={() => adjust(-step)}
          className={`${arrowPad} h-full bg-bg-tertiary text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors text-sm`}
        >
          ◀
        </button>
        <button
          onClick={confirm}
          title="Click to confirm"
          className={`px-4 h-full flex items-center justify-center ${textSize} font-bold tabular-nums cursor-pointer hover:opacity-80 transition-opacity`}
          style={{ backgroundColor: color, color: ratio > 0.35 && ratio < 0.65 ? "#000" : "#fff" }}
        >
          {displayValue.toFixed(1)}
        </button>
        <button
          onClick={() => adjust(step)}
          className={`${arrowPad} h-full bg-bg-tertiary text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors text-sm`}
        >
          ▶
        </button>
      </div>
    );
  }

  const w = compact ? "w-10" : "w-12";
  const textSize = compact ? "text-sm" : "text-base";
  const arrowBtnPad = compact ? "py-1.5" : "py-2";
  const valuePad = compact ? "py-3" : "py-4";

  return (
    <div
      className={`inline-flex flex-col items-center rounded-lg border border-border overflow-hidden ${w} select-none`}
      onWheel={handleWheel}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <button
        onClick={() => adjust(step)}
        className={`${arrowBtnPad} w-full bg-bg-tertiary text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors text-sm text-center`}
      >
        ▲
      </button>
      <button
        onClick={confirm}
        title="Click to confirm"
        className={`${valuePad} w-full flex items-center justify-center ${textSize} font-bold tabular-nums cursor-pointer hover:opacity-80 transition-opacity`}
        style={{ backgroundColor: color, color: ratio > 0.35 && ratio < 0.65 ? "#000" : "#fff" }}
      >
        {displayValue.toFixed(1)}
      </button>
      <button
        onClick={() => adjust(-step)}
        className={`${arrowBtnPad} w-full bg-bg-tertiary text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors text-sm text-center`}
      >
        ▼
      </button>
    </div>
  );
}

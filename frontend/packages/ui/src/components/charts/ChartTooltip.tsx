import { useState } from "react";

type TooltipData = {
  label: string;
  value: string | number;
  x: number;
  y: number;
};

export function useTooltip() {
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);

  function show(label: string, value: string | number, x: number, y: number) {
    setTooltip({ label, value, x, y });
  }

  function hide() {
    setTooltip(null);
  }

  return { tooltip, show, hide };
}

export function ChartTooltip({ tooltip }: { tooltip: TooltipData | null }) {
  if (!tooltip) return null;

  return (
    <div
      className="absolute pointer-events-none z-10 bg-bg-secondary border border-border rounded px-2.5 py-1.5 text-xs shadow-lg"
      style={{
        left: tooltip.x,
        top: tooltip.y,
        transform: "translate(-50%, -120%)",
      }}
    >
      <span className="text-text-muted">{tooltip.label}</span>
      <span className="text-text-primary font-medium ml-2">{tooltip.value}</span>
    </div>
  );
}

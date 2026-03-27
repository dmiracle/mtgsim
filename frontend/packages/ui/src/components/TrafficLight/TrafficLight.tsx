import { useState } from "react";

type Signal = "none" | "green" | "yellow" | "red";

const CYCLE: Signal[] = ["none", "green", "yellow", "red"];

type Aspect = {
  key: string;
  label: string;
  iconClass: string;
  disabled?: boolean;
};

type TrafficLightProps = {
  aspects: Aspect[];
  onComplete: (ratings: Record<string, Signal>) => void;
};

const signalStyles: Record<Signal, string> = {
  none: "bg-bg-tertiary border-border text-text-muted hover:border-border-hover",
  green: "bg-success/20 border-success text-success",
  yellow: "bg-warning/20 border-warning text-warning",
  red: "bg-danger/20 border-danger text-danger",
};

export function TrafficLight({ aspects, onComplete }: TrafficLightProps) {
  const activeAspects = aspects.filter((a) => !a.disabled);

  const [signals, setSignals] = useState<Record<string, Signal>>(
    () => Object.fromEntries(activeAspects.map((a) => [a.key, "none"]))
  );
  const [submitted, setSubmitted] = useState(false);

  function cycle(key: string) {
    if (submitted) return;
    setSignals((prev) => {
      const current = prev[key];
      const idx = CYCLE.indexOf(current);
      const next = CYCLE[(idx + 1) % CYCLE.length];
      return { ...prev, [key]: next };
    });
  }

  function setAll(signal: Signal) {
    if (submitted) return;
    setSignals(Object.fromEntries(activeAspects.map((a) => [a.key, signal])));
  }

  const allSet = activeAspects.every((a) => signals[a.key] !== "none");

  function submit() {
    if (!allSet || submitted) return;
    setSubmitted(true);
    onComplete(signals);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-center gap-1.5">
        {/* All green */}
        <button
          onClick={() => { setAll("green"); }}
          disabled={submitted}
          className="w-10 h-10 rounded-lg border-2 border-success/40 bg-success/10 text-success hover:bg-success/20 transition-all disabled:opacity-60 flex items-center justify-center"
        >
          <i className="ms ms-ability-transform" style={{ fontSize: "1.2em" }} />
        </button>

        <div className="w-px h-6 bg-border mx-1" />

        {/* Individual aspect icons */}
        {aspects.map((aspect) => {
          if (aspect.disabled) {
            return (
              <div key={aspect.key} className="relative group">
                <div className="w-10 h-10 rounded-lg border-2 border-border/30 bg-bg-tertiary/50 flex items-center justify-center opacity-30">
                  <i className={aspect.iconClass} style={{ fontSize: "1.2em" }} />
                </div>
                <div className="pointer-events-none absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                  <div className="bg-bg-primary border border-border rounded px-2 py-0.5 text-[10px] font-semibold text-text-muted whitespace-nowrap shadow-lg">
                    {aspect.label} — N/A
                  </div>
                </div>
              </div>
            );
          }

          const signal = signals[aspect.key];
          return (
            <div key={aspect.key} className="relative group">
              <button
                onClick={() => cycle(aspect.key)}
                disabled={submitted}
                className={`w-10 h-10 rounded-lg border-2 flex items-center justify-center transition-all disabled:opacity-60 ${signalStyles[signal]}`}
              >
                <i className={aspect.iconClass} style={{ fontSize: "1.2em" }} />
              </button>
              <div className="pointer-events-none absolute -top-8 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                <div className="bg-bg-primary border border-border rounded px-2 py-0.5 text-[10px] font-semibold text-text-secondary whitespace-nowrap shadow-lg">
                  {aspect.label}
                  {signal !== "none" && (
                    <span className={`ml-1 ${signal === "green" ? "text-success" : signal === "yellow" ? "text-warning" : "text-danger"}`}>
                      {signal}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        <div className="w-px h-6 bg-border mx-1" />

        {/* All red */}
        <button
          onClick={() => { setAll("red"); }}
          disabled={submitted}
          className="w-10 h-10 rounded-lg border-2 border-danger/40 bg-danger/10 text-danger hover:bg-danger/20 transition-all disabled:opacity-60 flex items-center justify-center"
        >
          <i className="ms ms-ability-transform" style={{ fontSize: "1.2em", transform: "scaleX(-1)" }} />
        </button>
      </div>

      {allSet && !submitted && (
        <div className="flex justify-center">
          <button
            onClick={submit}
            className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-accent text-white hover:bg-accent/80 transition-colors"
          >
            Submit
          </button>
        </div>
      )}
    </div>
  );
}

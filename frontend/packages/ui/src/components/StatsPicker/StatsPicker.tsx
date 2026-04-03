import { useState } from "react";

type StatsPickerProps = {
  power?: string;
  toughness?: string;
  onChange: (power: string, toughness: string) => void;
};

export function StatsPicker({ power: initP = "", toughness: initT = "", onChange }: StatsPickerProps) {
  const [power, setPower] = useState(initP);
  const [toughness, setToughness] = useState(initT);

  function updatePower(v: string) {
    setPower(v);
    onChange(v, toughness);
  }

  function updateToughness(v: string) {
    setToughness(v);
    onChange(power, v);
  }

  return (
    <div className="flex items-center justify-center gap-2">
      <input
        type="text"
        value={power}
        onChange={(e) => updatePower(e.target.value)}
        placeholder="P"
        className="w-12 h-12 rounded-lg bg-bg-tertiary border border-border text-center text-lg font-bold text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
      />
      <span className="text-xl font-bold text-text-muted">/</span>
      <input
        type="text"
        value={toughness}
        onChange={(e) => updateToughness(e.target.value)}
        placeholder="T"
        className="w-12 h-12 rounded-lg bg-bg-tertiary border border-border text-center text-lg font-bold text-text-primary placeholder-text-muted focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent/30 transition-all"
      />
    </div>
  );
}

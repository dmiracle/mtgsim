import { useState } from "react";

type StatsPickerProps = {
  power?: string;
  toughness?: string;
  onChange: (power: string, toughness: string) => void;
};

const COMMON_VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "*"];

export function StatsPicker({ power: initP = "", toughness: initT = "", onChange }: StatsPickerProps) {
  const [power, setPower] = useState(initP);
  const [toughness, setToughness] = useState(initT);
  const [editing, setEditing] = useState<"power" | "toughness">("power");

  function pick(value: string) {
    if (editing === "power") {
      setPower(value);
      onChange(value, toughness);
      setEditing("toughness");
    } else {
      setToughness(value);
      onChange(power, value);
    }
  }

  return (
    <div className="space-y-3">
      {/* Display */}
      <div className="flex items-center justify-center gap-2">
        <button
          onClick={() => setEditing("power")}
          className={`w-12 h-12 rounded-lg text-lg font-bold flex items-center justify-center border-2 transition-all ${
            editing === "power"
              ? "border-accent text-accent bg-accent/10"
              : power
                ? "border-border text-text-primary bg-bg-secondary"
                : "border-border border-dashed text-text-muted bg-bg-tertiary"
          }`}
        >
          {power || "P"}
        </button>
        <span className="text-xl font-bold text-text-muted">/</span>
        <button
          onClick={() => setEditing("toughness")}
          className={`w-12 h-12 rounded-lg text-lg font-bold flex items-center justify-center border-2 transition-all ${
            editing === "toughness"
              ? "border-accent text-accent bg-accent/10"
              : toughness
                ? "border-border text-text-primary bg-bg-secondary"
                : "border-border border-dashed text-text-muted bg-bg-tertiary"
          }`}
        >
          {toughness || "T"}
        </button>
      </div>

      {/* Label */}
      <p className="text-[10px] uppercase tracking-widest text-text-muted text-center font-semibold">
        {editing === "power" ? "Select Power" : "Select Toughness"}
      </p>

      {/* Number pad */}
      <div className="flex flex-wrap gap-1 justify-center">
        {COMMON_VALUES.map((v) => (
          <button
            key={v}
            onClick={() => pick(v)}
            className="w-9 h-9 rounded-full text-xs font-bold bg-bg-tertiary border border-border text-text-muted hover:border-border-hover hover:text-text-secondary transition-all active:scale-90"
          >
            {v}
          </button>
        ))}
      </div>
    </div>
  );
}

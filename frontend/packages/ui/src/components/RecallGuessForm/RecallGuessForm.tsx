import { useState } from "react";
import { ManaValuePicker } from "@/components/ManaValuePicker/ManaValuePicker";
import { TypeLinePicker } from "@/components/TypeLinePicker/TypeLinePicker";
import { StatsPicker } from "@/components/StatsPicker/StatsPicker";
import { OracleTextInput } from "@/components/OracleTextInput/OracleTextInput";

export type RecallGuess = {
  manaCost: string;
  typeLine: string;
  power: string;
  toughness: string;
  oracleText: string;
};

type RecallGuessFormProps = {
  cardName: string;
  showStats?: boolean;
  onReveal: (guess: RecallGuess) => void;
};

export function RecallGuessForm({ cardName, showStats = true, onReveal }: RecallGuessFormProps) {
  const [manaCost, setManaCost] = useState("");
  const [typeLine, setTypeLine] = useState("");
  const [power, setPower] = useState("");
  const [toughness, setToughness] = useState("");
  const [oracleText, setOracleText] = useState("");

  function handleReveal() {
    onReveal({ manaCost, typeLine, power, toughness, oracleText });
  }

  return (
    <div className="bg-bg-secondary border-2 border-accent rounded-xl overflow-hidden">
      <div className="p-5 space-y-4">
        {/* Card name */}
        <div className="text-center">
          <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold mb-1">
            Card Recall
          </p>
          <h2 className="text-2xl sm:text-3xl font-bold text-text-primary">{cardName}</h2>
        </div>

        {/* Mana cost */}
        <Section label="Mana Cost">
          <ManaValuePicker value={manaCost} onChange={setManaCost} />
        </Section>

        {/* Type line */}
        <Section label="Type">
          <TypeLinePicker value={typeLine} onChange={setTypeLine} />
        </Section>

        {/* Stats */}
        {showStats && (
          <Section label="Power / Toughness">
            <StatsPicker
              power={power}
              toughness={toughness}
              onChange={(p, t) => { setPower(p); setToughness(t); }}
            />
          </Section>
        )}

        {/* Oracle text */}
        <Section label="Oracle Text">
          <OracleTextInput value={oracleText} onChange={setOracleText} />
        </Section>

        {/* Reveal */}
        <button
          onClick={handleReveal}
          className="w-full py-3 rounded-xl bg-accent text-white font-semibold text-sm hover:bg-accent/80 active:scale-[0.98] transition-all"
        >
          Reveal Card
        </button>
      </div>
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <p className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">{label}</p>
      {children}
    </div>
  );
}

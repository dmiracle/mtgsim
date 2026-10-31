const SYMBOL_BG: Record<string, string> = {
  W: "bg-mana-w",
  U: "bg-mana-u",
  B: "bg-mana-b",
  R: "bg-mana-r",
  G: "bg-mana-g",
};

export function ManaCost({ cost }: { cost: string | null }) {
  const symbols = cost?.match(/\{[^}]+\}/g) ?? [];
  return (
    <span className="inline-flex gap-0.5">
      {symbols.map((s, i) => {
        const sym = s.slice(1, -1);
        return (
          <span
            key={i}
            className={`inline-flex size-5 items-center justify-center rounded-full text-[11px] font-bold text-bg ${
              SYMBOL_BG[sym] ?? "bg-mana-c"
            }`}
          >
            {sym in SYMBOL_BG ? "" : sym}
          </span>
        );
      })}
    </span>
  );
}

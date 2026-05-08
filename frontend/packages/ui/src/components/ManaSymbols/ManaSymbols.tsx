type ManaSymbolsProps = {
  cost: string;
  size?: "sm" | "md" | "lg";
  shadow?: boolean;
  dimmed?: boolean;
  interactive?: boolean;
};

const sizePx = {
  sm: "0.85em",
  md: "1.2em",
  lg: "1.8em",
};

function symbolToClass(symbol: string): string {
  const lower = symbol.toLowerCase();
  if (lower.includes("/")) {
    return `ms-${lower.replace(/\//g, "")}`;
  }
  return `ms-${lower}`;
}

export function ManaSymbols({ cost, size = "md", shadow = true, dimmed = false, interactive = false }: ManaSymbolsProps) {
  if (!cost) return null;

  const symbols = cost.match(/\{([^}]+)\}/g);
  if (!symbols) return <span>{cost}</span>;

  return (
    <span className="inline-flex items-center gap-0.5">
      {symbols.map((raw, i) => {
        const symbol = raw.replace(/[{}]/g, "");
        const classes = [
          "ms",
          "ms-cost",
          symbolToClass(symbol),
        ].join(" ");

        const style: React.CSSProperties = {
          fontSize: sizePx[size],
          ...(shadow ? { boxShadow: "-0.06em 0.07em 0 rgba(0,0,0,0.6), 0 0.06em 0 rgba(0,0,0,0.6)" } : {}),
          ...(dimmed ? { filter: "grayscale(100%) opacity(0.35)" } : {}),
          ...(interactive ? { transition: "filter 0.15s, transform 0.15s", cursor: "pointer" } : {}),
        };

        return <i key={i} className={classes} style={style} aria-hidden="true" title={symbol} />;
      })}
    </span>
  );
}

// Single mana icon for use in pickers
type ManaIconProps = {
  symbol: string;
  size?: "sm" | "md" | "lg";
  shadow?: boolean;
  dimmed?: boolean;
  glowing?: boolean;
};

const SYMBOL_CLASS: Record<string, string> = { m: "multicolor" };

export function ManaIcon({ symbol, size = "md", shadow = true, dimmed = false, glowing = false }: ManaIconProps) {
  const lower = symbol.toLowerCase();
  const classes = [
    "ms",
    "ms-cost",
    `ms-${SYMBOL_CLASS[lower] ?? lower}`,
  ].join(" ");

  const style: React.CSSProperties = {
    fontSize: sizePx[size],
    transition: "filter 0.15s, transform 0.15s, box-shadow 0.15s",
    ...(shadow ? { boxShadow: "-0.06em 0.07em 0 rgba(0,0,0,0.6), 0 0.06em 0 rgba(0,0,0,0.6)" } : {}),
    ...(dimmed ? { filter: "grayscale(100%) opacity(0.35)" } : {}),
    ...(glowing ? { boxShadow: "0 0 10px 3px var(--color-accent), -0.06em 0.07em 0 rgba(0,0,0,0.6)" } : {}),
  };

  return <i className={classes} style={style} aria-hidden="true" title={symbol} />;
}

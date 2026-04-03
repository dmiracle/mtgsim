type CardTypeIconProps = {
  type: string;
  size?: number;
  className?: string;
};

const typeToMs: Record<string, string> = {
  creature: "ms-creature",
  instant: "ms-instant",
  sorcery: "ms-sorcery",
  enchantment: "ms-enchantment",
  artifact: "ms-artifact",
  planeswalker: "ms-planeswalker",
  land: "ms-land",
  battle: "ms-saga",
};

export function CardTypeIcon({ type, size = 18, className = "" }: CardTypeIconProps) {
  const key = type.toLowerCase();
  const msClass = typeToMs[key];

  if (!msClass) {
    return (
      <span
        className={`inline-flex items-center justify-center ${className}`}
        style={{ width: size, height: size, fontSize: size * 0.6 }}
        title={type}
      >
        ?
      </span>
    );
  }

  return (
    <i
      className={`ms ${msClass} ${className}`}
      style={{ fontSize: size }}
      aria-hidden="true"
      title={type}
    />
  );
}

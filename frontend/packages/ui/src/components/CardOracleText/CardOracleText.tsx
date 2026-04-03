import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";

type CardOracleTextProps = {
  text: string;
  flavor_text?: string | null;
};

// Split text on mana symbols like {W}, {2}{U}, {T}, etc and render them inline
function renderTextWithMana(text: string) {
  const parts = text.split(/(\{[^}]+\}(?:\{[^}]+\})*)/g);
  return parts.map((part, i) => {
    if (part.match(/^\{[^}]+\}/)) {
      return <ManaSymbols key={i} cost={part} size="sm" shadow={false} />;
    }
    return <span key={i}>{part}</span>;
  });
}

export function CardOracleText({ text, flavor_text }: CardOracleTextProps) {
  const paragraphs = text.split("\n");

  return (
    <div className="space-y-3">
      <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-2">
        {paragraphs.map((p, i) => (
          <p key={i} className="text-sm text-text-primary leading-relaxed">
            {renderTextWithMana(p)}
          </p>
        ))}
      </div>
      {flavor_text && (
        <div className="border-l-2 border-border pl-4">
          <p className="text-sm text-text-muted italic leading-relaxed">{flavor_text}</p>
        </div>
      )}
    </div>
  );
}

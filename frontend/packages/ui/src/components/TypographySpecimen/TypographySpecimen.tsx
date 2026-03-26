import { ManaSymbols } from "@/components/ManaSymbols/ManaSymbols";
import { SetBadge } from "@/components/SetBadge/SetBadge";

export function TypographySpecimen() {
  return (
    <div className="space-y-8">
      {/* Heading scale */}
      <section className="space-y-3">
        <h3 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Heading Scale</h3>
        <div className="space-y-2">
          <h1 className="text-3xl text-text-primary" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number, letterSpacing: "var(--font-letter-heading)" }}>
            MTG Deck Viewer
          </h1>
          <h2 className="text-2xl text-text-primary" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number, letterSpacing: "var(--font-letter-heading)" }}>
            Modern Horizons 2
          </h2>
          <h3 className="text-xl text-text-primary" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number, letterSpacing: "var(--font-letter-heading)" }}>
            Deck Statistics
          </h3>
          <h4 className="text-lg text-text-primary" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number, letterSpacing: "var(--font-letter-heading)" }}>
            Format Legality
          </h4>
          <h5 className="text-base text-text-primary" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number, letterSpacing: "var(--font-letter-heading)" }}>
            Keyword Abilities
          </h5>
        </div>
      </section>

      {/* Body text */}
      <section className="space-y-3">
        <h3 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Body Text</h3>
        <p className="text-sm text-text-primary leading-relaxed max-w-lg" style={{ fontFamily: "var(--font-body)" }}>
          Lightning Bolt deals 3 damage to any target. One of the most iconic cards in Magic's history,
          it has defined red aggressive strategies since Alpha. Legal in Modern, Legacy, Vintage, Commander, and Pauper.
        </p>
        <p className="text-xs text-text-secondary leading-relaxed max-w-lg" style={{ fontFamily: "var(--font-body)" }}>
          The sparkmage shrieked, calling on the rage of the storms of his youth. To his surprise,
          the sky responded with a fierce energy he'd never thought to see again.
        </p>
      </section>

      {/* Card context */}
      <section className="space-y-3">
        <h3 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Card Context</h3>
        <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3 max-w-md">
          <div className="flex items-start justify-between">
            <h4 className="text-base text-text-primary" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number }}>
              Ragavan, Nimble Pilferer
            </h4>
            <ManaSymbols cost="{R}" size="md" />
          </div>
          <p className="text-xs text-text-secondary" style={{ fontFamily: "var(--font-body)" }}>
            Legendary Creature — Monkey Pirate
          </p>
          <p className="text-xs text-text-primary leading-relaxed" style={{ fontFamily: "var(--font-body)" }}>
            Whenever Ragavan, Nimble Pilferer deals combat damage to a player, create a Treasure token and exile the top card of that player's library. Until end of turn, you may cast that card.
          </p>
          <p className="text-xs text-text-primary" style={{ fontFamily: "var(--font-body)" }}>
            Dash <ManaSymbols cost="{1}{R}" size="sm" shadow={false} />
          </p>
          <div className="flex items-center justify-between pt-2 border-t border-border">
            <SetBadge code="MH2" name="Modern Horizons 2" rarity="mythic" size="sm" />
            <span className="text-xs text-text-muted" style={{ fontFamily: "var(--font-body)" }}>2/1</span>
            <span className="text-xs text-success font-medium" style={{ fontFamily: "var(--font-body)" }}>$55.00</span>
          </div>
        </div>
      </section>

      {/* Labels & UI text */}
      <section className="space-y-3">
        <h3 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Labels & UI</h3>
        <div className="flex flex-wrap gap-3 items-center">
          <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold" style={{ fontFamily: "var(--font-body)" }}>FILTER LABEL</span>
          <span className="text-xs font-medium text-text-secondary" style={{ fontFamily: "var(--font-body)" }}>Section Title</span>
          <span className="text-xs text-text-muted" style={{ fontFamily: "var(--font-body)" }}>Helper text</span>
          <span className="text-xs font-semibold text-accent" style={{ fontFamily: "var(--font-body)" }}>Link Text</span>
          <span className="text-sm font-bold text-success tabular-nums" style={{ fontFamily: "var(--font-body)" }}>$42.50</span>
          <span className="text-lg font-bold text-text-primary tabular-nums" style={{ fontFamily: "var(--font-heading)" }}>28,500</span>
        </div>
      </section>

      {/* Monospace */}
      <section className="space-y-3">
        <h3 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Monospace</h3>
        <div className="bg-bg-tertiary rounded-lg p-4 space-y-1">
          <p className="text-xs text-text-secondary" style={{ fontFamily: "var(--font-mono)" }}>
            a1b2c3d4-e5f6-7890-abcd-ef1234567890
          </p>
          <p className="text-xs text-text-secondary" style={{ fontFamily: "var(--font-mono)" }}>
            {`{ "name": "Lightning Bolt", "mana_cost": "{R}" }`}
          </p>
          <p className="text-xs text-text-muted" style={{ fontFamily: "var(--font-mono)" }}>
            GET /api/cards?q=bolt&format=modern&page=1
          </p>
        </div>
      </section>

      {/* Numbers */}
      <section className="space-y-3">
        <h3 className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">Numbers & Data</h3>
        <div className="grid grid-cols-4 gap-3">
          {[
            { label: "Total Decks", value: "42" },
            { label: "Total Cards", value: "28,500" },
            { label: "Collection Value", value: "$1,245.50" },
            { label: "Avg per Card", value: "$2.13" },
          ].map((stat) => (
            <div key={stat.label} className="bg-bg-secondary border border-border rounded-lg p-3 text-center">
              <p className="text-[10px] text-text-muted" style={{ fontFamily: "var(--font-body)" }}>{stat.label}</p>
              <p className="text-xl font-bold text-text-primary tabular-nums mt-1" style={{ fontFamily: "var(--font-heading)", fontWeight: "var(--font-weight-heading)" as unknown as number }}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

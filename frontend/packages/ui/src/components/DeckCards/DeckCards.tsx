import type { DeckCard, TagCount } from "@/types/api";
import { CardFilterBar } from "@/components/CardFilterBar/CardFilterBar";
import type { CardFilters } from "@/components/CardFilterBar/CardFilterBar";
import { CardGrid } from "@/components/CardGrid/CardGrid";
import type { CardSummary } from "@/types/api";

type DeckCardsProps = {
  commander: DeckCard[];
  main_board: DeckCard[];
  side_board: DeckCard[];
  filters: CardFilters;
  onFiltersChange: (filters: CardFilters) => void;
  availableTags?: TagCount[];
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
};

function deckCardToSummary(card: DeckCard): CardSummary {
  return {
    uuid: card.uuid,
    name: card.name,
    type: card.type,
    mana_cost: card.mana_cost,
    mana_value: card.mana_value,
    rarity: card.rarity,
    set_code: "",
    color_identity: card.colors,
    tags: card.tags,
    text: card.text,
    price: card.price,
    image_url: card.image_url,
    owns: card.owns_enough,
    wants: false,
    total_owned: card.owned_count,
    total_wanted: 0,
  };
}

function Section({ title, cards, count, onCardClick, onSetClick }: {
  title: string;
  cards: DeckCard[];
  count: number;
  onCardClick?: (uuid: string) => void;
  onSetClick?: (code: string) => void;
}) {
  if (cards.length === 0) return null;

  const quantities = Object.fromEntries(cards.map((c) => [c.uuid, c.count]));

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-text-secondary">
        {title} <span className="text-text-muted font-normal">({count})</span>
      </h3>
      <CardGrid
        cards={cards.map(deckCardToSummary)}
        quantities={quantities}
        onCardClick={onCardClick}
        onSetClick={onSetClick}
      />
    </div>
  );
}

export function DeckCards({
  commander,
  main_board,
  side_board,
  filters,
  onFiltersChange,
  availableTags = [],
  onCardClick,
  onSetClick,
}: DeckCardsProps) {
  const totalCommander = commander.reduce((s, c) => s + c.count, 0);
  const totalMain = main_board.reduce((s, c) => s + c.count, 0);
  const totalSide = side_board.reduce((s, c) => s + c.count, 0);

  return (
    <div className="space-y-4">
      <CardFilterBar
        filters={filters}
        onChange={onFiltersChange}
        availableTags={availableTags}
      />
      <Section title="Commander" cards={commander} count={totalCommander} onCardClick={onCardClick} onSetClick={onSetClick} />
      <Section title="Main Board" cards={main_board} count={totalMain} onCardClick={onCardClick} onSetClick={onSetClick} />
      <Section title="Sideboard" cards={side_board} count={totalSide} onCardClick={onCardClick} onSetClick={onSetClick} />
    </div>
  );
}

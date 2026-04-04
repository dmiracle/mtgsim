import { useMemo } from "react";
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

function applyFilters(cards: DeckCard[], filters: CardFilters): DeckCard[] {
  return cards.filter((c) => {
    if (filters.text && !c.text.toLowerCase().includes(filters.text.toLowerCase()) && !c.name.toLowerCase().includes(filters.text.toLowerCase())) return false;
    if (filters.colors.length && !filters.colors.some((color) => c.colors.includes(color))) return false;
    if (filters.rarities.length && !filters.rarities.includes(c.rarity)) return false;
    if (filters.types.length && !filters.types.some((t) => c.type.toLowerCase().includes(t.toLowerCase()))) return false;
    if (filters.tags.length && !filters.tags.some((tag) => c.tags.includes(tag))) return false;
    if (filters.manaValue.length) {
      const mv = Math.floor(c.mana_value);
      const has7Plus = filters.manaValue.includes(7);
      if (!filters.manaValue.includes(mv) && !(has7Plus && mv >= 7)) return false;
    }
    return true;
  });
}

const RARITY_ORDER: Record<string, number> = { common: 0, uncommon: 1, rare: 2, mythic: 3 };

function sortCards(cards: DeckCard[], sort: string, order: "asc" | "desc"): DeckCard[] {
  const dir = order === "asc" ? 1 : -1;
  return [...cards].sort((a, b) => {
    let cmp = 0;
    switch (sort) {
      case "mana_value":
        cmp = a.mana_value - b.mana_value;
        break;
      case "rarity":
        cmp = (RARITY_ORDER[a.rarity] ?? 0) - (RARITY_ORDER[b.rarity] ?? 0);
        break;
      case "price":
        cmp = a.price - b.price;
        break;
      default:
        cmp = a.name.localeCompare(b.name);
    }
    return cmp * dir;
  });
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
  const hasFilter = !!(filters.text || filters.colors.length || filters.rarities.length || filters.types.length || filters.tags.length || filters.manaValue.length);

  const filteredCommander = useMemo(() => sortCards(hasFilter ? applyFilters(commander, filters) : commander, filters.sort, filters.order), [commander, filters, hasFilter]);
  const filteredMain = useMemo(() => sortCards(hasFilter ? applyFilters(main_board, filters) : main_board, filters.sort, filters.order), [main_board, filters, hasFilter]);
  const filteredSide = useMemo(() => sortCards(hasFilter ? applyFilters(side_board, filters) : side_board, filters.sort, filters.order), [side_board, filters, hasFilter]);

  const totalCommander = filteredCommander.reduce((s, c) => s + c.count, 0);
  const totalMain = filteredMain.reduce((s, c) => s + c.count, 0);
  const totalSide = filteredSide.reduce((s, c) => s + c.count, 0);

  return (
    <div className="space-y-4">
      <CardFilterBar
        filters={filters}
        onChange={onFiltersChange}
        availableTags={availableTags}
      />
      <Section title="Commander" cards={filteredCommander} count={totalCommander} onCardClick={onCardClick} onSetClick={onSetClick} />
      <Section title="Main Board" cards={filteredMain} count={totalMain} onCardClick={onCardClick} onSetClick={onSetClick} />
      <Section title="Sideboard" cards={filteredSide} count={totalSide} onCardClick={onCardClick} onSetClick={onSetClick} />
    </div>
  );
}

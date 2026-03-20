import type { CardDetail, KeywordsResponse } from "@/types/api";
import { CardIdentity } from "@/components/CardIdentity/CardIdentity";
import { CardOracleText } from "@/components/CardOracleText/CardOracleText";
import { QuadrantRating } from "@/components/QuadrantRating/QuadrantRating";
import { CardKeywords } from "@/components/CardKeywords/CardKeywords";
import { CardMetadata } from "@/components/CardMetadata/CardMetadata";
import { CardPrices } from "@/components/CardPrices/CardPrices";
import { FormatLegalityBadges } from "@/components/FormatLegalityBadges/FormatLegalityBadges";
import { OtherPrintings } from "@/components/OtherPrintings/OtherPrintings";
import { DeckAppearances } from "@/components/DeckAppearances/DeckAppearances";
import { CollectionStatus } from "@/components/CollectionStatus/CollectionStatus";
import { RawJsonViewer } from "@/components/RawJsonViewer/RawJsonViewer";

type CardDetailPageProps = {
  card: CardDetail;
  keywordTypes?: KeywordsResponse;
  onBack: () => void;
  onSetClick: (code: string) => void;
  onPrintingClick: (uuid: string) => void;
  onDeckClick: (file: string) => void;
  onAddToDeck: () => void;
  onAddToCollection: () => void;
  onSaveRating: (rating: { developing: number | null; ahead: number | null; behind: number | null; parity: number | null; notes: string | null }) => void;
};

function buildKeywordGroups(card: CardDetail, keywordTypes?: KeywordsResponse) {
  if (!keywordTypes || card.keywords.length === 0) return [];

  const typeMap = new Map<string, string>();
  for (const kw of keywordTypes.keyword_abilities) typeMap.set(kw.term.toLowerCase(), "Keyword Abilities");
  for (const kw of keywordTypes.keyword_actions) typeMap.set(kw.term.toLowerCase(), "Keyword Actions");
  for (const kw of keywordTypes.ability_words) typeMap.set(kw.term.toLowerCase(), "Ability Words");

  const defMap = new Map<string, string>();
  for (const list of [keywordTypes.keyword_abilities, keywordTypes.keyword_actions, keywordTypes.ability_words]) {
    for (const kw of list) defMap.set(kw.term.toLowerCase(), kw.definition);
  }

  const groups = new Map<string, { term: string; definition: string }[]>();
  for (const kw of card.keywords) {
    const cat = typeMap.get(kw.toLowerCase()) ?? "Other";
    if (!groups.has(cat)) groups.set(cat, []);
    groups.get(cat)!.push({ term: kw, definition: defMap.get(kw.toLowerCase()) ?? "" });
  }

  return [...groups.entries()].map(([category, keywords]) => ({ category, keywords }));
}

export function CardDetailPage({
  card,
  keywordTypes,
  onBack,
  onSetClick,
  onPrintingClick,
  onDeckClick,
  onAddToDeck,
  onAddToCollection,
  onSaveRating,
}: CardDetailPageProps) {
  const keywordGroups = buildKeywordGroups(card, keywordTypes);

  return (
    <div className="space-y-4">
      {/* Back button */}
      <button onClick={onBack} className="text-xs text-text-muted hover:text-accent transition-colors">&larr; Back</button>

      <div className="grid grid-cols-1 md:grid-cols-[1fr_280px] lg:grid-cols-[1fr_320px] gap-4 md:gap-6">
        {/* Left column: main card info */}
        <div className="space-y-4">
          <CardIdentity
            name={card.name}
            mana_cost={card.mana_cost}
            mana_value={card.mana_value}
            type={card.type}
            types={card.types}
            power={card.power}
            toughness={card.toughness}
            loyalty={card.loyalty}
            defense={card.defense}
            onAddToDeck={onAddToDeck}
          />

          <CardOracleText text={card.text} flavor_text={card.flavor_text} />

          <CardKeywords groups={keywordGroups} />

          {/* Legality */}
          <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
            <h3 className="text-sm font-medium text-text-secondary">Format Legality</h3>
            <FormatLegalityBadges legalities={card.legalities} />
          </div>

          <CardPrices prices={card.all_prices} />

          <OtherPrintings printings={card.other_printings} onSelect={onPrintingClick} />

          <DeckAppearances decks={card.appears_in_decks} onSelect={onDeckClick} />

          <RawJsonViewer data={card} title="Card JSON" />
        </div>

        {/* Right column: sidebar */}
        <div className="space-y-4">
          {/* Card image */}
          <div className="aspect-[5/7] bg-bg-tertiary rounded-lg flex items-center justify-center border border-border overflow-hidden">
            {card.image_url ? (
              <img src={card.image_url} alt={card.name} className="w-full h-full object-cover" />
            ) : (
              <div className="text-center p-4">
                <p className="text-text-muted text-sm">{card.name}</p>
                <p className="text-text-muted text-xs mt-1">No image</p>
              </div>
            )}
          </div>

          <CardMetadata
            set_code={card.set_code}
            set_name={card.set_name}
            rarity={card.rarity}
            number={card.number}
            artist={card.artist}
            layout={card.layout}
            finishes={card.finishes}
            border_color={card.border_color}
            frame_version={card.frame_version}
            is_reprint={card.is_reprint}
            is_reserved={card.is_reserved}
            is_promo={card.is_promo}
            onSetClick={() => onSetClick(card.set_code)}
          />

          <CollectionStatus
            owns={card.owns}
            collection={card.collection}
            onAddToCollection={onAddToCollection}
          />

          <QuadrantRating
            rating={card.quadrant_rating}
            onSave={onSaveRating}
          />
        </div>
      </div>
    </div>
  );
}

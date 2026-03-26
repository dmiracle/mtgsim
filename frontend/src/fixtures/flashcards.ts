import type {
  FlashcardQuestion,
  StudyStats,
  CollectionInfo,
} from "@/types/flashcards";

export const flashcardCollections: CollectionInfo[] = [
  { id: 1, name: "keywords_keyword_abilities", card_count: 52 },
  { id: 2, name: "keywords_keyword_actions", card_count: 28 },
  { id: 3, name: "keywords_ability_words", card_count: 15 },
  { id: 4, name: "card_oracle_FIN", card_count: 309 },
  { id: 5, name: "card_mana_cost_FIN", card_count: 280 },
  { id: 6, name: "card_stats_FIN", card_count: 145 },
];

export const flashcardStats: StudyStats = {
  total_cards: 829,
  cards_due: 42,
  cards_new: 387,
  reviews_today: 18,
  cards_learning: 65,
  cards_young: 280,
  cards_mature: 97,
  average_ease: 2.4,
  total_reviews: 1240,
  streak_days: 5,
  due_tomorrow: 38,
  due_this_week: 185,
  collections: flashcardCollections,
};

export const keywordFlashcard: FlashcardQuestion = {
  flashcard_id: 101,
  question: {
    card_type: "keyword_definition",
    keyword: "Flying",
    keyword_type: "keyword_abilities",
  },
  answer: {
    definition: "This creature can't be blocked except by creatures with flying and/or reach.",
  },
  collection: "keywords_keyword_abilities",
};

export const cardOracleFlashcard: FlashcardQuestion = {
  flashcard_id: 202,
  question: {
    card_type: "card_oracle",
    card_name: "Lightning Bolt",
    set_code: "M10",
    image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
  },
  answer: {
    oracle_text: "Lightning Bolt deals 3 damage to any target.",
    mana_cost: "{R}",
    type_line: "Instant",
    image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg",
  },
  collection: "card_oracle_M10",
};

export const manaCostFlashcard: FlashcardQuestion = {
  flashcard_id: 303,
  question: {
    card_type: "card_mana_cost",
    card_name: "Wrath of God",
    oracle_text: "Destroy all creatures. They can't be regenerated.",
    type_line: "Sorcery",
  },
  answer: {
    mana_cost: "{2}{W}{W}",
    mana_value: 4,
    image_url: "https://cards.scryfall.io/normal/front/6/6/664e6656-36a3-4f9e-a4c4-5ec4cae2a29c.jpg",
  },
  collection: "card_mana_cost_2XM",
};

export const cardStatsFlashcard: FlashcardQuestion = {
  flashcard_id: 404,
  question: {
    card_type: "card_stats",
    card_name: "Tarmogoyf",
    oracle_text: "Tarmogoyf's power is equal to the number of card types among cards in all graveyards and its toughness is equal to that number plus 1.",
    type_line: "Creature — Lhurgoyf",
  },
  answer: {
    power: "*",
    toughness: "1+*",
    image_url: "https://cards.scryfall.io/normal/front/6/9/69daba76-96e8-4bcc-ab79-2f00189ad8fb.jpg",
  },
  collection: "card_stats_MH2",
};

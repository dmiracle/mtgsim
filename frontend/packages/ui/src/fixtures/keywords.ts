import type { KeywordsResponse, KeywordFrequencies } from "@/types/api";

export const keywordsResponse: KeywordsResponse = {
  keyword_abilities: [
    { term: "Flying", definition: "This creature can't be blocked except by creatures with flying and/or reach." },
    { term: "Trample", definition: "This creature can deal excess combat damage to the player or planeswalker it's attacking." },
    { term: "Deathtouch", definition: "Any amount of damage this deals to a creature is enough to destroy it." },
    { term: "Haste", definition: "This creature can attack and {T} as soon as it comes under your control." },
    { term: "First Strike", definition: "This creature deals combat damage before creatures without first strike." },
    { term: "Lifelink", definition: "Damage dealt by this creature also causes you to gain that much life." },
  ],
  keyword_actions: [
    { term: "Destroy", definition: "Move a permanent from the battlefield to its owner's graveyard." },
    { term: "Exile", definition: "Move a card to the exile zone." },
    { term: "Create", definition: "Put a token onto the battlefield." },
    { term: "Sacrifice", definition: "Move a permanent you control from the battlefield to its owner's graveyard." },
  ],
  ability_words: [
    { term: "Delirium", definition: "An ability that checks if you have four or more card types in your graveyard." },
    { term: "Domain", definition: "An ability that counts the number of basic land types among lands you control." },
    { term: "Landfall", definition: "An ability that triggers whenever a land enters the battlefield under your control." },
  ],
};

export const keywordFrequencies: KeywordFrequencies = {
  keyword_abilities: {
    flying: 32,
    trample: 18,
    deathtouch: 15,
    haste: 12,
    first_strike: 10,
    lifelink: 8,
  },
  keyword_actions: {
    destroy: 22,
    exile: 18,
    create: 45,
    sacrifice: 12,
  },
  ability_words: {
    delirium: 8,
    domain: 5,
    landfall: 12,
  },
};

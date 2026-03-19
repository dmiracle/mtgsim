export interface KeywordDefinition {
  term: string
  definition: string
}

export interface KeywordsResponse {
  keyword_abilities: KeywordDefinition[]
  keyword_actions: KeywordDefinition[]
  ability_words: KeywordDefinition[]
}

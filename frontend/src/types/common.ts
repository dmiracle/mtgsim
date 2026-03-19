export interface Pagination {
  page: number
  limit: number
  total: number
  pages: number
}

export interface HistogramBucket {
  range: string
  count: number
}

export interface KeywordCounts {
  keyword_abilities: Record<string, number>
  keyword_actions: Record<string, number>
  ability_words: Record<string, number>
}

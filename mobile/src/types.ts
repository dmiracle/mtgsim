export interface Card {
  uuid: string;
  name: string;
  type: string | null;
  mana_cost: string | null;
  mana_value: number | null;
  rarity: string | null;
  set_code: string | null;
  number: string | null;
  colors: string[];
  color_identity: string[];
  tags: string[];
  user_tags: string[];
  note_count: number;
  text: string | null;
  price: number | null;
  image_url: string | null;
  owns: boolean;
  wants: boolean;
}

export interface CardSet {
  code: string;
  name: string;
  type: string;
  release_date: string | null;
  total_set_size: number;
}

export interface UserTag {
  tag: string;
  card_count: number;
}

export interface TierList {
  id: number;
  name: string;
  set_code: string | null;
  entry_count: number;
}

export interface TierListDetail extends TierList {
  entries: { card_name: string; tier: string }[];
}

export interface Pagination {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface Page<T> {
  data: T[];
  pagination: Pagination;
}

export interface Ranking {
  id: number;
  name: string;
  filters: Record<string, string>;
  comparison_count: number;
  updated_at: string;
}

export interface RankingDetail extends Ranking {
  comparisons: { winner_name: string; loser_name: string }[];
}

export const SITUATIONS = [
  { key: "developing", label: "Developing" },
  { key: "parity", label: "Parity" },
  { key: "behind", label: "Behind" },
  { key: "ahead", label: "Ahead" },
] as const;

export type Situation = (typeof SITUATIONS)[number]["key"];

// Stars 1-5 per game state; null = not rated yet.
export type Scores = Record<Situation, number | null>;

export interface CardEvaluation extends Scores {
  card_name: string;
}

export interface EvaluationSet {
  id: number;
  name: string;
  set_code: string | null;
  entry_count: number;
}

export interface EvaluationSetDetail extends EvaluationSet {
  entries: CardEvaluation[];
}

export interface CardStats {
  total: number;
  mana_curve: Record<string, number>;
  type_distribution: Record<string, number>;
  power_distribution: Record<string, number>;
  toughness_distribution: Record<string, number>;
}

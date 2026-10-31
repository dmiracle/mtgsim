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

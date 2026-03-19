export interface BoosterCard {
  uuid: string
  name: string
  set_code: string
  rarity: string
  slot: string
  number: string
  is_foil: boolean
  image_url: string | null
  mana_cost: string | null
  mana_value: number
  type_line: string
  colors: string[]
}

export interface BoosterPack {
  set_code: string
  set_name: string
  booster_type: string
  cards: BoosterCard[]
}

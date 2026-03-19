import type { BoosterPack } from "../types/booster"
import { apiFetch } from "./client"

export function fetchBooster(setCode: string, type?: string) {
  const params: Record<string, string> = {}
  if (type) params.type = type
  return apiFetch<BoosterPack>(`/boosters/${setCode}`, params)
}

export function fetchBoosterBatch(setCode: string, count: number, type?: string) {
  const params: Record<string, unknown> = { count }
  if (type) params.type = type
  return apiFetch<BoosterPack[]>(`/boosters/${setCode}/batch`, params)
}

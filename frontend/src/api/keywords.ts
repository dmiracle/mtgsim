import type { KeywordsResponse } from "../types/keyword"
import { apiFetch } from "./client"

export function fetchKeywords() {
  return apiFetch<KeywordsResponse>("/keywords")
}

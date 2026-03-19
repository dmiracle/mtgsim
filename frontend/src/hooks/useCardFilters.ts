import { useCallback } from "react"
import { useSearchParams } from "react-router-dom"
import type { CardFilters } from "../types/filters"

const FILTER_KEYS: (keyof CardFilters)[] = [
  "q", "text", "sets", "rarity", "type", "colors", "format",
  "keywords", "tags", "owns", "unique", "sort", "order", "page", "limit",
]

export function useCardFilters() {
  const [searchParams, setSearchParams] = useSearchParams()

  const filters: CardFilters = {}
  for (const key of FILTER_KEYS) {
    const val = searchParams.get(key)
    if (val !== null) {
      if (key === "owns" || key === "unique") {
        ;(filters as Record<string, unknown>)[key] = val === "true"
      } else if (key === "page" || key === "limit") {
        ;(filters as Record<string, unknown>)[key] = Number(val)
      } else {
        ;(filters as Record<string, unknown>)[key] = val
      }
    }
  }

  const setFilter = useCallback(
    (key: keyof CardFilters, value: unknown) => {
      setSearchParams((prev) => {
        const next = new URLSearchParams(prev)
        if (value === undefined || value === null || value === "") {
          next.delete(key)
        } else {
          next.set(key, String(value))
        }
        if (key !== "page") next.delete("page")
        return next
      })
    },
    [setSearchParams],
  )

  const resetFilters = useCallback(() => {
    setSearchParams({})
  }, [setSearchParams])

  return { filters, setFilter, resetFilters }
}

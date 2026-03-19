import { useQuery } from "@tanstack/react-query"
import { fetchKeywords } from "../api/keywords"

export function useKeywords() {
  return useQuery({
    queryKey: ["keywords"],
    queryFn: fetchKeywords,
    staleTime: Infinity,
  })
}

import { useQuery } from "@tanstack/react-query"
import { fetchHomeStats } from "../api/stats"

export function useHomeStats() {
  return useQuery({
    queryKey: ["homeStats"],
    queryFn: fetchHomeStats,
    staleTime: 60_000,
  })
}

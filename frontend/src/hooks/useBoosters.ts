import { useMutation } from "@tanstack/react-query"
import { fetchBooster, fetchBoosterBatch } from "../api/boosters"
import type { BoosterPack } from "../types/booster"

export function useOpenPacks() {
  return useMutation({
    mutationFn: async ({
      setCode,
      count,
      type,
    }: {
      setCode: string
      count: number
      type?: string
    }): Promise<BoosterPack[]> => {
      if (count === 1) {
        const pack = await fetchBooster(setCode, type)
        return [pack]
      }
      return fetchBoosterBatch(setCode, count, type)
    },
  })
}

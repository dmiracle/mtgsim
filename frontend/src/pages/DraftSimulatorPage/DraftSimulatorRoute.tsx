import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSets, useOpenPacks } from "@/api/hooks";
import { DraftSimulatorPage } from "./DraftSimulatorPage";
import type { BoosterPack } from "@/types/api";

export function DraftSimulatorRoute() {
  const navigate = useNavigate();
  const { data: setsData } = useSets({ limit: 100, sort: "release_date", order: "desc" });
  const openPacks = useOpenPacks();
  const [packs, setPacks] = useState<BoosterPack[]>([]);

  function handleOpen(setCode: string, boosterType: string, count: number) {
    const type = boosterType === "auto" ? undefined : boosterType;
    openPacks.mutate({ setCode, count, type }, {
      onSuccess: (result) => {
        const newPacks = Array.isArray(result) ? result : [result];
        setPacks((prev) => [...newPacks, ...prev]);
      },
    });
  }

  return (
    <DraftSimulatorPage
      sets={setsData?.data ?? []}
      packs={packs}
      onOpenPacks={handleOpen}
      onCardClick={(uuid) => navigate(`/cards/${uuid}`)}
      loading={openPacks.isPending}
    />
  );
}

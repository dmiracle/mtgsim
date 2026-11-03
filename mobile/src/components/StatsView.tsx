import { histogram, largestFirst } from "../stats";
import type { CardStats } from "../types";
import { BarList } from "./BarList";
import { Histogram } from "./Histogram";

const CAP = 7;

export function StatsView({ stats }: { stats: CardStats }) {
  return (
    <div className="space-y-8">
      <p className="text-sm text-muted">{stats.total.toLocaleString()} cards</p>
      <Histogram title="Mana value" buckets={histogram(stats.mana_curve, CAP)} />
      <BarList title="Card type" buckets={largestFirst(stats.type_distribution)} />
      <Histogram title="Power" buckets={histogram(stats.power_distribution, CAP)} />
      <Histogram title="Toughness" buckets={histogram(stats.toughness_distribution, CAP)} />
    </div>
  );
}

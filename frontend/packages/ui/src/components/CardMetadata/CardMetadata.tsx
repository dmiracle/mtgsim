import { SetBadge } from "@/components/SetBadge/SetBadge";

type CardMetadataProps = {
  set_code: string;
  set_name: string;
  rarity: string;
  number: string;
  artist: string;
  layout: string;
  finishes: string[];
  border_color: string;
  frame_version: string;
  is_reprint: boolean;
  is_reserved: boolean;
  is_promo: boolean;
  onSetClick?: () => void;
};

export function CardMetadata({
  set_code,
  set_name,
  rarity,
  number,
  artist,
  layout,
  finishes,
  border_color,
  frame_version,
  is_reprint,
  is_reserved,
  is_promo,
  onSetClick,
}: CardMetadataProps) {
  const flags = [
    is_reprint && "Reprint",
    is_reserved && "Reserved List",
    is_promo && "Promo",
  ].filter(Boolean) as string[];

  const rows: [string, React.ReactNode][] = [
    ["Set", <SetBadge key="set" code={set_code} name={set_name} rarity={rarity as "common" | "uncommon" | "rare" | "mythic"} size="sm" navigable onClick={onSetClick} />],
    ["Rarity", <span key="r" className="capitalize">{rarity}</span>],
    ["Number", number],
    ["Artist", artist],
    ["Layout", <span key="l" className="capitalize">{layout}</span>],
    ["Finishes", finishes.join(", ")],
    ["Border", <span key="b" className="capitalize">{border_color}</span>],
    ["Frame", frame_version],
  ];

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <h3 className="text-sm font-medium text-text-secondary">Details</h3>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
        {rows.map(([label, value]) => (
          <div key={label} className="contents">
            <dt className="text-xs text-text-muted text-right">{label}</dt>
            <dd className="text-xs text-text-primary">{value}</dd>
          </div>
        ))}
      </dl>
      {flags.length > 0 && (
        <div className="flex gap-1.5 pt-1">
          {flags.map((f) => (
            <span key={f} className="px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide rounded bg-warning/15 text-warning border border-warning/30">
              {f}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

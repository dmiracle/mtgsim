type FormatLegalityBadgesProps = {
  legalities: Record<string, string>;
};

const statusStyles: Record<string, string> = {
  legal: "bg-success/15 text-success border-success/30",
  restricted: "bg-warning/15 text-warning border-warning/30",
  banned: "bg-danger/15 text-danger border-danger/30",
  not_legal: "bg-bg-tertiary text-text-muted border-border",
};

const statusLabels: Record<string, string> = {
  legal: "Legal",
  restricted: "Restricted",
  banned: "Banned",
  not_legal: "Not Legal",
};

function sortEntries(entries: [string, string][]) {
  const order = ["legal", "restricted", "banned", "not_legal"];
  return entries.sort((a, b) => {
    const ai = order.indexOf(a[1]);
    const bi = order.indexOf(b[1]);
    if (ai !== bi) return ai - bi;
    return a[0].localeCompare(b[0]);
  });
}

export function FormatLegalityBadges({ legalities }: FormatLegalityBadgesProps) {
  const entries = sortEntries(Object.entries(legalities));

  return (
    <div className="flex flex-wrap gap-1.5">
      {entries.map(([format, status]) => (
        <span
          key={format}
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded border ${statusStyles[status] ?? statusStyles.not_legal}`}
        >
          <span className="capitalize">{format}</span>
          <span className="opacity-70">{statusLabels[status] ?? status}</span>
        </span>
      ))}
    </div>
  );
}

import { useState } from "react";

type CardRawDataProps = {
  uuid: string;
  data: Record<string, unknown>;
};

export function CardRawData({ uuid, data }: CardRawDataProps) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  function copyUuid() {
    navigator.clipboard.writeText(uuid);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-text-secondary">Raw Data</h3>
        <div className="flex items-center gap-2">
          <button
            onClick={copyUuid}
            className="text-xs px-2 py-1 rounded border border-border text-text-muted hover:text-text-secondary hover:border-border-hover transition-colors"
          >
            {copied ? "Copied!" : "Copy UUID"}
          </button>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs px-2 py-1 rounded border border-border text-text-muted hover:text-text-secondary hover:border-border-hover transition-colors"
          >
            {expanded ? "Hide JSON" : "Show JSON"}
          </button>
        </div>
      </div>
      <p className="text-xs text-text-muted font-mono break-all">{uuid}</p>
      {expanded && (
        <pre className="text-[11px] text-text-secondary bg-bg-tertiary rounded p-3 overflow-auto max-h-96 font-mono leading-relaxed">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}

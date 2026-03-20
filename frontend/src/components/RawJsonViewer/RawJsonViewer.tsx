import { useState } from "react";

type RawJsonViewerProps = {
  data: unknown;
  title?: string;
  defaultExpanded?: boolean;
  maxHeight?: number;
};

export function RawJsonViewer({ data, title = "Raw JSON", defaultExpanded = false, maxHeight = 400 }: RawJsonViewerProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [copied, setCopied] = useState(false);

  const json = JSON.stringify(data, null, 2);

  function handleCopy() {
    navigator.clipboard.writeText(json);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div className="bg-bg-secondary border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-4 py-2.5 hover:bg-bg-hover transition-colors"
      >
        <span className="text-xs font-medium text-text-secondary">{title}</span>
        <span className="text-xs text-text-muted">{expanded ? "▲" : "▼"}</span>
      </button>

      {expanded && (
        <div className="border-t border-border">
          <div className="flex justify-end px-3 py-1.5 bg-bg-tertiary/50">
            <button
              onClick={handleCopy}
              className="text-[10px] px-2 py-0.5 rounded border border-border text-text-muted hover:text-text-secondary hover:border-border-hover transition-colors"
            >
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>
          <pre
            className="px-4 py-3 text-[11px] text-text-secondary font-mono leading-relaxed overflow-auto"
            style={{ maxHeight }}
          >
            {json}
          </pre>
        </div>
      )}
    </div>
  );
}

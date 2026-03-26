import { useState } from "react";

type CopyUuidButtonProps = {
  uuid: string;
  size?: "sm" | "md";
};

export function CopyUuidButton({ uuid, size = "sm" }: CopyUuidButtonProps) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(uuid);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  const sizeClasses = size === "sm" ? "text-xs px-2 py-1" : "text-sm px-3 py-1.5";

  return (
    <button
      onClick={handleCopy}
      title="Copy UUID"
      className={`${sizeClasses} rounded font-medium border transition-colors ${
        copied
          ? "bg-success/15 text-success border-success/30"
          : "bg-bg-tertiary text-text-muted border-border hover:text-text-secondary hover:border-border-hover"
      }`}
    >
      {copied ? "Copied!" : "UUID"}
    </button>
  );
}

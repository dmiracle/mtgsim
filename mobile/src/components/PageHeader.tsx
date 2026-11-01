import type { ReactNode } from "react";

interface PageHeaderProps {
  title: string;
  onBack: () => void;
  backLabel: string;
  action?: ReactNode;
}

export function PageHeader({ title, onBack, backLabel, action }: PageHeaderProps) {
  return (
    <header className="sticky top-0 z-10 flex items-center gap-3 border-b border-line bg-bg px-4 pt-[max(0.75rem,env(safe-area-inset-top))] pb-2">
      <button onClick={onBack} className="min-h-10 rounded-lg border border-line px-3 text-sm">
        ‹ {backLabel}
      </button>
      <h1 className="flex-1 truncate font-semibold">{title}</h1>
      {action}
    </header>
  );
}

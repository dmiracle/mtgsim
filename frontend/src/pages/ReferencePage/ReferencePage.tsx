import { useState } from "react";
import type { KeywordsResponse } from "@/types/api";
import { KeywordBrowser } from "@/components/KeywordBrowser/KeywordBrowser";
import { GlossaryBrowser } from "@/components/GlossaryBrowser/GlossaryBrowser";

type GlossaryEntry = {
  term: string;
  definition: string;
  category: string;
};

type ReferencePageProps = {
  keywords: KeywordsResponse;
  glossary: GlossaryEntry[];
};

export function ReferencePage({ keywords, glossary }: ReferencePageProps) {
  const [tab, setTab] = useState<"keywords" | "glossary">("keywords");

  const tabs = [
    { id: "keywords" as const, label: "Keywords" },
    { id: "glossary" as const, label: "Glossary" },
  ];

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold text-text-primary">Reference</h2>

      <div className="flex items-center gap-1 border-b border-border">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors -mb-px ${
              tab === t.id ? "border-accent text-accent" : "border-transparent text-text-muted hover:text-text-secondary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "keywords" && <KeywordBrowser keywords={keywords} />}
      {tab === "glossary" && <GlossaryBrowser entries={glossary} />}
    </div>
  );
}

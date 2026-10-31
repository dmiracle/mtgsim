import { useMemo, useState } from "react";
import type { UserTagSummary } from "@/types/api";

export type UserTagEditorProps = {
  tags: string[];
  vocabulary: UserTagSummary[];
  onAdd: (tag: string) => void;
  onRemove: (tag: string) => void;
  onSaveDefinition?: (tag: string, description: string) => void;
};

function normalizeTag(raw: string): string {
  return raw.trim().replace(/\s+/g, " ").toLowerCase();
}

export function UserTagEditor({ tags, vocabulary, onAdd, onRemove, onSaveDefinition }: UserTagEditorProps) {
  const [input, setInput] = useState("");
  const [focused, setFocused] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [draftDefinition, setDraftDefinition] = useState("");

  const suggestions = useMemo(() => {
    const needle = normalizeTag(input);
    return vocabulary
      .filter((v) => !tags.includes(v.tag) && (needle === "" || v.tag.includes(needle)))
      .slice(0, 8);
  }, [input, vocabulary, tags]);

  const selectedDefinition = vocabulary.find((v) => v.tag === selectedTag)?.description ?? null;

  function addTag(tag: string) {
    const normalized = normalizeTag(tag);
    if (normalized === "" || tags.includes(normalized)) return;
    onAdd(normalized);
    setInput("");
  }

  function selectTag(tag: string) {
    const next = selectedTag === tag ? null : tag;
    setSelectedTag(next);
    setDraftDefinition(next ? (vocabulary.find((v) => v.tag === next)?.description ?? "") : "");
  }

  return (
    <div className="space-y-3">
      <div className="relative">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setTimeout(() => setFocused(false), 150)}
          onKeyDown={(e) => {
            if (e.key === "Enter") addTag(input);
          }}
          placeholder="Add a tag..."
          className="w-full bg-bg-tertiary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent"
        />
        {focused && suggestions.length > 0 && (
          <div className="absolute z-10 mt-1 w-full bg-bg-secondary border border-border rounded-lg shadow-lg overflow-hidden">
            {suggestions.map((s) => (
              <button
                key={s.tag}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => addTag(s.tag)}
                className="w-full flex items-baseline gap-2 px-3 py-1.5 text-left hover:bg-bg-tertiary transition-colors"
              >
                <span className="text-xs text-accent font-medium">{s.tag}</span>
                <span className="text-[10px] text-text-muted">{s.card_count} cards</span>
                {s.description && (
                  <span className="text-[10px] text-text-muted truncate flex-1">{s.description}</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {tags.length === 0 ? (
        <p className="text-xs text-text-muted">No tags yet. Type above to add one.</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {tags.map((tag) => (
            <span
              key={tag}
              className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded border transition-colors ${
                selectedTag === tag
                  ? "bg-accent/20 text-accent border-accent"
                  : "bg-accent/10 text-accent border-accent/30"
              }`}
            >
              <button onClick={() => selectTag(tag)} className="hover:underline">
                {tag}
              </button>
              <button
                onClick={() => onRemove(tag)}
                aria-label={`Remove ${tag}`}
                className="text-accent/60 hover:text-danger transition-colors"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {selectedTag && (
        <div className="bg-bg-tertiary border border-border rounded-lg p-3 space-y-2">
          <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold">
            {selectedTag}
          </span>
          {onSaveDefinition ? (
            <>
              <textarea
                value={draftDefinition}
                onChange={(e) => setDraftDefinition(e.target.value)}
                placeholder="What does this tag mean?"
                rows={2}
                className="w-full bg-bg-secondary border border-border rounded-lg px-3 py-2 text-sm text-text-primary placeholder-text-muted focus:outline-none focus:border-accent resize-none"
              />
              {draftDefinition !== (selectedDefinition ?? "") && (
                <button
                  onClick={() => onSaveDefinition(selectedTag, draftDefinition)}
                  className="text-xs px-3 py-1 rounded bg-accent text-white hover:bg-accent-hover transition-colors"
                >
                  Save definition
                </button>
              )}
            </>
          ) : (
            <p className="text-xs text-text-secondary">{selectedDefinition ?? "No definition."}</p>
          )}
        </div>
      )}
    </div>
  );
}

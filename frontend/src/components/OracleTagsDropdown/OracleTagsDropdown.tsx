import { useState, useRef, useEffect } from "react";
import type { TagCount } from "@/types/api";

type OracleTagsDropdownProps = {
  tags: TagCount[];
  selected: string[];
  onChange: (selected: string[]) => void;
};

export function OracleTagsDropdown({ tags, selected, onChange }: OracleTagsDropdownProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const filtered = tags.filter((t) =>
    t.tag.toLowerCase().includes(search.toLowerCase())
  );

  function toggle(tag: string) {
    if (selected.includes(tag)) {
      onChange(selected.filter((t) => t !== tag));
    } else {
      onChange([...selected, tag]);
    }
  }

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 text-xs rounded border border-border bg-bg-secondary text-text-secondary hover:border-border-hover transition-colors"
      >
        <span>Tags</span>
        {selected.length > 0 && (
          <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
            {selected.length}
          </span>
        )}
        <span className="text-text-muted ml-1">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="absolute z-20 top-full left-0 mt-1 w-64 bg-bg-secondary border border-border rounded-lg shadow-lg overflow-hidden">
          <div className="p-2 border-b border-border">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Filter tags..."
              className="w-full bg-bg-tertiary border-none rounded px-2 py-1.5 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
              autoFocus
            />
          </div>
          <div className="max-h-60 overflow-y-auto">
            {filtered.length === 0 && (
              <p className="px-3 py-4 text-xs text-text-muted text-center">No tags found</p>
            )}
            {filtered.map((t) => {
              const active = selected.includes(t.tag);
              return (
                <button
                  key={t.tag}
                  onClick={() => toggle(t.tag)}
                  className={`w-full flex items-center justify-between px-3 py-1.5 text-xs transition-colors ${
                    active
                      ? "bg-accent-muted text-accent"
                      : "text-text-secondary hover:bg-bg-hover"
                  }`}
                >
                  <span className="truncate">{t.tag}</span>
                  <span className="text-text-muted ml-2 shrink-0">{t.count}</span>
                </button>
              );
            })}
          </div>
          {selected.length > 0 && (
            <div className="p-2 border-t border-border">
              <button
                onClick={() => onChange([])}
                className="text-xs text-danger hover:underline"
              >
                Clear all
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

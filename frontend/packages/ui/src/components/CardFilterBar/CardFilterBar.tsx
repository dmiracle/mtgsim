import { useState, useRef, useEffect } from "react";
import type { TagCount, SetSummary } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
import { SetBadge } from "@/components/SetBadge/SetBadge";
import { ColorIdentityPicker } from "@/components/ColorIdentityPicker/ColorIdentityPicker";
import { RarityFilter } from "@/components/RarityFilter/RarityFilter";
import { CardTypeFilter } from "@/components/CardTypeFilter/CardTypeFilter";
import { OracleTagsDropdown } from "@/components/OracleTagsDropdown/OracleTagsDropdown";
import { SortSelect } from "@/components/SortSelect/SortSelect";
import { OwnershipToggle } from "@/components/OwnershipToggle/OwnershipToggle";

type CardFilters = {
  text: string;
  colors: string[];
  rarities: string[];
  types: string[];
  subtype: string;
  sets: string[];
  formats: string[];
  tags: string[];
  manaValue: number[];
  ownership: "all" | "owned" | "not_owned";
  platform: "any" | "paper" | "mtga";
  sort: string;
  order: "asc" | "desc";
  unique: boolean;
};

type CardFilterBarProps = {
  filters: CardFilters;
  onChange: (filters: CardFilters) => void;
  availableTags?: TagCount[];
  availableSets?: SetSummary[];
  onSetSearch?: (query: string) => void;
  resultCount?: number;
  showUnique?: boolean;
  sortOptions?: { value: string; label: string }[];
};

const DEFAULT_SORT_OPTIONS = [
  { value: "name", label: "Name" },
  { value: "mana_value", label: "Mana Value" },
  { value: "rarity", label: "Rarity" },
  { value: "price", label: "Price" },
];

export type { CardFilters };

const FORMATS = ["standard", "pioneer", "modern", "legacy", "vintage", "commander", "brawl", "historic", "pauper"];

export function CardFilterBar({
  filters,
  onChange,
  availableTags = [],
  availableSets = [],
  onSetSearch,
  resultCount,
  showUnique = false,
  sortOptions = DEFAULT_SORT_OPTIONS,
}: CardFilterBarProps) {
  const [expanded, setExpanded] = useState(true);
  const [setSearchOpen, setSetSearchOpen] = useState(false);
  const [setSearch, setSetSearch] = useState("");
  const setDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (setDropdownRef.current && !setDropdownRef.current.contains(e.target as Node)) {
        setSetSearchOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const filteredSets = onSetSearch
    ? availableSets.slice(0, 15)
    : setSearch
      ? availableSets.filter((s) => s.name.toLowerCase().includes(setSearch.toLowerCase()) || s.code.toLowerCase().includes(setSearch.toLowerCase()))
      : availableSets.slice(0, 15);

  function toggleSet(code: string) {
    const next = filters.sets.includes(code)
      ? filters.sets.filter((c) => c !== code)
      : [...filters.sets, code];
    update({ sets: next });
  }

  function toggleFormat(format: string) {
    const next = filters.formats.includes(format)
      ? filters.formats.filter((f) => f !== format)
      : [...filters.formats, format];
    update({ formats: next });
  }

  function toggleManaValue(mv: number) {
    const next = filters.manaValue.includes(mv)
      ? filters.manaValue.filter((v) => v !== mv)
      : [...filters.manaValue, mv].sort((a, b) => a - b);
    update({ manaValue: next });
  }

  function update(partial: Partial<CardFilters>) {
    onChange({ ...filters, ...partial });
  }

  const activeCount =
    (filters.text ? 1 : 0) +
    filters.colors.length +
    filters.rarities.length +
    filters.types.length +
    (filters.subtype ? 1 : 0) +
    filters.sets.length +
    filters.formats.length +
    filters.tags.length +
    (filters.manaValue.length > 0 ? 1 : 0) +
    (filters.ownership !== "all" ? 1 : 0);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg overflow-visible">
      {/* Top bar */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3 p-3 bg-bg-primary/50">
        <div className="flex-1 min-w-[150px]">
          <SearchInput
            value={filters.text}
            placeholder='Search oracle text — supports AND / OR / NOT, "phrase", (groups), prefix*'
            onChange={(text) => update({ text })}
          />
        </div>
        <div className="flex items-center gap-2">
          <SortSelect
            options={sortOptions}
            sort={filters.sort}
            order={filters.order}
            onSortChange={(sort) => update({ sort })}
            onOrderChange={(order) => update({ order })}
          />
          {resultCount !== undefined && (
            <span className="text-xs font-medium text-text-secondary whitespace-nowrap tabular-nums hidden sm:inline">
              {resultCount.toLocaleString()}
            </span>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="px-2 py-1 text-xs rounded border border-border text-text-muted hover:text-text-secondary hover:border-border-hover transition-colors whitespace-nowrap"
          >
            {expanded ? "▲ Filters" : `▼ Filters${activeCount > 0 ? ` (${activeCount})` : ""}`}
          </button>
        </div>
      </div>

      {/* Filter panels */}
      {expanded && (
        <div className="border-t border-border">
          {/* Filters — vertical stack on mobile, horizontal rows on desktop */}
          <div className="p-3 sm:px-4 sm:py-3 space-y-3 sm:space-y-2">
            {/* Color */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">Color</span>
              <ColorIdentityPicker
                selected={filters.colors}
                onChange={(colors) => update({ colors })}
                size="sm"
              />
            </div>

            {/* Type */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">Type</span>
              <CardTypeFilter
                selected={filters.types}
                onChange={(types) => update({ types })}
              />
            </div>

            {/* Subtype */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">Sub</span>
              <input
                type="text"
                value={filters.subtype}
                onChange={(e) => update({ subtype: e.target.value })}
                placeholder="e.g. Dragon, Human, Equipment"
                className="bg-bg-tertiary border border-border rounded px-2 py-1 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:border-accent w-48"
              />
            </div>

            {/* Sets */}
            <div className="flex flex-col sm:flex-row sm:items-start gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10 pt-1">Sets</span>
              <div ref={setDropdownRef} className="relative">
                <button
                  onClick={() => setSetSearchOpen(!setSearchOpen)}
                  className="flex items-center gap-2 px-2 py-1 text-xs rounded border border-border bg-bg-tertiary text-text-secondary hover:border-border-hover transition-colors"
                >
                  <span>Sets</span>
                  {filters.sets.length > 0 && (
                    <span className="bg-accent text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
                      {filters.sets.length}
                    </span>
                  )}
                  <span className="text-text-muted">{setSearchOpen ? "▲" : "▼"}</span>
                </button>
                {setSearchOpen && (
                  <div className="absolute z-20 top-full left-0 mt-1 w-64 bg-bg-secondary border border-border rounded-lg shadow-lg overflow-hidden">
                    <div className="p-2 border-b border-border">
                      <input
                        type="text"
                        value={setSearch}
                        onChange={(e) => { setSetSearch(e.target.value); onSetSearch?.(e.target.value); }}
                        placeholder="Search sets..."
                        className="w-full bg-bg-tertiary border-none rounded px-2 py-1.5 text-xs text-text-primary placeholder-text-muted focus:outline-none focus:ring-1 focus:ring-accent"
                        autoFocus
                      />
                    </div>
                    <div className="max-h-48 overflow-y-auto">
                      {filteredSets.map((s) => {
                        const selected = filters.sets.includes(s.code);
                        return (
                          <button
                            key={s.code}
                            onClick={() => toggleSet(s.code)}
                            className={`w-full flex items-center justify-between px-3 py-1.5 text-xs transition-colors ${
                              selected ? "bg-accent-muted text-accent" : "text-text-secondary hover:bg-bg-hover"
                            }`}
                          >
                            <SetBadge code={s.code} name={s.name} size="sm" />
                            <span className="text-text-muted">{s.collection_stats?.total_cards ?? s.base_set_size}</span>
                          </button>
                        );
                      })}
                    </div>
                    {filters.sets.length > 0 && (
                      <div className="p-2 border-t border-border">
                        <button onClick={() => update({ sets: [] })} className="text-xs text-danger hover:underline">Clear sets</button>
                      </div>
                    )}
                  </div>
                )}
                {filters.sets.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-1">
                    {filters.sets.map((code) => (
                      <button
                        key={code}
                        onClick={() => toggleSet(code)}
                        className="flex items-center gap-1 px-1.5 py-0.5 text-[10px] rounded bg-accent/20 text-accent hover:bg-accent/30"
                      >
                        {code} ×
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Format / Legality */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">Legal</span>
              <div className="flex flex-wrap gap-1">
                {FORMATS.map((f) => {
                  const active = filters.formats.includes(f);
                  return (
                    <button
                      key={f}
                      onClick={() => toggleFormat(f)}
                      className={`px-2 py-0.5 text-[10px] font-medium rounded border capitalize transition-colors ${
                        active
                          ? "bg-accent text-white border-accent"
                          : "bg-bg-tertiary border-border text-text-muted hover:border-border-hover"
                      }`}
                    >
                      {f}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Rarity */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">Rarity</span>
              <RarityFilter
                selected={filters.rarities}
                onChange={(rarities) => update({ rarities })}
              />
            </div>

            {/* Mana Value */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">MV</span>
              <div className="flex gap-1">
                {[0, 1, 2, 3, 4, 5, 6, 7].map((mv) => {
                  const active = filters.manaValue.includes(mv);
                  return (
                    <button
                      key={mv}
                      onClick={() => toggleManaValue(mv)}
                      className={`w-7 h-7 rounded-full text-xs font-bold transition-colors ${
                        active
                          ? "bg-accent text-white"
                          : "bg-bg-tertiary border border-border text-text-muted hover:border-border-hover hover:text-text-secondary"
                      }`}
                      title={mv === 7 ? "Mana value 7+" : `Mana value ${mv}`}
                    >
                      {mv === 7 ? "7+" : mv}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tags + Ownership + Unique — row that wraps */}
            <div className="flex flex-wrap items-center gap-2 sm:gap-3">
              <OracleTagsDropdown
                tags={availableTags}
                selected={filters.tags}
                onChange={(tags) => update({ tags })}
              />
              <OwnershipToggle
                value={filters.ownership}
                platform={filters.platform}
                onChange={(ownership) => update({ ownership, platform: ownership === "owned" ? filters.platform : "any" })}
                onPlatformChange={(platform) => update({ platform })}
              />
              {showUnique && (
                <label className="inline-flex items-center gap-1.5 text-xs text-text-secondary cursor-pointer">
                  <input
                    type="checkbox"
                    checked={filters.unique}
                    onChange={(e) => update({ unique: e.target.checked })}
                    className="accent-accent"
                  />
                  Unique
                </label>
              )}
              {activeCount > 0 && (
                <button
                  onClick={() =>
                    onChange({
                      text: "",
                      colors: [],
                      rarities: [],
                      types: [],
                      subtype: "",
                      sets: [],
                      formats: [],
                      tags: [],
                      manaValue: [],
                      ownership: "all",
                      platform: "any",
                      sort: filters.sort,
                      order: filters.order,
                      unique: filters.unique,
                    })
                  }
                  className="text-xs font-medium text-danger hover:underline ml-auto"
                >
                  Clear ({activeCount})
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

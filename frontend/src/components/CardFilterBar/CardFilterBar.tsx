import { useState } from "react";
import type { TagCount } from "@/types/api";
import { SearchInput } from "@/components/SearchInput/SearchInput";
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
  tags: string[];
  ownership: "all" | "owned" | "not_owned";
  sort: string;
  order: "asc" | "desc";
  unique: boolean;
};

type CardFilterBarProps = {
  filters: CardFilters;
  onChange: (filters: CardFilters) => void;
  availableTags?: TagCount[];
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

export function CardFilterBar({
  filters,
  onChange,
  availableTags = [],
  resultCount,
  showUnique = false,
  sortOptions = DEFAULT_SORT_OPTIONS,
}: CardFilterBarProps) {
  const [expanded, setExpanded] = useState(true);

  function update(partial: Partial<CardFilters>) {
    onChange({ ...filters, ...partial });
  }

  const activeCount =
    (filters.text ? 1 : 0) +
    filters.colors.length +
    filters.rarities.length +
    filters.types.length +
    filters.tags.length +
    (filters.ownership !== "all" ? 1 : 0);

  return (
    <div className="bg-bg-secondary border border-border rounded-lg overflow-hidden">
      {/* Top bar */}
      <div className="flex flex-wrap items-center gap-2 sm:gap-3 p-3 bg-bg-primary/50">
        <div className="flex-1 min-w-[150px]">
          <SearchInput
            value={filters.text}
            placeholder="Search oracle text..."
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

            {/* Rarity */}
            <div className="flex flex-col sm:flex-row sm:items-center gap-1.5 sm:gap-2.5">
              <span className="text-[10px] uppercase tracking-widest text-text-muted font-semibold sm:w-10">Rarity</span>
              <RarityFilter
                selected={filters.rarities}
                onChange={(rarities) => update({ rarities })}
              />
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
                onChange={(ownership) => update({ ownership })}
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
                      tags: [],
                      ownership: "all",
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

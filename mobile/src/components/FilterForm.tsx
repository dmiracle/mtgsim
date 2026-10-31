import type { ReactNode } from "react";
import {
  COLORS,
  FORMATS,
  MANA_VALUES,
  RARITIES,
  SORTS,
  TIERS,
  listParam,
  setParam,
  toggleInList,
  type Filters,
} from "../filters";
import type { CardSet, TierList, UserTag } from "../types";
import { ChipRow } from "./ChipRow";
import { SetPicker } from "./SetPicker";

interface FilterFormProps {
  filters: Filters;
  onChange: (filters: Filters) => void;
  sets: CardSet[];
  setQuery: string;
  onSetQueryChange: (q: string) => void;
  userTags: UserTag[];
  tierLists: TierList[];
  count: number | undefined;
  onStart: () => void;
  onReset: () => void;
}

const opts = (values: string[]) => values.map((v) => ({ value: v, label: v }));

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-2">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted">{title}</h3>
      {children}
    </section>
  );
}

const inputClass = "w-full rounded-lg border border-line bg-surface px-3 py-2.5 text-base";

export function FilterForm(props: FilterFormProps) {
  const { filters, onChange } = props;
  const set = (key: string, value: string) => onChange(setParam(filters, key, value));
  const toggle = (key: string) => (value: string) => onChange(toggleInList(filters, key, value));
  const single = (key: string) => (value: string) => set(key, filters[key] === value ? "" : value);
  const colors = filters.colors?.split("") ?? [];
  const toggleColor = (c: string) =>
    set("colors", colors.includes(c) ? colors.filter((x) => x !== c).join("") : [...colors, c].join(""));
  const [sort1 = "name", sort2 = ""] = listParam(filters, "sort");
  const setSort = (primary: string, secondary: string) => set("sort", [primary, secondary].filter(Boolean).join(","));
  const sorts = SORTS.filter((s) => s.value !== "tier" || filters.tier_list_id);

  const selectTierList = (id: string) => {
    let next = setParam(filters, "tier_list_id", id);
    if (!id) {
      next = setParam(next, "tiers", "");
      next = setParam(next, "sort", listParam(next, "sort").filter((s) => s !== "tier").join(","));
    }
    onChange(next);
  };

  return (
    <div className="space-y-6 px-4 pt-[max(1rem,env(safe-area-inset-top))] pb-36">
      <h1 className="text-2xl font-bold">Card Review</h1>

      <Section title="Sets">
        <SetPicker
          sets={props.sets}
          selected={listParam(filters, "sets")}
          query={props.setQuery}
          onQueryChange={props.onSetQueryChange}
          onToggle={toggle("sets")}
        />
      </Section>

      <Section title="Rarity">
        <ChipRow options={opts(RARITIES)} selected={[filters.rarity]} onToggle={single("rarity")} />
      </Section>

      <Section title="Color identity (any of)">
        <ChipRow options={opts(COLORS)} selected={colors} onToggle={toggleColor} />
      </Section>

      <Section title="Mana value">
        <ChipRow
          options={MANA_VALUES.map((v) => ({ value: v, label: v === "7" ? "7+" : v }))}
          selected={listParam(filters, "mana_value")}
          onToggle={toggle("mana_value")}
        />
      </Section>

      <Section title="Type, name, rules text">
        <input
          className={inputClass}
          placeholder="Type (e.g. Creature)"
          value={filters.type ?? ""}
          onChange={(e) => set("type", e.target.value)}
        />
        <input
          className={inputClass}
          placeholder="Name contains"
          value={filters.q ?? ""}
          onChange={(e) => set("q", e.target.value)}
        />
        <input
          className={inputClass}
          placeholder="Rules text contains"
          value={filters.text ?? ""}
          onChange={(e) => set("text", e.target.value)}
        />
      </Section>

      <Section title="Format">
        <ChipRow options={opts(FORMATS)} selected={[filters.format]} onToggle={single("format")} />
      </Section>

      {props.userTags.length > 0 && (
        <Section title="My tags">
          <ChipRow
            options={props.userTags.map((t) => ({ value: t.tag, label: `${t.tag} (${t.card_count})` }))}
            selected={listParam(filters, "user_tags")}
            onToggle={toggle("user_tags")}
          />
        </Section>
      )}

      {props.tierLists.length > 0 && (
        <Section title="Tier list">
          <select
            className={inputClass}
            value={filters.tier_list_id ?? ""}
            onChange={(e) => selectTierList(e.target.value)}
          >
            <option value="">None</option>
            {props.tierLists.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name} ({t.entry_count})
              </option>
            ))}
          </select>
          {filters.tier_list_id && (
            <ChipRow options={opts(TIERS)} selected={listParam(filters, "tiers")} onToggle={toggle("tiers")} />
          )}
        </Section>
      )}

      <Section title="Price">
        <div className="flex gap-3">
          <input
            className={inputClass}
            inputMode="decimal"
            placeholder="Min $"
            value={filters.price_min ?? ""}
            onChange={(e) => set("price_min", e.target.value)}
          />
          <input
            className={inputClass}
            inputMode="decimal"
            placeholder="Max $"
            value={filters.price_max ?? ""}
            onChange={(e) => set("price_max", e.target.value)}
          />
        </div>
      </Section>

      <Section title="Collection">
        <ChipRow
          options={[
            { value: "true", label: "Owned" },
            { value: "false", label: "Not owned" },
          ]}
          selected={[filters.owns]}
          onToggle={single("owns")}
        />
        <label className="flex min-h-10 items-center gap-3">
          <input
            type="checkbox"
            className="size-5 accent-accent"
            checked={filters.unique === "true"}
            onChange={(e) => set("unique", e.target.checked ? "true" : "")}
          />
          One printing per card name
        </label>
      </Section>

      <Section title="Order">
        <div className="flex gap-3">
          <select className={inputClass} value={sort1} onChange={(e) => setSort(e.target.value, sort2)}>
            {sorts.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
          <select className={inputClass} value={sort2} onChange={(e) => setSort(sort1, e.target.value)}>
            <option value="">then Name</option>
            {sorts.map((s) => (
              <option key={s.value} value={s.value}>
                then {s.label}
              </option>
            ))}
          </select>
        </div>
        <ChipRow
          options={[
            { value: "asc", label: "Ascending" },
            { value: "desc", label: "Descending" },
          ]}
          selected={[filters.order ?? "asc"]}
          onToggle={(v) => set("order", v)}
        />
      </Section>

      <div className="fixed inset-x-0 bottom-0 flex gap-3 border-t border-line bg-bg/95 px-4 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] backdrop-blur">
        <button onClick={props.onReset} className="min-h-12 rounded-xl border border-line px-4">
          Reset
        </button>
        <button
          onClick={props.onStart}
          disabled={!props.count}
          className="min-h-12 flex-1 rounded-xl bg-accent font-semibold text-bg disabled:opacity-40"
        >
          {props.count === undefined ? "Counting…" : `Review ${props.count.toLocaleString()} cards`}
        </button>
      </div>
    </div>
  );
}

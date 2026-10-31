import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { DEFAULT_FILTERS } from "../filters";
import { sets, tierLists, userTags } from "../fixtures";
import { FilterForm } from "./FilterForm";

const meta: Meta<typeof FilterForm> = { title: "Mobile/FilterForm", component: FilterForm };
export default meta;

function Interactive({ initial }: { initial: Record<string, string> }) {
  const [filters, setFilters] = useState(initial);
  const [query, setQuery] = useState("");
  return (
    <div>
      <FilterForm
        filters={filters}
        onChange={setFilters}
        sets={sets}
        setQuery={query}
        onSetQueryChange={setQuery}
        userTags={userTags}
        tierLists={tierLists}
        count={23}
        onStart={() => {}}
        onReset={() => setFilters(DEFAULT_FILTERS)}
        onRank={() => {}}
        onCreateGradeList={() => setFilters((f) => ({ ...f, grade_list: "1" }))}
      />
      <pre className="px-4 pb-40 text-xs text-muted">{JSON.stringify(filters, null, 2)}</pre>
    </div>
  );
}

export const Empty: StoryObj = { render: () => <Interactive initial={DEFAULT_FILTERS} /> };

export const WhiteCommonsInStarTrek: StoryObj = {
  render: () => <Interactive initial={{ sets: "TRK", rarity: "common", colors: "W", sort: "mana_value,price", order: "asc" }} />,
};

import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { sets } from "../fixtures";
import { SetPicker } from "./SetPicker";

const meta: Meta<typeof SetPicker> = { title: "Mobile/SetPicker", component: SetPicker };
export default meta;

export const Default: StoryObj<typeof SetPicker> = {
  render: () => {
    const [selected, setSelected] = useState(["TRK"]);
    const [query, setQuery] = useState("");
    return (
      <div className="p-4">
        <SetPicker
          sets={sets.filter((s) => s.name.toLowerCase().includes(query.toLowerCase()))}
          selected={selected}
          query={query}
          onQueryChange={setQuery}
          onToggle={(c) => setSelected((s) => (s.includes(c) ? s.filter((x) => x !== c) : [...s, c]))}
        />
      </div>
    );
  },
};

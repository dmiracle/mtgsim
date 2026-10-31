import type { Meta, StoryObj } from "@storybook/react-vite";
import { useState } from "react";
import { RARITIES } from "../filters";
import { ChipRow } from "./ChipRow";

const meta: Meta<typeof ChipRow> = { title: "Mobile/ChipRow", component: ChipRow };
export default meta;

export const Rarities: StoryObj<typeof ChipRow> = {
  render: () => {
    const [selected, setSelected] = useState(["common"]);
    return (
      <div className="p-4">
        <ChipRow
          options={RARITIES.map((r) => ({ value: r, label: r }))}
          selected={selected}
          onToggle={(v) => setSelected((s) => (s.includes(v) ? s.filter((x) => x !== v) : [...s, v]))}
        />
      </div>
    );
  },
};

import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { SetPicker } from "./SetPicker";

const sampleSets = [
  { code: "FIN", name: "Final Fantasy", base_set_size: 309 },
  { code: "TDM", name: "Tarkir: Dragonstorm", base_set_size: 291 },
  { code: "DFT", name: "Aetherdrift", base_set_size: 291 },
  { code: "DSK", name: "Duskmourn: House of Horror", base_set_size: 286 },
  { code: "BLB", name: "Bloomburrow", base_set_size: 281 },
  { code: "MH3", name: "Modern Horizons 3", base_set_size: 303 },
  { code: "STX", name: "Strixhaven: School of Mages", base_set_size: 275 },
  { code: "FDN", name: "Foundations", base_set_size: 291 },
];

const meta: Meta<typeof SetPicker> = {
  title: "App-v2/SetPicker",
  component: SetPicker,
  decorators: [
    (Story) => (
      <div className="max-w-lg mx-auto p-4 bg-bg-primary min-h-screen">
        <Story />
      </div>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof SetPicker>;

export const Empty: Story = {
  render: () => {
    const [selected, setSelected] = useState<string[]>([]);
    const [search, setSearch] = useState("");
    return (
      <SetPicker
        sets={sampleSets}
        selected={selected}
        search={search}
        onSearchChange={setSearch}
        onToggle={(code) =>
          setSelected((prev) =>
            prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
          )
        }
        onClear={() => setSelected([])}
      />
    );
  },
};

export const WithSelections: Story = {
  render: () => {
    const [selected, setSelected] = useState(["FIN", "TDM", "BLB"]);
    const [search, setSearch] = useState("");
    return (
      <SetPicker
        sets={sampleSets}
        selected={selected}
        search={search}
        onSearchChange={setSearch}
        onToggle={(code) =>
          setSelected((prev) =>
            prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code]
          )
        }
        onClear={() => setSelected([])}
      />
    );
  },
};

export const NoResults: Story = {
  render: () => {
    const [search, setSearch] = useState("");
    return (
      <SetPicker
        sets={[]}
        selected={[]}
        search={search}
        onSearchChange={setSearch}
        onToggle={() => {}}
      />
    );
  },
};

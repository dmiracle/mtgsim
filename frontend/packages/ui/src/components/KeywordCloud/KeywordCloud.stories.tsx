import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { KeywordCloud } from "./KeywordCloud";
import { keywordFrequencies } from "@/fixtures";

const meta: Meta<typeof KeywordCloud> = {
  title: "Cards/KeywordCloud",
  component: KeywordCloud,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-2xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof KeywordCloud>;

export const Interactive: Story = {
  render: () => {
    const [selected, setSelected] = useState<string[]>(["flying"]);
    return (
      <KeywordCloud
        frequencies={keywordFrequencies}
        selectedKeywords={selected}
        onToggleKeyword={(kw) =>
          setSelected((prev) =>
            prev.includes(kw) ? prev.filter((k) => k !== kw) : [...prev, kw]
          )
        }
        keywordDefinitions={{
          flying: "This creature can't be blocked except by creatures with flying and/or reach.",
          trample: "This creature can deal excess combat damage to the player or planeswalker it's attacking.",
          deathtouch: "Any amount of damage this deals to a creature is enough to destroy it.",
        }}
      />
    );
  },
};

export const NoneSelected: Story = {
  args: {
    frequencies: keywordFrequencies,
    selectedKeywords: [],
    onToggleKeyword: () => {},
  },
};

export const MultipleSelected: Story = {
  args: {
    frequencies: keywordFrequencies,
    selectedKeywords: ["flying", "create", "landfall"],
    onToggleKeyword: () => {},
  },
};

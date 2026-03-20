import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardFilterBar } from "./CardFilterBar";
import type { CardFilters } from "./CardFilterBar";

const sampleTags = [
  { tag: "removal", count: 245 },
  { tag: "burn", count: 128 },
  { tag: "board-wipe", count: 67 },
  { tag: "counter", count: 89 },
  { tag: "draw", count: 312 },
  { tag: "ramp", count: 156 },
  { tag: "token", count: 201 },
  { tag: "graveyard", count: 98 },
];

const emptyFilters: CardFilters = {
  text: "",
  colors: [],
  rarities: [],
  types: [],
  tags: [],
  ownership: "all",
  sort: "name",
  order: "asc",
  unique: false,
};

const meta: Meta<typeof CardFilterBar> = {
  title: "Filters/CardFilterBar",
  component: CardFilterBar,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 max-w-4xl min-h-[500px]">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CardFilterBar>;

export const Empty: Story = {
  args: {
    filters: emptyFilters,
    availableTags: sampleTags,
    resultCount: 28500,
    onChange: () => {},
  },
};

export const Interactive: Story = {
  render: () => {
    const [filters, setFilters] = useState<CardFilters>({
      text: "",
      colors: ["R"],
      rarities: ["rare", "mythic"],
      types: ["Creature"],
      tags: ["burn"],
      ownership: "all",
      sort: "name",
      order: "asc",
      unique: false,
    });
    return (
      <div className="space-y-4">
        <CardFilterBar
          filters={filters}
          onChange={setFilters}
          availableTags={sampleTags}
          resultCount={142}
          showUnique
        />
        <pre className="text-xs text-text-muted bg-bg-secondary p-3 rounded overflow-auto">
          {JSON.stringify(filters, null, 2)}
        </pre>
      </div>
    );
  },
};

export const WithActiveFilters: Story = {
  args: {
    filters: {
      text: "destroy",
      colors: ["B", "R"],
      rarities: ["uncommon", "rare"],
      types: ["Instant", "Sorcery"],
      tags: ["removal"],
      ownership: "owned",
      sort: "mana_value",
      order: "asc",
      unique: true,
    },
    availableTags: sampleTags,
    resultCount: 37,
    showUnique: true,
    onChange: () => {},
  },
};

export const WithUniqueToggle: Story = {
  args: {
    filters: emptyFilters,
    availableTags: sampleTags,
    resultCount: 500,
    showUnique: true,
    onChange: () => {},
  },
};

export const CustomSortOptions: Story = {
  args: {
    filters: { ...emptyFilters, sort: "number" },
    availableTags: sampleTags,
    resultCount: 303,
    sortOptions: [
      { value: "name", label: "Name" },
      { value: "mana_value", label: "Mana Value" },
      { value: "number", label: "Collector #" },
      { value: "rarity", label: "Rarity" },
      { value: "price", label: "Price" },
    ],
    onChange: () => {},
  },
};

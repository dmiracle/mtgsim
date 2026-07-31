import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { SortSelect } from "./SortSelect";

const cardSortOptions = [
  { value: "name", label: "Name" },
  { value: "mana_value", label: "Mana Value" },
  { value: "rarity", label: "Rarity" },
  { value: "price", label: "Price" },
];

const meta: Meta<typeof SortSelect> = {
  title: "Filters/SortSelect",
  component: SortSelect,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SortSelect>;

export const Default: Story = {
  args: {
    options: cardSortOptions,
    sort: "name",
    order: "asc",
    onSortChange: () => {},
    onOrderChange: () => {},
  },
};

export const Interactive: Story = {
  render: () => {
    const [sort, setSort] = useState("name");
    const [order, setOrder] = useState<"asc" | "desc">("asc");
    return (
      <div className="space-y-3">
        <SortSelect
          options={cardSortOptions}
          sort={sort}
          order={order}
          onSortChange={setSort}
          onOrderChange={setOrder}
        />
        <p className="text-text-muted text-sm">Sort: {sort} {order}</p>
      </div>
    );
  },
};

export const WithSecondarySort: Story = {
  args: {
    options: [...cardSortOptions, { value: "color", label: "Color" }],
    sort: "color",
    secondary: "mana_value",
    order: "asc",
  },
};

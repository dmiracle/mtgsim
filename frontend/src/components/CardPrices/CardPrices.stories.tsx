import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardPrices } from "./CardPrices";

const meta: Meta<typeof CardPrices> = {
  title: "CardDetail/CardPrices",
  component: CardPrices,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-md"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardPrices>;

export const Default: Story = {
  args: {
    prices: [
      { provider: "tcgplayer", finish: "nonfoil", listing_type: "market", price: 1.5 },
      { provider: "tcgplayer", finish: "foil", listing_type: "market", price: 3.25 },
      { provider: "cardkingdom", finish: "nonfoil", listing_type: "retail", price: 1.99 },
      { provider: "cardmarket", finish: "nonfoil", listing_type: "trend", price: 1.2 },
    ],
  },
};

export const Empty: Story = {
  args: { prices: [] },
};

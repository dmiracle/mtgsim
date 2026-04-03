import type { Meta, StoryObj } from "@storybook/react-vite";
import { RawJsonViewer } from "./RawJsonViewer";
import { cardDetail, deckDetail, setDetail } from "@/fixtures";

const meta: Meta<typeof RawJsonViewer> = {
  title: "Shared/RawJsonViewer",
  component: RawJsonViewer,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-2xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof RawJsonViewer>;

export const CardData: Story = {
  args: { data: cardDetail, title: "Card JSON" },
};

export const DeckData: Story = {
  args: { data: deckDetail, title: "Deck JSON" },
};

export const SetData: Story = {
  args: { data: setDetail, title: "Set JSON" },
};

export const DefaultExpanded: Story = {
  args: { data: { name: "Lightning Bolt", mana_cost: "{R}", type: "Instant" }, title: "Simple Object", defaultExpanded: true },
};

export const SmallMaxHeight: Story = {
  args: { data: cardDetail, title: "Scrollable", maxHeight: 150 },
};

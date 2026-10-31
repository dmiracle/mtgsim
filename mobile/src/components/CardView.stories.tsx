import type { Meta, StoryObj } from "@storybook/react-vite";
import { cards } from "../fixtures";
import { CardView } from "./CardView";

const meta: Meta<typeof CardView> = {
  title: "Mobile/CardView",
  component: CardView,
  decorators: [(Story) => <div className="p-4"><Story /></div>],
};
export default meta;
type Story = StoryObj<typeof CardView>;

export const WithTags: Story = { args: { card: cards[0] } };
export const Spell: Story = { args: { card: cards[1] } };
export const NoImage: Story = { args: { card: { ...cards[2], image_url: null } } };

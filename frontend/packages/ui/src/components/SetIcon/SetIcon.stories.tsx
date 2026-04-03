import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SetIcon } from "./SetIcon";

const meta: Meta<typeof SetIcon> = {
  title: "Shared/SetIcon",
  component: SetIcon,
  tags: ["autodocs"],
  args: { onClick: fn() },
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-8">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SetIcon>;

export const Default: Story = {
  args: { code: "MH2", name: "Modern Horizons 2" },
};

export const Common: Story = {
  args: { code: "DMU", name: "Dominaria United", rarity: "common" },
};

export const Uncommon: Story = {
  args: { code: "DMU", name: "Dominaria United", rarity: "uncommon" },
};

export const Rare: Story = {
  args: { code: "DMU", name: "Dominaria United", rarity: "rare" },
};

export const Mythic: Story = {
  args: { code: "DMU", name: "Dominaria United", rarity: "mythic" },
};

export const Small: Story = {
  args: { code: "ONE", name: "Phyrexia: All Will Be One", size: "sm" },
};

export const Large: Story = {
  args: { code: "ONE", name: "Phyrexia: All Will Be One", size: "lg", rarity: "mythic" },
};

export const Navigable: Story = {
  args: { code: "LTR", name: "Lord of the Rings", navigable: true, rarity: "rare" },
};

export const AllRarities: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <SetIcon code="MH2" name="Modern Horizons 2" rarity="common" size="lg" />
      <SetIcon code="MH2" name="Modern Horizons 2" rarity="uncommon" size="lg" />
      <SetIcon code="MH2" name="Modern Horizons 2" rarity="rare" size="lg" />
      <SetIcon code="MH2" name="Modern Horizons 2" rarity="mythic" size="lg" />
    </div>
  ),
};

export const MultipleSets: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <SetIcon code="MH2" name="Modern Horizons 2" rarity="rare" />
      <SetIcon code="ONE" name="Phyrexia: All Will Be One" rarity="mythic" />
      <SetIcon code="DMU" name="Dominaria United" rarity="uncommon" />
      <SetIcon code="M10" name="Magic 2010" rarity="common" />
      <SetIcon code="LTR" name="Lord of the Rings" rarity="rare" />
      <SetIcon code="2XM" name="Double Masters" rarity="mythic" />
    </div>
  ),
};

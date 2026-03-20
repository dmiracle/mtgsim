import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { SetBadge } from "./SetBadge";

const meta: Meta<typeof SetBadge> = {
  title: "Shared/SetBadge",
  component: SetBadge,
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
type Story = StoryObj<typeof SetBadge>;

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
      <SetBadge code="MH2" name="Modern Horizons 2" rarity="common" />
      <SetBadge code="MH2" name="Modern Horizons 2" rarity="uncommon" />
      <SetBadge code="MH2" name="Modern Horizons 2" rarity="rare" />
      <SetBadge code="MH2" name="Modern Horizons 2" rarity="mythic" />
    </div>
  ),
};

export const MultipleSets: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <SetBadge code="MH2" name="Modern Horizons 2" rarity="rare" />
      <SetBadge code="ONE" name="Phyrexia: All Will Be One" rarity="mythic" />
      <SetBadge code="DMU" name="Dominaria United" rarity="uncommon" />
      <SetBadge code="M10" name="Magic 2010" />
      <SetBadge code="LTR" name="Lord of the Rings" rarity="rare" />
    </div>
  ),
};

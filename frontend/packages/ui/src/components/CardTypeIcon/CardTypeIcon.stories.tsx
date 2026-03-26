import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardTypeIcon } from "./CardTypeIcon";

const meta: Meta<typeof CardTypeIcon> = {
  title: "Shared/CardTypeIcon",
  component: CardTypeIcon,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-8">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof CardTypeIcon>;

export const AllTypes: Story = {
  render: () => (
    <div className="flex flex-wrap gap-6">
      {["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land", "Battle"].map(
        (type) => (
          <div key={type} className="flex flex-col items-center gap-2">
            <CardTypeIcon type={type} size={32} className="text-text-secondary" />
            <span className="text-xs text-text-muted">{type}</span>
          </div>
        )
      )}
    </div>
  ),
};

export const Small: Story = {
  render: () => (
    <div className="flex items-center gap-3">
      {["Creature", "Instant", "Sorcery", "Land"].map((type) => (
        <CardTypeIcon key={type} type={type} size={14} className="text-text-muted" />
      ))}
    </div>
  ),
};

export const Large: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      {["Creature", "Instant", "Sorcery", "Enchantment", "Artifact", "Planeswalker", "Land"].map(
        (type) => (
          <CardTypeIcon key={type} type={type} size={48} className="text-accent" />
        )
      )}
    </div>
  ),
};

export const WithAccentColor: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <CardTypeIcon type="Creature" size={32} className="text-success" />
      <CardTypeIcon type="Instant" size={32} className="text-accent" />
      <CardTypeIcon type="Sorcery" size={32} className="text-warning" />
      <CardTypeIcon type="Enchantment" size={32} className="text-danger" />
    </div>
  ),
};

export const InlineWithText: Story = {
  render: () => (
    <div className="flex items-center gap-2 text-text-secondary text-sm">
      <CardTypeIcon type="Creature" size={16} className="text-text-secondary" />
      <span>Creature — Human Wizard</span>
    </div>
  ),
};

export const Unknown: Story = {
  args: { type: "Tribal", size: 24 },
};

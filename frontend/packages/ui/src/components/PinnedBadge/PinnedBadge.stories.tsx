import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { PinnedBadge } from "./PinnedBadge";

const meta: Meta<typeof PinnedBadge> = {
  title: "Shared/PinnedBadge",
  component: PinnedBadge,
  tags: ["autodocs"],
  argTypes: {
    icon: {
      control: "select",
      options: ["pin", "loyalty", "planeswalker", "saga", "rarity", "acorn"],
    },
    size: { control: "select", options: ["sm", "md"] },
  },
  decorators: [
    (Story) => (
      <div className="flex items-center gap-4 p-6 bg-bg-primary">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof PinnedBadge>;

export const Interactive: Story = {
  render: () => {
    const [pinned, setPinned] = useState(false);
    return <PinnedBadge pinned={pinned} onToggle={() => setPinned(!pinned)} />;
  },
};

export const AllIcons: Story = {
  render: () => {
    const icons = ["pin", "loyalty", "planeswalker", "saga", "rarity", "acorn"] as const;
    return (
      <div className="space-y-6">
        <div>
          <p className="text-xs text-text-muted mb-3">Pinned state</p>
          <div className="flex items-center gap-6">
            {icons.map((icon) => (
              <div key={icon} className="flex flex-col items-center gap-2">
                <PinnedBadge pinned onToggle={() => {}} icon={icon} size="md" />
                <span className="text-[10px] text-text-muted">{icon}</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs text-text-muted mb-3">Unpinned state</p>
          <div className="flex items-center gap-6">
            {icons.map((icon) => (
              <div key={icon} className="flex flex-col items-center gap-2">
                <PinnedBadge pinned={false} onToggle={() => {}} icon={icon} size="md" />
                <span className="text-[10px] text-text-muted">{icon}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  },
};

export const OnCard: Story = {
  render: () => {
    const icons = ["pin", "loyalty", "planeswalker", "saga", "rarity", "acorn"] as const;
    const [selected, setSelected] = useState<Record<string, boolean>>({});
    return (
      <div className="flex gap-4 flex-wrap">
        {icons.map((icon) => (
          <div key={icon} className="relative w-32 h-44 bg-bg-tertiary rounded-lg overflow-hidden">
            <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900" />
            <div className="absolute top-1.5 left-1.5">
              <PinnedBadge
                pinned={!!selected[icon]}
                onToggle={() => setSelected((s) => ({ ...s, [icon]: !s[icon] }))}
                icon={icon}
              />
            </div>
            <span className="absolute bottom-2 left-2 text-[10px] text-white/60">{icon}</span>
          </div>
        ))}
      </div>
    );
  },
};

export const OnListItem: Story = {
  render: () => {
    const icons = ["pin", "loyalty", "planeswalker", "saga", "rarity", "acorn"] as const;
    const [selected, setSelected] = useState<Record<string, boolean>>({});
    return (
      <div className="space-y-3 w-80">
        {icons.map((icon) => (
          <div key={icon} className="relative flex items-center gap-3 px-4 py-3 bg-bg-secondary border border-border rounded-lg">
            <div className="absolute -top-1.5 -left-1.5">
              <PinnedBadge
                pinned={!!selected[icon]}
                onToggle={() => setSelected((s) => ({ ...s, [icon]: !s[icon] }))}
                icon={icon}
              />
            </div>
            <span className="text-sm text-text-primary ml-2">Deck with {icon} icon</span>
          </div>
        ))}
      </div>
    );
  },
};

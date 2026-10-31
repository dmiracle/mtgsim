import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { TierListBoard } from "./TierListBoard";
import { tierListDetail } from "@/fixtures";
import type { Tier, TierEntry } from "@/types/api";

const meta: Meta<typeof TierListBoard> = {
  title: "UserData/TierListBoard",
  component: TierListBoard,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    entries: tierListDetail.entries,
    onMove: fn(),
    onRemove: fn(),
    onNoteChange: fn(),
    onCardClick: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary p-4 max-w-3xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof TierListBoard>;

export const Default: Story = {};

export const Empty: Story = {
  args: { entries: [] },
};

export const ReadOnly: Story = {
  args: { onRemove: undefined, onNoteChange: undefined },
};

export const Interactive: Story = {
  render: () => {
    const [entries, setEntries] = useState<TierEntry[]>(tierListDetail.entries);

    function move(cardName: string, tier: Tier, position?: number) {
      setEntries((prev) => {
        const moving = prev.find((e) => e.card_name === cardName);
        if (!moving) return prev;
        const rest = prev.filter((e) => e.card_name !== cardName);
        const siblings = rest.filter((e) => e.tier === tier).sort((a, b) => a.position - b.position);
        const insertAt = position ?? siblings.length;
        siblings.splice(Math.min(insertAt, siblings.length), 0, { ...moving, tier });
        const renumbered = siblings.map((e, i) => ({ ...e, position: i }));
        return [...rest.filter((e) => e.tier !== tier), ...renumbered];
      });
    }

    return (
      <TierListBoard
        entries={entries}
        onMove={move}
        onRemove={(cardName) => setEntries((prev) => prev.filter((e) => e.card_name !== cardName))}
        onNoteChange={(cardName, note) =>
          setEntries((prev) => prev.map((e) => (e.card_name === cardName ? { ...e, note: note || null } : e)))
        }
        onCardClick={(uuid) => console.log("card click", uuid)}
      />
    );
  },
};

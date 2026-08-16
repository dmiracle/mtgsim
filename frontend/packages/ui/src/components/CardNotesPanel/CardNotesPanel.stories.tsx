import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { CardNotesPanel } from "./CardNotesPanel";
import { cardNotes } from "@/fixtures";
import type { CardNote } from "@/types/api";

const meta: Meta<typeof CardNotesPanel> = {
  title: "UserData/CardNotesPanel",
  component: CardNotesPanel,
  tags: ["autodocs"],
  parameters: { layout: "padded" },
  args: {
    notes: cardNotes,
    onCreate: fn(),
    onUpdate: fn(),
    onDelete: fn(),
  },
  decorators: [(Story) => <div className="bg-bg-primary p-4 max-w-lg"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardNotesPanel>;

export const Default: Story = {};

export const Empty: Story = {
  args: { notes: [] },
};

export const SingleNote: Story = {
  args: { notes: cardNotes.slice(0, 1) },
};

export const Interactive: Story = {
  render: () => {
    const [notes, setNotes] = useState<CardNote[]>(cardNotes);
    return (
      <CardNotesPanel
        notes={notes}
        onCreate={(data) =>
          setNotes((prev) => [
            ...prev,
            {
              id: Math.max(0, ...prev.map((n) => n.id)) + 1,
              card_name: "Lightning Bolt",
              extra: {},
              created_at: "2026-08-16T12:00:00Z",
              updated_at: "2026-08-16T12:00:00Z",
              ...data,
            },
          ])
        }
        onUpdate={(id, data) =>
          setNotes((prev) => prev.map((n) => (n.id === id ? { ...n, ...data } : n)))
        }
        onDelete={(id) => setNotes((prev) => prev.filter((n) => n.id !== id))}
      />
    );
  },
};

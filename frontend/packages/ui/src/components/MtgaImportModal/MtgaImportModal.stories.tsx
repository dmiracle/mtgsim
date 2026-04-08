import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { MtgaImportModal } from "./MtgaImportModal";

const meta: Meta<typeof MtgaImportModal> = {
  title: "Collection/MtgaImportModal",
  component: MtgaImportModal,
  tags: ["autodocs"],
  parameters: { layout: "fullscreen" },
  args: {
    open: true,
    onImport: fn(),
    onClose: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof MtgaImportModal>;

export const Default: Story = {};

export const Importing: Story = {
  args: { importing: true },
};

export const WithResult: Story = {
  args: {
    result: {
      matched: 1250,
      created: 48,
      updated: 1202,
      unmatched: [],
    },
  },
};

export const WithUnmatched: Story = {
  args: {
    result: {
      matched: 1200,
      created: 30,
      updated: 1170,
      unmatched: ["Alchemy Card Alpha", "Alchemy Card Beta", "Some Arena Special"],
    },
  },
};

export const Interactive: Story = {
  render: () => {
    const [open, setOpen] = useState(true);
    return (
      <div className="h-screen bg-bg-primary p-8">
        <button onClick={() => setOpen(true)} className="text-sm px-3 py-1.5 rounded bg-accent text-white">
          Import MTGA
        </button>
        <MtgaImportModal
          open={open}
          onImport={(file) => console.log("import", file.name)}
          onClose={() => setOpen(false)}
        />
      </div>
    );
  },
};

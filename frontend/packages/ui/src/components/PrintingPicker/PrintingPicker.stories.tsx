import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { fn } from "storybook/test";
import { PrintingPicker } from "./PrintingPicker";
import type { DeckCardPrinting } from "@/types/api";

const mockPrintings: DeckCardPrinting[] = [
  { uuid: "p1", set_code: "M10", set_name: "Magic 2010", number: "146", language: "English", is_default_printing: false, image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg" },
  { uuid: "p2", set_code: "2X2", set_name: "Double Masters 2022", number: "195", language: "English", is_default_printing: false, image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg" },
  { uuid: "p3", set_code: "A25", set_name: "Masters 25", number: "141", language: "English", is_default_printing: false, image_url: null },
  { uuid: "p4", set_code: "STA", set_name: "Strixhaven Mystical Archive", number: "62", language: "English", is_default_printing: false, image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg" },
  { uuid: "p5", set_code: "TSR", set_name: "Time Spiral Remastered", number: "163", language: "English", is_default_printing: false, image_url: "https://cards.scryfall.io/normal/front/f/2/f29ba16f-c8fb-42fe-aabf-87089cb214a7.jpg" },
  { uuid: "p6", set_code: "MM2", set_name: "Modern Masters 2015", number: "123", language: "English", is_default_printing: false, image_url: null },
];

const meta: Meta<typeof PrintingPicker> = {
  title: "Decks/PrintingPicker",
  component: PrintingPicker,
  tags: ["autodocs"],
  parameters: { layout: "fullscreen" },
  args: {
    open: true,
    cardName: "Lightning Bolt",
    printings: mockPrintings,
    onSelect: fn(),
    onClose: fn(),
  },
};

export default meta;
type Story = StoryObj<typeof PrintingPicker>;

export const Default: Story = {};

export const WithSelected: Story = {
  args: { currentUuid: "p2" },
};

export const SinglePrinting: Story = {
  args: { printings: mockPrintings.slice(0, 1) },
};

export const Interactive: Story = {
  render: () => {
    const [open, setOpen] = useState(true);
    const [selected, setSelected] = useState("p1");
    return (
      <div className="h-screen bg-bg-primary p-8">
        <button onClick={() => setOpen(true)} className="text-sm px-3 py-1.5 rounded bg-accent text-white">
          Open Picker
        </button>
        <PrintingPicker
          open={open}
          cardName="Lightning Bolt"
          printings={mockPrintings}
          currentUuid={selected}
          onSelect={(uuid) => { setSelected(uuid); setOpen(false); }}
          onClose={() => setOpen(false)}
        />
      </div>
    );
  },
};

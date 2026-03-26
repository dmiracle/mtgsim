import type { Meta, StoryObj } from "@storybook/react-vite";
import { CardOracleText } from "./CardOracleText";

const meta: Meta<typeof CardOracleText> = {
  title: "CardDetail/CardOracleText",
  component: CardOracleText,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-lg"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof CardOracleText>;

export const SimpleText: Story = {
  args: {
    text: "Lightning Bolt deals 3 damage to any target.",
    flavor_text: "The sparkmage shrieked, calling on the rage of the storms of his youth.",
  },
};

export const WithManaSymbols: Story = {
  args: {
    text: "Add {B}{B}{B}.",
    flavor_text: null,
  },
};

export const MultiParagraph: Story = {
  args: {
    text: "Haste\nWhenever Goblin Guide attacks, defending player reveals the top card of their library. If it's a land card, that player puts it into their hand.",
    flavor_text: null,
  },
};

export const ComplexText: Story = {
  args: {
    text: "{T}: Add {C}.\n{1}, {T}, Sacrifice Fabled Passage: Search your library for a basic land card, put it onto the battlefield tapped, then shuffle. If you control four or more lands, put that card onto the battlefield untapped instead.",
    flavor_text: null,
  },
};

export const NoFlavor: Story = {
  args: {
    text: "Counter target spell.",
  },
};

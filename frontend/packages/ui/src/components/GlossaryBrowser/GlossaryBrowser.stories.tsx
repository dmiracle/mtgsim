import type { Meta, StoryObj } from "@storybook/react-vite";
import { GlossaryBrowser } from "./GlossaryBrowser";

const sampleEntries = [
  { term: "Battlefield", definition: "The zone where permanents exist. Cards enter the battlefield when they are played or put there by an effect.", category: "Zone" },
  { term: "Commander", definition: "A format where each player builds a 100-card singleton deck led by a legendary creature.", category: "Format" },
  { term: "Creature", definition: "A card type representing beings that can attack and block.", category: "Card Type" },
  { term: "Deathtouch", definition: "Any amount of damage this deals to a creature is enough to destroy it.", category: "Keyword" },
  { term: "Exile", definition: "A zone for cards removed from the game. Cards in exile are face up unless stated otherwise.", category: "Zone" },
  { term: "Flash", definition: "You may cast this spell any time you could cast an instant.", category: "Keyword" },
  { term: "Graveyard", definition: "A player's discard pile. Cards go here when destroyed, discarded, or milled.", category: "Zone" },
  { term: "Hand", definition: "The zone of cards a player has drawn but not yet played.", category: "Zone" },
  { term: "Instant", definition: "A card type that can be cast at any time you have priority.", category: "Card Type" },
  { term: "Library", definition: "A player's draw pile. Cards are drawn from the top.", category: "Zone" },
  { term: "Modern", definition: "A constructed format using cards from Eighth Edition forward.", category: "Format" },
  { term: "Pioneer", definition: "A constructed format using cards from Return to Ravnica forward.", category: "Format" },
  { term: "Sorcery", definition: "A card type that can only be cast during your main phase when the stack is empty.", category: "Card Type" },
  { term: "Standard", definition: "A rotating constructed format using the most recent sets.", category: "Format" },
  { term: "Stack", definition: "The zone where spells and abilities exist while waiting to resolve.", category: "Zone" },
  { term: "Trample", definition: "This creature can deal excess combat damage to the defending player.", category: "Keyword" },
];

const meta: Meta<typeof GlossaryBrowser> = {
  title: "Reference/GlossaryBrowser",
  component: GlossaryBrowser,
  tags: ["autodocs"],
  decorators: [(Story) => <div className="bg-bg-primary p-6 max-w-2xl"><Story /></div>],
};

export default meta;
type Story = StoryObj<typeof GlossaryBrowser>;

export const Default: Story = {
  args: { entries: sampleEntries },
};

export const Empty: Story = {
  args: { entries: [] },
};

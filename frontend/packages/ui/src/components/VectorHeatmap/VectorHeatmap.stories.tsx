import type { Meta, StoryObj } from "@storybook/react-vite";
import { VectorHeatmap } from "./VectorHeatmap";

// Simulated 64-dim vectors
const emptyVector = Array(64).fill(0);
const randomVector = Array.from({ length: 64 }, () => Math.random());
const sparseVector = emptyVector.map((_, i) => [3, 5, 8, 15, 21, 23, 26, 28, 36].includes(i) ? [1, 0.2, 1, 0.1, 1, 0.09, 1, 1, 1][[3, 5, 8, 15, 21, 23, 26, 28, 36].indexOf(i)] : 0);
const hotVector = Array.from({ length: 64 }, (_, i) => i < 32 ? 0.8 + Math.random() * 0.2 : Math.random() * 0.3);
const deckVector = Array.from({ length: 64 }, () => Math.random() * 0.6 + 0.1);

const featureNames = [
  "color_W", "color_U", "color_B", "color_R", "color_G", "color_count", "is_multicolor", "is_colorless",
  "is_creature", "is_instant", "is_sorcery", "is_enchantment", "is_artifact", "is_land", "is_planeswalker", "is_legendary",
  "mana_value", "power", "toughness", "loyalty", "defense", "has_oracle_text", "has_flavor", "text_complexity",
  "is_common", "is_uncommon", "is_rare", "is_mythic", "is_reprint", "is_reserved", "is_promo", "has_subtypes",
  "kw_flying", "kw_trample", "kw_haste", "kw_lifelink", "kw_deathtouch", "kw_vigilance", "kw_reach", "kw_menace",
  "kw_first_strike", "kw_flash", "kw_hexproof", "kw_indestructible", "kw_defender", "kw_prowess", "kw_ward", "kw_equip",
  "tag_removal", "tag_ramp", "tag_draw", "tag_counter", "tag_burn", "tag_lifegain", "tag_tutor", "tag_token",
  "tag_graveyard", "tag_exile", "tag_sacrifice", "tag_discard", "tag_mill", "tag_blink", "tag_pump", "tag_evasion",
];

const meta: Meta<typeof VectorHeatmap> = {
  title: "Shared/VectorHeatmap",
  component: VectorHeatmap,
  tags: ["autodocs"],
  decorators: [
    (Story) => (
      <div className="bg-bg-primary p-6 space-y-6">
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof VectorHeatmap>;

export const SingleCard: Story = {
  args: { vector: sparseVector, featureNames, label: "Lightning Bolt" },
};

export const DeckFingerprint: Story = {
  args: { vector: deckVector, featureNames, label: "Mono Red Burn" },
};

export const Empty: Story = {
  args: { vector: emptyVector, label: "No data" },
};

export const FullRandom: Story = {
  args: { vector: randomVector, featureNames, label: "Random" },
};

export const HotCold: Story = {
  args: { vector: hotVector, featureNames, label: "Hot/Cold split" },
};

export const Small: Story = {
  args: { vector: sparseVector, label: "Small", size: "sm" },
};

export const Large: Story = {
  args: { vector: deckVector, featureNames, label: "Large", size: "lg" },
};

export const Comparison: Story = {
  render: () => (
    <div className="flex gap-6">
      <VectorHeatmap vector={sparseVector} featureNames={featureNames} label="Lightning Bolt" />
      <VectorHeatmap vector={hotVector} featureNames={featureNames} label="Tarmogoyf" />
      <VectorHeatmap vector={deckVector} featureNames={featureNames} label="Deck Average" />
    </div>
  ),
};

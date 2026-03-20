import type { Preview } from '@storybook/react-vite'
import '../src/index.css'

const THEMES = [
  // Dark - clean
  { value: 'dark-slate', title: 'Dark Slate', icon: 'circle' },
  { value: 'dark-zinc', title: 'Dark Zinc', icon: 'circle' },
  { value: 'dark-emerald', title: 'Dark Emerald', icon: 'circle' },
  { value: 'dark-rose', title: 'Dark Rose', icon: 'circle' },
  // Dark - wild
  { value: 'dark-cyberpunk', title: 'Cyberpunk', icon: 'star' },
  { value: 'dark-synthwave', title: 'Synthwave', icon: 'star' },
  { value: 'dark-blood', title: 'Blood Moon', icon: 'star' },
  { value: 'dark-gold', title: 'Gold Vault', icon: 'star' },
  { value: 'dark-arctic', title: 'Arctic', icon: 'star' },
  { value: 'dark-terminal', title: 'Terminal', icon: 'star' },
  // Light - clean
  { value: 'light-default', title: 'Light Default', icon: 'circlehollow' },
  { value: 'light-warm', title: 'Light Warm', icon: 'circlehollow' },
  { value: 'light-lavender', title: 'Light Lavender', icon: 'circlehollow' },
  { value: 'light-ocean', title: 'Light Ocean', icon: 'circlehollow' },
  // Light - wild
  { value: 'light-bubblegum', title: 'Bubblegum', icon: 'starhollow' },
  { value: 'light-mint', title: 'Mint', icon: 'starhollow' },
  { value: 'light-sunset', title: 'Sunset', icon: 'starhollow' },
  { value: 'light-newspaper', title: 'Newspaper', icon: 'starhollow' },
];

const preview: Preview = {
  globalTypes: {
    theme: {
      description: 'Color theme',
      toolbar: {
        title: 'Theme',
        icon: 'paintbrush',
        items: THEMES,
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: {
    theme: 'dark-slate',
  },
  decorators: [
    (Story, context) => {
      const theme = context.globals.theme || 'dark-slate';
      document.documentElement.setAttribute('data-theme', theme);
      return Story();
    },
  ],
  parameters: {
    controls: {
      matchers: {
       color: /(background|color)$/i,
       date: /Date$/i,
      },
    },
    a11y: {
      test: 'todo'
    },
    backgrounds: { disable: true },
  },
};

export default preview;

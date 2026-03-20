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

const FONTS = [
  // Clean
  { value: 'system', title: 'System Default', icon: 'document' },
  { value: 'inter', title: 'Inter', icon: 'document' },
  { value: 'geist', title: 'Geist', icon: 'document' },
  { value: 'clean', title: 'DM Sans', icon: 'document' },
  { value: 'compact', title: 'IBM Plex', icon: 'document' },
  { value: 'sora', title: 'Sora', icon: 'document' },
  // Expressive
  { value: 'serif', title: 'Playfair + Source Serif', icon: 'bookmark' },
  { value: 'mechanical', title: 'Rajdhani + Exo 2', icon: 'bookmark' },
  { value: 'fantasy', title: 'Cinzel + Cormorant', icon: 'bookmark' },
  // Wild
  { value: 'streetwear', title: 'Streetwear', icon: 'lightning' },
  { value: 'luxury', title: 'Luxury', icon: 'lightning' },
  { value: 'arcade', title: 'Retro Arcade', icon: 'lightning' },
  { value: 'brutalist', title: 'Brutalist', icon: 'lightning' },
  { value: 'neo-tokyo', title: 'Neo Tokyo', icon: 'lightning' },
  { value: 'comic', title: 'Comic Book', icon: 'lightning' },
  { value: 'western', title: 'Western', icon: 'lightning' },
  { value: 'art-deco', title: 'Art Deco', icon: 'lightning' },
  { value: 'grunge', title: 'Grunge', icon: 'lightning' },
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
    font: {
      description: 'Typography theme',
      toolbar: {
        title: 'Font',
        icon: 'document',
        items: FONTS,
        dynamicTitle: true,
      },
    },
  },
  initialGlobals: {
    theme: 'dark-slate',
    font: 'system',
  },
  decorators: [
    (Story, context) => {
      const theme = context.globals.theme || 'dark-slate';
      const font = context.globals.font || 'system';
      document.documentElement.setAttribute('data-theme', theme);
      document.documentElement.setAttribute('data-font', font);
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
    viewport: {
      options: {
        mobile: { name: 'iPhone SE', styles: { width: '375px', height: '667px' } },
        mobileLg: { name: 'iPhone 14 Pro', styles: { width: '393px', height: '852px' } },
        tablet: { name: 'iPad Mini', styles: { width: '768px', height: '1024px' } },
        tabletLg: { name: 'iPad Pro', styles: { width: '1024px', height: '1366px' } },
        laptop: { name: 'Laptop', styles: { width: '1366px', height: '768px' } },
        desktop: { name: 'Desktop', styles: { width: '1920px', height: '1080px' } },
        ultrawide: { name: 'Ultrawide', styles: { width: '2560px', height: '1080px' } },
      },
    },
  },
};

export default preview;

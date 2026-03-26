import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const dirname = typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    host: '0.0.0.0',
    allowedHosts: [
      'deltron.tail4ca9d8.ts.net',
      'dylans-macbook-pro-2.tail4ca9d8.ts.net',
      'iphone-15.tail4ca9d8.ts.net',
      'macbookpro.tail4ca9d8.ts.net',
    ],
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:8001',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.join(dirname, 'src'),
      '@mtgsim/ui': path.join(dirname, '..', 'ui', 'src'),
    },
  },
});

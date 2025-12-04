import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

// Build to Flask static dir and reference assets via /static/app/
export default defineConfig({
  plugins: [react()],
  root: '.',
  base: '/static/app/',
  build: {
    outDir: resolve(__dirname, '../static/app'),
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
});

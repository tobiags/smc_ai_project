import { defineConfig } from 'vite'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      // Toutes les requêtes /api partent vers le backend FastAPI
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  plugins: [
    tanstackStart(),
    // le plugin react doit venir après celui de Start
    viteReact(),
  ],
})

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Konfiguracja proxy do przekierowywania żądań API do backendu FastAPI
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Adres backendu FastAPI
        changeOrigin: true,
        rewrite: ( ścieżka ) => ścieżka.replace(/^\/api/, '/api'), // Upewnij się, że /api jest zachowane
      },
      '/ws': {
        target: 'ws://localhost:8000', // Adres backendu FastAPI dla WebSocket
        ws: true, // Włącz proxy dla WebSocket
        changeOrigin: true,
        rewrite: ( ścieżka ) => ścieżka.replace(/^\/ws/, '/ws'), // Upewnij się, że /ws jest zachowane
      },
       '/stats': {
        target: 'http://localhost:8000', // Adres backendu FastAPI dla metryk
        changeOrigin: true,
        rewrite: ( ścieżka ) => ścieżka.replace(/^\/stats/, '/stats'),
      }
    }
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})

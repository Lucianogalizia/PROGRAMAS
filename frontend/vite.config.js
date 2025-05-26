import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: './',
  base: './',
  server: {
    host: true,       // escucha en 0.0.0.0
    port: 5173,       // mantiene tu puerto actual
    proxy: {
      // todo lo que vaya a /process se redirige a tu FastAPI local
      '/process': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})

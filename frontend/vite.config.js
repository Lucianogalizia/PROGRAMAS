import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  root: './',            // carpeta raíz
  base: './',
  server: { port: 5173 }
})

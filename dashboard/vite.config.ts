import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { defineConfig } from 'vite'

const root = import.meta.dirname

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@domain': resolve(root, 'src/domain'),
      '@infra': resolve(root, 'src/infrastructure'),
      '@presentation': resolve(root, 'src/presentation'),
    },
  },
})

import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { defineConfig } from 'vite'

const root = import.meta.dirname
// Load .env from the project root so SOCRATA_APP_TOKEN and VITE_* vars
// defined there are available without duplicating the file in dashboard/.
const projectRoot = resolve(root, '..')

export default defineConfig({
  plugins: [react()],
  envDir: projectRoot,
  resolve: {
    alias: {
      '@domain': resolve(root, 'src/domain'),
      '@infra': resolve(root, 'src/infrastructure'),
      '@presentation': resolve(root, 'src/presentation'),
    },
  },
})

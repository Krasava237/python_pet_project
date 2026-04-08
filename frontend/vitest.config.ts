import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      thresholds: {
        branches: 45,
        functions: 45,
        lines: 50,
        statements: 50,
      },
    },
    environment: 'jsdom',
    globals: true,
    maxWorkers: 1,
    pool: 'threads',
    setupFiles: ['./src/test/setup.ts'],
  },
})

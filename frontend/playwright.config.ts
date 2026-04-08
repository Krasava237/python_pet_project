import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

import { defineConfig } from '@playwright/test'

const repoRoot = resolve(import.meta.dirname, '..')
const windowsVenvPython = resolve(repoRoot, '.venv', 'Scripts', 'python.exe')
const posixVenvPython = resolve(repoRoot, '.venv', 'bin', 'python')
const pythonExecutable = existsSync(windowsVenvPython)
  ? `"${windowsVenvPython}"`
  : existsSync(posixVenvPython)
    ? `"${posixVenvPython}"`
    : 'python'

export default defineConfig({
  testDir: './e2e',
  testMatch: /.*\.e2e\.ts/,
  timeout: 60_000,
  use: {
    baseURL: 'http://127.0.0.1:4173',
    trace: 'retain-on-failure',
  },
  webServer: [
    {
      // Поднимаем отдельный backend для e2e, чтобы сценарии не зависели от локально запущенного окружения.
      command: `${pythonExecutable} scripts/run_test_server.py`,
      cwd: repoRoot,
      reuseExistingServer: false,
      timeout: 120_000,
      url: 'http://127.0.0.1:8001/health/live',
    },
    {
      // Frontend получает тестовый API base URL так же, как в production он получает env-конфиг.
      command:
        'npm run dev -- --host 127.0.0.1 --port 4173',
      cwd: import.meta.dirname,
      env: {
        ...process.env,
        VITE_API_BASE_URL: 'http://127.0.0.1:8001',
        VITE_PUBLIC_APP_URL: 'http://127.0.0.1:4173',
      },
      reuseExistingServer: false,
      timeout: 120_000,
      url: 'http://127.0.0.1:4173',
    },
  ],
})

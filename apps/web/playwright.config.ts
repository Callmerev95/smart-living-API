import { defineConfig, devices } from "@playwright/test";

/**
 * Konfigurasi E2E (`docs/technical-architecture.md` §20.4).
 *
 * `webServer` menyalakan API dan web sendiri, jadi test bisa dijalankan mandiri
 * tanpa perlu menyiapkan server manual. Web dijalankan dari build production —
 * bukan `next dev` — karena `NEXT_PUBLIC_API_BASE_URL` dibakar saat build dan
 * kita ingin menguji bundle yang benar-benar akan di-deploy.
 */

const API_URL = "http://localhost:8000";
const WEB_URL = "http://localhost:3000";
const isCI = Boolean(process.env.CI);

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  // Gagalkan CI bila ada `test.only` yang tertinggal.
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  workers: isCI ? 1 : undefined,
  reporter: isCI ? [["github"], ["html", { open: "never" }]] : "list",

  use: {
    baseURL: WEB_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],

  webServer: [
    {
      name: "API",
      command: "uv run uvicorn app.main:app --host 127.0.0.1 --port 8000",
      cwd: "../api",
      url: `${API_URL}/api/v1/health`,
      reuseExistingServer: !isCI,
      timeout: 120_000,
      stdout: "pipe",
      stderr: "pipe",
    },
    {
      name: "Web",
      command: "pnpm build && pnpm start",
      url: WEB_URL,
      env: { NEXT_PUBLIC_API_BASE_URL: API_URL },
      reuseExistingServer: !isCI,
      timeout: 300_000,
      stdout: "pipe",
      stderr: "pipe",
    },
  ],
});

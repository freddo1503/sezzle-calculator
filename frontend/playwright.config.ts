import { defineConfig, devices } from "@playwright/test";

/**
 * One smoke test against the running stack.
 *
 * Unit tests prove each hop in isolation. This proves the composition: the
 * arithmetic engine, the contract, the generated client, the runtime Zod
 * validation and the rendering, in one pass. It is the only artefact that shows
 * the exactness argument surviving every boundary, which is why there is one
 * and why there is not a suite.
 *
 * Playwright starts both layers itself, so `just e2e` needs nothing running.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: "uv run uvicorn app.main:app --port 8000",
      cwd: "../backend",
      url: "http://localhost:8000/openapi.json",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: "pnpm dev",
      url: "http://localhost:5173",
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
  ],
});

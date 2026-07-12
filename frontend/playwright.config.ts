import { defineConfig, devices } from "@playwright/test";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontendDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(frontendDir, "..");
const isExhibitionDemoE2E = process.env.VITE_EXHIBITION_DEMO_MODE === "true";

export default defineConfig({
  testDir: "./e2e",
  testIgnore: isExhibitionDemoE2E ? [] : "**/exhibition-demo.spec.ts",
  timeout: 30_000,
  retries: process.env.CI ? 2 : 0,
  use: {
    baseURL: "http://localhost:4173",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: "python scripts/setup_db.py && uvicorn src.dashboard.app:app --host 127.0.0.1 --port 8011",
      cwd: projectRoot,
      url: "http://localhost:8011/health/ready",
      reuseExistingServer: !process.env.CI,
      env: {
        APP_ENV: "e2e",
        DATABASE_URL: "sqlite:///./data/e2e.db",
        JWT_SECRET_KEY: "e2e-secret-key",
        FRONTEND_URL: "http://localhost:4173",
        CORS_ORIGINS: "http://localhost:4173",
      },
    },
    {
      command: "npm run dev -- --host localhost --port 4173",
      cwd: frontendDir,
      url: "http://localhost:4173",
      reuseExistingServer: !process.env.CI,
      env: {
        VITE_API_BASE_URL: "http://localhost:8011",
        VITE_EXHIBITION_DEMO_MODE: process.env.VITE_EXHIBITION_DEMO_MODE ?? "false",
      },
    },
  ],
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
});

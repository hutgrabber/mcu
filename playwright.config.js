import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  testIgnore: ["legacy/**"],
  fullyParallel: true,
  reporter: [["list"]],
  use: { baseURL: "http://localhost:4173", viewport: { width: 1440, height: 900 } },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
  webServer: { command: "node tests/serve.mjs", url: "http://localhost:4173", reuseExistingServer: true },
});

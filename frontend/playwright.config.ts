import { defineConfig, devices } from "@playwright/test";

const frontendUrl = "http://localhost:3000";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  retries: 0,
  reporter: "list",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: frontendUrl,
    browserName: "chromium",
    channel: "msedge",
    headless: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "off",
  },
  projects: [
    {
      name: "core-demo",
      use: {
        ...devices["Desktop Chrome"],
      },
    },
  ],
});

import { expect, test } from "@playwright/test";

test("shows an explicit error state when the briefing API fails", async ({ page }) => {
  await page.route("**/api/briefing", (route) =>
    route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "provider unavailable" }) }),
  );
  await page.goto("/");
  await expect(page.locator(".pipeline-status")).toContainText("API data unavailable");
});

test("shows fallback metadata instead of presenting seed data as live", async ({ page }) => {
  await page.route("**/api/briefing", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        asOf: "2026-07-06T00:00:00Z",
        signal: "YELLOW",
        riskScore: 50,
        headline: "Fallback briefing",
        summary: ["Stored fallback is active."],
        keyNews: [],
        providerStatus: { seed: "fallback" },
        dataSource: "seed_fallback",
        providers: ["seed"],
        isFallback: true,
        lastUpdated: "2026-07-06T00:00:00Z",
        warnings: ["Provider unavailable"],
      }),
    }),
  );
  await page.goto("/");
  await expect(page.locator(".pipeline-status")).toContainText("fallback active");
  await expect(page.locator(".pipeline-status")).toContainText("Provider unavailable");
});

test("renders an empty briefing payload without crashing", async ({ page }) => {
  await page.route("**/api/briefing", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        asOf: "2026-07-06T00:00:00Z",
        signal: "GREEN",
        riskScore: 0,
        headline: "No material events",
        summary: [],
        keyNews: [],
        providerStatus: {},
        dataSource: "real",
        providers: [],
        isFallback: false,
        lastUpdated: "2026-07-06T00:00:00Z",
        warnings: [],
      }),
    }),
  );
  await page.goto("/");
  await expect(page.locator(".pipeline-status")).toContainText("real");
  await expect(page.locator("body")).toContainText("No material events");
});

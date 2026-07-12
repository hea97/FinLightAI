import { expect, test } from "@playwright/test";

const emptyNewsGuardPayload = {
  stats: {
    collectedNewsCount: 0,
    trustedNewsCount: 0,
    watchNewsCount: 0,
    blockedNewsCount: 0,
    averageReliabilityScore: 0,
    deltaCollectedNewsCount: 0,
  },
  distribution: {
    trusted: { count: 0, ratio: 0 },
    watch: { count: 0, ratio: 0 },
    blocked: { count: 0, ratio: 0 },
  },
  blockReasons: [],
  quickFilters: [],
  providerHealth: [],
  articles: [],
  dataSource: "real",
  providers: [],
  isFallback: false,
  lastUpdated: "2026-07-13T00:00:00Z",
  warnings: [],
};

test("shows an explicit News Guard error without mock counts or providers", async ({ page }) => {
  await page.route("**/api/news-guard**", (route) =>
    route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "provider unavailable" }) }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "뉴스 가드" }).click();

  await expect(page.getByRole("heading", { name: "News Guard API 연결 실패" })).toBeVisible();
  await expect(page.locator(".pipeline-status")).toContainText("unavailable");
  await expect(page.locator("body")).not.toContainText("128건");
  await expect(page.locator("body")).not.toContainText("평균 신뢰도");
  await expect(page.locator("body")).not.toContainText("Guardian");
  await expect(page.locator("body")).not.toContainText("Finnhub");
});

test("shows an empty News Guard state without mock articles or provider health", async ({ page }) => {
  await page.route("**/api/news-guard**", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(emptyNewsGuardPayload) }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "뉴스 가드" }).click();

  await expect(page.getByRole("heading", { name: "분석 가능한 뉴스가 없습니다" })).toBeVisible();
  await expect(page.locator(".pipeline-status")).toContainText("real");
  await expect(page.locator("body")).not.toContainText("TechCrunch");
  await expect(page.locator("body")).not.toContainText("Guardian");
  await expect(page.locator("body")).not.toContainText("Finnhub");
});

test("labels fallback News Guard data and only shows response providers", async ({ page }) => {
  await page.route("**/api/news-guard**", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        ...emptyNewsGuardPayload,
        stats: {
          collectedNewsCount: 1,
          trustedNewsCount: 0,
          watchNewsCount: 1,
          blockedNewsCount: 0,
          averageReliabilityScore: 0.62,
          deltaCollectedNewsCount: 0,
        },
        distribution: {
          trusted: { count: 0, ratio: 0 },
          watch: { count: 1, ratio: 100 },
          blocked: { count: 0, ratio: 0 },
        },
        providerHealth: [{ provider: "GDELT", status: "fallback", message: "대체 데이터" }],
        articles: [
          {
            id: "fallback-news-1",
            title: "Fallback news item",
            source: "Stored seed",
            provider: "GDELT",
            publishedAgo: "2026-07-13",
            summary: "Fallback response article.",
            reliabilityLevel: "watch",
            reliabilityScore: 0.62,
            impactScore: 40,
            sentimentScore: 0,
            industries: ["반도체"],
            tags: ["fallback"],
            reasons: ["provider fallback"],
            qualityStatus: "seed_fallback",
          },
        ],
        dataSource: "seed_fallback",
        providers: ["GDELT"],
        isFallback: true,
        warnings: ["Provider unavailable"],
      }),
    }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "뉴스 가드" }).click();

  await expect(page.locator(".pipeline-status")).toContainText("fallback active");
  await expect(page.locator(".pipeline-status")).toContainText("대체 데이터 표시 중");
  await expect(page.locator(".pipeline-status")).toContainText("Provider unavailable");
  await expect(page.locator("body")).toContainText("Fallback news item");
  await expect(page.locator("body")).toContainText("GDELT");
  await expect(page.locator("body")).not.toContainText("Guardian");
  await expect(page.locator("body")).not.toContainText("Finnhub");
});

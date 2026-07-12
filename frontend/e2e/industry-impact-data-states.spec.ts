import { expect, test } from "@playwright/test";

const emptyIndustryPayload = {
  industries: [],
  details: {},
  dataSource: "real",
  providers: [],
  isFallback: false,
  lastUpdated: "2026-07-13T00:00:00Z",
  warnings: [],
};

const fallbackIndustryDetail = {
  industryId: "semiconductor",
  title: "반도체 상세",
  score: 12,
  statusLabel: "대체 데이터",
  description: "Fallback industry detail.",
  relatedStocks: ["Fallback Semiconductor"],
  newsCount: 1,
  averageSentiment: 0.1,
  riskPoints: 1,
  updatedAt: "2026-07-13T00:00:00Z",
  reasons: {
    positive: ["fallback positive reason"],
    caution: ["fallback caution reason"],
  },
  topNews: [
    {
      id: "semiconductor-news-1",
      rank: 1,
      title: "Semiconductor fallback evidence",
      source: "Stored seed",
      sentimentLabel: "중립",
      impactScore: 0.12,
    },
  ],
};

test("shows an explicit Industry Impact error without mock scores or stocks", async ({ page }) => {
  await page.route("**/api/industry-impact", (route) =>
    route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "provider unavailable" }) }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "산업 영향도" }).click();

  await expect(page.getByRole("heading", { name: "산업 영향도 API 연결 실패" })).toBeVisible();
  await expect(page.locator(".pipeline-status")).toContainText("unavailable");
  await expect(page.locator("body")).not.toContainText("+78");
  await expect(page.locator("body")).not.toContainText("삼성전자");
  await expect(page.locator("body")).not.toContainText("SK하이닉스");
});

test("shows an empty Industry Impact state without neutral or mock scores", async ({ page }) => {
  await page.route("**/api/industry-impact", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(emptyIndustryPayload) }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "산업 영향도" }).click();

  await expect(page.getByRole("heading", { name: "산업 영향 분석 데이터가 없습니다" })).toBeVisible();
  await expect(page.locator(".pipeline-status")).toContainText("real");
  await expect(page.locator("body")).not.toContainText("중립");
  await expect(page.locator("body")).not.toContainText("뉴스 12건");
  await expect(page.locator("body")).not.toContainText("삼성전자");
});

test("labels fallback Industry Impact data and renders only response evidence", async ({ page }) => {
  await page.route("**/api/industry-impact", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        industries: [
          { id: "semiconductor", name: "반도체", score: 12, tone: "weak_positive", toneLabel: "대체 데이터", newsCount: 1, icon: "S" },
        ],
        details: {
          semiconductor: fallbackIndustryDetail,
        },
        dataSource: "seed_fallback",
        providers: ["seed"],
        isFallback: true,
        lastUpdated: "2026-07-13T00:00:00Z",
        warnings: ["Provider unavailable"],
      }),
    }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "산업 영향도" }).click();

  await expect(page.locator(".pipeline-status")).toContainText("fallback active");
  await expect(page.locator(".pipeline-status")).toContainText("대체 데이터 표시 중");
  await expect(page.locator("body")).toContainText("Semiconductor fallback evidence");
  await expect(page.locator("body")).toContainText("Fallback Semiconductor");
  await expect(page.locator("body")).not.toContainText("삼성전자");
});

test("does not substitute another industry's evidence when selected industry has no detail", async ({ page }) => {
  await page.route("**/api/industry-impact", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        industries: [
          { id: "semiconductor", name: "반도체", score: 0, tone: "neutral", toneLabel: "데이터 없음", newsCount: 0, icon: "S" },
          { id: "finance", name: "금융", score: -20, tone: "caution", toneLabel: "주의", newsCount: 1, icon: "F" },
        ],
        details: {
          finance: {
            ...fallbackIndustryDetail,
            industryId: "finance",
            title: "금융 상세",
            topNews: [
              {
                id: "finance-news-1",
                rank: 1,
                title: "Finance-only evidence",
                source: "Stored seed",
                sentimentLabel: "부정",
                impactScore: -0.2,
              },
            ],
          },
        },
        dataSource: "real",
        providers: ["test-provider"],
        isFallback: false,
        lastUpdated: "2026-07-13T00:00:00Z",
        warnings: [],
      }),
    }),
  );

  await page.goto("/");
  await page.getByRole("button", { name: "산업 영향도" }).click();

  await expect(page.getByRole("heading", { name: "선택 산업 근거 데이터가 없습니다" })).toBeVisible();
  await expect(page.locator("body")).not.toContainText("Finance-only evidence");
});

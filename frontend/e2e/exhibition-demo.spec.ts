import { expect, test } from "@playwright/test";

const forbiddenApiPaths = [
  "/api/briefing",
  "/api/news-guard",
  "/api/industry-impact",
  "/api/portfolio",
  "/api/mypage",
  "/api/settings",
  "/api/email-subscription",
  "/api/auth/me",
];

test("renders complete exhibition demo screens without API requests", async ({ page }) => {
  const apiRequests: string[] = [];

  page.on("request", (request) => {
    const url = new URL(request.url());
    if (forbiddenApiPaths.some((path) => url.pathname.startsWith(path))) {
      apiRequests.push(`${request.method()} ${url.pathname}`);
    }
  });

  await page.goto("/");

  await expect(page.locator(".demo-status-banner").first()).toContainText("전시용 데모 데이터");
  await expect(page.locator("body")).toContainText("실시간 API가 아닌 미리 구성한 샘플 데이터");
  await expect(page.locator("body")).toContainText("투자 추천이나 매수·매도 지시가 아닌");
  await expect(page.locator("body")).toContainText("AI 반도체 수출 규제");
  await expect(page.locator("body")).toContainText("YELLOW");

  await page.locator(".main-nav button").nth(1).click();
  await expect(page.locator(".demo-status-banner")).toContainText("전시용 데모 데이터");
  await expect(page.locator(".news-guard-kpi").first()).toContainText("8");
  await expect(page.locator(".news-guard-card")).toHaveCount(8);
  await expect(page.locator("body")).toContainText("Exhibition Demo");
  await expect(page.locator("body")).toContainText("전시용 샘플");
  await expect(page.locator("body")).toContainText("전시 데이터 상태");

  await page.locator(".news-filter-tabs button").nth(1).click();
  await expect(page.locator(".news-guard-card")).toHaveCount(3);
  await page.locator(".news-filter-tabs button").nth(2).click();
  await expect(page.locator(".news-guard-card")).toHaveCount(3);
  await page.locator(".news-filter-tabs button").nth(3).click();
  await expect(page.locator(".news-guard-card")).toHaveCount(2);
  await page.locator(".news-filter-tabs button").nth(0).click();
  await expect(page.locator(".news-guard-card")).toHaveCount(8);

  await page.locator(".main-nav button").nth(2).click();
  await expect(page.locator(".demo-status-banner")).toContainText("전시용 데모 데이터");
  await expect(page.locator("body")).toContainText("AI");
  await expect(page.locator("body")).toContainText("Semiconductor");
  await expect(page.locator("body")).toContainText("Robotics");
  await expect(page.locator("body")).toContainText("Policy");
  await expect(page.locator("body")).toContainText("NVDA");

  await page.locator(".main-nav button").nth(3).click();
  await expect(page.locator(".demo-status-banner")).toContainText("전시용 데모 데이터");
  await expect(page.locator("body")).toContainText("NVIDIA");
  await expect(page.locator("body")).toContainText("AMD");
  await expect(page.locator("body")).toContainText("005930.KS");
  await expect(page.locator("body")).toContainText("000660.KS");
  await expect(page.locator("body")).toContainText("실제 계좌 데이터가 아닌 전시용 예시");

  await page.locator(".user-menu").click();
  await expect(page.locator(".demo-status-banner")).toContainText("전시용 데모 데이터");
  await expect(page.locator("body")).toContainText("FinLightAI 데모 사용자");
  await expect(page.locator("body")).toContainText("demo@finlightai.local");
  await expect(page.locator("body")).toContainText("frontend-only demo user");

  await page.locator(".main-nav button").nth(4).click();
  await expect(page.locator(".demo-status-banner")).toContainText("전시용 데모 데이터");
  await page.getByRole("button", { name: /YELLOW.*알림|YELLOW.*signal/i }).click();
  await page.getByRole("button", { name: /저장|Save/i }).click();
  await expect(page.locator("body")).toContainText("브라우저에 저장");

  const storedSettings = await page.evaluate(() => window.localStorage.getItem("finlight_exhibition_demo_settings"));
  expect(storedSettings).toContain("yellow-signal");

  await expect(page.locator("body")).not.toContainText("UNAVAILABLE");
  await expect(page.locator("body")).not.toContainText("API 연결 실패");
  await expect(page.locator("body")).not.toContainText("Unexpected token");
  await expect(page.locator("body")).not.toContainText("providers: not connected");
  await expect(page.locator("body")).not.toContainText("mock data is not displayed as live data");
  await expect(page.locator("body")).not.toContainText("다시 시도");
  await expect(page.locator("body")).not.toContainText("카카오");
  await expect(page.locator("body")).not.toContainText("n8n");
  await expect(page.locator("body")).not.toContainText("챗봇");
  expect(apiRequests).toEqual([]);
});

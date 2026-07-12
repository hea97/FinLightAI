import { expect, test } from "@playwright/test";

test("renders exhibition demo data across the core screens", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator(".pipeline-status").first()).toContainText("exhibition_demo");
  await expect(page.locator(".pipeline-status").first()).toContainText("전시용 데모");
  await expect(page.locator("body")).toContainText("실시간 API가 아닌 미리 구성한 샘플 데이터");
  await expect(page.locator("body")).toContainText("투자 추천이나 매수/매도 지시가 아닌");
  await expect(page.locator("body")).toContainText("AI 반도체 수출 규제");

  await page.getByRole("button", { name: /뉴스|가드|News/i }).click();
  await expect(page.locator("body")).toContainText("전시 샘플: 한국 AI 반도체 수출 규제");
  await expect(page.locator("body")).toContainText("Exhibition Demo");
  await expect(page.locator("body")).toContainText("출처가 확인되지 않은 인수설");

  await page.getByRole("button", { name: /산업|영향/i }).click();
  await expect(page.locator("body")).toContainText("Semiconductor");
  await expect(page.locator("body")).toContainText("Robotics");
  await expect(page.locator("body")).toContainText("Policy");

  await page.getByRole("button", { name: /포트|Portfolio/i }).click();
  await expect(page.locator("body")).toContainText("NVIDIA");
  await expect(page.locator("body")).toContainText("005930.KS");
  await expect(page.locator("body")).toContainText("실제 계좌 데이터가 아닌 전시용 예시");

  await page.getByRole("button", { name: /FinLightAI 데모 사용자|Demo login/i }).click();
  await expect(page.locator("body")).toContainText("demo@finlightai.local");
  await expect(page.locator("body")).toContainText("frontend-only demo user");

  await page.locator(".main-nav").getByRole("button", { name: /설정/i }).click();
  await page.getByRole("button", { name: /YELLOW 즉시 알림/i }).click();
  await page.getByRole("button", { name: /저장|Save/i }).click();
  await expect(page.locator("body")).toContainText("브라우저에 저장");

  const storedSettings = await page.evaluate(() => window.localStorage.getItem("finlight_exhibition_demo_settings"));
  expect(storedSettings).toContain("yellow-signal");
  await expect(page.locator("body")).not.toContainText("n8n");
});

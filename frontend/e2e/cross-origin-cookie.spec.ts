import { expect, test } from "@playwright/test";

test("cross-origin credential request stores and sends the HttpOnly session cookie", async ({ page, context }) => {
  await page.goto("/");

  const sessionResponsePromise = page.waitForResponse("http://localhost:8011/api/auth/e2e/session");
  const result = await page.evaluate(async () => {
    const sessionResponse = await fetch("http://localhost:8011/api/auth/e2e/session", {
      method: "POST",
      credentials: "include",
    });
    const meResponse = await fetch("http://localhost:8011/api/auth/me", {
      credentials: "include",
    });
    return {
      sessionStatus: sessionResponse.status,
      me: await meResponse.json(),
      visibleCookies: document.cookie,
    };
  });
  const sessionResponse = await sessionResponsePromise;

  expect(result.sessionStatus).toBe(204);
  expect((await sessionResponse.allHeaders())["access-control-allow-credentials"]).toBe("true");
  expect(result.me).toMatchObject({ authenticated: true, user: { id: "e2e-user" } });
  expect(result.visibleCookies).not.toContain("finlight_session");
  expect((await context.cookies()).some((cookie) => cookie.name === "finlight_session" && cookie.httpOnly)).toBe(true);
});

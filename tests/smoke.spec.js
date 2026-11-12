import { test, expect } from "@playwright/test";

test("the page loads without errors", async ({ page }) => {
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  await page.goto("/");
  await expect(page.locator("h1")).toHaveText("hut's mcu helper");
  await expect(page.locator("#mainLane .stop").first()).toBeVisible();
  expect(errors).toEqual([]);
});

test("a shared link opens through the w/ page", async ({ page }) => {
  await page.goto("/w/#m");
  await expect(page.locator("#sheet-t")).toHaveText("This link carries a watched list of 22 titles.");
});

test("the emulator refuses a signed-out write", async ({ request }) => {
  const host = process.env.FIRESTORE_EMULATOR_HOST;
  test.skip(!host, "Runs only under npm run test:all");
  const url = `http://${host}/v1/projects/demo-mcu/databases/(default)/documents/users?documentId=someone`;
  expect((await request.post(url, { data: { fields: {} } })).status()).toBe(403);
  // The emulator's admin token skips the rules, which proves the 403 came from the rules and not a wrong address.
  expect((await request.post(url.replace("someone", "admin-check"), { data: { fields: {} }, headers: { authorization: "Bearer owner" } })).status()).toBe(200);
});

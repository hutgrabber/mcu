import { test, expect, open, stored, DATA, keyOf } from "./helpers.js";

const E = DATA.entries, PHASE1 = DATA.main.filter(id => E[id].phase === 1).map(id => keyOf(E[id]));

test("Mark as watched on the up-next card, then undo", async ({ page }) => {
  await open(page);
  const first = await page.locator("#next-t").textContent();
  await page.click("#next-done");
  expect(await stored(page)).toHaveLength(1);
  await expect(page.locator("#next-t")).not.toHaveText(first);
  await page.locator("#toast button").click();
  expect(await stored(page)).toEqual([]);
  await expect(page.locator("#next-t")).toHaveText(first);
});

test("Undo reverses only its own change, keeping later ticks and earlier ones", async ({ page }) => {
  await open(page, "/", { watched: ["ironman|2008"] });
  await page.keyboard.press("w");
  await page.click("#b-endgame");
  const afterBulk = await stored(page);
  expect(afterBulk).toHaveLength(22);
  const shows = page.locator(".b-grp").nth(6).locator(".b-row");
  await shows.nth(1).click(); await shows.nth(2).click();
  const showKeys = (await stored(page)).filter(k => !afterBulk.includes(k));
  expect(showKeys).toHaveLength(2);
  await page.locator("#toast button").click();
  expect((await stored(page)).sort()).toEqual(["ironman|2008", ...showKeys].sort());
});

test("Clear all asks twice, then can be undone", async ({ page }) => {
  await open(page, "/", { watched: PHASE1 });
  await page.keyboard.press("w");
  await page.click("#b-none");
  expect(await stored(page)).toHaveLength(PHASE1.length);
  await page.click("#b-none");
  expect(await stored(page)).toEqual([]);
  await page.locator("#toast button").click();
  expect((await stored(page)).sort()).toEqual([...PHASE1].sort());
});

test("a list that was already complete doesn't celebrate when the page opens", async ({ page }) => {
  await open(page, "/", { watched: PHASE1 });
  await page.waitForTimeout(1500);
  await expect(page.locator("#cheer")).not.toHaveClass(/show/);
});

test("finishing a Phase celebrates", async ({ page }) => {
  await open(page, "/", { watched: PHASE1.filter(k => k !== "theavengers|2012") });
  await page.keyboard.press("w");
  await page.locator(".b-grp").nth(0).locator(".b-row", { hasText: "The Avengers" }).click();
  await expect(page.locator("#cheer")).toHaveClass(/show/);
  await expect(page.locator("#cheer")).toContainText("Phase 1 complete");
});

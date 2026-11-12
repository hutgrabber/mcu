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

test("a tap straight after the page opens still counts", async ({ browser, baseURL }) => {
  // Holding the page's own timer at 100 milliseconds makes this tap land in its first half-second every time.
  const page = await browser.newPage({ baseURL });
  await page.addInitScript(() => { performance.now = () => 100; });
  await open(page);
  await page.click("#next-done");
  expect(await stored(page)).toHaveLength(1);
  await page.close();
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
  await page.addInitScript(() => addEventListener("DOMContentLoaded", () => {
    const c = document.querySelector("#cheer"); window.cheered = c.classList.contains("show");
    new MutationObserver(() => { if (c.classList.contains("show")) window.cheered = true; }).observe(c, { attributes: true });
  }, { capture: true }));
  await open(page, "/", { watched: PHASE1 });
  await page.waitForTimeout(1500);
  expect(await page.evaluate(() => window.cheered), "the celebration showed").toBe(false);
});

test("finishing a Phase celebrates", async ({ page }) => {
  await open(page, "/", { watched: PHASE1.filter(k => k !== "theavengers|2012") });
  await page.keyboard.press("w");
  await page.locator(".b-grp").nth(0).locator(".b-row", { hasText: "The Avengers" }).click();
  await expect(page.locator("#cheer")).toHaveClass(/show/);
  await expect(page.locator("#cheer")).toContainText("Phase 1 complete");
});

test.describe("switching theme", () => {
  const theme = page => page.evaluate(() => [document.documentElement.dataset.theme, localStorage.getItem("hut-mcu-helper-theme")]);

  test("changes the theme, saves it, and tidies up after the animation", async ({ page }) => {
    await open(page);
    const [start] = await theme(page), other = start === "dark" ? "light" : "dark";
    await page.click("#theme");
    await expect.poll(() => theme(page)).toEqual([other, other]);
    await expect(page.locator(".splash")).toHaveCount(0);
    await expect(page.locator("html")).not.toHaveClass(/\bvt\b/);
  });

  test("a second press during the animation doesn't undo the first", async ({ page }) => {
    await open(page);
    const [start] = await theme(page), other = start === "dark" ? "light" : "dark";
    await page.click("#theme"); await page.click("#theme");
    await page.waitForTimeout(900);
    expect(await theme(page)).toEqual([other, other]);
  });

  test("with reduced motion it switches straight away", async ({ browser, baseURL }) => {
    const page = await browser.newPage({ baseURL, reducedMotion: "reduce" });
    await open(page);
    const [start] = await theme(page);
    await page.click("#theme");
    expect((await theme(page))[0]).not.toBe(start);
    await expect(page.locator(".splash")).toHaveCount(0);
    await page.close();
  });
});

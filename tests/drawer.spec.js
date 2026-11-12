import { test, expect, open } from "./helpers.js";

const drawer = page => page.locator("#drawer");
const hash = page => page.evaluate(() => location.hash);

test("Back closes a story, Forward reopens it, Escape closes it", async ({ page }) => {
  await open(page);
  await page.locator("#mainLane .card").nth(2).click();
  await expect(drawer(page)).toHaveClass(/open/);
  expect(await hash(page)).toMatch(/^#t=/);
  const depth = await page.evaluate(() => history.length);

  const first = await page.locator("#d-title").textContent(), firstHash = await hash(page);
  for (let i = 0; i < 3; i++) await page.keyboard.press("ArrowRight");
  await expect(page.locator("#d-title")).not.toHaveText(first);
  expect(await hash(page)).not.toBe(firstHash);
  expect(await page.evaluate(() => history.length), "stepping through stories adds no history").toBe(depth);

  await page.goBack();
  await expect(drawer(page)).not.toHaveClass(/open/);
  expect(await hash(page)).toBe("");

  await page.goForward();
  await expect(drawer(page)).toHaveClass(/open/);

  await page.keyboard.press("Escape");
  await expect(drawer(page)).not.toHaveClass(/open/);
  await expect.poll(() => hash(page)).toBe("");
});

test("a link to a story far down the page opens it", async ({ page }) => {
  await open(page, "/#t=helstrom-2020");
  await expect(drawer(page)).toHaveClass(/open/);
  await expect(page.locator("#d-title")).toHaveText("Helstrom");
});

test("a link to a story that doesn't exist is ignored quietly", async ({ page }) => {
  await open(page, "/#t=nope");
  await expect.poll(() => hash(page)).toBe("");
  await expect(drawer(page)).not.toHaveClass(/open/);
});

test("marking earlier stops from a story can be undone", async ({ page }) => {
  await open(page);
  await page.locator("#mainLane .card").nth(6).click();
  await page.click("#d-upto");
  await expect(page.locator("#d-upto")).toHaveCount(0);
  await page.locator("#toast button").click();
  await expect(page.locator("#d-upto")).toHaveCount(1);
});

test("search: Enter jumps, Escape clears", async ({ page }) => {
  await open(page);
  await page.click("#q");
  await page.keyboard.type("loki");
  await expect(page.locator(".stop.dim").first()).toBeAttached();
  await page.keyboard.press("Enter");
  await page.keyboard.press("Escape");
  await expect(page.locator(".stop.dim")).toHaveCount(0);
  await expect(page.locator("#q")).toHaveValue("");
});

test("switching what the main line shows doesn't replay the tick animation", async ({ page }) => {
  await open(page, "/", { watched: ["ironman|2008", "thor|2011"] });
  await page.click("#mode [data-mode=all]");
  expect(await page.locator(".stop.just").count()).toBe(0);
});

test("reduced motion shows every line straight away", async ({ browser, baseURL }) => {
  const page = await browser.newPage({ baseURL, reducedMotion: "reduce" });
  await open(page, "/", { all: true });
  await expect(page.locator(".lane.waiting")).toHaveCount(0);
  await page.close();
});

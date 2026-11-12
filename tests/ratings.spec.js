import { test, expect, open, DATA, CHARTS, fixture, withRatings as swapIn } from "./helpers.js";
const withRatings = (page, ratings = SAMPLE) => swapIn(page, ratings);
import { test as plain } from "@playwright/test";
import { readFileSync } from "node:fs";

const read = p => JSON.parse(readFileSync(new URL(p, import.meta.url)));
const RATINGS = read("../src/ratings.json"), IMDB = read("../src/imdb.json"), SAMPLE = fixture("ratings-sample");
const E = DATA.entries;

/* ---------- the saved data ---------- */
plain("every title has an IMDb id, and seasons say which season", () => {
  expect(Object.keys(IMDB).map(Number).sort((a, b) => a - b)).toEqual([...CHARTS.share].sort((a, b) => a - b));
  for (const [id, v] of Object.entries(IMDB)){
    expect(v.imdb, E[id].title).toMatch(/^tt\d{7,9}$/);
    expect(v.title, `src/imdb.json ${id} names its title`).toBe(E[id].title);
    if (/, Season \d+$/.test(E[id].title)) expect(v.season, E[id].title).toBe(+E[id].title.match(/(\d+)$/)[1]);
    else expect(v.season, E[id].title).toBeUndefined();
  }
  const whole = Object.values(IMDB).filter(v => !v.season).map(v => v.imdb);
  expect(new Set(whole).size, "two titles share an IMDb id").toBe(whole.length);
});

plain("saved ratings have the right shape and belong to released titles", () => {
  expect(RATINGS.asOf === null || /^\d{4}-\d{2}-\d{2}$/.test(RATINGS.asOf)).toBe(true);
  for (const [id, r] of Object.entries(RATINGS.titles)){
    const e = E[id];
    expect(CHARTS.share, `${id} is one of the titles`).toContain(+id);
    expect(e.upcoming, `${e.title} isn't out yet`).toBe(false);
    for (const k of Object.keys(r)) expect(["imdb", "votes", "rt", "eps"], `${e.title}: ${k}`).toContain(k);
    if ("imdb" in r) expect(r.imdb >= 1 && r.imdb <= 10 && Math.round(r.imdb * 10) === r.imdb * 10, `${e.title}: imdb ${r.imdb}`).toBe(true);
    if ("votes" in r) expect(Number.isInteger(r.votes) && r.votes > 0, `${e.title}: votes`).toBe(true);
    if ("rt" in r) expect(Number.isInteger(r.rt) && r.rt >= 0 && r.rt <= 100, `${e.title}: rt`).toBe(true);
    if ("eps" in r) expect(Number.isInteger(r.eps) && r.eps > 0 && !("rt" in r), `${e.title}: a season has episodes and no Tomatometer`).toBe(true);
  }
});

/* ---------- the page, with a known set of ratings swapped in ---------- */
const card = (page, title) => page.locator("#mainLane .card").filter({ has: page.locator(".t", { hasText: new RegExp("^" + title + "$") }) }).first();

test("the stars are gone", async ({ page }) => {
  await withRatings(page);
  await open(page, "/", { all: true });
  await expect(page.locator(".stars")).toHaveCount(0);
  expect(await page.evaluate(() => document.body.innerText.includes("★"))).toBe(false);
});

test("a card shows its IMDb rating and Tomatometer", async ({ page }) => {
  await withRatings(page);
  await open(page);
  const c = card(page, "Iron Man");
  await expect(c.locator(".sc-i")).toHaveText("IMDb7.9");
  await expect(c.locator(".sc-r")).toHaveText("94%");
  await expect(c.locator(".sc-r")).toHaveClass(/fresh/);
  await expect(c).toHaveAttribute("aria-label", /IMDb 7\.9 out of 10, Tomatometer 94%/);
  await expect(card(page, "Ant-Man and the Wasp: Quantumania").locator(".sc-r")).toHaveClass(/rotten/);
});

test("the story shows both scores, filled in once the animation ends", async ({ page }) => {
  await withRatings(page);
  await open(page);
  await card(page, "Iron Man").click();
  const box = page.locator("#d-body .d-rate");
  await expect(box.locator(".rate.imdb b")).toHaveText("7.9");
  await expect(box.locator(".rate.imdb p")).toContainText("1.1M ratings");
  await expect(box.locator(".rate.tomato b")).toHaveText("94");
  await expect(box.locator(".rate.tomato")).toContainText("Fresh with critics");
  await expect(page.locator("#d-body .d-rate-src")).toContainText("November 12, 2026");
});

test("a season shows its episodes' average, and an unreleased film says when ratings come", async ({ page }) => {
  await withRatings(page);
  await open(page, "/#t=lokiseason1-2021");
  await expect(page.locator("#d-body .rate.imdb p")).toContainText("Average of 6 episodes");
  await expect(page.locator("#d-body .rate.none")).toBeVisible();
  await page.keyboard.press("Escape");
  await open(page, "/#t=avengersdoomsday-2026");
  await expect(page.locator("#d-body .d-rate-none")).toHaveText("Ratings arrive once it's out.");
});

test("with no ratings saved, nothing about ratings shows", async ({ page }) => {
  await withRatings(page, { asOf: null, source: "OMDb", titles: {} });
  await open(page);
  await expect(page.locator(".sc")).toHaveCount(0);
  await card(page, "Iron Man").click();
  await expect(page.locator("#d-body .d-rate, #d-body .d-rate-none")).toHaveCount(0);
});

test("the ranking orders the films and re-sorts by Tomatometer", async ({ page }) => {
  await withRatings(page);
  await open(page);
  await page.getByRole("button", { name: "How the films were received" }).click();
  const names = () => page.locator("#chart-ratings-main .rk .t").allTextContents();
  await expect.poll(names).toEqual(["Avengers: Endgame", "The Avengers", "Iron Man", "Ant-Man and the Wasp: Quantumania"]);
  await expect(page.locator("#chart-ratings-main .rk .val").first()).toHaveText("8.4");
  await expect.poll(() => page.locator("#chart-ratings-main .rk-bar i").first().evaluate(i => i.getBoundingClientRect().width / i.parentElement.getBoundingClientRect().width)).toBeCloseTo(0.84, 1);
  await page.locator("#chart-ratings-main .rank-by button", { hasText: "Tomatometer" }).click();
  // a tie keeps release order: Iron Man (2008) before Endgame (2019)
  await expect.poll(names).toEqual(["Iron Man", "Avengers: Endgame", "The Avengers", "Ant-Man and the Wasp: Quantumania"]);
  await page.locator("#chart-ratings-main .rk").first().click();
  await expect(page.locator("#d-title")).toHaveText("Iron Man");
});

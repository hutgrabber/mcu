import { test, expect, open, stored, fixture, DATA, keyOf, TODAY } from "./helpers.js";

const MINE = ["ironman|2008", "thor|2011", "theavengers|2012", "deadpool|2016", "logan|2017"];
const [CODE, THEIRS] = Object.entries(fixture("share-links").w).find(([c]) => c !== "m");
/* The comparison only counts titles that are already out */
const out = new Set(DATA.entries.filter(e => !e.upcoming || new Date(e.date + "T00:00:00") <= TODAY).map(keyOf));

test("comparing with a shared list, then adding it, then undoing", async ({ page }) => {
  await open(page, "/#w=" + CODE, { watched: MINE });
  await page.click("#sheet-cmp");
  await expect(page.locator("#compare")).toHaveAttribute("aria-hidden", "false");

  const theirs = THEIRS.filter(k => out.has(k)), both = theirs.filter(k => MINE.includes(k)).length;
  const onlyTheirs = theirs.length - both, onlyMine = MINE.length - both;
  await expect(page.locator("#c-sum")).toHaveText(`You've both seen ${both}. They have ${onlyTheirs} you haven't, and you have ${onlyMine} they haven't.`);
  await expect(page.locator("#cmp")).toBeVisible();

  await page.click("#c-add");
  expect((await stored(page)).sort()).toEqual([...new Set([...MINE, ...THEIRS])].sort());
  await page.locator("#toast button").click();
  expect((await stored(page)).sort()).toEqual([...MINE].sort());

  await page.click("#c-stop");
  await expect(page.locator("#cmp")).toBeHidden();
});

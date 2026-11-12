import { test, expect, open, DATA, keyOf } from "./helpers.js";
import { test as plain } from "@playwright/test";
import { readFileSync } from "node:fs";

const E = DATA.entries, strip = h => h.replace(/<[^>]+>/g, "");
/* ---------- the matching rules, lifted out of the page and run on their own ---------- */
function searchLogic(){
  const src = readFileSync(new URL("../src/template.html", import.meta.url), "utf8");
  const start = src.indexOf("/* search logic: start */"), end = src.indexOf("/* search logic: end */");
  if (start < 0 || end < start) throw new Error("Couldn't find the search logic in src/template.html");
  return new Function(src.slice(start, end) + "; return {normal, typos, searchIndex, searchTitles};")();
}
const { normal, typos, searchIndex, searchTitles } = searchLogic();
const index = searchIndex(E, strip, keyOf);
const top = (q, n = 1) => searchTitles(index, q).slice(0, n).map(r => E[r.id].title);

plain.describe("the matching rules", () => {
  plain("text is compared without case, accents or punctuation", () => {
    expect(normal("Spider-Man: No Way Home")).toBe("spider man no way home");
    expect(normal("Cloak & Dagger")).toBe("cloak and dagger");
    expect(normal("Pokémon")).toBe("pokemon");
  });
  plain("each title appears once, whichever lanes it's in", () => {
    const ids = index.map(r => keyOf(E[r.id]));
    expect(new Set(ids).size).toBe(ids.length);
    expect(index.some(r => E[r.id].alias)).toBe(false);
  });
  plain("the whole title, its start and the start of its words come first", () => {
    expect(top("spider-man")).toEqual(["Spider-Man"]);
    expect(top("endgame")).toEqual(["Avengers: Endgame"]);
    expect(top("guardians vol 3")).toEqual(["Guardians of the Galaxy Vol. 3"]);
    expect(top("winter")[0]).toMatch(/Winter Soldier/);
  });
  plain("initials find a title", () => {
    expect(top("gotg")).toEqual(["Guardians of the Galaxy"]);
    expect(top("nwh")).toEqual(["Spider-Man: No Way Home"]);
    expect(top("aiw")).toEqual(["Avengers: Infinity War"]);
  });
  plain("a small typo still finds it", () => {
    expect(typos("spidreman", "spiderman", 2)).toBe(1);
    expect(top("ragnarock")).toEqual(["Thor: Ragnarok"]);
    expect(top("wakanda forver")).toEqual(["Black Panther: Wakanda Forever"]);
  });
  plain("a year or a Phase lists its titles", () => {
    const byYear = searchTitles(index, "2019"), years = byYear.filter(r => r.how === "year");
    expect(years.length).toBeGreaterThan(2);
    expect(years.every(r => E[r.id].year === 2019)).toBe(true);
    expect(byYear.slice(0, years.length), "titles from 2019 come before stories that mention it").toEqual(years);
    const byPhase = searchTitles(index, "phase 4"), phases = byPhase.filter(r => r.how === "phase");
    expect(phases.length).toBeGreaterThan(5);
    expect(phases.every(r => E[r.id].phase === 4)).toBe(true);
    expect(byPhase.slice(0, phases.length)).toEqual(phases);
    expect(searchTitles(index, "p4").filter(r => r.how === "phase")).toEqual(phases);
  });
  plain("a character or actor is found in the stories, after any title matches", () => {
    const r = searchTitles(index, "thanos");
    expect(r.length).toBeGreaterThan(3);
    expect(r.every(x => x.how === "text")).toBe(true);
    expect(searchTitles(index, "loki")[0].how).toBe("title");
  });
  plain("nothing typed, nothing found; nonsense finds nothing", () => {
    expect(searchTitles(index, "  ")).toEqual([]);
    expect(searchTitles(index, "zzqxj")).toEqual([]);
  });
});

/* ---------- in the page ---------- */
const box = page => page.locator("#q"), list = page => page.locator("#sugg");
const options = page => page.locator("#sugg .sg");

test("suggestions appear as you type, with the match marked", async ({ page }) => {
  await open(page);
  await box(page).click();
  await page.keyboard.type("spider");
  await expect(list(page)).toHaveClass(/open/);
  await expect(box(page)).toHaveAttribute("aria-expanded", "true");
  await expect(options(page)).toHaveCount(8);
  await expect(options(page).first()).toHaveAttribute("aria-selected", "true");
  await expect(options(page).first().locator("mark").first()).toHaveText("Spider");
  await expect(page.locator("#sugg .sg-foot")).toContainText("matches, best 8 shown");
  await page.keyboard.type(" home");
  await expect(options(page).first().locator(".sg-t")).toHaveText("Spider-Man: Homecoming");
});

test("arrow keys choose, and Enter finds the title on the line", async ({ page }) => {
  await open(page);
  await box(page).click();
  await page.keyboard.type("iron man");
  await page.keyboard.press("ArrowDown");
  await expect(options(page).nth(1)).toHaveAttribute("aria-selected", "true");
  await expect(box(page)).toHaveAttribute("aria-activedescendant", "sg-1");
  const title = await options(page).nth(1).locator(".sg-t").textContent();
  await page.keyboard.press("Enter");
  await expect(list(page)).not.toHaveClass(/open/);
  const found = page.locator(".stop.found");
  await expect(found).toHaveCount(1);
  await expect(found.locator(".card .t")).toHaveText(title);
  await expect(found.locator(".card")).toBeFocused();
  await expect(page.locator("#mainLane .stop.dim").first()).toBeAttached();   // the line still shows what matched
});

test("a story match shows the text it matched", async ({ page }) => {
  await open(page);
  await box(page).click();
  await page.keyboard.type("thanos");
  await expect(options(page).first().locator(".sg-s mark")).toHaveText(/thanos/i);
});

test("tapping a suggestion finds it, even a show that's not on the main line yet", async ({ page }) => {
  await open(page);
  await box(page).click();
  await page.keyboard.type("echo");
  await options(page).filter({ hasText: "Echo" }).first().click();
  await expect(page.locator(".stop.found .card .t")).toHaveText("Echo");
});

test("Escape closes the list first, then clears the search", async ({ page }) => {
  await open(page);
  await box(page).click();
  await page.keyboard.type("loki");
  await page.keyboard.press("Escape");
  await expect(list(page)).not.toHaveClass(/open/);
  await expect(box(page)).toHaveValue("loki");
  await page.keyboard.press("Escape");
  await expect(box(page)).toHaveValue("");
  await expect(page.locator(".stop.dim")).toHaveCount(0);
});

test("no match says what to try", async ({ page }) => {
  await open(page);
  await box(page).click();
  await page.keyboard.type("zzqxj");
  await expect(page.locator("#sugg .sg-none")).toContainText('No titles match "zzqxj"');
});

test.describe("on a phone", () => {
  test.use({ viewport: { width: 375, height: 667 }, isMobile: true, hasTouch: true });
  test("the list spans the screen under the search box and a tap finds the title", async ({ page }) => {
    await open(page);
    await box(page).tap();
    await page.keyboard.type("thor");
    await expect(list(page)).toHaveClass(/open/);
    const r = await list(page).boundingBox();
    expect(r.x).toBeGreaterThanOrEqual(0);
    expect(r.x + r.width).toBeLessThanOrEqual(375);
    expect(r.width).toBeGreaterThan(300);
    await options(page).first().tap();
    await expect(page.locator(".stop.found .card .t")).toHaveText("Thor");
  });
});

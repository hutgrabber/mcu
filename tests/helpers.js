import { test as base, expect } from "@playwright/test";
import { readFileSync } from "node:fs";

const read = path => JSON.parse(readFileSync(new URL(path, import.meta.url)));
export const DATA = read("../src/data.json");
export const CHARTS = read("../src/charts.json");
export const fixture = name => read(`fixtures/${name}.json`);
export const keyOf = e => (e.title + "|" + e.year).toLowerCase().replace(/[^a-z0-9|]/g, "");

export const STORE = "hut-mcu-helper-watched";
/* The content is current as of November 10, 2026. Pinning the date keeps "Coming up" and the countdown the same in every run. */
export const TODAY = new Date("2026-11-11T12:00:00");

/* Every page fails its test if it throws or logs an error. */
export const test = base.extend({
  page: async ({ page }, use) => {
    const errors = watchErrors(page);
    await page.clock.setFixedTime(TODAY);
    await use(page);
    expect(errors, "errors in the page").toEqual([]);
  },
});
export { expect };

export function watchErrors(page){
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", m => { if (m.type() === "error") errors.push(m.text()); });
  return errors;
}

/* Opens the page, optionally with a watched list already saved. The page script runs before the load event, so it has drawn by then.
   all: also wait for the universes the page fills in while idle. */
export async function open(page, path = "/", { watched, all = false } = {}){
  if (watched) await page.addInitScript(([k, v]) => {
    if (!sessionStorage.getItem("seeded")){ localStorage.setItem(k, JSON.stringify(v)); sessionStorage.setItem("seeded", "1"); }
  }, [STORE, watched]);
  await page.goto(path);
  if (all) for (const sec of DATA.sections) await expect(page.locator(`#${sec.id} .lane`)).toHaveCount(sec.lanes.length);
}

/* The share-code functions, lifted out of the page source so they can be tested on their own. */
export function shareCodec(){
  const src = readFileSync(new URL("../src/template.html", import.meta.url), "utf8");
  const start = src.indexOf("const A62 = "), end = src.indexOf("/* The short /w/ page");
  if (start < 0 || end < start) throw new Error("Couldn't find the share-code functions in src/template.html");
  const watched = new Set();
  const fns = new Function("ORDER", "E", "keyOf", "watched", src.slice(start, end) + "; return {encodeList, decodeList};")(CHARTS.share, DATA.entries, keyOf, watched);
  return { ...fns, watched };
}

/* Run in a page: notes whether the celebration ever shows from now on, since it hides itself again after a few seconds */
export function watchCheer(){
  const c = document.querySelector("#cheer");
  window.cheered = c.classList.contains("show");
  new MutationObserver(() => { if (c.classList.contains("show")) window.cheered = true; }).observe(c, { attributes: true });
}

export const stored = page => page.evaluate(k => JSON.parse(localStorage.getItem(k) || "[]"), STORE);

/* Swaps a known set of ratings into the page, so tests don't depend on the real ones */
export async function withRatings(page, ratings){
  await page.route(url => url.pathname === "/" || url.pathname === "/index.html", async route => {
    const res = await route.fetch(), html = await res.text();
    await route.fulfill({ response: res, body: html.replace(/const RATINGS = \{.*?\};/, "const RATINGS = " + JSON.stringify(ratings) + ";") });
  });
}
/* The widest ratings possible on every released title, for layout checks */
export function fullRatings(){
  const titles = {};
  for (const id of CHARTS.share){ const e = DATA.entries[id]; if (!e.upcoming && e.date <= TODAY.toISOString().slice(0, 10)) titles[id] = /, Season \d+$/.test(e.title) ? {imdb: 10, eps: 12} : {imdb: 10, votes: 2500000, rt: 100}; }
  return {asOf: "2026-11-12", source: "OMDb", titles};
}


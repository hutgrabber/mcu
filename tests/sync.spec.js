// Signing in and syncing across devices, against the Firebase emulator. Runs only under npm run test:all.
// Each test uses its own pretend Google account, and each "device" is a separate browser profile.
import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { DATA, keyOf, watchErrors, watchCheer, STORE } from "./helpers.js";

const EMULATOR = process.env.FIRESTORE_EMULATOR_HOST;
const E = DATA.entries, PHASE1 = DATA.main.filter(id => E[id].phase === 1).map(id => keyOf(E[id]));

/* ---------- the merge rules, lifted out of the page and run on their own ---------- */
function syncLogic(){
  const src = readFileSync(new URL("../src/template.html", import.meta.url), "utf8");
  const start = src.indexOf("/* sync logic: start */"), end = src.indexOf("/* sync logic: end */");
  if (start < 0 || end < start) throw new Error("Couldn't find the sync logic in src/template.html");
  return new Function(src.slice(start, end) + "; return {cleanEntries, mergeEntries, changesBetween, firstMerge, onIds};")();
}

test.describe("the merge rules", () => {
  const { cleanEntries, mergeEntries, changesBetween, firstMerge, onIds } = syncLogic();

  test("the later change to a title wins, whichever side it's on", () => {
    const a = { 1: { on: true, at: 10 }, 2: { on: false, at: 30 } }, b = { 1: { on: false, at: 20 }, 2: { on: true, at: 25 }, 3: { on: true, at: 5 } };
    expect(mergeEntries(a, b)).toEqual({ 1: { on: false, at: 20 }, 2: { on: false, at: 30 }, 3: { on: true, at: 5 } });
    expect(mergeEntries(b, a)).toEqual(mergeEntries(a, b));
  });

  test("a tie keeps the title watched", () => {
    expect(mergeEntries({ 1: { on: false, at: 10 } }, { 1: { on: true, at: 10 } })).toEqual({ 1: { on: true, at: 10 } });
    expect(mergeEntries({ 1: { on: true, at: 10 } }, { 1: { on: false, at: 10 } })).toEqual({ 1: { on: true, at: 10 } });
  });

  test("entries the page can't read, or for titles it doesn't know, are dropped", () => {
    const known = new Map([["1", "a"], ["2", "b"], ["3", "c"], ["4", "d"]]);
    expect(cleanEntries({ 1: { on: true, at: 1 }, 2: { on: "yes", at: 1 }, 3: { on: true }, 4: null, 99: { on: true, at: 1 } }, known)).toEqual({ 1: { on: true, at: 1 } });
    expect(cleanEntries("junk", known)).toEqual({});
    expect(cleanEntries(undefined, known)).toEqual({});
  });

  test("a change to the list becomes one entry per title that changed", () => {
    expect(changesBetween(["1", "2"], ["2", "3"], 50)).toEqual({ 3: { on: true, at: 50 }, 1: { on: false, at: 50 } });
    expect(changesBetween(["1"], ["1"], 50)).toEqual({});
  });

  test("the first sign-in keeps everything watched on either side", () => {
    const cloud = { 1: { on: true, at: 5 }, 2: { on: false, at: 5 } };
    const { entries, added } = firstMerge(cloud, ["2", "3"], 100);
    expect(onIds(entries).sort()).toEqual(["1", "2", "3"]);
    expect(Object.keys(added).sort()).toEqual(["2", "3"]);
  });

  test("the first sign-in still wins against an account clock that runs ahead", () => {
    const { entries } = firstMerge({ 2: { on: false, at: 1000 } }, ["2"], 100);
    expect(entries[2]).toEqual({ on: true, at: 1001 });
  });
});

/* ---------- the real thing: two browsers and the emulator ---------- */
test.describe("syncing", () => {
  test.skip(!EMULATOR, "Runs only under npm run test:all");

  let n = 0;
  const account = () => `t${process.pid}-${++n}-${Math.random().toString(36).slice(2, 7)}@example.com`;
  const pages = [];
  async function device(browser, baseURL, { watched, allow = [] } = {}){
    const page = await browser.newPage({ baseURL });
    page.errors = watchErrors(page); page.allow = allow; pages.push(page);
    if (watched) await page.addInitScript(([k, v]) => { if (!sessionStorage.getItem("seeded")){ localStorage.setItem(k, JSON.stringify(v)); sessionStorage.setItem("seeded", "1"); } }, [STORE, watched]);
    await page.goto("/");
    return page;
  }
  test.afterEach(async () => {
    for (const page of pages.splice(0)){
      expect(page.errors.filter(e => !page.allow.some(a => e.includes(a))), "errors in the page").toEqual([]);
      await page.close();
    }
  });

  async function signIn(page, email){
    await page.click("#more");
    const [popup] = await Promise.all([page.waitForEvent("popup"), page.click("#m-sync")]);
    await popup.waitForLoadState("networkidle");
    const existing = popup.locator("li", { hasText: email });
    if (await existing.count()) await existing.click();
    else {
      await popup.getByRole("button", { name: "Add new account" }).click();
      await popup.fill("#email-input", email);
      await popup.fill("#display-name-input", email.split("@")[0]);
      await popup.click("#sign-in");
    }
    await expect(page.locator("#m-who")).toHaveText("Syncing as " + email);
    await synced(page);
  }
  /* Everything this browser changed has reached the account */
  const synced = page => page.waitForFunction(() => {
    const s = JSON.parse(localStorage.getItem("hut-mcu-helper-sync") || "null");
    return s && !Object.keys(s.pending).length && !s.prefsDirty;
  });
  const stored = page => page.evaluate(k => JSON.parse(localStorage.getItem(k) || "[]").sort(), STORE);
  const sorted = list => [...list].sort();
  /* What happens when someone switches back to this tab */
  const comeBack = page => page.evaluate(() => {
    Object.defineProperty(document, "visibilityState", { value: "visible", configurable: true });
    document.dispatchEvent(new Event("visibilitychange"));
  });

  test("the menu shows only the account options that apply", async ({ browser, baseURL }) => {
    const email = account(), page = await device(browser, baseURL);
    const shown = async () => { await page.click("#more"); const out = {}; for (const id of ["m-sync", "m-who", "m-out", "m-delete"]) out[id] = await page.locator("#" + id).isVisible(); await page.keyboard.press("Escape"); await page.mouse.click(5, 300); return out; };
    expect(await shown()).toEqual({ "m-sync": true, "m-who": false, "m-out": false, "m-delete": false });
    await signIn(page, email);
    expect(await shown()).toEqual({ "m-sync": false, "m-who": true, "m-out": true, "m-delete": true });
  });

  test("a tick on one device shows on the other, and so does undoing it", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL), laptop = await device(browser, baseURL);
    await signIn(phone, email); await signIn(laptop, email);
    await phone.click("#next-done");
    await synced(phone);
    await laptop.reload();
    await expect.poll(() => stored(laptop)).toEqual(["ironman|2008"]);
    await phone.locator("#toast button").click();
    await synced(phone);
    await laptop.reload();
    await expect.poll(() => stored(laptop)).toEqual([]);
  });

  test("switching back to a tab brings in changes from the other device", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL), laptop = await device(browser, baseURL);
    await signIn(phone, email); await signIn(laptop, email);
    await phone.click("#next-done");
    await synced(phone);
    await laptop.waitForTimeout(5100);   // the page fetches at most once every five seconds
    await comeBack(laptop);
    await expect.poll(() => stored(laptop)).toEqual(["ironman|2008"]);
  });

  test("the first sign-in on a browser merges both lists and says what it did", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL, { watched: PHASE1 });
    await signIn(phone, email);
    const laptopList = ["lokiseason1|2021", "theavengers|2012"], laptop = await device(browser, baseURL, { watched: laptopList });
    await signIn(laptop, email);
    await expect(laptop.locator("#toast")).toHaveText("Signed in and synced: 5 titles from your account added here, 1 title from this browser added to your account.");
    const both = sorted(new Set([...PHASE1, ...laptopList]));
    expect(await stored(laptop)).toEqual(both);
    await phone.reload();
    await expect.poll(() => stored(phone)).toEqual(both);
  });

  test("ticking a whole group at once is a single write", async ({ browser, baseURL }) => {
    const page = await device(browser, baseURL);
    await signIn(page, account());
    const writes = [];
    page.on("request", r => { if (r.url().includes(":commit")) writes.push(r.url()); });
    await page.keyboard.press("w");
    await page.click("#b-endgame");
    await page.locator(".b-grp").nth(6).locator(".b-g button").click();
    await synced(page);
    expect(writes).toHaveLength(1);
  });

  test("changes from another device don't set off confetti", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL, { watched: PHASE1.slice(1) });
    await signIn(phone, email);
    const laptop = await device(browser, baseURL);
    await signIn(laptop, email);
    await phone.keyboard.press("w");
    await phone.locator(".b-grp").nth(0).locator(".b-row").first().click();
    await expect(phone.locator("#cheer")).toHaveClass(/show/);
    await synced(phone);
    await laptop.waitForTimeout(5100);
    await laptop.evaluate(watchCheer);
    await comeBack(laptop);
    await expect.poll(() => stored(laptop)).toEqual(sorted(PHASE1));
    await laptop.waitForTimeout(500);
    expect(await laptop.evaluate(() => window.cheered), "the celebration showed").toBe(false);
  });

  test("Undo reverses only its own change, even after a change from another device", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL), laptop = await device(browser, baseURL);
    await signIn(phone, email); await signIn(laptop, email);
    await phone.keyboard.press("w");
    await phone.locator(".b-grp").nth(6).locator(".b-row").first().click();
    await synced(phone);
    const show = (await stored(phone))[0];

    await laptop.waitForTimeout(5100);
    await laptop.keyboard.press("w");
    await laptop.click("#b-endgame");
    await comeBack(laptop);
    await expect.poll(() => stored(laptop)).toContain(show);
    await laptop.locator("#toast button").click({ force: true });
    expect(await stored(laptop)).toEqual([show]);
    await synced(laptop);
    await phone.reload();
    await expect.poll(() => stored(phone)).toEqual([show]);
  });

  test("theme, spoiler setting and route follow you to a new browser", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL);
    await signIn(phone, email);
    const start = await phone.evaluate(() => document.documentElement.dataset.theme), other = start === "dark" ? "light" : "dark";
    await phone.click("#theme");
    await phone.click("#spoil");
    await phone.click('#route button[aria-pressed="false"] >> nth=0');
    const route = await phone.locator('#route button[aria-pressed="true"]').textContent();
    await synced(phone);

    const laptop = await device(browser, baseURL);
    await signIn(laptop, email);
    await expect(laptop.locator("html")).toHaveAttribute("data-theme", other);
    await expect(laptop.locator("body")).toHaveClass(/nospoil/);
    await expect(laptop.locator('#route button[aria-pressed="true"]')).toHaveText(route);
    expect(await laptop.evaluate(() => localStorage.getItem("hut-mcu-helper-theme")), "saved for the next visit's first paint").toBe(other);
  });

  test("a reload stays signed in and keeps the list", async ({ browser, baseURL }) => {
    const email = account(), page = await device(browser, baseURL);
    await signIn(page, email);
    await page.click("#next-done");
    await synced(page);
    await page.reload();
    await expect(page.locator("#m-who")).toHaveText("Syncing as " + email);
    expect(await stored(page)).toEqual(["ironman|2008"]);
  });

  test("a change made offline syncs once the connection is back", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL, { allow: ["net::ERR_INTERNET_DISCONNECTED", "RPC_ERROR"] });
    await signIn(phone, email);
    await phone.context().setOffline(true);
    await phone.click("#next-done");
    await expect(phone.locator("#toast")).toContainText("Couldn't sync just now", { timeout: 8000 });
    await phone.context().setOffline(false);
    await synced(phone);
    const laptop = await device(browser, baseURL);
    await signIn(laptop, email);
    expect(await stored(laptop)).toEqual(["ironman|2008"]);
  });

  test("a change made offline doesn't overwrite a later one from another device", async ({ browser, baseURL }) => {
    const email = account(), phone = await device(browser, baseURL, { watched: ["ironman|2008"], allow: ["net::ERR_INTERNET_DISCONNECTED", "RPC_ERROR"] });
    await signIn(phone, email);
    const laptop = await device(browser, baseURL);
    await signIn(laptop, email);

    await phone.context().setOffline(true);
    await phone.keyboard.press("w");
    await phone.locator(".b-grp").nth(0).locator(".b-row").first().click();   // unticks Iron Man, while offline
    await expect(phone.locator("#toast")).toContainText("Couldn't sync just now", { timeout: 8000 });

    await laptop.keyboard.press("w");
    const ironMan = laptop.locator(".b-grp").nth(0).locator(".b-row").first();
    await ironMan.click(); await ironMan.click();                              // unticks it and ticks it again, later
    await synced(laptop);

    await phone.context().setOffline(false);
    await synced(phone);
    await expect.poll(() => stored(phone)).toEqual(["ironman|2008"]);
    await laptop.reload();
    await expect.poll(() => stored(laptop)).toEqual(["ironman|2008"]);
    const tablet = await device(browser, baseURL);   // a fresh browser sees only what the account holds
    await signIn(tablet, email);
    expect(await stored(tablet)).toEqual(["ironman|2008"]);
  });

  test("signing out clears this browser, and signing back in brings the list back", async ({ browser, baseURL }) => {
    const email = account(), page = await device(browser, baseURL);
    await signIn(page, email);
    await page.click("#next-done");
    await page.click("#theme");
    await page.click('#route button[aria-pressed="false"] >> nth=0');
    await page.click("#more");
    await page.click("#m-out");
    await expect(page.locator("#toast")).toContainText("Signed out");
    expect(await stored(page)).toEqual([]);
    expect(await page.evaluate(() => ["hut-mcu-helper-sync", "hut-mcu-helper-theme", "hut-mcu-helper-spoilers", "hut-mcu-helper-route"].map(k => localStorage.getItem(k)))).toEqual([null, null, null, null]);
    await expect(page.locator('#route button[aria-pressed="true"]')).toHaveText("Ready for Doomsday");
    await expect(page.locator("#m-sync")).toBeAttached();
    await expect(page.locator("#m-sync")).not.toHaveAttribute("hidden");
    await signIn(page, email);
    expect(await stored(page)).toEqual(["ironman|2008"]);
  });

  test("Delete my data removes the account, its list and this browser's copy", async ({ browser, baseURL, request }) => {
    const email = account(), page = await device(browser, baseURL);
    await signIn(page, email);
    await page.click("#next-done");
    await synced(page);
    const uid = await page.evaluate(() => JSON.parse(localStorage.getItem("hut-mcu-helper-sync")).uid);
    const docUrl = `http://${EMULATOR}/v1/projects/demo-mcu/databases/(default)/documents/users/${uid}`, admin = { headers: { authorization: "Bearer owner" } };
    expect((await request.get(docUrl, admin)).status()).toBe(200);

    await page.click("#more");
    await page.click("#m-delete");
    await expect(page.locator("#m-delete")).toHaveText("Tap again to delete your account and synced list");
    await page.click("#m-delete");
    await expect(page.locator("#toast")).toContainText("Deleted");
    expect(await stored(page)).toEqual([]);
    expect((await request.get(docUrl, admin)).status(), "the synced list is gone").toBe(404);
    const accounts = await request.post(`http://${process.env.FIREBASE_AUTH_EMULATOR_HOST}/identitytoolkit.googleapis.com/v1/projects/demo-mcu/accounts:lookup`, { ...admin, data: { localId: [uid] } });
    expect((await accounts.json()).users, "the account is gone").toBeUndefined();
  });
});

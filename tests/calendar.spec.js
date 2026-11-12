import { test, expect, open, CHARTS, TODAY, watchErrors } from "./helpers.js";
import { test as plain } from "@playwright/test";
import { readFileSync, readdirSync } from "node:fs";

const slug = t => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const DATED = CHARTS.soon.filter(s => !s.month), FIRST = DATED.find(s => s.date > TODAY.toISOString().slice(0, 10));
const file = s => readFileSync(new URL(`../cal/${slug(s.title)}.ics`, import.meta.url), "utf8");

const UA = {
  iPhone: "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Mobile/15E148 Safari/604.1",
  iPad: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15",
  Mac: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15",
  Android: "Mozilla/5.0 (Linux; Android 16; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Mobile Safari/537.36",
  Chromebook: "Mozilla/5.0 (X11; CrOS x86_64 16000.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
  Windows: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
};

/* ---------- the calendar files ---------- */
plain("every dated release has a calendar file, and nothing else is in cal/", () => {
  expect(readdirSync(new URL("../cal/", import.meta.url)).sort()).toEqual(DATED.map(s => slug(s.title) + ".ics").sort());
});

plain("each file is a valid all-day event on the release date", () => {
  for (const s of DATED){
    const text = file(s), day = s.date.replace(/-/g, "");
    expect(text.endsWith("\r\n"), s.title).toBe(true);
    expect(text.replace(/\r\n/g, "").includes("\n"), `${s.title}: every line ends in CRLF`).toBe(false);
    for (const line of text.split("\r\n")) expect(Buffer.byteLength(line), `${s.title}: line too long: ${line}`).toBeLessThanOrEqual(75);
    const unfolded = text.replace(/\r\n /g, "");
    for (const k of ["BEGIN:VCALENDAR", "BEGIN:VEVENT", "END:VEVENT", "END:VCALENDAR", "METHOD:PUBLISH", "DTSTART;VALUE=DATE:" + day, "UID:" + day + "-" + slug(s.title) + "@mcu.hutlab.dev"])
      expect(unfolded, `${s.title}: ${k}`).toContain(k);
    expect(unfolded).toMatch(new RegExp("SUMMARY:" + s.title.replace(/[.*+?^${}()|[\]\\]/g, "\\$&").replace(/,/g, "\\\\,") + " (opens in cinemas|premieres)"));
  }
});

/* ---------- in the page, on each kind of device ---------- */
async function device(browser, baseURL, name){
  const ctx = await browser.newContext({ baseURL, userAgent: UA[name], hasTouch: name !== "Mac" && name !== "Windows" && name !== "Chromebook", isMobile: name === "iPhone" || name === "Android", viewport: { width: 1024, height: 900 } });
  if (name === "iPad") await ctx.addInitScript(() => Object.defineProperty(Navigator.prototype, "maxTouchPoints", { get: () => 5 }));
  if (name === "Mac") await ctx.addInitScript(() => Object.defineProperty(Navigator.prototype, "maxTouchPoints", { get: () => 0 }));
  await ctx.route("https://calendar.google.com/**", r => r.fulfill({ status: 200, contentType: "text/html", body: "<title>Google Calendar</title>" }));
  const page = await ctx.newPage();
  page.errors = watchErrors(page);
  await page.clock.setFixedTime(TODAY);
  await page.goto("/#soon");
  return page;
}
const button = page => page.locator(`#soon-list .cal[aria-label="Add ${FIRST.title} to your calendar"]`);

for (const name of ["iPhone", "iPad"])
  test(`on an ${name} it opens the calendar file, which iOS shows in Calendar`, async ({ browser, baseURL }) => {
    const page = await device(browser, baseURL, name);
    const opened = page.waitForRequest(r => r.isNavigationRequest() && r.url().endsWith(`/cal/${slug(FIRST.title)}.ics`));
    await button(page).click();
    const req = await opened;
    const res = await (await page.context().request.get(req.url()));
    expect(res.headers()["content-type"]).toContain("text/calendar");
    expect(await res.text()).toBe(file(FIRST));
    expect(page.errors).toEqual([]);
    await page.context().close();
  });

for (const name of ["Android", "Chromebook"])
  test(`on ${name === "Android" ? "an Android phone" : "a Chromebook"} it opens Google Calendar's new-event screen`, async ({ browser, baseURL }) => {
    const page = await device(browser, baseURL, name);
    const [popup] = await Promise.all([page.context().waitForEvent("page"), button(page).click()]);
    const url = new URL(popup.url());
    expect(url.origin + url.pathname).toBe("https://calendar.google.com/calendar/render");
    expect(url.searchParams.get("action")).toBe("TEMPLATE");
    expect(url.searchParams.get("text")).toBe(FIRST.title + " opens in cinemas");
    const d = new Date(FIRST.date + "T00:00:00"); d.setDate(d.getDate() + 1);
    expect(url.searchParams.get("dates")).toBe(FIRST.date.replace(/-/g, "") + "/" + d.toISOString().slice(0, 10).replace(/-/g, ""));
    expect(url.searchParams.get("details")).toContain("Release dates can move.");
    expect(page.errors).toEqual([]);
    await page.context().close();
  });

for (const name of ["Mac", "Windows"])
  test(`on a ${name} computer it downloads the calendar file`, async ({ browser, baseURL }) => {
    const page = await device(browser, baseURL, name);
    const [download] = await Promise.all([page.waitForEvent("download"), button(page).click()]);
    expect(download.suggestedFilename()).toBe(slug(FIRST.title) + ".ics");
    expect(readFileSync(await download.path(), "utf8")).toBe(file(FIRST));
    await expect(page.locator("#toast")).toContainText("downloaded");
    expect(page.errors).toEqual([]);
    await page.context().close();
  });

// Every screen size from phones to wide monitors, in both themes: nothing scrolls sideways and no card is cut off.
import { test, expect, open } from "./helpers.js";

const SIZES = [[320, 568], [375, 667], [390, 844], [844, 390], [768, 1024], [1024, 768], [1440, 900], [1920, 1080]];
const phone = (w, h) => Math.min(w, h) < 768;

for (const [width, height] of SIZES)
  for (const theme of ["dark", "light"])
    test.describe(`${width}×${height} ${theme}`, () => {
      test.use({ viewport: { width, height }, colorScheme: theme, isMobile: phone(width, height), hasTouch: phone(width, height) });

      test("nothing overflows or gets clipped", async ({ page }) => {
        await open(page, "/", { all: true });
        expect(await page.evaluate(() => document.documentElement.dataset.theme)).toBe(theme);
        const sideways = () => page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        expect(await sideways(), "page scrolls sideways").toBe(0);

        await page.evaluate(() => document.querySelectorAll(".chip").forEach(c => c.click()));
        await page.waitForTimeout(800);
        expect(await sideways(), "page scrolls sideways with every chart open").toBe(0);

        for (const mode of ["films", "essential", "all"]){
          await page.click(`#mode [data-mode=${mode}]`);
          const { clipped, checked } = await page.evaluate(() => {
            const out = []; let n = 0;
            document.querySelectorAll(".lane").forEach(lane => {
              const t = lane.querySelector(".track").getBoundingClientRect();
              lane.querySelectorAll(".card").forEach(c => { n++; const r = c.getBoundingClientRect(); if (r.top < t.top - .5 || r.bottom > t.bottom + .5) out.push(c.textContent.trim().slice(0, 40)); });
            });
            return { clipped: out, checked: n };
          });
          expect(checked, "cards found to check").toBeGreaterThan(100);
          expect(clipped, `cards cut off with the main line showing ${mode}`).toEqual([]);
        }
      });
    });

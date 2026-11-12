import { test, expect, open, stored, fixture, shareCodec, CHARTS, DATA, keyOf } from "./helpers.js";
import { test as plain } from "@playwright/test";

const links = fixture("share-links");

/* Adding a shared list to an empty one stores exactly the titles the code carries. */
for (const [kind, codes] of [["w", links.w], ["p", links.p]])
  for (const [code, keys] of Object.entries(codes))
    test(`the #${kind}=${code} link already out there still opens the same ${keys.length} titles`, async ({ page }) => {
      await open(page, `/#${kind}=${code}`);
      await expect(page.locator("#sheet-t")).toHaveText(`This link carries a watched list of ${keys.length} titles.`);
      await page.click("#sheet-yes");
      expect((await stored(page)).sort()).toEqual([...keys].sort());
    });

plain("every list survives a trip through a share code", () => {
  const { encodeList, decodeList, watched } = shareCodec(), keys = CHARTS.share.map(id => keyOf(DATA.entries[id])), problems = [];
  const check = list => {
    watched.clear(); list.forEach(k => watched.add(k));
    const code = encodeList(), back = decodeList(code) || [];
    if (back.length !== watched.size || back.some(k => !watched.has(k))) problems.push(code);
    if (/[-_]$/.test(code)) problems.push(code + " ends in - or _, which chat apps drop from links");
  };
  check(keys); check(keys.slice(0, 22)); check([keys.at(-1)]); check(keys.filter((k, i) => i % 2 === 0));
  for (let r = 0; r < 20000; r++){ const p = Math.random(); check(keys.filter(() => Math.random() < p)); }
  for (let r = 0; r < 5000; r++){
    const list = []; let on = Math.random() < .7;
    for (let i = 0; i < keys.length; on = !on){ const n = 1 + Math.floor(Math.random() * 30); if (on) list.push(...keys.slice(i, i + n)); i += n; }
    check(list);
  }
  expect(problems).toEqual([]);
});

plain("films through Endgame make the one-letter code m", () => {
  const { encodeList, watched } = shareCodec();
  CHARTS.share.slice(0, 22).forEach(id => watched.add(keyOf(DATA.entries[id])));
  expect(encodeList()).toBe("m");
});

test("a shared link clears itself from the address bar", async ({ page }) => {
  await open(page, "/#w=m");
  await expect(page.locator("#sheet")).toHaveClass(/open/);
  expect(await page.evaluate(() => location.hash)).toBe("");
});

test("the w/ page hands its code to the main page", async ({ page }) => {
  await page.goto("/w/#m");
  await expect(page.locator("#sheet-t")).toHaveText("This link carries a watched list of 22 titles.");
});

test("a link that carries no list says so", async ({ page }) => {
  await open(page);
  for (const hash of ["#w=!!", "#w=", "#p=!!"]){
    await page.evaluate(h => { location.hash = h; }, hash);
    await expect(page.locator("#toast"), hash).toContainText("That link doesn't carry a watched list");
    await expect.poll(() => page.evaluate(() => location.hash), hash).toBe("");
  }
});

test("a link pasted into an open tab still offers its list", async ({ page }) => {
  await open(page);
  await page.evaluate(() => { location.hash = "#w=m"; });
  await expect(page.locator("#sheet")).toHaveClass(/open/);
});

test("a list built in the panel opens the same on another device", async ({ page, browser, baseURL }) => {
  await open(page);
  await page.keyboard.press("w");
  await page.click("#b-endgame");
  await page.locator(".b-grp").nth(6).locator(".b-row").nth(2).click();
  await page.locator(".b-grp").nth(10).locator(".b-g button").click();
  await page.click("#b-copy");
  await expect(page.locator("#toast")).toContainText("Link copied");
  const link = new URL(await page.evaluate(() => navigator.clipboard.readText())), sent = await stored(page);
  expect(link.pathname + link.hash).toMatch(/^\/w\/#[\w-]+$/);

  const other = await browser.newPage({ baseURL });
  await other.goto(link.pathname + link.hash);
  await expect(other.locator("#sheet-t")).toHaveText(`This link carries a watched list of ${sent.length} titles.`);
  await other.click("#sheet-yes");
  expect((await stored(other)).sort()).toEqual([...sent].sort());
  await other.close();
});

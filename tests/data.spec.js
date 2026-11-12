// Rules for src/data.json and src/charts.json that keep shared links and saved lists working. No browser needed.
import { test, expect } from "@playwright/test";
import { DATA, CHARTS, fixture, keyOf } from "./helpers.js";

const E = DATA.entries, frozen = fixture("frozen-order");

test("every entry's id is its position in the list", () => {
  E.forEach((e, i) => expect(e.id, e.title).toBe(i));
});

test("share order only ever grows at the end", () => {
  expect(CHARTS.share.slice(0, frozen.share.length), "the start of share_order in src/charts.py changed").toEqual(frozen.share);
});

test("share order holds each title exactly once", () => {
  // One id per title: the first entry with that title. Later copies in other lanes and combined stops are left out.
  const canonical = E.filter((e, i) => !e.alias && E.findIndex(x => keyOf(x) === keyOf(e)) === i).map(e => e.id);
  expect(new Set(CHARTS.share).size, "share_order has a repeated id").toBe(CHARTS.share.length);
  expect([...CHARTS.share].sort((a, b) => a - b), "a title is missing from share_order, or a copy or combined stop is in it").toEqual(canonical);
});

test("combined stops point at real, single titles", () => {
  E.filter(e => e.alias).forEach(e => e.alias.forEach(id => {
    expect(E[id], `${e.title} points at ${id}`).toBeTruthy();
    expect(E[id].alias, `${e.title} points at another combined stop`).toBeUndefined();
  }));
});

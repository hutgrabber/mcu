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

/* ---------- the shape of every entry, so a content edit can't quietly break the page ---------- */
const FIELDS = { id: "number", title: "string", tag: "string", year: "number", date: "string", kind: "string", imp: "number",
  upcoming: "boolean", label: "string", meta: "object", story: "string", credits: "object", notes: "object" };
const OPTIONAL = { phase: v => v === null || [1, 2, 3, 4, 5, 6].includes(v), alias: Array.isArray, fresh: v => typeof v === "string" };
const texts = e => [e.title, e.tag, e.label, e.story, ...(e.meta || []), ...(e.credits || []), ...(e.notes || []), e.fresh || ""];

test("every entry has the fields the page reads, of the right type", () => {
  for (const e of E){
    for (const [k, type] of Object.entries(FIELDS)) expect(typeof e[k], `${e.title}: ${k}`).toBe(type);
    for (const k of ["meta", "credits", "notes"]) expect(Array.isArray(e[k]) && e[k].every(x => typeof x === "string"), `${e.title}: ${k} is a list of text`).toBe(true);
    for (const k of Object.keys(e)) expect(k in FIELDS || k in OPTIONAL, `${e.title}: unknown field ${k}`).toBe(true);
    for (const [k, ok] of Object.entries(OPTIONAL)) if (k in e) expect(ok(e[k]), `${e.title}: ${k}`).toBe(true);
    expect(["film", "show", "special"], `${e.title}: kind`).toContain(e.kind);
    expect([0, 1, 2, 3], `${e.title}: imp`).toContain(e.imp);
    expect(e.title.trim(), `${e.title}: title`).not.toBe("");
    expect(e.story.trim(), `${e.title}: story`).not.toBe("");
  }
});

test("every date is a real calendar date", () => {
  for (const e of E){
    expect(e.date, e.title).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    const d = new Date(e.date + "T00:00:00Z");
    expect(d.toISOString().slice(0, 10), `${e.title}: ${e.date}`).toBe(e.date);
  }
});

test("an upcoming title says what's known and when it comes", () => {
  for (const e of E.filter(e => e.upcoming)){
    expect(e.label, e.title).toBe("What is known");
    expect(e.tag, `${e.title}: tag`).toMatch(/^Coming /);
  }
});

test("text uses only the markup the page expects, and no dashes as punctuation", () => {
  for (const e of E) for (const t of texts(e)){
    const tags = [...t.matchAll(/<\/?([a-zA-Z0-9]+)([^>]*)>/g)];
    for (const [whole, tag, attrs] of tags){
      expect(["strong", "em", "span"], `${e.title}: <${tag}> in "${t.slice(0, 60)}"`).toContain(tag.toLowerCase());
      if (tag === "span" && !whole.startsWith("</")) expect(attrs.trim(), `${e.title}: a span only marks a spoiler`).toBe('class="sp"');
    }
    for (const tag of ["strong", "em", "span"])
      expect((t.match(new RegExp(`<${tag}[ >]`, "g")) || []).length, `${e.title}: unclosed <${tag}> in "${t.slice(0, 60)}"`).toBe((t.match(new RegExp(`</${tag}>`, "g")) || []).length);
    expect(t, `${e.title}: an em or en dash`).not.toMatch(/[–—]/);
  }
});

test("every list and chart points at entries that exist", () => {
  const ids = [...DATA.main, ...DATA.mainShows, ...DATA.sections.flatMap(s => s.lanes.flatMap(l => l.ids)),
    ...CHARTS.routes.flatMap(r => r.ids), ...CHARTS.story.ids, ...CHARTS.soon.filter(s => s.e != null).map(s => s.e)];
  for (const id of ids) expect(E[id], `id ${id}`).toBeTruthy();
});

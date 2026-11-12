import asyncio, re
from qa import browser, new_page, SITE
async def main():
    t=open('template3.html').read()
    a=t.index('const A62 = '); b=t.index('/* The short /w/ page next to this one')
    src=t[a:b]
    async with browser() as b_:
        pg = await new_page(b_, 800, 600)
        await pg.goto(SITE); await pg.wait_for_timeout(800)
        out = await pg.evaluate("""(src) => {
          const E = DATA.entries, ORDER = CHARTS.share, keyOf = e => (e.title + "|" + e.year).toLowerCase().replace(/[^a-z0-9|]/g, "");
          const watched = new Set();
          const f = new Function("ORDER", "E", "keyOf", "watched", src + "; return {encodeList, decodeList};")(ORDER, E, keyOf, watched);
          const keys = ORDER.map(id => keyOf(E[id])); let bad = 0, maxLen = 0, sum = 0, n = 0; const samples = {};
          const run = (set, label) => { watched.clear(); set.forEach(k => watched.add(k)); const code = f.encodeList(); const back = new Set(f.decodeList(code) || []); let ok = back.size === watched.size; watched.forEach(k => { if (!back.has(k)) ok = false; }); if (!ok) bad++; maxLen = Math.max(maxLen, code.length); sum += code.length; n++; if (label) samples[label] = code; if (/[-_]$/.test(code)) bad += 1000; };
          run(keys.slice(0, 22), "films through Endgame"); run(keys.slice(0, 38), "every film so far"); run(keys, "everything"); run(keys.slice(0, 60), "all films and shows"); run([keys[103]], "only the last title"); run(keys.filter((k, i) => i % 2 === 0), "every other title");
          run(keys.slice(0, 38).concat(keys.slice(40, 60).filter((k, i) => [0,2,3,5,6,10,12,19].includes(i))), "all films, eight shows");
          for (let r = 0; r < 20000; r++){ const p = Math.random(); run(keys.filter(() => Math.random() < p)); }
          for (let r = 0; r < 5000; r++){ const s = []; let on = Math.random() < .7, i = 0; while (i < keys.length){ const len = 1 + Math.floor(Math.random() * 30); if (on) for (let k = i; k < Math.min(keys.length, i + len); k++) s.push(keys[k]); i += len; on = !on; } run(s); }
          return {bad, maxLen, avg: (sum / n).toFixed(1), n, samples, oldLen: Math.ceil(Math.ceil(113 / 8) * 4 / 3)};
        }""", src)
        print(out)
asyncio.run(main())

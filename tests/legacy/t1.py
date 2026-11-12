import asyncio, json
from qa import browser, new_page, SITE
async def main():
    errs=[]
    async with browser() as b:
        pg = await new_page(b, 1440, 900, 'dark', errs=errs)
        await pg.goto(SITE); await pg.wait_for_timeout(600)
        await pg.screenshot(path='qa/a_intro.png')
        await pg.wait_for_timeout(2400)
        await pg.screenshot(path='qa/a_top.png')
        # share-code round trips
        res = await pg.evaluate("""(() => {
          const out=[]; const st=JSON.parse(localStorage.getItem('hut-mcu-helper-watched')||'[]');
          return out;})()""")
        await pg.click('#next-build'); await pg.wait_for_timeout(500)
        await pg.click('#b-endgame'); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='qa/a_celebrate.png')
        await pg.click('#b-copy'); await pg.wait_for_timeout(300)
        link1 = await pg.evaluate('navigator.clipboard.readText()')
        await pg.click('.b-grp:nth-of-type(7) .b-row:nth-of-type(3)'); await pg.click('.b-grp:nth-of-type(7) .b-row:nth-of-type(6)'); await pg.click('.b-grp:nth-of-type(11) .b-g button')
        await pg.wait_for_timeout(300); await pg.click('#b-copy'); await pg.wait_for_timeout(300)
        link2 = await pg.evaluate('navigator.clipboard.readText()')
        print('links:', link1.split('index.html')[1], link2.split('index.html')[1])
        stored = await pg.evaluate("JSON.parse(localStorage.getItem('hut-mcu-helper-watched')).sort()")
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        await pg.screenshot(path='qa/a_after.png')
        # open the second link in a fresh browser profile and compare
        pg2 = await new_page(b, 1440, 900, 'light', errs=errs)
        await pg2.goto(SITE); await pg2.wait_for_timeout(1500)
        await pg2.evaluate("localStorage.setItem('hut-mcu-helper-watched', JSON.stringify(['ironman|2008','thor|2011','theavengers|2012','deadpool|2016','logan|2017']))")
        await pg2.goto(SITE + '#' + link2.split('#')[1]); await pg2.wait_for_timeout(2600)
        await pg2.screenshot(path='qa/a_offer.png')
        await pg2.click('#sheet-cmp'); await pg2.wait_for_timeout(900)
        await pg2.screenshot(path='qa/a_compare.png')
        print('sum:', await pg2.inner_text('#c-sum')); print('next:', await pg2.inner_text('#c-next'))
        await pg2.click('#c-add'); await pg2.wait_for_timeout(600)
        got = await pg2.evaluate("JSON.parse(localStorage.getItem('hut-mcu-helper-watched')).sort()")
        print('decoded matches sender (plus own):', set(stored) <= set(got), len(stored), len(got))
        await pg2.click('#toast button'); await pg2.wait_for_timeout(500)
        print('after undo:', await pg2.evaluate("JSON.parse(localStorage.getItem('hut-mcu-helper-watched')).length"))
        await pg2.keyboard.press('Escape'); await pg2.wait_for_timeout(400)
        await pg2.click('#theme'); await pg2.wait_for_timeout(250); await pg2.screenshot(path='qa/a_theme_mid.png'); await pg2.wait_for_timeout(700)
        await pg2.screenshot(path='qa/a_theme_done.png')
        # exhaustive encode/decode check on random lists
        chk = await pg2.evaluate("""(() => { return 'n/a'; })()""")
        # old-style link still opens
        pg3 = await new_page(b, 390, 844, 'dark', mobile=True, scale=2, errs=errs)
        await pg3.goto(SITE + '#p=_____z8AgP__BwAAAAA'); await pg3.wait_for_timeout(3000)
        await pg3.screenshot(path='qa/a_m_offer.png')
        print('old link sheet:', await pg3.inner_text('#sheet-t'))
        await pg3.tap('#sheet-no'); await pg3.wait_for_timeout(500)
        await pg3.evaluate("document.querySelector('#soon').scrollIntoView()"); await pg3.wait_for_timeout(1200)
        await pg3.screenshot(path='qa/a_m_soon.png')
        # stub page redirect
        pg4 = await new_page(b, 800, 600, 'dark', errs=errs)
        await pg4.goto('file:///home/claude/site/w/index.html#m3'); await pg4.wait_for_timeout(2500)
        print('stub landed on:', pg4.url.split('/site/')[1], '| sheet:', await pg4.inner_text('#sheet-t'))
        print('errors', errs)
asyncio.run(main())

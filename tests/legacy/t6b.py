import asyncio, json
from qa import browser, new_page
NEXT='file:///home/claude/site/index.html'
async def main():
    errs=[]
    async with browser() as b:
        pg = await new_page(b, 1440, 900, 'dark', errs=errs)
        await pg.goto(NEXT); await pg.wait_for_timeout(300)
        print('lanes at 300ms:', await pg.evaluate("document.querySelectorAll('.lane').length"))
        await pg.wait_for_timeout(2400)
        print('lanes at 2.7s:', await pg.evaluate("document.querySelectorAll('.lane').length"), '| nav links:', await pg.evaluate("document.querySelectorAll('#nav a').length"), '| prog:', await pg.inner_text('#prog'))
        await pg.screenshot(path='qa/e_top.png')
        # stale-undo bug: bulk add, tick two more, undo -> expect 2 left
        await pg.keyboard.press('w'); await pg.wait_for_timeout(500)
        await pg.click('#b-endgame'); await pg.wait_for_timeout(500)
        await pg.click('.b-grp:nth-of-type(7) .b-row:nth-of-type(2)'); await pg.click('.b-grp:nth-of-type(7) .b-row:nth-of-type(3)'); await pg.wait_for_timeout(300)
        await pg.click('#toast button'); await pg.wait_for_timeout(500)
        print('after stale undo, list size (expect 2):', await pg.evaluate("JSON.parse(localStorage.getItem('hut-mcu-helper-watched')).length"))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        # back button closes story
        await pg.evaluate("document.querySelectorAll('#mainLane .card')[2].click()"); await pg.wait_for_timeout(900)
        print('hash with story open:', await pg.evaluate('location.hash'))
        for _ in range(3): await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(350)
        print('hash after 3 next:', await pg.evaluate('location.hash'), '| history length', await pg.evaluate('history.length'))
        await pg.go_back(); await pg.wait_for_timeout(700)
        print('after Back: url', pg.url.split('/')[-1], '| drawer open:', await pg.evaluate("document.querySelector('#drawer').classList.contains('open')"), '| focus on:', await pg.evaluate("document.activeElement.textContent.slice(0,22)"))
        await pg.go_forward(); await pg.wait_for_timeout(1300)
        print('after Forward: drawer open:', await pg.evaluate("document.querySelector('#drawer').classList.contains('open')"), await pg.evaluate('location.hash'))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(700)
        print('after Escape: hash', repr(await pg.evaluate('location.hash')), 'drawer open', await pg.evaluate("document.querySelector('#drawer').classList.contains('open')"))
        # d-upto returns after undo
        await pg.evaluate("document.querySelectorAll('#mainLane .card')[6].click()"); await pg.wait_for_timeout(900)
        await pg.click('#d-upto'); await pg.wait_for_timeout(400)
        print('upto present after click:', await pg.evaluate("!!document.querySelector('#d-upto')"))
        await pg.click('#toast button'); await pg.wait_for_timeout(500)
        print('upto present after undo:', await pg.evaluate("!!document.querySelector('#d-upto')"))
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
        # search then Enter then Escape clears
        await pg.click('#q'); await pg.keyboard.type('loki'); await pg.wait_for_timeout(400); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(900); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
        print('dimmed after Escape:', await pg.evaluate("document.querySelectorAll('.stop.dim').length"), '| q:', repr(await pg.input_value('#q')))
        # mode switch does not replay flashes
        await pg.click('#mode [data-mode=all]'); await pg.wait_for_timeout(300)
        print('just after mode switch:', await pg.evaluate("document.querySelectorAll('.stop.just').length"))
        # malformed hashes
        for h in ('#w=!!','#t=nope','#w='):
            await pg.evaluate(f"location.hash='{h}'"); await pg.wait_for_timeout(500)
            print(h, '->', repr(await pg.evaluate('location.hash')), '| toast:', await pg.inner_text('#toast'))
        # shared link arriving in an open tab
        await pg.evaluate("location.hash='#w=m'"); await pg.wait_for_timeout(1300)
        print('sheet open after hash change:', await pg.evaluate("document.querySelector('#sheet').classList.contains('open')"))
        await pg.click('#sheet-no')
        # deep link to a far section: lane visible, no blink
        pg2 = await new_page(b, 1440, 900, 'dark', errs=errs)
        await pg2.goto(NEXT+'#t=helstrom-2020'); await pg2.wait_for_timeout(2500)
        print('deep link title:', await pg2.inner_text('#d-title'), '| lane classes:', await pg2.evaluate("document.querySelector('.stop.current').closest('.lane').className"))
        await pg2.screenshot(path='qa/e_deeplink.png')
        pg3 = await new_page(b, 1440, 900, 'dark', errs=errs)
        await pg3.goto(NEXT+'#soon'); await pg3.wait_for_timeout(1500)
        print('#soon anchor: scrollY', await pg3.evaluate('scrollY'), 'soon top', await pg3.evaluate("Math.round(document.querySelector('#soon').getBoundingClientRect().top)"))
        # scrolling down: lanes draw
        pg4 = await new_page(b, 1440, 900, 'light', errs=errs)
        await pg4.goto(NEXT); await pg4.wait_for_timeout(2500)
        await pg4.evaluate("document.querySelector('#spider').scrollIntoView()"); await pg4.wait_for_timeout(350)
        await pg4.screenshot(path='qa/e_draw_mid.png'); await pg4.wait_for_timeout(2200)
        await pg4.screenshot(path='qa/e_draw_done.png')
        print('waiting lanes left in view:', await pg4.evaluate("[...document.querySelectorAll('.lane.waiting')].filter(l=>{const r=l.getBoundingClientRect();return r.top<innerHeight*0.7&&r.bottom>innerHeight*0.3}).length"))
        # reduced motion: everything visible
        pg5 = await new_page(b, 1440, 900, 'dark', errs=errs, reduced=True)
        await pg5.goto(NEXT); await pg5.wait_for_timeout(1800)
        print('reduced: waiting lanes', await pg5.evaluate("document.querySelectorAll('.lane.waiting').length"), 'lanes', await pg5.evaluate("document.querySelectorAll('.lane').length"))
        print('errors', errs)
asyncio.run(main())

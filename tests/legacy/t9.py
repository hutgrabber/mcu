import asyncio
from qa import browser, new_page, SITE
async def main():
    errs=[]
    async with browser() as b:
        pg = await new_page(b, 390, 844, 'dark', mobile=True, scale=2, errs=errs)
        await pg.goto(SITE); await pg.wait_for_timeout(2500)
        await pg.screenshot(path='qa/g_m_top.png')
        await pg.tap('#next-done'); await pg.wait_for_timeout(450)
        await pg.evaluate("window.scrollTo(0, document.querySelector('#main').offsetTop - 80)"); await pg.wait_for_timeout(900)
        await pg.tap('#mainLane .stop.upnext .card'); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.querySelector('#d-body').scrollTop=99999"); await pg.wait_for_timeout(300)
        await pg.screenshot(path='qa/g_m_drawer.png')
        await pg.tap('#d-watch'); await pg.wait_for_timeout(600)
        await pg.screenshot(path='qa/g_m_drawer_toast.png')
        pg2 = await new_page(b, 1440, 900, 'light', errs=errs)
        await pg2.goto(SITE); await pg2.wait_for_timeout(2500)
        await pg2.click('#next-done'); await pg2.wait_for_timeout(350)
        await pg2.screenshot(path='qa/g_d_mark.png')
        print(errs)
asyncio.run(main())

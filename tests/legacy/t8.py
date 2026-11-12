import asyncio
from qa import browser, new_page, SITE
async def main():
    errs=[]
    async with browser() as b:
        res=[]
        for w,h,mob in ((320,568,True),(390,844,True),(844,390,True),(768,1024,False),(1024,768,False),(1440,900,False),(1920,1080,False)):
            for theme in ('dark','light'):
                pg = await new_page(b, w, h, theme, mobile=mob, scale=2 if mob else 1, errs=errs)
                await pg.goto(SITE); await pg.wait_for_timeout(2300)
                ov = await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
                # open every chart; check overflow and card clipping across all lanes and modes
                await pg.evaluate("document.querySelectorAll('.chip').forEach(c=>c.click())"); await pg.wait_for_timeout(1500)
                ov2 = await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
                clip = await pg.evaluate("""(()=>{let bad=0;for(const m of ['films','essential','all']){document.querySelector('#mode [data-mode='+m+']').click();
                  document.querySelectorAll('.lane').forEach(l=>{const t=l.querySelector('.track').getBoundingClientRect();l.querySelectorAll('.card').forEach(c=>{const r=c.getBoundingClientRect();if(r.top<t.top-0.5||r.bottom>t.bottom+0.5)bad++;});});}
                  document.querySelector('#mode [data-mode=films]').click();return bad})()""")
                res.append((w,h,theme,ov,ov2,clip, await pg.evaluate("document.querySelectorAll('.lane').length")))
                if theme=='dark' and w in (320,1024,1920):
                    await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(500); await pg.screenshot(path=f'qa/f_top_{w}.png')
                await pg.context.close()
        for r in res: print(r)
        print('errors', errs)
asyncio.run(main())

"""Shared test helper: headless Chrome with the page's real fonts served locally (Google Fonts is blocked in this sandbox)."""
import asyncio, contextlib
from playwright.async_api import async_playwright
FD='/home/claude/fonts/'
FILES={'archivo.woff2':FD+'fontsource-variable-archivo-5.3.0/package/files/archivo-latin-standard-normal.woff2',
       'archivo-i.woff2':FD+'fontsource-variable-archivo-5.3.0/package/files/archivo-latin-standard-italic.woff2',
       'ss4.woff2':FD+'fontsource-variable-source-serif-4-5.3.1/package/files/source-serif-4-latin-opsz-normal.woff2',
       'ss4-i.woff2':FD+'fontsource-variable-source-serif-4-5.3.1/package/files/source-serif-4-latin-opsz-italic.woff2'}
def font_css(base):
    return f'''@font-face{{font-family:"Archivo";font-style:normal;font-weight:100 900;font-stretch:62% 125%;src:url({base}archivo.woff2) format("woff2")}}
@font-face{{font-family:"Archivo";font-style:italic;font-weight:100 900;font-stretch:62% 125%;src:url({base}archivo-i.woff2) format("woff2")}}
@font-face{{font-family:"Source Serif 4";font-style:normal;font-weight:200 900;src:url({base}ss4.woff2) format("woff2")}}
@font-face{{font-family:"Source Serif 4";font-style:italic;font-weight:200 900;src:url({base}ss4-i.woff2) format("woff2")}}'''
async def wire_fonts(ctx):
    async def css(route): await route.fulfill(status=200, content_type='text/css', headers={'access-control-allow-origin':'*'}, body=font_css('https://localfonts.test/'))
    async def font(route):
        name=route.request.url.rsplit('/',1)[1]
        await route.fulfill(status=200, content_type='font/woff2', headers={'access-control-allow-origin':'*'}, body=open(FILES[name],'rb').read())
    await ctx.route('**/fonts.googleapis.com/**', css)
    await ctx.route('https://localfonts.test/**', font)
    await ctx.route('**/fonts.gstatic.com/**', lambda r: r.abort())
@contextlib.asynccontextmanager
async def browser():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        try: yield b
        finally: await b.close()
async def new_page(b, width=1440, height=900, theme='dark', mobile=False, scale=1, errs=None, reduced=False):
    ctx = await b.new_context(viewport={'width':width,'height':height}, color_scheme=theme, device_scale_factor=scale, has_touch=mobile, is_mobile=mobile, reduced_motion='reduce' if reduced else 'no-preference')
    await wire_fonts(ctx)
    try: await ctx.grant_permissions(['clipboard-read','clipboard-write'])
    except Exception: pass
    pg = await ctx.new_page()
    if errs is not None:
        pg.on('pageerror', lambda e: errs.append('PAGEERR '+str(e)))
        pg.on('console', lambda m: errs.append('CONSOLE '+m.text) if m.type=='error' and 'ERR_' not in m.text else None)
    return pg
SITE='file:///home/claude/site/index.html'

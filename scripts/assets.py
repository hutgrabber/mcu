import asyncio, json, math, random, io
from PIL import Image
from qa import browser, font_css, FILES
OUT='/home/claude/site/'
FRAME="M6 13C5.6 7.6 9.6 5.2 16 5c7.6-.3 11.6 1.9 16 1.9S40.4 4.7 48 5c6.4.2 10.4 2.6 10 8-.6 8.4-4.2 14.6-12 14.6-5.8 0-8.9-3.9-10.3-8.3-.8-2.5-6.6-2.5-7.4 0C26.9 23.7 23.8 27.6 18 27.6 10.200 27.600 6.600 21.400 6 13z".replace('10.200 27.600 6.600 21.400','10.2 27.6 6.6 21.4')
LL="M10.6 13.2c-.2-3 1.7-4.3 5.6-4.5 4.7-.2 8.8.6 10.3 2.3 1.3 1.5.3 5.9-1.9 9-1.7 2.4-3.9 3.4-6.600 3.400-4.7 0-7-4.4-7.4-10.2z".replace('6.600 3.400','6.6 3.4')
LR="M53.4 13.2c.2-3-1.7-4.3-5.6-4.5-4.7-.2-8.8.6-10.3 2.3-1.3 1.5-.3 5.9 1.9 9 1.7 2.4 3.9 3.4 6.6 3.4 4.7 0 7-4.4 7.4-10.2z"
SHINE="M14 15.4l4.6-3.8M15.8 18.2l2-1.6M40.6 15.4l4.6-3.8M42.4 18.2l2-1.6"
ARMS="M7 11.5C3.6 10.6 2 12.2 1.6 15.2M57 11.5c3.4-.9 5 .7 5.4 3.7"
INK,BG,TEXT,RED,CYAN='#0D0B22','#1A1838','#EEEBFF','#FF4D6D','#3CE7FF'
P=['#EF5350','#F4B740','#9B7BFF','#2EC4B6','#FF8A3D','#5AB0FF']

def glasses(frame=TEXT, outline=None, offsets=True, arms=True, shine=True):
    """the logo, in its own 64x33 box"""
    o=f' stroke="{outline}" stroke-width="1.6" stroke-linejoin="round"' if outline else ''
    s='<g transform="rotate(-5 32 16)">'
    if arms: s+=f'<path d="{ARMS}" fill="none" stroke="{outline or frame}" stroke-width="{4.2 if outline else 2.6}" stroke-linecap="round"/>'+(f'<path d="{ARMS}" fill="none" stroke="{frame}" stroke-width="2.2" stroke-linecap="round"/>' if outline else '')
    if offsets: s+=f'<path d="{FRAME}" fill="{RED}" transform="translate(-1.6 .5)"/><path d="{FRAME}" fill="{CYAN}" transform="translate(1.6 .5)"/>'
    s+=f'<path d="{FRAME}" fill="{frame}"{o}/><path d="{LL}" fill="{RED}"/><path d="{LR}" fill="{CYAN}"/>'
    if shine: s+=f'<path d="{SHINE}" fill="none" stroke="#fff" stroke-opacity=".8" stroke-width="1.7" stroke-linecap="round"/>'
    return s+'</g>'

def icon_svg(size=64, rx=14, scale=.94, pad_bg=BG, rich=False):
    t=(64-64*scale)/2
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{size}" height="{size}"><rect width="64" height="64" rx="{rx}" fill="{pad_bg}"/><g transform="translate({t:.2f} {16.5 - (scale-.94)*16:.2f}) scale({scale})">{glasses(arms=False, offsets=rich, shine=rich)}</g></svg>'

FONT=font_css('file://'+'/'.join(FILES['archivo.woff2'].split('/')[:-1])+'/').replace('archivo.woff2','archivo-latin-standard-normal.woff2').replace('archivo-i.woff2','archivo-latin-standard-italic.woff2')
SS=FILES['ss4.woff2']

def base_css():
    return f'''<style>{FONT}
html,body{{margin:0}} body{{width:1200px;height:630px;position:relative;overflow:hidden;background:{BG};color:{TEXT};font-family:"Archivo",sans-serif;
 background-image:radial-gradient(rgba(169,165,214,.11) 1.5px,transparent 1.8px);background-size:30px 30px}}
.glow{{position:absolute;border-radius:50%;filter:blur(90px);opacity:.33}}
h1{{margin:0;font-weight:800;font-stretch:118%;letter-spacing:-.03em;line-height:.92;text-shadow:-5px 0 0 {RED},5px 0 0 {CYAN}}}
.site{{position:absolute;font-size:25px;color:#A9A5D6;font-weight:600;font-stretch:96%}}
</style>'''

def og_site():
    # a transit line across the bottom: six phases, stops, one "up next" ring
    counts=[4,4,6,5,4,3]; y=500; line=''; x0=40; sp=40
    for p,n in enumerate(counts):
        x1=x0+n*sp+20
        line+=f'<path d="M{x0} {y}H{x1 if p<5 else 1200}" stroke="{P[p]}" stroke-width="11"/>'
        line+=f'<text x="{x0+16}" y="{y-36}" font-size="88" font-weight="800" fill="{P[p]}" style="font-stretch:125%;letter-spacing:-4px">{p+1}</text>'
        for i in range(n):
            x=x0+30+i*sp
            done=(p<3) or (p==3 and i<2)
            sq=(p>=3 and i%3==1)
            fill=P[p] if done else BG
            shape=f'<rect x="{x-12.5}" y="{y-12.5}" width="25" height="25" rx="7" fill="{fill}" stroke="{P[p]}" stroke-width="6"/>' if sq else f'<circle cx="{x}" cy="{y}" r="13" fill="{fill}" stroke="{P[p]}" stroke-width="6"/>'
            if p==3 and i==2: shape=f'<circle cx="{x}" cy="{y}" r="24" fill="{BG}" stroke="{CYAN}" stroke-width="4"/>'+shape
            line+=shape
            if done: line+=f'<path d="M{x-5.5} {y+.5}l4 4 7.5-8.5" fill="none" stroke="{INK}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
        x0=x1
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">{base_css()}</head><body>
<div class="glow" style="left:-160px;top:330px;width:520px;height:420px;background:{RED}"></div>
<div class="glow" style="right:-160px;top:-180px;width:560px;height:460px;background:{CYAN};opacity:.26"></div>
<svg style="position:absolute;left:62px;top:54px;overflow:visible" width="190" height="98" viewBox="0 0 64 33">{glasses()}</svg>
<h1 style="position:absolute;left:66px;top:182px;font-size:104px">hut's mcu helper</h1>
<p style="position:absolute;left:70px;top:290px;margin:0;font-size:40px;font-weight:650;font-stretch:96%">Every Marvel story, one line at a time.</p>
<svg style="position:absolute;left:0;top:0" width="1200" height="630" viewBox="0 0 1200 630"><g stroke-linecap="butt">{line}</g></svg>
<div class="site" style="right:60px;top:78px">mcu.hutlab.dev</div>
<div class="site" style="left:70px;top:566px;color:#EEEBFF;font-weight:500">Watch order, story summaries, credit scenes and a checklist that remembers.</div>
</body></html>'''

def popcorn(cx, top, w_top=250, w_bot=176, h=250):
    random.seed(7)
    # bucket stripes
    n=7; s=''
    xt0,xt1=cx-w_top/2,cx+w_top/2; xb0,xb1=cx-w_bot/2,cx+w_bot/2; yb=top+h
    s+=f'<path d="M{xt0} {top}L{xt1} {top}L{xb1} {yb-14}Q{xb1-2} {yb} {xb1-18} {yb}L{xb0+18} {yb}Q{xb0+2} {yb} {xb0} {yb-14}Z" fill="#FFF4E0" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
    clip=f'<clipPath id="bk"><path d="M{xt0} {top}L{xt1} {top}L{xb1} {yb-14}Q{xb1-2} {yb} {xb1-18} {yb}L{xb0+18} {yb}Q{xb0+2} {yb} {xb0} {yb-14}Z"/></clipPath>'
    st=''
    for i in range(0,n,2):
        a0=xt0+(xt1-xt0)*i/n; a1=xt0+(xt1-xt0)*(i+1)/n; b0=xb0+(xb1-xb0)*i/n; b1=xb0+(xb1-xb0)*(i+1)/n
        st+=f'<path d="M{a0} {top}L{a1} {top}L{b1} {yb}L{b0} {yb}Z" fill="{RED}"/>'
    s+=clip+f'<g clip-path="url(#bk)">{st}<path d="M{xt0} {top}h{w_top}v26h-{w_top}z" fill="{INK}" opacity=".18"/></g>'
    s+=f'<path d="M{xt0} {top}L{xt1} {top}L{xb1} {yb-14}Q{xb1-2} {yb} {xb1-18} {yb}L{xb0+18} {yb}Q{xb0+2} {yb} {xb0} {yb-14}Z" fill="none" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>'
    # popcorn puffs: draw outlines first, then fills, so overlapping circles read as one shape
    puffs=[]
    rows=[(top-18,[-96,-52,-6,40,88]),(top-62,[-74,-26,22,68]),(top-104,[-44,6,50]),(top-140,[-8])]
    for y,xs in rows:
        for x in xs:
            puffs.append((cx+x+random.uniform(-6,6), y+random.uniform(-6,6), random.uniform(30,37)))
    circles=[]
    for (x,y,r) in puffs:
        circles.append((x,y,r))
        for k in range(3):
            a=random.uniform(0,6.28); circles.append((x+math.cos(a)*r*.62, y+math.sin(a)*r*.5, r*.62))
    out=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r+3.5:.1f}" fill="{INK}"/>' for x,y,r in circles)
    fill=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="#FFF1C9"/>' for x,y,r in circles)
    shade=''.join(f'<circle cx="{x+r*.22:.1f}" cy="{y+r*.28:.1f}" r="{r*.5:.1f}" fill="#F7D98B" opacity=".75"/>' for x,y,r in puffs)
    hi=''.join(f'<circle cx="{x-r*.3:.1f}" cy="{y-r*.34:.1f}" r="{r*.2:.1f}" fill="#fff"/>' for x,y,r in puffs)
    rim=f'<rect x="{xt0-12}" y="{top-14}" width="{w_top+24}" height="30" rx="13" fill="#FFF4E0" stroke="{INK}" stroke-width="7"/>'
    return out+fill+shade+hi+s+rim

def strip(w=1000, frames=None, checks=True):
    h=150; s=f'<rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="#0F0D26" stroke="#3A3680" stroke-width="3"/>'
    for x in range(16,w-20,38):
        s+=f'<rect x="{x}" y="11" width="20" height="13" rx="4" fill="#322E6E"/><rect x="{x}" y="{h-24}" width="20" height="13" rx="4" fill="#322E6E"/>'
    fw=132; i=0; x=22
    while x+fw<w-10:
        c=P[i%6]; done=frames is None or i in frames
        s+=f'<rect x="{x}" y="34" width="{fw}" height="82" rx="9" fill="{c if done else "#27245A"}"/>'
        if done and checks: s+=f'<path d="M{x+fw/2-17} {76}l12 12 23-25" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
        elif not done: s+=f'<circle cx="{x+fw/2}" cy="75" r="15" fill="none" stroke="{c}" stroke-width="6" stroke-dasharray="9 8"/>'
        x+=fw+16; i+=1
    return s

def sparkle(x,y,r,c):
    k=r*.28
    return f'<path d="M{x} {y-r}Q{x+k} {y-k} {x+r} {y}Q{x+k} {y+k} {x} {y+r}Q{x-k} {y+k} {x-r} {y}Q{x-k} {y-k} {x} {y-r}z" fill="{c}"/>'

def og_list():
    art=f'''<g transform="translate(596 372) rotate(-9)" opacity=".9">{strip(760, frames={0,1,2,3})}</g>
<g transform="translate(-40 520) rotate(-4)">{strip(1320, frames={0,1,2,3,4,5})}</g>
{popcorn(930,262)}
<g transform="translate(700 398) rotate(-10) scale(5.4)">{glasses(frame=TEXT, outline=INK)}</g>
{sparkle(742,150,24,CYAN)}{sparkle(1118,196,16,'#F4B740')}{sparkle(690,300,12,RED)}{sparkle(1090,90,10,TEXT)}'''
    return f'''<!DOCTYPE html><html><head><meta charset="utf-8">{base_css()}</head><body>
<div class="glow" style="left:-220px;top:-240px;width:520px;height:440px;background:{RED};opacity:.2"></div>
<div class="glow" style="right:-120px;top:120px;width:560px;height:500px;background:{CYAN};opacity:.24"></div>
<svg style="position:absolute;left:0;top:0" width="1200" height="630" viewBox="0 0 1200 630">{art}</svg>
<svg style="position:absolute;left:64px;top:58px;overflow:visible" width="104" height="54" viewBox="0 0 64 33">{glasses()}</svg>
<div class="site" style="left:186px;top:70px;color:{TEXT};font-weight:750;font-size:30px;font-stretch:108%">hut's mcu helper</div>
<h1 style="position:absolute;left:64px;top:176px;font-size:84px;width:660px">My Marvel<br>watched list</h1>
<p style="position:absolute;left:68px;top:356px;margin:0;font-size:32px;line-height:1.25;font-weight:600;font-stretch:96%;width:520px">Open it to compare with yours, or add it to your own.</p>
</body></html>'''

async def main():
    open(OUT+'favicon.svg','w').write(icon_svg())
    async with browser() as b:
        pg = await b.new_page(viewport={'width':1200,'height':630})
        for name,html in (('og',og_site()),('og-list',og_list())):
            open(f'/home/claude/web/{name}.html','w').write(html)
            await pg.goto(f'file:///home/claude/web/{name}.html'); await pg.wait_for_timeout(700)
            await pg.screenshot(path=OUT+name+'.png')
        # icons
        async def shot(svg, size, path, transparent=False):
            p2 = await b.new_page(viewport={'width':size,'height':size})
            await p2.set_content(f'<body style="margin:0;background:{"transparent" if transparent else BG}">{svg}</body>')
            await p2.screenshot(path=path, omit_background=transparent); await p2.close()
        await shot(icon_svg(180, rx=0, scale=.86, rich=True), 180, OUT+'apple-touch-icon.png')
        await shot(icon_svg(192, rx=14, scale=.88, rich=True), 192, OUT+'icon-192.png', True)
        await shot(icon_svg(512, rx=14, scale=.88, rich=True), 512, OUT+'icon-512.png', True)
        await shot(icon_svg(512, rx=0, scale=.7, rich=True), 512, OUT+'icon-maskable-512.png')
        await shot(icon_svg(256, rx=14), 256, '/home/claude/web/icon-256.png', True)
    im=Image.open('/home/claude/web/icon-256.png').convert('RGBA')
    im.save(OUT+'favicon.ico', sizes=[(16,16),(32,32),(48,48)])
    for n in ('og','og-list'):
        im=Image.open(OUT+n+'.png').convert('RGB'); im.save(OUT+n+'.png', optimize=True)
    json.dump({"name":"hut's mcu helper","short_name":"mcu helper","description":"Every Marvel film and show on one line, with a checklist that remembers what you've seen.","start_url":"./","scope":"./","display":"standalone","background_color":"#1A1838","theme_color":"#1A1838",
      "icons":[{"src":"icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icon-512.png","sizes":"512x512","type":"image/png"},{"src":"icon-maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]}, open(OUT+'site.webmanifest','w'), indent=1)
asyncio.run(main())

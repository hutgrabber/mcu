import json, re
d=json.load(open('data_raw.json')); E=d['entries']; C=d['charts']
MON={m:i+1 for i,m in enumerate('January February March April May June July August September October November December'.split())}
def rdate(e):
    t=' '.join(e['meta'])+' '+e['heading']
    m=re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2})',t)
    y=re.search(r'(19|20)\d\d', t[m.end():] if m else t)
    yr=int(y.group(0)) if y else (e['year'] or 0)
    return f"{yr:04d}-{MON[m.group(1)] if m else 1:02d}-{int(m.group(2)) if m else 1:02d}"
out=[]
for i,e in enumerate(E):
    h=e['rawTitle']
    imp=h.count('★')
    h=re.sub(r'\s*★.*$','',h).strip()
    m=re.match(r'^(.*?)\s*\(([^)]*)\)\s*(?::\s*(.*))?$',h)
    title,tag=h,''
    upcoming=False
    if m:
        title=m.group(1); par=m.group(2); after=m.group(3) or ''
        if re.fullmatch(r'(19|20)\d\d',par): tag=after
        else:
            tag=par[0].upper()+par[1:] if par else ''
            if after: tag=(tag+'. '+after) if tag else after
        if par.startswith('coming'): upcoming=True
    if 'never officially released' in e['heading']: tag='Never officially released'
    kind='film'
    if e['part'].startswith('Part 2') or "X-Men '97" in h: kind='show'
    if 'Special Presentation' in e['heading']: kind='special'
    tag=tag.replace('Special Presentation','').strip(' .')
    out.append(dict(id=i,title=title,tag=tag,year=e['year'],date=rdate(e),phase=e['phase'],kind=kind,imp=imp,upcoming=upcoming,
        label=e['storyLabel'],meta=e['metaHtml'],story=e['storyHtml'],credits=e['creditsHtml'],notes=e['notesHtml']))
# lanes
L=lambda name,ids,color,order='release',note='':dict(name=name,ids=ids,color=color,order=order,note=note)
sections=[
 dict(id='spider',title='Spider-Man, across three universes',intro="Sony owns Spider-Man, so there are three live-action Peter Parkers, each in his own world, until No Way Home brings them together. Miles Morales has his own animated story.",
   lanes=[L('Tobey Maguire · Earth-96283',[40,41,42],'#EF5350'),L('Andrew Garfield · Earth-120703',[43,44],'#5AB0FF'),
          L("Tom Holland · the main universe, told from Peter's side",[45,46,47,48,49,50],'#F4B740'),L('Miles Morales · the animated Spider-Verse',[51,52,53],'#9B7BFF')],charts=[3]),
 dict(id='sony',title="Venom and Sony's Spider-Man Universe",intro="Six films about Spider-Man's villains, set in their own world (Earth-688). Only the Venom films and Morbius touch the main story. Sony has paused the series.",
   lanes=[L('Earth-688',[54,55,56,57,58,59],'#2EC4B6')],charts=[4]),
 dict(id='shows',title='The shows',intro="Stars show how much a show matters to the main story: three means the films assume you've seen it, one means it stands on its own.",
   lanes=[L('Wanda, Vision and Agatha · an official trilogy',[60,72,79],'#EF5350'),L('Loki and the multiverse',[62,70],'#2EC4B6'),
          L('The street level · Netflix to Disney+',[80,81,82,83,84,85,63,71,73,77,78],'#F4B740'),
          L('Everything else on Disney+',[61,64,65,66,67,68,69,74,75,76],'#9B7BFF'),
          L('Older shows · optional, not on the official timeline',[86,87,88,89,90,91],'#7C78A8')],charts=[5,6,7]),
 dict(id='xmen',title='The X-Men and the mutant story',intro="Fox made these films in their own universe (Earth-10005). Days of Future Past rewrites history in 1973, splitting them into two timelines. These lines run in story order.",
   lanes=[L('Original timeline',[96,95,92,93,94,97,98],'#F4B740','story'),L('Revised timeline, after Days of Future Past',[100,103,99,102,104,101,105],'#5AB0FF','story'),
          L('How mutants reach the main universe',[27,65,29,32,33,37,38],'#FF8A3D','release','Stops on the main line'),L("The animated X-Men '97",[106],'#7C78A8')],charts=[8]),
 dict(id='ff',title='The Fantastic Four',intro="Three separate Fox versions, one that was never released, and the Marvel Studios family from Earth-828 who cross into the main universe for Avengers: Doomsday.",
   lanes=[L('Every Fantastic Four film',[107,108,109,110,111],'#5AB0FF'),L('Fantastic Four in other films',[27,33,35,38],'#FF8A3D','release','Stops on the main line')],charts=[9]),
]
data=dict(entries=out,main=list(range(0,40)),mainShows=list(range(60,80)),sections=sections,
  mainCharts=[0,1,2],charts=[c['text'] for c in C])
json.dump(data,open('data.json','w'),ensure_ascii=False)
for o in out[:3]+out[45:47]+out[60:61]+out[67:68]+out[80:81]+out[107:108]: print(o['title'],'|',o['tag'],'|',o['date'],o['kind'],o['imp'],o['upcoming'])
print(out[59]['credits'])

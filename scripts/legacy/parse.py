import re, json, html, sys
src=open(sys.argv[1]).read()
lines=src.split('\n')
def inline(t):
    t=html.escape(t, quote=False)
    t=re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t=re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t=t.replace('\\*','*')
    return t
entries=[]; part=h2=h3=''; cur=None; charts=[]; infence=False; fence=[]
for ln in lines:
    if ln.startswith('```'):
        if infence:
            charts.append({'part':part,'h2':h2,'h3':h3,'text':'\n'.join(fence)}); fence=[]; infence=False
        else: infence=True
        continue
    if infence: fence.append(ln); continue
    if ln.startswith('# '): part=ln[2:].strip(); h2=h3=''; continue
    if ln.startswith('## '): h2=ln[3:].strip(); h3=''; cur=None; continue
    if ln.startswith('### '): h3=ln[4:].strip(); cur=None; continue
    if ln.startswith('#### '):
        cur={'heading':ln[5:].strip(),'part':part,'h2':h2,'h3':h3,'meta':[],'story':'','storyLabel':'','credits':[],'notes':[]}
        entries.append(cur); mode=None; continue
    if cur is None: continue
    if ln.strip()=='---' : continue
    m=re.match(r"\*\*(Story|What is known|Peter's story|The mutant story|The family's story|Story \(so far\)):\*\*\s*(.*)",ln)
    if m: cur['storyLabel']=m.group(1); cur['story']=m.group(2); mode='story'; continue
    m=re.match(r"\*\*Credit scenes(?: \(there are five\))?:\*\*\s*(.*)",ln)
    if m:
        mode='credits'
        if m.group(1): cur['credits'].append(m.group(1))
        continue
    if ln.startswith('- ') and mode=='credits': cur['credits'].append(ln[2:]); continue
    if ln.startswith('> '): cur['notes'].append(ln[2:]); continue
    if ln.startswith('**') and mode is None: cur['meta'].append(ln); continue
    if ln.startswith('*(') and mode is None: cur['notes'].append(ln.strip('*')); continue
    if ln.startswith('*(') and mode=='story': cur['notes'].append(ln.strip('*')); continue
for e in entries:
    h=e['heading']
    num=re.match(r'(\d+)\.\s+(.*)',h)
    e['num']=int(num.group(1)) if num else None
    t=num.group(2) if num else h
    e['rawTitle']=t
    y=re.findall(r'(?:19|20)\d\d',t+' '+' '.join(e['meta']))
    e['year']=int(y[0]) if y else None
    ph=re.search(r'\*\*Phase (\d)\*\*',' '.join(e['meta']))
    e['phase']=int(ph.group(1)) if ph else None
    e['metaHtml']=[inline(m) for m in e['meta']]
    e['storyHtml']=inline(e['story'])
    e['creditsHtml']=[inline(c) for c in e['credits']]
    e['notesHtml']=[inline(n) for n in e['notes']]
    e['titleHtml']=inline(t)
    e['essential']='★★★' in h
for i,e in []: print(i,'|',e['part'][:10],'|',e['h2'][:30],'|',e['h3'][:30],'|',e['rawTitle'][:50],'|',e['year'],e['phase'],len(e['credits']))
json.dump({'entries':entries,'charts':charts},open('data_raw.json','w'))
print(len(charts),'charts')
for i,c in []: print('chart',i,c['h2'][:40],'|',c['h3'][:40])

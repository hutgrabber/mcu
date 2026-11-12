"""Builds the published page: src/template.html + src/data.json + src/charts.json + src/ratings.json -> index.html, and writes w/index.html.
Run from anywhere: python3 src/build.py. With --check it writes nothing and fails if the committed files are out of date."""
import pathlib, sys
SRC=pathlib.Path(__file__).resolve().parent; ROOT=SRC.parent
t=(SRC/'template.html').read_text()
d=(SRC/'data.json').read_text().replace('</','<\\/')
c=(SRC/'charts.json').read_text().replace('</','<\\/')
r=(SRC/'ratings.json').read_text().strip().replace('</','<\\/')
assert t.count('/*DATA*/')==1 and t.count('/*CHARTS*/')==1 and t.count('/*RATINGS*/')==1
out=t.replace('/*DATA*/',d).replace('/*CHARTS*/',c).replace('/*RATINGS*/',r)
stub='''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A Marvel watched list, shared with you</title>
<meta name="description" content="Open it to see what they've watched, compare it with your own list, or add it to yours.">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#1A1838">
<link rel="icon" href="../favicon.ico" sizes="32x32">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="../apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="hut's mcu helper">
<meta property="og:title" content="A Marvel watched list, shared with you">
<meta property="og:description" content="Open it to see what they've watched, compare it with your own list, or add it to yours.">
<meta property="og:url" content="https://mcu.hutlab.dev/w/">
<meta property="og:image" content="https://mcu.hutlab.dev/og-list.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="My Marvel watched list: a tub of popcorn, red and blue 3D glasses and film strips with ticked frames.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="A Marvel watched list, shared with you">
<meta name="twitter:description" content="Open it to see what they've watched, compare it with your own list, or add it to yours.">
<meta name="twitter:image" content="https://mcu.hutlab.dev/og-list.png">
<script>
/* This page exists so shared lists get their own preview card. It hands the code to the main page straight away. */
(function(){
  var c = (location.hash || "").replace(/^#(w=)?/, "") || (location.search || "").slice(1).split("&")[0];
  c = /^[\\w-]{1,80}$/.test(c) ? c : "";
  location.replace("../" + (c ? "#w=" + c : ""));
})();
</script>
<style>
html{background:#1A1838;color:#EEEBFF;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
body{margin:0;min-height:100vh;display:grid;place-items:center;text-align:center;padding:24px}
a{color:#3CE7FF}
</style>
</head>
<body>
<p>Opening the watched list. <a href="../">Continue to hut's mcu helper</a></p>
</body>
</html>
'''
files={ROOT/'index.html': out, ROOT/'w'/'index.html': stub}

# A calendar file for each dated release in "Coming up". An iPhone or iPad opens it to show Calendar's own "Add" sheet;
# other computers download it. Android uses Google Calendar's own page instead, built in the page from the same details.
import datetime, json, re
def slug(t): return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', t.lower()))
def ics_text(t): return re.sub(r'<[^>]+>', '', t).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,').replace('\n', '\\n')
def fold(line):
    """Calendar lines longer than 75 bytes continue on the next line, which starts with a space"""
    out, cur = [], ''
    for ch in line:
        if len((cur + ch).encode()) > (75 if not out else 74): out.append(cur); cur = ''
        cur += ch
    return '\r\n '.join(out + [cur])
cals = {}
for s in json.loads((SRC/'charts.json').read_text())['soon']:
    if s.get('month'): continue
    day = datetime.date.fromisoformat(s['date']); a, b = day.strftime('%Y%m%d'), (day + datetime.timedelta(days=1)).strftime('%Y%m%d')
    lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', "PRODID:-//hut's mcu helper//EN", 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'BEGIN:VEVENT',
             'UID:' + a + '-' + slug(s['title']) + '@mcu.hutlab.dev', 'DTSTAMP:' + a + 'T000000Z', 'DTSTART;VALUE=DATE:' + a, 'DTEND;VALUE=DATE:' + b,
             'SUMMARY:' + ics_text(s['title'] + (' opens in cinemas' if s['kind'] == 'Film' else ' premieres')),
             'DESCRIPTION:' + ics_text(s['note'] + ' Release dates can move. https://mcu.hutlab.dev/#soon'), 'URL:https://mcu.hutlab.dev/#soon',
             'TRANSP:TRANSPARENT', 'END:VEVENT', 'END:VCALENDAR']
    cals[ROOT/'cal'/(slug(s['title']) + '.ics')] = '\r\n'.join(fold(l) for l in lines) + '\r\n'
files.update(cals)
stale=[p for p in (ROOT/'cal').glob('*.ics') if p not in cals] if (ROOT/'cal').exists() else []

if '--check' in sys.argv:
    bad=[str(p.relative_to(ROOT)) for p,text in files.items() if not p.exists() or p.read_bytes().decode()!=text]+[str(p.relative_to(ROOT))+' (no longer listed)' for p in stale]
    if bad: sys.exit('Out of date, run python3 src/build.py: '+', '.join(bad))
    print('Up to date')
else:
    for p,text in files.items(): p.parent.mkdir(exist_ok=True); p.write_bytes(text.encode())
    for p in stale: p.unlink()
    print(len(out))

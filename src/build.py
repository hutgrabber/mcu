"""Builds the published page: src/template.html + src/data.json + src/charts.json -> index.html, and writes w/index.html.
Run from anywhere: python3 src/build.py. With --check it writes nothing and fails if the committed files are out of date."""
import pathlib, sys
SRC=pathlib.Path(__file__).resolve().parent; ROOT=SRC.parent
t=(SRC/'template.html').read_text()
d=(SRC/'data.json').read_text().replace('</','<\\/')
c=(SRC/'charts.json').read_text().replace('</','<\\/')
assert t.count('/*DATA*/')==1 and t.count('/*CHARTS*/')==1
out=t.replace('/*DATA*/',d).replace('/*CHARTS*/',c)
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
if '--check' in sys.argv:
    stale=[str(p.relative_to(ROOT)) for p,text in files.items() if not p.exists() or p.read_text()!=text]
    if stale: sys.exit('Out of date, run python3 src/build.py: '+', '.join(stale))
    print('Up to date')
else:
    for p,text in files.items(): p.parent.mkdir(exist_ok=True); p.write_text(text)
    print(len(out))

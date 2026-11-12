"""Fetches IMDb ratings and Rotten Tomatoes scores from OMDb (https://www.omdbapi.com) into src/ratings.json.

Run it now and then, then rebuild:  python3 scripts/ratings.py && python3 src/build.py
It needs an OMDb key, read from the OMDB_API_KEY environment variable or a line OMDB_API_KEY=... in .env at the repo root.
The key stays on this machine: visitors' browsers never call OMDb, they read the saved ratings from the page.

Each title's IMDb id is in src/imdb.json, with "omdbTitle" where OMDb's name for it differs from the site's. Every answer is checked against the site's own title and year before anything
is saved, so a wrong id fails loudly instead of putting another film's score on the page. A season ("Loki, Season 1")
gets the average IMDb rating of its episodes; Rotten Tomatoes scores for single seasons aren't available from OMDb."""
import datetime, json, os, pathlib, re, sys, time, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"


def api_key():
    key = os.environ.get("OMDB_API_KEY", "").strip()
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("OMDB_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit("No OMDb key. Put OMDB_API_KEY=yourkey in .env at the repo root, or set it in the environment.")
    return key


def omdb(key, **params):
    url = "https://www.omdbapi.com/?" + urllib.parse.urlencode({**params, "apikey": key})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "mcu-helper-ratings/1.0"}), timeout=30) as r:
                data = json.load(r)
            if data.get("Response") == "False" and "limit" in data.get("Error", "").lower():
                sys.exit("OMDb says the daily request limit is reached. Try again tomorrow.")
            if data.get("Response") == "False" and "invalid api key" in data.get("Error", "").lower():
                sys.exit("OMDb doesn't accept the key. Check OMDB_API_KEY, and that the key was activated from its email.")
            return data
        except (OSError, ValueError) as err:
            if attempt == 2:
                raise SystemExit(f"Couldn't reach OMDb: {err}")
            time.sleep(2 * (attempt + 1))


norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("&", "and"))
number = lambda s: float(s) if s and re.fullmatch(r"\d+(\.\d+)?", s) else None


def same_title(ours, theirs):
    """OMDb sometimes adds a subtitle ("X2: X-Men United") or Netflix's "Marvel's" prefix. The year check catches a sequel."""
    a, b = norm(ours), norm(theirs)
    return a == b or b.startswith(a) or a.startswith(b) or b == "marvels" + a


def main():
    key = api_key()
    entries = json.loads((SRC / "data.json").read_text())["entries"]
    ids = json.loads((SRC / "imdb.json").read_text())
    today = datetime.date.today()
    titles, problems = {}, []
    for sid, info in ids.items():
        e = entries[int(sid)]
        released = not e["upcoming"] and datetime.date.fromisoformat(e["date"]) <= today
        if not released:
            continue
        base = re.sub(r", Season \d+$", "", e["title"])
        d = omdb(key, i=info["imdb"])
        if d.get("Response") == "False":
            problems.append(f'{e["title"]}: OMDb has nothing for {info["imdb"]} ({d.get("Error")})')
            continue
        year = int(re.match(r"\d{4}", d.get("Year", "0")).group(0)) if re.match(r"\d{4}", d.get("Year", "")) else None
        wrong = []
        if not same_title(info.get("omdbTitle", base), d.get("Title", "")):
            wrong.append(f'title "{d.get("Title")}"')
        if "season" not in info and (year is None or abs(year - e["year"]) > 1):
            wrong.append(f'year {d.get("Year")}')
        if (d.get("Type") == "series") != (e["kind"] == "show") and e["kind"] != "special":
            wrong.append(f'type {d.get("Type")}')
        if wrong:
            problems.append(f'{e["title"]} ({e["year"]}): {info["imdb"]} is {", ".join(wrong)}. Fix its id in src/imdb.json.')
            continue
        r = {}
        if "season" in info:
            s = omdb(key, i=info["imdb"], Season=info["season"])
            eps = [number(x.get("imdbRating")) for x in s.get("Episodes", [])]
            eps = [x for x in eps if x is not None]
            if eps:
                r["imdb"] = round(sum(eps) / len(eps), 1)
                r["eps"] = len(eps)
        else:
            if number(d.get("imdbRating")) is not None:
                r["imdb"] = number(d["imdbRating"])
            votes = d.get("imdbVotes", "").replace(",", "")
            if votes.isdigit():
                r["votes"] = int(votes)
            rt = next((x["Value"] for x in d.get("Ratings", []) if x.get("Source") == "Rotten Tomatoes"), None)
            if rt and re.fullmatch(r"\d{1,3}%", rt):
                r["rt"] = int(rt[:-1])
        if r:
            titles[sid] = r
        time.sleep(0.1)
    if problems:
        print("Nothing saved. These need fixing first:\n  " + "\n  ".join(problems), file=sys.stderr)
        sys.exit(1)
    out = {"asOf": today.isoformat(), "source": "OMDb", "titles": titles}
    (SRC / "ratings.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n")
    rated = sum(1 for r in titles.values() if "imdb" in r)
    print(f"Saved ratings for {len(titles)} titles ({rated} with an IMDb rating, "
          f"{sum(1 for r in titles.values() if 'rt' in r)} with a Rotten Tomatoes score). Now run python3 src/build.py")


if __name__ == "__main__":
    main()

# MCU Helper
A quick tool for understanding and managing your MCU watch list. Live at [mcu.hutlab.dev](https://mcu.hutlab.dev).

## Layout

GitHub Pages serves the repo root, so the built site lives there: `index.html`, `w/index.html` (the page shared lists open through, so they get their own preview card), the icons, `og.png`, `og-list.png`, `site.webmanifest`, `CNAME` and `.nojekyll`. Don't move or rename any of these.

| Folder | Holds |
|---|---|
| `src/template.html` | The page itself: styles, markup and script, with two placeholders, `/*DATA*/` and `/*CHARTS*/` |
| `src/data.json` | Every title and its story text. Edit content here. |
| `src/charts.py` | Phases, routes, the "Coming up" list, the share order and the section charts. Writes `src/charts.json`. |
| `src/build.py` | Fills the template and writes `index.html`, `w/index.html` and the calendar files in `cal/` to the root |
| `src/imdb.json`, `src/ratings.json` | Each title's IMDb id, and the ratings fetched by `scripts/ratings.py` |
| `src/watch-guide.md` | The long-form guide the data first came from (current as of November 8, 2026) |
| `scripts/assets.py` | Draws the icons, favicons and preview cards, and writes `site.webmanifest` |
| `scripts/legacy/` | The first steps that turned the guide into raw data. Kept for reference only. |
| `tests/` | Playwright tests, the test server and the Docker image |
| `tests/fixtures/` | Frozen copies of the share order and of links already shared. Never edit these to make a test pass. |
| `.claude/agents/content-editor.md` | The content-editor agent, and `.claude/skills/update-site/` the `/update-site` command that runs it |
| `firebase/firestore.rules` | The security rules for the synced watched lists. The site has no server, so these rules are its backend. |

## Building

The build needs only Python 3, with nothing to install.

```bash
python3 src/charts.py && python3 src/build.py
```

To check that the committed page matches the source without writing anything:

```bash
python3 src/build.py --check
```

Commit the source change and the rebuilt `index.html` together.

## Testing and other tools

Everything else runs in Docker, so only Docker Desktop is needed on the Mac. The first run builds the image and installs the test tools into a Docker volume, which takes a few minutes.

```bash
docker compose run --rm dev npm test
```

That checks the build is current and runs the Playwright tests against a local copy of the site: the rules for ids and share order, share links old and new, comparing, Undo, story drawers and Back, search, celebrations, and every screen size from 320 pixels wide to 1920 in both themes. To run them against the Firebase emulator too:

```bash
docker compose run --rm dev npm run test:all
```

That adds the sync tests, which sign two or three browsers into the same pretend Google account and check that ticks, Undo, settings, sign-out, deletion and offline changes all behave, and the security rules tests: only you can read, change or delete your own document, only Google sign-in counts, nothing else in the database can be touched, and a document can only hold the known fields within their size limits.

The emulator uses the project id `demo-mcu`, which Firebase treats as offline only, so tests can never touch the real project.

To redraw the icons and preview cards after changing `scripts/assets.py`:

```bash
docker compose run --rm dev npm run assets
```

The icons come out pixel for pixel the same as the published ones. The preview cards don't: Google Fonts renders the text slightly narrower than the font files the chat sandbox used, which moves one line break on `og-list.png`. Check both cards by eye before committing new ones.

## Syncing across devices

Signing in is optional: without an account the site keeps everything in the browser, as it always has. With an account, the watched list, theme, spoiler setting and last route follow you to every device you sign in on.

- **Sign-in** is Google only, in a pop-up window. The Firebase browser modules load only for people who sign in.
- **Storage** is one Firestore document per person (`users/{their user id}`). It holds an entry per title, saying whether it's watched and when that last changed, so two devices merge by keeping the later change. The page code is in `src/template.html`, in the sections headed "syncing across devices".
- **Writes** are batched: one write two seconds after the last change, or when the tab is hidden. Before writing, the page fetches the account's list unless it did so in the last 30 seconds, so an old change can't overwrite a newer one.
- **Sign-in is remembered:** Firebase keeps it in the browser, so you sign in once per browser, not once per visit. The sign-in button only comes back if that saved sign-in really ends, such as after clearing the site's data. If Firebase can't load when the page opens (offline, say), you stay signed in and the page catches up once it can.
- **Reads** happen when the page opens, whenever the tab comes back into view, and every minute while you're using the page. The every-minute sync pauses after ten minutes without a tap, key press or scroll, so a tab left open all day doesn't use up the free daily reads, and it syncs again on the next tap. It also retries any write that failed.
- **The first sign-in** on a browser merges both lists, and anything watched on either side stays watched.
- **Signing out** clears the list and settings from that browser. "Delete my account and synced list" removes the document and the account.

The Firebase project is `backend-mcu`. Its web config sits in `FIREBASE` in `src/template.html`; it's public by design, and the security rules are what protect the data. In `.firebaserc`, `default` is the offline emulator project and `live` is the real one, so a command only touches the real project when it says `--project live`.

To put a change to `firebase/firestore.rules` live, sign the Firebase tool into your Google account once (it opens a link to approve in your browser and remembers the sign-in in a Docker volume), then deploy:

```bash
docker compose run --rm dev npx firebase login --no-localhost
```

```bash
docker compose run --rm dev npm run deploy:rules
```

Run the tests first: the rules only go live after `npm run test:all` passes on them.

On `localhost`, the page signs in and syncs through the Firebase emulator, so local testing never touches the real project. Add `?live` to the address to use the real project instead.

## Updating the content with the content-editor agent

`.claude/agents/content-editor.md` is a Claude Code agent, running on Claude Opus 5.5, that keeps the site's content current. It researches the latest Marvel release information, or makes the small text change you ask for, then rebuilds the page, runs the tests and opens a pull request.

From a Claude Code session in this folder:

- `/update-site fix the typo in Thor's story`: a small text change. Once the tests pass on GitHub, it merges on its own and goes live.
- `/update-site add the release date for Blade`: research. It checks reliable sources and opens a pull request listing each fact and where it came from, for you to review and merge.
- `/update-site`: a full refresh. It checks for every change since the footer's "Current as of" date and opens a pull request for review.

To publish research without reviewing it, say so in the request, for example `/update-site add Blade's release date and publish it`. You can also call the agent by name, for example "use the content-editor agent to …", or with `@content-editor`.

The agent only edits `src/data.json`, `src/charts.py` and the text in `src/template.html`. It never touches the sync code, the security rules or the tests, and it never pushes to `main` directly. Docker Desktop needs to be running, because it runs the tests before opening a pull request. The tests also check every entry's shape: the right fields and types, real dates, only the expected markup, no em or en dashes, and ids that exist.

## Ratings

Cards, stories and the "How they were received" charts show each title's IMDb rating and Rotten Tomatoes Tomatometer. They come from [OMDb](https://www.omdbapi.com), fetched while building, so visitors' browsers never call it and the key never reaches the site.

- `src/imdb.json` holds each title's IMDb id. A single season points at its series and names the season, and gets the average IMDb rating of its episodes.
- `src/ratings.json` holds the saved ratings. Don't edit it by hand.

To refresh them, put your free OMDb key in `.env` at the repo root (git ignores it) as `OMDB_API_KEY=yourkey`, then:

```bash
python3 scripts/ratings.py && python3 src/build.py
```

**They refresh on their own every Monday.** `.github/workflows/ratings.yml` runs the script on GitHub with the key stored as the repository secret `OMDB_API_KEY`, rebuilds the page, runs the full test suite on a temporary branch, and moves `main` to it only if every test passes. To refresh straight away, open the repo's **Actions** tab, choose **Refresh ratings**, then **Run workflow**. If it fails, for example because a title's IMDb id no longer matches, GitHub emails you and the site keeps its last ratings.

Every answer is checked against the site's own title, year and type before anything is saved, so a wrong id stops the script instead of showing another film's score. The free key allows 1,000 requests a day, and a refresh uses about 110. You can also ask the content agent: `/update-site refresh the ratings`.

## Adding a release to a calendar

"Add to calendar" in "Coming up" does what each device handles best. The build writes a calendar file for each dated release into `cal/`, and the page picks:

- **iPhone and iPad:** opens that file, which iOS shows in Calendar's own "Add" sheet.
- **Android and Chromebooks:** opens Google Calendar's new-event screen, filled in.
- **Mac, Windows and Linux:** downloads the file for whatever calendar app the computer uses.

## Rules that keep shared links working

- **Never renumber, reorder or insert entries in `src/data.json`.** An entry's `id` is its position in the list, and synced lists will store ids. Add new titles at the end.
- **Only ever append to `share_order` in `src/charts.py`.** Share codes are written against that order, so any other change makes old links open the wrong list.
- **Don't run `scripts/legacy/parse.py` over `src/data.json`.** The data was edited by hand after parsing, and those edits would be lost.

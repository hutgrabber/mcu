# MCU Helper
A quick tool for understanding and managing your MCU watch list. Live at [mcu.hutlab.dev](https://mcu.hutlab.dev).

## Layout

GitHub Pages serves the repo root, so the built site lives there: `index.html`, `w/index.html` (the page shared lists open through, so they get their own preview card), the icons, `og.png`, `og-list.png`, `site.webmanifest`, `CNAME` and `.nojekyll`. Don't move or rename any of these.

| Folder | Holds |
|---|---|
| `src/template.html` | The page itself: styles, markup and script, with two placeholders, `/*DATA*/` and `/*CHARTS*/` |
| `src/data.json` | Every title and its story text. Edit content here. |
| `src/charts.py` | Phases, routes, the "Coming up" list, the share order and the section charts. Writes `src/charts.json`. |
| `src/build.py` | Fills the template and writes `index.html` and `w/index.html` to the root |
| `src/watch-guide.md` | The long-form guide the data first came from (current as of November 8, 2026) |
| `scripts/assets.py` | Draws the icons, favicons and preview cards, and writes `site.webmanifest` |
| `scripts/legacy/` | The first steps that turned the guide into raw data. Kept for reference only. |
| `tests/` | Playwright tests, the test server and the Docker image |
| `tests/fixtures/` | Frozen copies of the share order and of links already shared. Never edit these to make a test pass. |
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

On `localhost`, the page signs in and syncs through the Firebase emulator, so local testing never touches the real project. Add `?live` to the address to use the real project instead. Until the real project's config is filled in (`FIREBASE` in `src/template.html`), the published site doesn't offer sign-in at all.

## Rules that keep shared links working

- **Never renumber, reorder or insert entries in `src/data.json`.** An entry's `id` is its position in the list, and synced lists will store ids. Add new titles at the end.
- **Only ever append to `share_order` in `src/charts.py`.** Share codes are written against that order, so any other change makes old links open the wrong list.
- **Don't run `scripts/legacy/parse.py` over `src/data.json`.** The data was edited by hand after parsing, and those edits would be lost.

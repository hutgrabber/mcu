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
| `tests/legacy/` | The test scripts from the chat sessions, still to be ported |

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

## Rules that keep shared links working

- **Never renumber, reorder or insert entries in `src/data.json`.** An entry's `id` is its position in the list. Add new titles at the end.
- **Only ever append to `share_order` in `src/charts.py`.** Share codes are written against that order, so any other change makes old links open the wrong list.
- **Don't run `scripts/legacy/parse.py` over `src/data.json`.** The data was edited by hand after parsing, and those edits would be lost.

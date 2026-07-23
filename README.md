# docs.tiknix

Article-style documentation for the Tiknix framework. Flat static HTML — no server-side
code, no runtime dependencies.

## Layout

```
build.py                  # wraps fragments in the shared shell, writes public/
src/index-intro.html      # hero + stats + "how to read this" block on the index
src/articles/<slug>.html  # one body fragment per article (no <html>/<head>/nav)
public/                   # BUILD OUTPUT — serve this directory
  index.html
  <slug>.html
  assets/docs.css         # design tokens ported from tiknix's design-system.php
  assets/docs.js          # theme toggle + mobile sidebar
  img/tiknix.svg
```

## Build

```bash
python3 build.py
```

Rebuilds `public/index.html` and every article. Output is deterministic — safe to
re-run and commit.

## Editing

- **Article text** → edit `src/articles/<slug>.html`, rebuild.
- **Title, category, blurb, read time, order** → edit the `ARTICLES` list in `build.py`.
  Order in that list drives the index, the sidebar, the article numbering, and the
  prev/next links.
- **New article** → add a fragment in `src/articles/` and a matching row in `ARTICLES`.
- **New category** → add to `CATEGORIES` and `CHIP_CLASS` in `build.py`.
- **Design** → `public/assets/docs.css`. Tokens at the top mirror
  `tiknix/views/components/design-system.php`; keep them in sync when the app's
  palette changes.

Do not hand-edit files in `public/` — the next build overwrites them.

## Fragment conventions

A fragment is body HTML only. The build adds the `<h1>`, category chip, article
number, lede, sidebar, topbar, and prev/next nav.

- `<h2>` for sections, `<h3>` for subsections.
- Code: `<pre><code>…</code></pre>`. Escape `<` and `&`.
- Tables: wrap in `<div class="table-wrap">` so they scroll on mobile.
- Callouts: `<div class="callout callout-tip">` or `callout-honest`, with a
  `<span class="callout-title">` label.
- **Every article ends with an `Honest notes` callout** — trade-offs, sharp edges, and
  what the framework does not do. That is the editorial contract for this series.

## Serving

Point a web server at `public/`. For a quick local preview:

```bash
cd public && php -S 127.0.0.1:8799
```

Links are root-relative (`/assets/docs.css`, `/build-on-primitives.html`), so the site
must be served from a domain root, not a subdirectory.

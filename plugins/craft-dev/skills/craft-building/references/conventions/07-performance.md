<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## 13. Performance

Page performance is a first-class requirement, not an afterthought — **on every layer**: PHP, Twig, CSS, JavaScript, and the number of requests the page makes. **All Lighthouse categories must stay green** (90+), and Core Web Vitals are the budget: **LCP < 2.5s**, **CLS < 0.1**, **INP < 200ms**. Check Lighthouse (mobile) before and after any change that touches the layout, images, fonts, or JS.

### 13.1 PHP & Twig

- **Eager-load in the adapter/organism layer** — the same place queries happen: `.with(['image', 'items:commonImage'])` in block adapters, `.eagerly()` on lazy matrix relations. Molecules receive resolved data. **No N+1 queries**: an element query inside a `{% for %}` loop is a bug — hoist it and eager-load.
- For deep builders, keep **eager-loading maps in `variables.twig`** on `_globals` (e.g. `_globals.set('pageBuilderEagerLoading', [...])`) so depth is controlled in one place.
- **Query once per request**: anything used twice (navigation, switcher links, newsletter settings) is stashed on `_globals` (§5.3). Never repeat a global query in two components.
- **Fetch only what you render**: `.limit()` on every overview query, `.count()` instead of `|length` on a query, `.exists()` instead of fetching to test emptiness, `.select()`/field-limited queries for large lists.
- Twig stays thin: templates render, they don't compute. Repeated expressions get a `{% set %}` once in the Variables section; heavy logic belongs in a Twig extension or module, not in a loop body.
- `{% cache %}` around genuinely expensive fragments (large overviews) — not around everything. In PHP (plugins/modules), use Craft's cache service for expensive derived data.
- Production hygiene: `devMode` off, a real queue runner (`runQueueAutomatically(false)` + a daemon/cron), opcache on.

### 13.2 Images — optimized *and* sharp

All content images go through the `image` atom; these rules live there once:

- **webp** for everything except SVG/GIF, via named transforms (§10.7). Quality tuned per transform (~80 is usually right); never ship originals.
- **Sharp on every screen**: a `srcset` with 1x/2x density variants (or a width series + correct `sizes`) so retina displays get a genuinely larger source. Optimized never means blurry — if an image looks soft at 2x, the transform set is too small.
- **Sized, so nothing shifts**: always render intrinsic `width`/`height` (or `aspect-ratio` in CSS) — CLS from images must be zero.
- **Lazy by default, eager for the hero**: `loading="lazy" decoding="async"` below the fold; the LCP image gets `loading="eager"` + `fetchpriority="high"` (an `eager` param on the atom, set by hero molecules).

### 13.3 Frontend delivery — CSS, JS, requests

- **Few requests by architecture**: one JS bundle + one CSS bundle (the single Vite entry), icons inlined as SVG in the markup (§7.2 — zero icon requests), no CDN libraries, no icon fonts, at most 2–3 font files. Every additional request on the critical path needs a reason.
- **CSS stays small**: only component styles that exist in the project (the glob imports nothing unused), no utility-class frameworks, no resets beyond `00_fundamentals`. Dead component = deleted folder = deleted CSS.
- **JS stays tiny** because there is no framework (§9); components only instantiate when their selector matches, and anything CSS can do is done in CSS (§8.3). Heavy dependencies (a slider library) must earn their bytes — prefer scroll-snap first. Debounce/passive-listen scroll and resize handlers; use `IntersectionObserver`, never scroll-position polling.
- **Fonts**: preconnect (or self-host + preload the woff2), `font-display: swap`, subset to the weights actually used in `_fonts-config.scss` — no 9-weight families.
- **Tracking last**: analytics load at the end of `<body>` (`meta/_tracking.twig`), deferred — third-party scripts never block rendering.
- Mobile first (§8.3) doubles as a performance rule: the base payload is the small-screen one.

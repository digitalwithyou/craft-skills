<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## 11. i18n

- Multi-site per language, one site group; the primary language is canonical.
- **Every user-facing string that isn't authored content goes through `|t('site')`**: `{{ 'articles.overview.filter'|t('site') }}`. No exceptions — including `aria-label`s, button labels, and form placeholders.
- Translations live in `translations/<lang>/site.php`, flat arrays. Prefer dotted, namespaced keys (`'newsletter.input.submit.label' => 'Inschrijven'`); English-source keys are acceptable for the CTA-fallback strings (§10.3).
- Localized section URIs are configured per-site in the CP — **`config/routes.php` is only for feeds**:

  ```php
  return [
      'dutch' => [
          'artikels.rss' => ['template' => '00_feeds/articles.rss.twig'],
      ],
      'english' => [
          'articles.rss' => ['template' => '00_feeds/articles.rss.twig'],
      ],
  ];
  ```

## 12. SEO, meta, semantics, accessibility, errors, feeds

- **`00_fundamentals/meta/`** holds `_seo.twig` (title/description/canonical/og + **hreflang alternates** built from the same per-site URL list as the language switcher), `_feed.twig` (feed `<link>`s), `_tracking.twig` (analytics, included last in `<body>`). All three are included from `_master.twig` only.

### 12.1 HTML semantics

Respect and use HTML semantics — the element **is** the meaning:

- Landmarks: one `<main>`, `<header>`/`<footer>` for chrome, `<nav>` (with `aria-label` when there's more than one), `<section>`/`<article>`/`<aside>` where they apply. Never a `<div>` where a semantic element exists.
- One `<h1>` per page; heading levels descend without skipping — the `heading` atom's `level` param exists so the *parent* sets the correct level per context, decoupled from visual size (style via class, not tag).
- Links navigate (`<a href>`), buttons act (`<button type="button|submit">`). Never a click handler on a `<div>`, never an `<a>` without `href`.
- Native elements before ARIA widgets: `<details>`/`<summary>` for accordions, `<dialog>` for modals, `<time datetime>` in the `date` atom, `<figure>`/`<figcaption>`, real `<ul>`/`<ol>` for lists, `<label>` bound to every control (the `form-field` atom enforces this). ARIA supplements semantics, it never replaces them.

### 12.2 Accessibility baseline

Every component ships with at least this — it is part of a block's definition of done (§15.1):

- **Full keyboard support**: everything interactive is reachable and operable by keyboard, in a logical order. Menus, modals and dropdowns handle `Escape` and trap/return focus appropriately; no positive `tabindex`.
- **Visible focus**: `:focus-visible` styles on every interactive element — never `outline: none` without a replacement.
- **Readability**: body text ≥ 16px (`1rem`), line-height ≈ 1.5 for copy, line length capped (`max-inline-size` in `ch`), WCAG AA contrast for text and interactive states — verify tokens in both themes.
- Skip link as the first body element (`.text-assistive` visually-hidden utility) targeting `<main id="main">`; ARIA-patterned navigation/breadcrumbs/dialogs with generated ids for `aria-controls` wiring; `fill="currentColor"` icons with text alternatives; meaningful `alt` on content images, empty `alt` on decorative ones; honor `prefers-reduced-motion` (§8.3).
### 12.3 Errors, feeds, theming

- **Error pages**: `errorTemplatePrefix('04_templates/errors/_')` → `_404.twig` / `_500.twig`, which render like normal pages using content from the `notFound` / `serverError` globals (hero + page-builder included, so editors control the copy).
- **Feeds**: RSS/Atom templates in `00_feeds/`, routed per-site (§11).
- Optional **theme toggle** pattern: `html[data-theme]` + no-flash bootstrap in the layout + `theme-toggle` atom persisting to `localStorage`.

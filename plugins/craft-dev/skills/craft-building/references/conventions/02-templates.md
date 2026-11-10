<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## Contents

- 5. Template architecture
- 5.1 The atomic layers
- 5.2 Per-component folder contract
- 5.3 The extends chain
- 5.4 `_routing.twig` — one entry point for the whole site
- 5.5 The rendering chain
- 6. Template file convention
- 7. Component catalog
- 7.1 Foundational atoms
- 7.2 Icon system
- 7.3 Typical molecules
- 7.4 Organisms
- 7.5 Templates (`04_templates/`)

## 5. Template architecture

### 5.1 The atomic layers

Everything frontend lives under `templates/`, in depth-prefixed folders:

```
templates/
├── 00_config/          design tokens (_colors-config.scss, _fonts-config.scss,
│                       _breakpoints-config.scss, _animations-config.scss)
│                       + variables.twig (site vars, _globals cache — see §5.3)
├── 00_fundamentals/    reset/ (in @layer reset) boxing/ typography/ colors/
│                       utilities/ animations/
│                       meta/ (_seo.twig, _feed.twig, _tracking.twig) vendors/
├── 00_feeds/           RSS / Atom templates (routed via config/routes.php)
├── 00_mails/           transactional mail templates
├── 00_layouts/         _master.twig — extended by _routing.twig
├── 01_atoms/           smallest building blocks: buttons, icons, heading,
│                       rich-text, image, link, form-field, …
├── 02_molecules/       composed components: cards, navigation-*, forms,
│                       page-block-*, section-label, …
├── 03_organisms/       page regions: site-header, site-footer, page-builder,
│                       article-builder, hero, footer (CTA band), …
├── 04_templates/       _routing.twig + one folder per entry type
└── site.js             the single Vite entry (see §9)
```

### 5.2 Per-component folder contract

**One folder per component. The folder holds everything the component is made of:**

```
templates/02_molecules/page-block-pillars/
├── _page-block-pillars.twig     Twig template
├── _page-block-pillars.scss     scoped styles
└── PageBlockPillars.js          optional interactivity
```

Naming rules:

- Folder name is kebab-case and **is** the BEM block name: folder `page-block-pillars` → root class `.page-block-pillars`.
- **All `.twig` and `.scss` filenames start with `_`** and match the folder name. (SCSS `@use` imports drop the underscore: `@use '../../00_config/colors-config' as *;`.)
- JS files are PascalCase class files with **no** underscore: `PageBlockPillars.js`, default-exporting one ES class.
- Builder block adapters (see §5.5) are the one camelCase exception: `_pageBlockPillars.twig`, matching the entry-type handle exactly.
- Deleting a component = deleting one folder (plus its line in `site.js` if it had JS).

### 5.3 The extends chain

Three levels, computed before any markup:

```
00_config/variables.twig   ← site-wide variables + _globals request cache
        ▲ extends
00_layouts/_master.twig    ← the HTML document
        ▲ extends
04_templates/_routing.twig ← template dispatch (§5.4)
```

**`00_config/variables.twig`** sets `siteLanguageCode`, `bodyAttributes`, language-switcher links, and stashes anything needed in more than one place on Craft 5's request-scoped `_globals` collection — so it is queried exactly once:

```twig
{#
    The navigation is managed by globals. It is needed in both the main
    navigation and the footer navigation, so we load it once and share it.
#}
{% do _globals.set('mainMenu', navigation.navigationMatrix.all()) %}
```

It ends with `{% block html %}{% endblock %}` — the only output it defines.

**`00_layouts/_master.twig`** overrides `{% block html %}` with the document: doctype, meta viewport, `{% include "00_fundamentals/meta/_seo" %}` + `_feed`, the single `craft.vite.script(...)` line, a skip link (`<a class="text-assistive" href="#main">{{ 'main.skip.label'|t('site') }}</a>`), `03_organisms/site-header`, `<main id="main">{% block main %}{% endblock %}</main>`, `03_organisms/site-footer`, and `meta/_tracking`. No `no-js`/`js` class on `<html>`: styles for visitors without JavaScript go in `@media (scripting: none)`. If the design has a light/dark theme, the no-flash bootstrap script (an inline IIFE reading `localStorage` before paint and setting `html[data-theme]`) also lives here.

### 5.4 `_routing.twig` — one entry point for the whole site

Every section's `siteSettings.template` in Project Config points at `04_templates/_routing.twig`. All template selection is one readable switch on the entry-type handle:

```twig
{% extends "00_layouts/_master" %}

{# Variables #}

{% if entry is defined %}
    {% set handle = entry.type.handle %}
{% elseif category is defined %}
    {% set handle = category.group.handle %}
    {% set entry = category %}
{% else %}
    {% exit 404 %}
{% endif %}

{% set overviewPage = null %}
{% set templatePath = null %}
{% set headPath = null %}

{# Routes #}

{% switch handle %}

    {% case "pageHome" %}
        {% set templatePath = "04_templates/home/_home" %}

    {% case "pageGeneric" %}
        {% set templatePath = "04_templates/generic/_generic" %}
        {% set headPath = "04_templates/generic/_head" %}

    {% case "pageArticleOverview" %}
        {% set templatePath = "04_templates/article-overview/_article-overview" %}

    {% case "article" %}
        {% set overviewPage = craft.entries().section('pages').type('pageArticleOverview').one() %}
        {% set templatePath = "04_templates/article/_article" %}
        {% set headPath = "04_templates/article/_head" %}

    {% default %}
        {% exit 404 %}

{% endswitch %}


{# Output #}

{% block main %}
    {% include templatePath with {
        overviewPage: overviewPage,
        entry: entry,
    } only %}
{% endblock %}

{% block head %}
    {{ parent() }}
    {% if headPath %}
        {% include headPath with {
            overviewPage: overviewPage,
            entry: entry,
        } only %}
    {% endif %}
{% endblock %}
```

Rules and options:

- `{% default %}{% exit 404 %}` — an unrouted entry type fails loudly. Add a `{% case %}` for every new entry type.
- Channel detail pages resolve their `overviewPage` here (for breadcrumbs/back links), not in the leaf template.
- Optional per-page `_head.twig` for extra head markup (structured data, per-type meta).
- *Optional escape hatch* for bespoke landing pages — a slug-specific override array:

  ```twig
  {% case "pageEvent" %}
      {% set templatePath = [
          "04_templates/event/custom/_" ~ entry.slug,
          "04_templates/event/_event",
      ] %}
  ```

  with `{% include templatePath ... ignore missing %}`. Beware: renaming the slug silently drops the custom template.

A leaf template under `04_templates/<x>/` is tiny — it only composes organisms:

```twig
{# 04_templates/generic/_generic.twig #}
{% include "03_organisms/hero/_hero" %}
{% include "03_organisms/page-builder/_page-builder" %}
{% include "03_organisms/footer/_footer" with { blocks: entry.footer.all() } only %}
```

### 5.5 The rendering chain

```
_routing.twig
  → 04_templates/<type>/_<type>.twig          (composes organisms)
    → 03_organisms/page-builder/_page-builder.twig   (matrix dispatcher)
      → 03_organisms/page-builder/blocks/_pageBlockFoo.twig   (thin adapter — the ONLY
                                                               place block.* is read)
        → 02_molecules/foo/_foo.twig          (explicit params, CMS-agnostic)
          → 01_atoms/…                        (primitives)
```

The **builder dispatcher** is ~10 lines and identical for every builder (`page-builder`, `article-builder`, `case-builder`, `hero`, `footer`):

```twig
{#
    Organism: Page Builder

    When blocks are passed as an array, we assume they are already eager loaded.

    @param {array[Entry]} blocks (optional)
#}

{# Variables #}

{% if entry is defined %}
    {% set blocks = blocks ?? entry.pageBuilder %}
{% endif %}


{# Output #}

{% for block in blocks %}
    {% include "03_organisms/page-builder/blocks/_" ~ block.type ignore missing %}
{% endfor %}
```

The `blocks = blocks ?? entry.pageBuilder` contract lets the same file serve the default path, an eager-loaded override, and the shared-blocks recursion (§10.4).

The **block adapter** maps Craft field handles to clean molecule params and does all query resolution (`.one()`, `.all()`, `.with([...])`) so molecules never see Craft queries:

```twig
{# 03_organisms/page-builder/blocks/_pageBlockPillars.twig #}
{% include "02_molecules/page-block-pillars/_page-block-pillars" with {
    items: block.items.with([
        "image",
        "symbol",
    ]).all(),
} only %}
```

Field handles appear in adapters and leaf templates only. Molecules and atoms take plain data — which is what makes them reusable across builders and outside CMS content entirely.

## 6. Template file convention

Every component template follows the exact same shape: **header docblock → `{# Variables #}` → two blank lines → `{# Output #}`**.

```twig
{#
    Molecule: Page Block Rich Text

    @param {array[string]} classes (optional)
    @param {string} heading (optional)
    @param {string} text (optional)
    @param {string} layout (optional): "centered" (default), "medium", "small"
#}

{# Variables #}

{% set layout = layout ?? null %}

{% set attributes = {
    "class": [
        "page-block-rich-text",
        layout ? "page-block-rich-text--" ~ layout|lower : null,
    ]|merge(classes ?? []),
} %}


{# Output #}

<div {{ attr(attributes) }}>
    <div class="page-block-rich-text__container">

        {% include "01_atoms/heading/_heading" with {
            classes: ['page-block-rich-text__heading'],
            level: 2,
            text: heading,
        } only %}

        {% include "01_atoms/rich-text/_rich-text" with {
            classes: ['page-block-rich-text__text'],
            html: text,
        } only %}

    </div>
</div>
```

The rules, all of them mandatory:

1. **Docblock first**: `Atom:` / `Molecule:` / `Organism:` / `Template:` + name, an optional description sentence, then `@param {type} name (optional): allowed values`. Enumerate allowed values for enum-like params — they double as the CP dropdown option list.
2. **`{# Variables #}` section**: param defaults first, then always an **`attributes` hash** whose `class` entry is `["block-name", …modifiers]|merge(classes ?? [])`. Modifier classes derive from params (`layout ? "block--" ~ layout : null` — `attr()` drops nulls). Data attributes for JS also go here.
3. **Two blank lines** between the Variables section and `{# Output #}`.
4. Root element rendered with **`<div {{ attr(attributes) }}>`** — never a hand-written `class="…"` string on the root.
5. **Every component accepts a `classes` array.** The parent owns positional/element classes (`classes: ['pillar__case']`); the component owns its own block class. This is how BEM elements from a parent land on a child component.
6. **All includes use `with { … } only`** — no ambient context leaks, every input is greppable.
7. **Molecules and atoms never read globals or `entry`** — only explicit params. Globals are read in `variables.twig`, organisms, and block adapters.
8. **Guard every optional field**: `{% if heading %}…{% endif %}` (or let the atom render nothing on empty input). Empty content ⇒ omit the markup. Never substitute placeholder/default copy.
9. **All user-facing strings translatable**: `{{ 'articles.overview.filter'|t('site') }}` (§11).

## 7. Component catalog

The typical component set nearly every project needs. Names are the standard; params shown are the established contracts.

### 7.1 Foundational atoms

| Atom | Params | Role |
|---|---|---|
| `heading` | `level` (1–6), `text`/`html`, `classes` | The universal title primitive: `<h{level}>`. Renders nothing when empty. |
| `rich-text` | `html`, `classes` | Wrapper around CKEditor output; the only place long-form typography is styled. |
| `link` | `linkfield` (Craft Link field) **or** `url`/`label`/`openInNewWindow`, `classes` | The `<a>` primitive. Normalizes Link fields, auto-sets `target="_blank" rel="noopener"` for external URLs. Base for both buttons. |
| `button-primary` / `button-secondary` | same as `link` | `link` with a button class; the CTA pair. |
| `image` | `asset` (Craft Asset), `classes`, optional `transform` | `<img>` with intrinsic width/height, alt from the asset, webp + `srcset`. |
| `form-field` | `id`, `name`, `label`, `type` (`text\|email\|tel\|textarea`), `required`, `autocomplete`, `classes` | The single labelled-control primitive behind every form. |
| `pill` / `radio-pill` | `text`, `classes` / + input attrs | Inline chip; radio variant for filter/choice UIs. |
| `date` | `date` (DateTime), `classes` | Formatted date line (with calendar icon). |
| `tag-list` | `tags` (elements), `classes` | `<ul>` of tag links. |
| `logo` | `asHomepageLink` (bool), `classes` | Brand mark, used by site-header and site-footer. |
| `spacer` | `size` | Pure vertical-rhythm element, driven by `pageBlockSpacer`. |
| `modal` / `modal-video` | element-driven, JS-paired | Dialog primitives (when the design needs them). |

### 7.2 Icon system

- **Icons are always SVG, inlined in the markup.** Never icon fonts, never raster icon images, never icon files loaded via `<img>` — inline SVG styles with CSS (`currentColor`), scales sharply at any size, and costs zero requests.
- **One folder per icon**: `01_atoms/icon-<name>/_icon-<name>.twig` containing a bare inline `<svg viewBox="…" fill="currentColor">` — color inherits from CSS. Optimize the SVG source (SVGO/hand-cleaned: no editor metadata, no fixed width/height, sensible precision).
- Chrome icons (caret, hamburger, logo, globe) are included statically. CMS-selectable icons resolve **dynamically from a slug**:

  ```twig
  {% include "01_atoms/icon-" ~ icon ~ "/_icon-" ~ icon ignore missing only %}
  ```

  where `icon` comes from a Dropdown field. **Adding an icon = adding a folder**; nothing else needs editing (keep the Dropdown options in sync).
- Optionally register `web/icons` as an extra template root in a small module so raw SVG files can be `{% include "icons/foo.svg" %}`.

### 7.3 Typical molecules

| Molecule | Role |
|---|---|
| `section-label` | Auto-numbered section eyebrow. Takes **only** a `label` string — the two-digit ordinal comes from a CSS counter (reset on `body`, incremented per label), so numbering follows document order and skips sections without a label. Renders nothing when empty. |
| `section-heading` | Section title + optional caption text. |
| `card` variants (`post-card`, `work-card`, …) | One tile of an overview/list. Explicit params (`url`, `title`, `excerpt`, `image`, `tags`…), one card per content shape. |
| `navigation-main` | Desktop navigation; reads the nav items from `_globals` (set in `variables.twig`), composes `navigation-link` / dropdown / megamenu atoms + `language-switcher`. Carries the `js-navigation-main` hook. |
| `navigation-dropdown` / `navigation-megamenu` | Submenu variants; compute `isActive` against the current URL. |
| `language-switcher` | Site-switch dropdown fed by the alternate-URL list built in `variables.twig` (shared with the hreflang tags). |
| `breadcrumbs` | W3C ARIA breadcrumb from the entry's ancestry / `overviewPage`. |
| `contact-form` / `form-newsletter` | Forms composed from `form-field` atoms; JS binds via `data-*` attributes, endpoints/config passed as params. |
| `ctas` | Row of CTA buttons from an array of Link fields. |
| `page-block-*` family | One molecule per builder block type (§10.2) — each is the single render target of its adapter. |
| `media-gallery`, `marquee-*`, `logo-slider` | Interactive media molecules with a JS partner class. |

### 7.4 Organisms

| Organism | Data source | Role |
|---|---|---|
| `site-header` | `navigation`/`header` global | Site chrome: logo + `navigation-main` (+ scroll behavior via `data-*` attrs from global preferences). Included once from `_master.twig`. |
| `site-footer` | `navigation`, `companyInfo`, `socialMedia`, `legal` globals | Site chrome: brand, nav columns, social links, legal line. |
| `page-builder` | `entry.pageBuilder` (overridable `blocks`) | THE content dispatcher (§5.5) + `blocks/` adapters. |
| `article-builder` / `case-builder` | `entry.articleBuilder` / `entry.caseBuilder` | Same dispatcher pattern for channel body content. |
| `hero` | `entry.hero` matrix | Hero dispatcher with its own small block set (`heroText`, `heroPhoto`, `heroVisual`…). |
| `footer` (CTA band) | `blocks` passed in | Page-level pre-footer band (CTAs, newsletter) — distinct from `site-footer`. |
| `layout-sidebar` | `navigation[]`, `currentEntryId`, `title`, `body` | Two-column docs/sub-nav shell. |

### 7.5 Templates (`04_templates/`)

One folder per entry type: `04_templates/<kebab-type>/_<kebab-type>.twig` + optional `_head.twig` (+ optional `_<x>.scss` for page-scoped styles). They compose organisms only — no direct atom/molecule includes, no field-handle spelunking beyond passing matrix fields to dispatchers.

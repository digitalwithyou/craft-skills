# Craft CMS 5 Conventions — Structure, Naming & Way of Working

This document is the target-state specification for Craft CMS projects. It is written for an AI coding agent (or a developer) tasked with bringing an existing project in line with this structure.

**Usage scenarios:**

1. **Craft 4 → Craft 5 upgrade + restructure.** Run the official Craft upgrade first, then follow the Migration Playbook (§14) to restructure toward this spec.
2. **Custom-built PHP CMS → Craft CMS 5.** Follow the Migration Playbook from step 1; everything else in this document is the destination.
3. **New project.** Scaffold directly to this spec.

Rules in this document use MUST / never deliberately. When an existing project conflicts with this spec, the spec wins unless the user says otherwise.

---

## 1. Stack

- **Craft CMS 5** (solo or pro edition), PHP 8.3+, MySQL 8.
- **DDEV** for local development. Everything runs inside DDEV — never invoke `npm`, `npx`, `composer`, or `./craft` on the host directly; always prefix with `ddev`.
- **Vite 7 + Sass** for the frontend build, wired into Craft via `nystudio107/craft-vite`.
- **Vanilla ES modules** — no React, no Vue, no Alpine, no jQuery. If a task seems to need a framework, stop and ask.
- **CKEditor** (`craftcms/ckeditor`) for all rich text.
- In-house plugins ship as **local-path Composer packages** in `plugins/` (see §4).

| Purpose | Command |
|---|---|
| Start the site | `ddev start` |
| Install npm dependencies (wires husky) | `ddev npm install` |
| Vite dev server (HMR on `:5173`) | `ddev npm run dev` |
| Production asset build (`web/dist/`) | `ddev npm run build` |
| Lint all SCSS | `ddev npm run lint:scss` |
| Lint + auto-fix SCSS | `ddev npm run lint:scss:fix` |
| Lint staged files (pre-commit hook) | `ddev npx lint-staged` |
| Install Composer dependencies | `ddev composer install` |
| Any Craft CLI command | `ddev craft <command>` |
| Apply Project Config YAML | `ddev craft project-config/apply` |

---

## 2. Project layout

```
project/
├── .ddev/                  DDEV config (exposes Vite port, see §3)
├── .husky/                 pre-commit hook → ddev npx lint-staged
├── config/
│   ├── general.php         fluent GeneralConfig (see §3)
│   ├── vite.php            craft-vite plugin config (see §4)
│   ├── routes.php          feeds only — never entry routing (see §11)
│   └── project/            Project Config YAML — source of truth (see §10.8)
├── modules/                small site modules (template roots, Twig extension)
├── plugins/                in-house plugins as local-path Composer packages
├── templates/              ALL frontend source: Twig + SCSS + JS (see §5)
│   └── site.js             the single Vite entry
├── translations/
│   ├── nl/site.php
│   └── en/site.php
├── web/
│   ├── dist/               Vite build output (gitignored)
│   └── uploads/            the default asset filesystem (others: §10.7)
├── vite.config.mjs
├── .stylelintrc.json
├── package.json
├── composer.json
└── .env.example.{dev,staging,production}
```

---

## 3. Environment & tooling

### 3.1 DDEV

`.ddev/config.yaml` — the essentials:

```yaml
name: <project>
type: craftcms
docroot: web
php_version: "8.4"
database:
    type: mysql
    version: "8.0"
web_extra_exposed_ports:
  - name: craft-vite
    container_port: 5173
    http_port: 5172
    https_port: 5173
upload_dirs: ['web/uploads']
```

`web_extra_exposed_ports` routes the Vite dev server through DDEV's router so HMR works on the `https://<project>.ddev.site:5173` origin.

### 3.2 Environment files

Ship three examples: `.env.example.dev`, `.env.example.staging`, `.env.example.production`. Composer copies the dev one on install:

```json
"scripts": {
    "post-root-package-install": [
        "@php -r \"file_exists('.env') || copy('.env.example.dev', '.env');\""
    ]
}
```

Key variables: `CRAFT_ENVIRONMENT`/`ENVIRONMENT` (`dev|staging|production`), `PRIMARY_SITE_URL`, `DEV_MODE`, `ALLOW_ADMIN_CHANGES` (true only in dev), `DISALLOW_ROBOTS` (true everywhere except production).

### 3.3 `config/general.php`

Use the fluent builder. These settings are load-bearing for the whole architecture:

```php
<?php

use craft\config\GeneralConfig;
use craft\helpers\App;

return GeneralConfig::create()
    ->defaultWeekStartDay(1)
    ->omitScriptNameInUrls()
    ->devMode(App::env('DEV_MODE') ?? false)
    ->preloadSingles()                                 // globals readable in Twig without passing
    ->allowAdminChanges(App::env('ALLOW_ADMIN_CHANGES') ?? false)
    ->disallowRobots(App::env('DISALLOW_ROBOTS') ?? false)
    ->partialTemplatesPath('01_atoms/rich-text')       // CKEditor nested-entry partials
    ->errorTemplatePrefix('04_templates/errors/_')     // → _404.twig / _500.twig
    ->privateTemplateTrigger('')                       // no public template routing at all
    ->preventUserEnumeration()
    ->sendPoweredByHeader(false)
    ->aliases([
        '@webroot' => dirname(__DIR__) . '/web',
        '@web' => App::env('PRIMARY_SITE_URL'),
    ])
;
```

- `privateTemplateTrigger('')` disables direct template routing entirely — every URL resolves through sections + `_routing.twig`, and every template file can safely start with `_`.
- `preloadSingles()` makes global sets available in every template by handle (`companyInfo.email`, `navigation.navigationMatrix`) without explicit passing.

### 3.4 Linting & git hooks

`package.json`:

```json
{
    "type": "module",
    "scripts": {
        "dev": "vite",
        "build": "vite build",
        "lint:scss": "stylelint \"templates/**/*.scss\"",
        "lint:scss:fix": "stylelint \"templates/**/*.scss\" --fix",
        "prepare": "husky"
    },
    "lint-staged": {
        "templates/**/*.scss": ["stylelint --fix"]
    }
}
```

devDependencies: `vite`, `vite-plugin-restart`, `sass`, `husky`, `lint-staged`, `stylelint`, `stylelint-config-standard-scss`, `stylelint-order`, `stylelint-use-logical`.

The husky pre-commit hook shells into DDEV: `ddev npx lint-staged`. `ddev npm install` wires the hook automatically via the `prepare` script.

### 3.5 In-house plugins

Ship project-specific plugins in-repo as local-path Composer packages:

```json
"repositories": [
    { "type": "path", "url": "plugins/apex-redirect" }
],
"require": {
    "acme/apex-redirect": "dev-main"
}
```

Edit them in place; run `ddev composer dump-autoload` when adding classes.

---

## 4. Vite pipeline

Three files cooperate; copy them nearly verbatim into any project.

### 4.1 `vite.config.mjs`

```js
import { defineConfig } from 'vite';
import ViteRestart from 'vite-plugin-restart';

// Only set origin on the local development environment DDEV
let primaryUrl = process.env.DDEV_PRIMARY_URL
    ? new URL(process.env.DDEV_PRIMARY_URL)
    : new URL('http://localhost');

let vitePort = 5173;
let viteOrigin = `${primaryUrl.protocol}//${primaryUrl.hostname}:${vitePort}`;

export default defineConfig(({ command }) => {
    return {
        base: command === 'serve' ? '' : '/dist/',
        build: {
            target: 'baseline-widely-available',
            emptyOutDir: true,
            manifest: true,
            outDir: './web/dist/',
            rollupOptions: {
                input: {
                    site: './templates/site.js',
                },
            },
        },
        plugins: [
            ViteRestart({
                reload: [
                    './templates/**/*',
                ],
            }),
        ],
        server: {
            host: '0.0.0.0',
            port: vitePort,
            strictPort: true,
            origin: viteOrigin,
            cors: true,
            allowedHosts: [
                `${primaryUrl.hostname}`,
            ],
        },
    };
});
```

No `@vitejs/plugin-legacy`: the browser floor is Baseline Widely available, every browser at that floor runs ES modules, and the plugin only adds a nomodule bundle (in this project 20 files, ~420 KB, one of them re-embedding the whole stylesheet as a JS string), two inline shims per page and a CSS target of Chrome 61 that down-levels `inset` and friends. `build.target` is Vite's default, written out so the floor is a visible decision.

DDEV support lives in three places: `DDEV_PRIMARY_URL` drives `server.origin` and `allowedHosts` here; `host: '0.0.0.0'` makes the container port reachable; and `.ddev/config.yaml` exposes port 5173 (§3.1).

### 4.2 `config/vite.php`

```php
<?php

use craft\helpers\App;

$port = 5173;
$primarySiteUrl = App::env('PRIMARY_SITE_URL');

// When using ddev the primary site url can contain a port,
// it needs to be replaced by the vite port
$parsedSiteUrl = parse_url($primarySiteUrl);
if (isset($parsedSiteUrl['port'])) {
    $primarySiteUrl = $parsedSiteUrl['scheme'] . "://" . $parsedSiteUrl['host'];
}

return [
    'useDevServer' => App::env('ENVIRONMENT') === 'dev' || App::env('CRAFT_ENVIRONMENT') === 'dev',
    'manifestPath' => '@webroot/dist/.vite/manifest.json',
    'devServerPublic' => $primarySiteUrl . ':' . $port,
    'serverPublic' => App::env('PRIMARY_SITE_URL') . '/dist/',
    'errorEntry' => './templates/site.js',
    'cacheKeySuffix' => '',
    'devServerInternal' => 'http://localhost:' . $port,
    'checkDevServer' => true,
    'includeReactRefreshShim' => false,
    'includeModulePreloadShim' => false, // modulepreload is Baseline Widely available
    'criticalPath' => '@webroot/dist/criticalcss',
    'criticalSuffix' => '_critical.min.css',
];
```

### 4.3 Injection & the CSS manifest rule

The layout injects exactly one line:

```twig
{{ craft.vite.script("templates/site.js", false) }}
```

There is no separate CSS entry and no `site.scss` import manifest. The first line of `site.js` is the entire stylesheet pipeline:

```js
import.meta.glob('./**/*.scss', { eager: true });
```

Every `_*.scss` file anywhere under `templates/` is bundled automatically. **Creating a component's SCSS file next to its Twig file is all the wiring there is.** Never maintain a manual `@use`/`@import` list of component styles.

---

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

---

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

---

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

---

## 8. SCSS conventions

### 8.1 Stylelint config (enforced via pre-commit)

`.stylelintrc.json`:

```json
{
  "extends": [
    "stylelint-config-standard-scss"
  ],
  "plugins": [
    "stylelint-order",
    "stylelint-use-logical"
  ],
  "rules": {
    "order/properties-alphabetical-order": true,

    "csstools/use-logical": "always",

    "declaration-property-value-disallowed-list": {
      "/^padding-(top|right|bottom|left)$/": ["/.*/"],
      "/^margin-(top|right|bottom|left)$/": ["/.*/"],
      "/^border-(top|right|bottom|left)(-.*)?$/": ["/.*/"],
      "/^(top|right|bottom|left)$/": ["/.*/"],
      "text-align": ["left", "right"]
    },

    "max-nesting-depth": 5,
    "selector-max-compound-selectors": 4,

    "selector-class-pattern": [
      "^[a-z][a-z0-9]*(-[a-z0-9]+)*(__[a-z0-9]+(-[a-z0-9]+)*)*(--[a-z0-9]+(-[a-z0-9]+)*)?$",
      {
        "message": "Class names should follow chained-BEM: .block__element__sub--modifier",
        "resolveNestedSelectors": true
      }
    ],

    "no-descending-specificity": null,
    "rule-empty-line-before": ["always", {
      "except": ["first-nested"],
      "ignore": ["after-comment"]
    }],

    "scss/selector-no-redundant-nesting-selector": true,

    "color-function-notation": null,
    "alpha-value-notation": null,
    "hue-degree-notation": null,
    "media-feature-range-notation": null
  },
  "ignoreFiles": [
    "node_modules/**",
    "vendor/**",
    "web/dist/**",
    "storage/**"
  ]
}
```

### 8.2 The rules in prose

- **Chained BEM via SCSS nesting.** Elements nest under elements: `&__item { &__emoji { … } }` compiles to `.block__item__emoji` — not flat `.block__emoji`. Twig class names must match the chained output. Modifiers: `&--large`.
- **Alphabetical property order** inside every rule.
- **Logical properties only**, no exceptions: `inline-size`/`block-size`, `max-inline-size`, `padding-inline-*`/`padding-block-*`, `margin-inline`/`margin-block`, `inset-inline-*`, `border-block-*`, `text-align: start/end`. `stylelint --fix` rewrites physical properties automatically.
- **Design tokens as CSS custom properties** — `var(--color-ink)`, `var(--font-display)`, `var(--s-sec-y)` — never SCSS variables in component files. SCSS variables are only for compile-time needs (breakpoints in `@media` are the common case: `@use '../../00_config/breakpoints-config' as *;`).
- `rem` for typography, `clamp()` for fluid sizes, `text-wrap: balance` on headlines / `pretty` on long-form copy.
- Formatting: 4-space indent, single blank line between sibling rules, no blank line before a first-nested rule.
- One SCSS file per component, scoped to its block class. No global component styles outside `00_fundamentals`.

### 8.3 Modern CSS

Write CSS as it is in the current decade — this is a hard requirement, not a preference:

- **Layout with CSS Grid and Flexbox.** Grid for two-dimensional layout and page/section structure, flex for one-dimensional alignment. **Never floats** for layout, never absolute-positioning hacks where grid/flex does the job, no clearfix utilities.
- **No `!important`.** If specificity forces it, the selector structure is wrong — fix the nesting/order instead.
- **Mobile first.** The unqueried base styles are the small-screen styles; enhance upward with `@media (min-width: …)` only. Never write desktop-default styles overridden back down with `max-width` queries.
- **Prefer intrinsic/fluid sizing over breakpoints**: `clamp()`, `minmax()`, `auto-fit`/`auto-fill`, `aspect-ratio`, `gap`, container-relative units. A component that only works at specific widths is a bug.
- **CSS over JavaScript, always.** If CSS can do it, CSS does it: sticky headers (`position: sticky`), smooth scrolling (`scroll-behavior`), scroll snapping, accordions (`<details>`), simple carousels (scroll snap), transitions/animations, auto-numbering (counters, §8.4), `:hover`/`:focus-visible`/`:has()` state styling. JS is reserved for genuine behavior (fetching, complex state, focus management).
- Use modern selectors and features freely (`:has()`, `:is()`/`:where()`, `@supports` for progressive enhancement); animate only `transform` and `opacity`, and wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)`.

### 8.4 Token files (`templates/00_config/`)

- **`_colors-config.scss`** — two layers: SCSS `$vars` (compile-time mirror) → `:root { --color-x: #{$color-x}; }`, then semantic aliases (`--color-text`, `--color-background`, `--color-border`). If the design has themes, a `html[data-theme="dark"]` block overrides only the themeable tokens, and theme-stable tokens (e.g. `--color-slab*` for always-dark bands) stay put.
- **`_fonts-config.scss`** — font stacks (`--font-display`, `--font-text`, `--font-mono`), a fluid type scale (`--fs-display` … `--fs-meta`, `clamp()`-based), and a density scale for spacing (`--s-hero-y`, `--s-sec-y`, `--s-block`, `--gutter`). Section/hero padding always uses the density tokens — no ad-hoc px.
- **`_breakpoints-config.scss`** — SCSS breakpoint variables + `$max-width`.

A trick worth reusing: CMS-free auto-numbering with CSS counters (`body { counter-reset: section; }` + `.section-label { counter-increment: section; }` + `content: counter(section, decimal-leading-zero)`) — the CMS stores only labels, order and numbering stay correct automatically.

---

## 9. JavaScript conventions

### 9.1 `site.js` — the single entry

The prescribed shape — a registry map, one boot loop, zero per-component boilerplate:

```js
import.meta.glob('./**/*.scss', { eager: true });

import LanguageSwitcher from './02_molecules/language-switcher/LanguageSwitcher';
import NavigationMain from './02_molecules/navigation-main/NavigationMain';
import ThemeToggle from './01_atoms/theme-toggle/ThemeToggle';
import PageBlockLogoSlider from './02_molecules/page-block-logo-slider/PageBlockLogoSlider';

/**
 * Selector → component class. One entry per interactive component.
 * Every selector is a `js-*` hook class, never a styling class.
 */
const components = new Map([
    ['.js-language-switcher', LanguageSwitcher],
    ['.js-navigation-main', NavigationMain],
    ['.js-theme-toggle', ThemeToggle],
    ['.js-page-block-logo-slider', PageBlockLogoSlider],
]);

document.addEventListener('DOMContentLoaded', () => {
    for (const [selector, Component] of components) {
        document.querySelectorAll(selector).forEach((element) => new Component(element));
    }
});
```

Adding an interactive component = one import + one Map entry.

### 9.2 Module rules

- **One default-export ES class per file**, PascalCase filename, co-located in the component's folder (§5.2). No frameworks, no global scripts.
- **Constructor takes the root element** and must no-op safely (guard against missing children). The registry only instantiates when the selector matches, so absence on a page costs nothing.
- **`js-*` hook classes** are the only JS↔DOM contract on the root; inside the component prefer `[data-*]` selectors so BEM renames never break behavior. Never style a `js-*` class; never bind JS to a BEM class.
- **Configuration via `data-*` attributes** written by the Twig template — scalars as plain attributes (`data-marquee-speed="40"`), complex config as JSON (`data-presets='{{ presets|json_encode }}'`). The class reads `element.dataset` with documented defaults. No inline `<script>` config.
- The Twig side sets both in the `attributes` hash:

  ```twig
  {% set attributes = {
      "class": ["logo-slider", "js-page-block-logo-slider"]|merge(classes ?? []),
      "data-speed": speed ?? 40,
  } %}
  ```

---

## 10. Craft content model

### 10.1 Sections — no singles, a Pages structure

**Never create Singles.** The content model is:

- **`pages` (structure)** — the home of every page on the site, including the homepage (`uriFormat: '{ parent.uri != "__home__" ? parent.uri }/{slug}'`, home entry uses `__home__`). Nesting gives URL hierarchy for free. Template: `04_templates/_routing.twig`.
- **Channels/structures only for genuinely different content**: `articles`, `cases`, `news`, `services`, … and data-only sections like `team` (team members). Each gets its own entry type + `{% case %}` in `_routing.twig`; overview pages are `pages` entries (`pageArticleOverview`, …), not singles.
- **`sharedBlocks` (structure)** — predefined reusable blocks (§10.4).

What used to be a Single (contact page, about page) is a `pages` entry — almost always `pageGeneric`. Site-wide *settings* that used to live on singles belong in Globals (§10.6).

### 10.2 Entry types & builders

Naming is strict and uniform:

- Page entry types start with `page`: **`pageGeneric`** (the workhorse — the type used to create most pages), `pageHome` (only when the homepage layout truly differs), `page<X>Overview` for channel overview pages.
- Builder block entry types are `<builder-prefix>Block<Name>`: `pageBlockMedia`, `pageBlockRichText`, `pageBlockCards`, `articleBlockQuote`, `caseBlockMedia`, … The block adapter template filename equals the handle: `blocks/_pageBlockMedia.twig`.
- Name blocks by **what they are**, never by where they're used: `work-section`, `logo-slider` — not `homepage-clients`.

**Builders are Matrix fields**: `pageBuilder` (on every page type — the body of the page), `articleBuilder`, `caseBuilder`. Settings: card view (`defaultIndexViewMode: cards`), and a `group` label per entry type so the CP block picker is organized (e.g. *Basic* / *Lists & Grids* / *Structures* / *Forms*).

A healthy `pageBuilder` starter set: `pageBlockHeading`, `pageBlockRichText`, `pageBlockMedia`, `pageBlockCards`, `pageBlockGrid`, `pageBlockLogoSlider`, `pageBlockFaq`, `pageBlockCta`, `pageBlockNewsletterForm`, `pageBlockOverview<X>`, `pageBlockSpacer`, `pageBlockSharedBlock`.

### 10.3 Fields — share aggressively, prefix `common`

- **Share fields whenever it makes sense.** One `heading` concept = one field reused across dozens of entry types, not per-type duplicates.
- **Shared generic fields get the `common` prefix and a generic name**: `commonText`, `commonTextMultiline`, `commonImage`, `commonImages`, `commonLogos`, `commonLink`, `commonLightswitch`, `commonIcon`, `commonEmail`, `commonCode`, … Non-`common` handles are reserved for genuinely specific fields (`articleBody`, `seoRobots`).
- **Link fields over label+url pairs.** A native Craft Link field carries `.label` and `.url` in one field — use it for every CTA. The **one sanctioned content fallback** in the whole system: a translated default label when a Link field's label is empty:

  ```twig
  {% set ctaLabel = (block.commonLink.label ?? null) ?: ('Read more'|t('site')) %}
  ```

- **Few CKEditor configs, as tiers.** 3–5 configs total, named by editorial affordance: `commonRichTextBasic` (bold/italic) → `commonRichTextSimple` (+ links, lists) → `commonRichTextFull` (+ headings, media, nested entries), plus `commonHeadline` (single-line, marks only). Settings live inline in the field YAML. Nested-entry rendering goes through `partialTemplatesPath('01_atoms/rich-text')` → `templates/01_atoms/rich-text/entry/<type>.twig`.

### 10.4 Shared blocks

A `sharedBlocks` **structure** holds predefined blocks that appear on multiple pages (a CTA used on ten pages, edited in one entry). Each `sharedBlock` entry's body is the **same `pageBuilder` Matrix**. In the page builder, a `pageBlockSharedBlock` entry type holds an Entries field (`sharedBlocks`) sourced only from that section. Rendering is a two-file hop that **recurses back into the page builder**:

```twig
{# 03_organisms/page-builder/blocks/_pageBlockSharedBlock.twig #}
{% include "02_molecules/page-block-shared-block/_page-block-shared-block" with {
    sharedBlocks: block.sharedBlocks.all(),
} only %}
```

```twig
{#
    Page block: Shared block

    @param {array[Entry]} sharedBlocks
#}

{% for sharedBlock in sharedBlocks %}
    {% include "03_organisms/page-builder/_page-builder" with {
        blocks: sharedBlock.pageBuilder.eagerly().all(),
    } only %}
{% endfor %}
```

Because it re-enters `_page-builder.twig` with a different `blocks` array (the `blocks ?? entry.pageBuilder` contract from §5.5), the shared block needs **zero dedicated templates** and every block type is automatically shareable.

### 10.5 Navigation

- Navigation is **globals-driven**: a `navigation` (or `header`) global set with Matrix fields (`mainMenu`, optionally `topNavigation`), editable by the client.
- Nav item entry types stay few by being **polymorphic**: a `type` Dropdown (`link` | `section`) with `elementCondition` rules on the field layout, so the CP shows either a single `commonLink` or a group label + nested `subitems` Matrix. Prefer this over one entry type per nav flavor.
- **Include the most-used structures in the main navigation** as section groups whose sublinks point at entries in `pages`/`cases`/`articles` — the nav mirrors the site's primary structures rather than a hand-maintained flat list.
- Query the nav **once** in `variables.twig`, stash on `_globals`, read it in both `navigation-main` and `site-footer` (§5.3).
- A small Twig extension helper `isActiveNavItem(linkfield)` (current path vs. the Link field's element URI, prefix-matched for sub-pages) keeps active states out of the templates.

### 10.6 Globals — site-wide settings

Globals replace settings-singles. Standard set (create what applies):

`navigation`, `companyInfo` (address, email, telephone), `socialMedia` (matrix of channels), `header` (behavior preferences), `footer` (CTA-band matrix), `seo` (defaults, og-image), `tracking`, `newsletter`, `legal`, `notFound`, `serverError`, `rss`.

With `preloadSingles()` on, templates read them by handle without passing — but **only** in `variables.twig`, organisms, and adapters (§6 rule 7).

### 10.7 Assets

- **Default filesystem**: `uploads` (`craft\fs\Local`, `@webroot/uploads`) for editorial and design assets.
- **Volumes as subpaths on it**: `images`, `videos`, `logos` — plus `symbols` or `illustrations` only when the design includes those. A new asset *category* is a volume on an existing filesystem.
- **User uploads on separate storage, preferably where no scripts can run**: files uploaded by visitors (front-end forms) go on their own filesystem, never in `@webroot/uploads`. Use object storage (an S3-compatible bucket served from its own domain): an uploaded script can't execute there, and the storage scales independently of the web server. Only when a project can't use object storage: a local filesystem outside the webroot, served without PHP execution.
- **More filesystems when the storage differs**: besides user uploads, for example private files or large media. Configure path and URL through environment variables, and give files that must stay private a filesystem without public URLs.
- **Named image transforms** per ratio/size (`sixteentonine_768x432`, `square_1200`, …) plus `openGraphImage` (1200×630 crop). The `image` atom applies transforms + webp + `srcset`; templates never call `.getUrl()` with inline transform hashes.

### 10.8 Project Config workflow

`config/project/*.yaml` is the source of truth. Make schema changes in the CP (dev only, `ALLOW_ADMIN_CHANGES=true`), let Craft write the YAML, commit it. Other environments have admin changes disabled and sync with `ddev craft project-config/apply`. Never hand-edit YAML except for mechanical renames you immediately apply and verify.

---

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

---

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

---

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

---

## 14. Migration playbook

Follow in order. Steps 1–2 are analysis only — no code until the mapping is approved.

**1. Audit the existing site.**
Inventory: all sections/content types (or DB tables in a custom CMS), all fields per type, all templates, all URLs (crawl the sitemap or dump routes), all globals/settings, all third-party integrations (forms, newsletter, analytics). Produce a table: *content type → count → fields → current URL pattern*.

**2. Map to the target content model.**
- Every single/one-off page → an entry in the `pages` structure, almost always `pageGeneric` (its content re-expressed as `pageBuilder` blocks).
- Repeating dated/listed content → channels (`articles`, `news`, `cases`); pure data → data channels (`team`).
- Page fragments repeated across pages (CTAs, banners) → `sharedBlocks` entries (§10.4).
- Field-by-field mapping to shared `common*` fields; flag genuinely specific fields for their own handles. Map every rich-text field to one of the CKEditor tiers.
- Every old URL → new URI (this becomes the redirect map in step 6).

**3. Build the Project Config** (dev, `ALLOW_ADMIN_CHANGES=true`): filesystems/volumes → fields (`common*` first) → CKEditor configs → sections + entry types → builder Matrix fields with grouped blocks → globals. Commit the YAML after each coherent chunk.

**4. Scaffold the tooling and skeleton**: DDEV config (§3.1), Vite pair (§4), stylelint + husky (§3.4), `templates/` skeleton — `00_config` tokens (from the design), `00_fundamentals`, `_master.twig` chain, empty `_routing.twig` with `{% default %}{% exit 404 %}`.

**5. Rebuild templates outside-in**: layout + site-header/site-footer first, then per entry type (add its `{% case %}` + `04_templates/` folder), then block-by-block using the §15 recipe. Port styles into the token system as you go — never copy legacy CSS wholesale.

**6. Migrate content, then redirects.**
Content: feed-me/console commands/manual entry depending on volume.
Redirects: **every old URL must keep working.** Apply the step-2 URL map as 301s — a redirects table/plugin for path changes, web-server rules for pattern-wide changes, apex→www at the edge. Verify with the crawled URL list from step 1.

**7. QA gate** (all must pass): `ddev npm run lint:scss` clean for new code; `ddev npm run build` succeeds; every entry type renders through `_routing.twig` (no `exit 404` for real types); 404/500 render with editable content; hreflang/canonical correct on both sites; feeds validate; redirect map spot-checked; Lighthouse (mobile) green across all categories on the homepage, a generic page and a channel detail page (§13); keyboard walk-through of header, forms and modals passes (§12.2); Project Config applies cleanly on a fresh clone (`ddev craft project-config/apply`).

**Craft 4 → 5 specifics**: run the official upgrade **first** (Craft 5 converts Matrix blocks to nested entries — let it), verify parity, and only then restructure: convert Singles to `pages` entries, rename entry types/fields to this naming scheme via the CP, rebuild templates. Never mix the version upgrade and the restructure in one step.

---

## 15. Recipes & definition of done

### 15.1 New page-builder block

1. **CP**: create the entry type `pageBlock<Name>` (reusing `common*` fields), add it to the `pageBuilder` Matrix under the right group. Commit the YAML.
2. **Adapter**: `templates/03_organisms/page-builder/blocks/_pageBlock<Name>.twig` — thin field→param mapping with eager loading, delegating `with { … } only`.
3. **Molecule**: `templates/02_molecules/<name>/_<name>.twig` + `_<name>.scss` following §6 and §8.
4. **JS (if interactive)**: `<Name>.js` in the same folder, registered in the `site.js` map under a `js-<name>` hook class.

**Definition of done** — check every box:

- [ ] Entry type handle `pageBlock<Name>`, named by what it is, added to `pageBuilder` with a group
- [ ] Adapter is the only file reading `block.*`; eager loads relations
- [ ] Molecule has the docblock, `attributes` hash, `classes` param; all includes `only`
- [ ] Every optional field guarded — empty content renders nothing, no placeholder copy
- [ ] All strings through `|t('site')`, keys added to every `translations/*/site.php`
- [ ] SCSS scoped to the block class, chained BEM, lint-clean (`ddev npm run lint:scss`)
- [ ] Mobile first, grid/flex layout, no floats/`!important`; CSS used over JS where possible (§8.3)
- [ ] Semantic HTML (§12.1); keyboard-operable with visible focus; readable contrast (§12.2)
- [ ] Images through the `image` atom: webp, sized, sharp 2x srcset, lazy unless LCP (§13.2)
- [ ] JS (if any): class file + registry entry + `data-*` config, no `js-*` styling
- [ ] Project Config YAML committed
- [ ] Editor manual: `modules/manual/content/{nl,en}/blocks/<slug>.md` (with `block: pageBlock<Name>`) and `modules/manual/samples/pageBlock<Name>.php`, and `ddev craft manual/check` passes (`docs/manual.md`)

### 15.2 New icon

Create `01_atoms/icon-<name>/_icon-<name>.twig` with the inline `<svg viewBox fill="currentColor">`. If CMS-selectable, add `<name>` to the icon Dropdown options. Done — dynamic resolution picks it up.

### 15.3 New section / entry type

CP: section + entry type (template `04_templates/_routing.twig`, uriFormat per site) → add the `{% case %}` in `_routing.twig` → create `04_templates/<kebab-name>/_<kebab-name>.twig` composing organisms → commit YAML. If it's a channel, also create its `page<X>Overview` page entry type and overview block/template.

### 15.4 New shared field

Check the existing `common*` fields first — reuse beats creation. If genuinely new and generic: handle `common<Name>`, generic label, no per-type instructions baked in. Commit YAML.

---

## 16. Anti-patterns — never do these

- **No Singles.** Pages live in the `pages` structure; settings live in Globals.
- **No hardcoded or default copy** in blocks/molecules — no `block.field ?? "Some text"`. Empty ⇒ omit markup. (Sole exception: the translated CTA-label fallback for empty Link fields.)
- **No single-purpose block naming** — a block is never "the homepage X section".
- **No framework JS** — no React/Vue/Alpine/jQuery. Vanilla ES classes only.
- **No physical CSS properties** — logical only (`padding-inline-start`, not `padding-left`).
- **No floats for layout, no `!important`, no clearfix** — grid/flex and correct specificity.
- **No desktop-first CSS** — base styles are mobile; `min-width` queries only.
- **No JS for what CSS can do** — sticky, scroll, accordions, transitions, state styling are CSS jobs (§8.3).
- **No unsized or non-webp content images, no `<img>` outside the `image` atom** — CLS and blurry retina output are both bugs.
- **No icon fonts or raster icons** — icons are inline SVG atoms (§7.2).
- **No element queries inside loops (N+1), no unlimited overview queries** — eager-load and `.limit()` (§13.1).
- **No click handlers on `<div>`s, no `outline: none` without a replacement, no skipped heading levels.**
- **No flat BEM in nesting** — `&__item { &__label }`, never a re-declared `.block__item__label`.
- **No label+url field pairs** — use Link fields.
- **No globals/`entry` reads inside molecules or atoms** — explicit params only.
- **No `{% include %}` without `only`** (layout-level fundamentals excepted).
- **No manual SCSS import manifest** — the glob in `site.js` is the manifest.
- **No undocumented component templates** — every one starts with the §6 docblock.
- **No styling `js-*` classes, no JS bound to BEM classes.**
- **No mass-rewriting legacy code in an unrelated PR** — migrate folder by folder.

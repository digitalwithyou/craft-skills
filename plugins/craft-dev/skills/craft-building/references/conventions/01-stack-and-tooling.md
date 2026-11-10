<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## Contents

- 1. Stack
- 2. Project layout
- 3. Environment & tooling
- 3.1 DDEV
- 3.2 Environment files
- 3.3 `config/general.php`
- 3.4 Linting & git hooks
- 3.5 In-house plugins
- 4. Vite pipeline
- 4.1 `vite.config.mjs`
- 4.2 `config/vite.php`
- 4.3 Injection & the CSS manifest rule

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

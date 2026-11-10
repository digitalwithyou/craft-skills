# Plugin notes

Plugins used across client projects. Formie is on every site; caching is Blitz, Cloudflare, or both; SEOmatic on some sites; plus in-house plugins (cookie banner, language selection on first visit, and others).

## Contents

- Formie
- Blitz
- Cloudflare
- SEOmatic
- In-house plugins and modules

## Formie (verbb/formie)

- **Update risk**: template overrides. If the project overrides Formie templates (check `templates/` for a `formie` folder or the form template settings), diff the changed default templates between versions and port the changes.
- Forms are content stored in the database, but form *templates* and integrations (email, CRM) may live in project config. Commit any project config changes after `ddev craft up`.
- **Verify**: submit every form type on dev (contact, newsletter, multi-page). Check email notifications in DDEV's Mailpit (`ddev launch -m`), and check that spam protection (captchas, honeypot) still renders.
- With Blitz: forms need fresh CSRF tokens on cached pages (Formie's own refresh or Blitz's dynamic content); verify a submission works on a cached page.

## Blitz (putyourlightson/blitz)

- After a deploy: `php craft blitz/cache/refresh` (regenerates in the background via the queue). Use `blitz/cache/clear` only when you need an empty cache.
- Requires a real queue runner on production (the conventions prescribe `runQueueAutomatically(false)` + a daemon); check it after updates.
- **Verify**: a cached page shows the new markup after the refresh; dynamic parts (forms, language selection, cookie banner state) still work on cached pages.

## Cloudflare

- When Cloudflare caches HTML (cache rules or APO-style setups), purge after a deploy that changes templates or assets: by URL for small changes, everything for template changes. Use the purger the project already uses (Blitz Cloudflare purger, a deploy step, or the dashboard; see `AGENTS.md`).
- `web/dist/` assets are content-hashed by Vite, so they don't need purging; HTML does.

## SEOmatic (nystudio107/craft-seomatic)

- Settings live partly in the database, not project config. Read the changelog for meta bundle migrations; after updating, open Settings → SEOmatic once on dev and check that no migration notice appears.
- **Verify**: view source on the homepage and a channel detail page: title, description, canonical, hreflang and JSON-LD are present and correct for each site.
- Sites without SEOmatic use the conventions' own `00_fundamentals/meta/_seo.twig` + `seo` global; don't introduce SEOmatic during an update.

## In-house plugins and modules

- Live in `plugins/<name>` as local path Composer packages (`"dev-main"`) or `modules/<name>`.
- Per update run:
  1. Search the plugin for APIs deprecated in the new Craft version (release notes "Deprecated" section). The 5.12 examples are `ElementHelper::renderElements()` (use `Template::render()`) and `PrismJsAsset` (use `HighlightAsset`).
  2. Run the plugin's checks if it has them (ECS, PHPStan, Pest).
  3. Bump the plugin's version key and add a changelog line if the plugin has a `CHANGELOG.md`.
  4. When a plugin is shared between projects, note which projects need the same change.
- Cookie banner and language-selection plugins interact with Blitz/Cloudflare caching: they must work on fully cached HTML (client-side state, no per-visitor server rendering). Verify on a cached page.
- Craft 6: plugins will need a new major version that requires `craftcms/cms` `^6.0`. Track readiness per plugin in the update report; don't port during routine updates.

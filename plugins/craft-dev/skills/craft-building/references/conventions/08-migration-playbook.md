<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

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

---
name: craft-building
description: Builds and configures Craft CMS 5 sites that use DWY's Craft conventions (atomic 00–04 template layers, one _routing.twig, pageBuilder blocks, common* fields, Sass/BEM, vanilla JS, Vite and DDEV). Covers Twig templates in the atomic 00–04 layers, builder blocks, sections, entry types, fields, globals, asset volumes, image transforms, SCSS/BEM, vanilla JS components, Vite, i18n, SEO, accessibility and performance. Also covers onboarding a project (AGENTS.md, MCP setup for Claude Code or Codex) and migrating Craft 4 or custom-PHP sites onto the conventions. Use for any templating, schema or front-end change in a Craft project that follows these conventions.
---

# Building Craft sites

The Craft conventions spec is the contract. When an existing project conflicts with it, the spec wins unless the user says otherwise. Load only the reference file you need:

| Task | Read |
|---|---|
| Stack, DDEV, env files, Vite wiring, project layout | [references/conventions/01-stack-and-tooling.md](references/conventions/01-stack-and-tooling.md) |
| Templates, extends chain, `_routing.twig`, rendering chain, template file convention, component catalog | [references/conventions/02-templates.md](references/conventions/02-templates.md) |
| SCSS, BEM, tokens, modern CSS | [references/conventions/03-scss.md](references/conventions/03-scss.md) |
| JS components and the `site.js` registry | [references/conventions/04-javascript.md](references/conventions/04-javascript.md) |
| Sections, entry types, builders, `common*` fields, shared blocks, navigation, globals, assets, project config | [references/conventions/05-content-model.md](references/conventions/05-content-model.md) |
| i18n, SEO meta, semantics, accessibility, errors, feeds | [references/conventions/06-i18n-seo-a11y.md](references/conventions/06-i18n-seo-a11y.md) |
| Performance budget, eager loading, images, delivery | [references/conventions/07-performance.md](references/conventions/07-performance.md) |
| Craft 4 → 5 or custom PHP → Craft migrations | [references/conventions/08-migration-playbook.md](references/conventions/08-migration-playbook.md) |
| Recipes, definition of done, anti-patterns | [references/conventions/09-recipes-and-anti-patterns.md](references/conventions/09-recipes-and-anti-patterns.md) |
| Formie, Blitz, SEOmatic, cookie banner and language plugins in templates | [references/plugin-integration.md](references/plugin-integration.md) |
| New project or first session in a project: AGENTS.md, MCP servers for Claude Code or Codex, `config/mcp.php`, AI user group | [references/project-setup.md](references/project-setup.md) |

Always also read the project's `AGENTS.md`: it records project-specific deviations.

## Ground rules

- Everything runs in DDEV: `ddev npm`, `ddev composer`, `ddev craft`. Never on the host. (In Claude Code, the craft-dev plugin's hook enforces this and asks before hand edits to `config/project/`.)
- Vanilla ES modules only. If a task seems to need a framework, stop and ask.
- Schema changes happen in **dev only** (`ALLOW_ADMIN_CHANGES=true`), and Craft writes the YAML. Never hand-edit `config/project/*.yaml` except mechanical renames you apply and verify immediately.
- Reuse before you create: check existing `common*` fields, blocks and atoms first.
- Empty content renders nothing. Never add placeholder or default copy (sole exception: the translated CTA-label fallback).

## Making schema changes

You can't click through the control panel, so use one of these, in order of preference:

1. **Craft MCP with full access in dev** (Craft 5.12+). Use the stdio server as an admin: the `craft-local-admin` server from `references/project-setup.md`. Call `info.get` first, then use the tools for fields, entry types and sections. Craft writes the YAML as if you used the CP.
2. **Ask the user to make the change in the CP** with an exact spec: handle, type, settings, field layout, Matrix group. Do this when MCP isn't available or the change involves settings the tools don't expose.
3. A Craft content migration (`ddev craft migrate/create`) only when the change must run as code, for example data transforms during a migration.

After any schema change: `git diff config/project` (review it: only the intended items changed), `ddev craft project-config/check`, commit the YAML with the templates that use it. Commit messages are one line in the EC git conventions (the project's `AGENTS.md`, `## Git`), for example `feat(page-builder): add timeline block`.

## Recipes

Each recipe ends with the definition of done in `09-recipes-and-anti-patterns.md`. Copy the checklist into your task list.

- **New builder block**: entry type `pageBlock<Name>` (reuse `common*` fields), add it to the builder Matrix under a group → adapter `03_organisms/page-builder/blocks/_pageBlock<Name>.twig` → molecule folder `02_molecules/<name>/` (Twig + SCSS, JS only if needed) → translations → editor manual entry → lint.
- **New section / entry type**: section + entry type with template `04_templates/_routing.twig` → `{% case %}` in `_routing.twig` → `04_templates/<kebab>/_<kebab>.twig` composing organisms → overview page type if it's a channel.
- **New icon**: `01_atoms/icon-<name>/_icon-<name>.twig` with a cleaned inline `<svg viewBox fill="currentColor">`; add to the icon Dropdown if CMS-selectable. Optimize hand-drawn or exported SVG: no editor metadata, no width/height, sensible precision.
- **New shared field**: check existing `common*` fields first; new generic field = `common<Name>`, generic label, no per-type instructions.
- **New global**: create only from the standard set (§10.6) unless asked; read it in `variables.twig`, organisms or adapters only.

## Validation loop

Run after every change set, fix, and repeat until clean:

```bash
python3 <this-skill>/scripts/lint_conventions.py .   # Twig structure, routing, adapters, translations, SCSS bans
ddev npm run lint:scss
ddev npm run build
ddev craft project-config/check
```

`lint_conventions.py` exits 1 on errors. Warnings need a reason if you leave them (some spec examples, such as leaf templates and the dispatcher, intentionally rely on context). Then render the affected pages and check the browser console and `storage/logs/`. For layout, image, font or JS changes, run Lighthouse mobile (all categories ≥ 90; LCP < 2.5s, CLS < 0.1, INP < 200ms).

## Handing over to content work

When a new block or section is ready for content, update the editor manual (`modules/manual/content/{nl,en}/blocks/<slug>.md`) and the block catalog in `docs/ai/instructions.md` (see project-setup.md), so the content skills know when to use the block.

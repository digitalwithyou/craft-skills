# Feature radar

New Craft features mapped to the Craft conventions (`spec/CRAFT-CONVENTIONS.md`). **Verified against Craft 5.12.0 on 2026-11-10.** When a newer release adds something relevant, append a row and update the verification line.

Status: `proposed` (worth a decision), `adopted` (in the conventions spec), `rejected` (decided against, with reason), `watch` (not yet actionable).

## Craft 5.12

| Feature | Impact on the conventions | Status |
|---|---|---|
| Built-in MCP server: authenticated HTTP (OAuth, acts as the user, read / read+write / full access), public HTTP, stdio `craft mcp/serve --user=…`; Settings → MCP | Basis for the content skills. Enable authenticated HTTP on staging + production; stdio locally. Setup in craft-building `references/project-setup.md`. | proposed |
| `config/mcp.php` `instructions` (also `CRAFT_MCP_INSTRUCTIONS`), appended to `info.get` | Load `docs/ai/instructions.md` (brand voice, block catalog, environment name) into every project. | proposed |
| Custom icon sets for Icon fields (`customIconPath`, "Icon Sets" field setting) | Could replace the icon Dropdown (§7.2) with a visual picker. Requires icons as `.svg` files, not Twig atoms; keep the inline-SVG rendering. | proposed |
| `project-config/check` command | Add to the migration QA gate (§14 step 7) and to deploy/CI. | proposed |
| "Sites" sidebar pane for multi-site editing | Editor UX only; mention in the editor manual. | adopted (no code) |
| Volume "Propagation Method"; assets save to the upload site | Check settings on multi-site projects with per-language assets. | watch |
| Color fields: translucent colors, `contrastColor`, `contrastRatio()` | Useful if a project lets editors pick colors: enforce WCAG AA in Twig. | watch |
| `{% render %}` Twig tag; `ElementHelper::renderElements()` deprecated | The conventions dispatch via `include`; no change. Search in-house plugins for the deprecated helper. | watch |
| Addresses support drafts | None unless a project uses Addresses. | watch |
| OAuth server + personal access tokens (My Account → Tokens), GraphQL OAuth | Only relevant for headless projects. | watch |
| Rate limits on login, TOTP and recovery-code endpoints | Free security gain; no action. | adopted (no code) |

## Craft 5.10–5.11

| Feature | Impact on the conventions | Status |
|---|---|---|
| Element deletion blockers modal (CKEditor references included) | Editor UX; no change. | adopted (no code) |
| `heading()`, `h1()`–`h6()` Twig functions | The `heading` atom keeps its contract; could use `heading(level, …)` internally. | watch |
| Opt-in origin verification (modern alternative to CSRF) | Evaluate with Blitz + Formie (cached forms) before enabling. | proposed |
| Replace custom fields inside existing layouts | Helps the migration playbook rename fields toward `common*`. | adopted (process) |
| Automatic alt text from image metadata | Good default; editors still review alt text. | adopted (no code) |
| 5.11: GraphQL user fields need "Query for users" in the schema | Only headless projects. | watch |

## Craft 5.8–5.9

| Feature | Impact on the conventions | Status |
|---|---|---|
| Content Block fields (single nested field group, reusable) | Candidate for grouping SEO fields or hero settings instead of loose fields. Decide per group. | proposed |
| Generated fields (Twig-computed values, sortable in indexes) | Useful for derived values (reading time, sort keys). | watch |
| Entry type groups in Matrix (grouped "Add" menus) | Matches §10.2 "group label per entry type"; check every builder uses groups. | adopted |
| Custom entry index pages (5.9) | Organize the CP sidebar: Pages / Articles / Shared blocks / Data. | proposed |
| Bulk Duplicate/Delete in Matrix cards and blocks views | Editor UX. | adopted (no code) |
| Element-based editability of tabs and fields | Lock fields per entry state when needed. | watch |
| Composer caret operator for automated requirement changes | Keep caret constraints (update-runbook.md). | adopted |

## Direction of travel

| Topic | Notes | Status |
|---|---|---|
| Entrification: global sets, categories and tags slated for removal in Craft 6 | The conventions keep Globals for site settings for now (owner decision, 2026-11). Track Craft 6 alpha/beta release notes for global-set support; the update report counts global sets per project. | watch |
| Craft 6 on Laravel: first alpha May 2026, GA targeted Q4 2026; Craft 5 is LTS for five years after 6 ships | Stay on Twig. `craft.app` is deprecated in favour of facades: the update report counts occurrences. In-house plugins need a `^6.0` major. | watch |
| Craft 6 MCP adds more tools (restore, validate, activity timeline, editorial comments) | Revisit the content skills when projects move to 6. | watch |

## Known inconsistency in the spec

`config/general.php` comments `preloadSingles()` as "globals readable in Twig without passing". Global sets are available in Twig without that setting; `preloadSingles` makes *Single* entries available by section handle. With no Singles in the model, the setting is inert. Fix the comment in the master spec (or keep the setting deliberately as preparation for Singles).

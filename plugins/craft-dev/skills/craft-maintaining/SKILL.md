---
name: craft-maintaining
description: Maintains Craft CMS 5 sites built with DWY's Craft conventions (atomic 00–04 template layers, one _routing.twig, pageBuilder blocks, common* fields, Sass/BEM, vanilla JS, Vite and DDEV). Updates Craft, plugins (Formie, Blitz, SEOmatic and others), in-house plugins and modules, and npm/Vite dependencies inside DDEV, then verifies, deploys and reports. Also proposes adopting new Craft features and checks Craft 6 readiness. Use when asked to update, upgrade, patch or audit a Craft site's dependencies, handle a security advisory, review deprecation warnings, or check what's new in Craft for a project.
---

# Maintaining Craft sites

Updates are low-freedom work: follow the sequence, never skip a verification step, and stop to ask when a step fails twice. Everything runs inside DDEV (`ddev composer`, `ddev npm`, `ddev craft`); never run composer, npm or `./craft` on the host.

Read the project's `AGENTS.md` first (Claude Code loads it via `CLAUDE.md`). It names the hosting (Ploi, Cloudflare), the deploy script and any project-specific plugins.

## Workflow

Copy this checklist into your task list and tick items off:

```
- [ ] 1. Preflight: clean git tree, new branch or worktree, DDEV running
- [ ] 2. Inventory: run scripts/update_report.py, save the report
- [ ] 3. Read changelogs and classify every change
- [ ] 4. Write the plan and get approval for majors and risky items
- [ ] 5. Back up: DDEV snapshot + Craft DB backup
- [ ] 6. Update Composer packages in groups, run migrations and project config
- [ ] 7. Update in-house plugins and modules
- [ ] 8. Update npm/Vite dependencies
- [ ] 9. Verify (all gates green)
- [ ] 10. Commit per group, merge, deploy
- [ ] 11. Feature adoption proposals + client report
```

### 1. Preflight

- `git status` must be clean. Work on `chore/updates-YYYY-MM` (or a worktree with its own DDEV project).
- `ddev start`, then `ddev craft migrate/all --interactive=0 && ddev craft project-config/apply` so you start from a consistent state.
- Read `## Lessons` in `AGENTS.md`: known traps from earlier runs on this project.
- If the local database is old, pull a fresh copy from production first (ask how; see `AGENTS.md`).

### 2. Inventory

```bash
python3 <this-skill>/scripts/update_report.py . --out storage/updates-report.md
```

The report lists Craft/PHP versions, outdated Composer and npm packages split into patch/minor/major, abandoned packages, in-house plugins with their Craft constraints, and Craft 6 readiness signals. It never changes anything.

### 3. Read changelogs and classify

For every package in the report, read the changelog between the installed and latest version: GitHub releases, `CHANGELOG.md` in the package, or plugins.craftcms.com/<handle>/changelog. Craft itself: github.com/craftcms/cms/releases.

Classify each change as **security** (GHSA/CVE), **breaking**, **feature** or **fix**. Note required actions (resave commands, template changes, config renames, PHP minimums). Never assume a minor release is harmless: Craft 5.11 changed GraphQL user-field visibility in a minor release.

**Many packages?** When more than ~5 packages have updates and your tool can run subagents (Claude Code, Codex), read the changelogs in parallel: one subagent per vendor group, a smaller/faster model is fine. Each returns only one line per package, so the changelogs never enter the main context:

```
package | from → to | security (IDs) | breaking | required actions | adopt? (feature worth proposing)
```

With 5 or fewer packages, read them yourself; the parallel setup costs more than it saves.

### 4. Plan

Write the plan to `docs/maintenance/YYYY-MM-DD-updates.md` (template in [references/update-runbook.md](references/update-runbook.md#plan-template)). Order: security first, then Craft minor by minor, then plugins, then npm. **Ask for approval** before any major version bump, any PHP or database version change, and anything marked breaking. For each of those, add one line: *"If this assumption is wrong: <what breaks, how we'd notice>"*. Patch and minor updates without breaking notes can proceed.

### 5. Back up

```bash
ddev snapshot --name pre-updates-$(date +%Y%m%d)
ddev craft db/backup
```

### 6. Composer updates

Follow [references/update-runbook.md](references/update-runbook.md). Per group: `ddev composer update <packages> -W`, then `ddev craft up --interactive=0` (migrations + project config), then `ddev craft project-config/check` (Craft 5.12+). Commit `composer.json`, `composer.lock` and any `config/project/` changes per group. Only run `composer update` locally; production only ever runs `composer install` from the committed lock file.

Plugin-specific notes (Formie, Blitz, Cloudflare, SEOmatic, in-house): [references/plugins.md](references/plugins.md).

### 7. In-house plugins and modules

Plugins in `plugins/` are local path packages. For each: read Craft's deprecations for the new version, fix them, run the plugin's own checks if it has them (ECS, PHPStan, Pest), bump its version, and `ddev composer dump-autoload` when classes were added. Keep the `craftcms/cms` constraint honest. See [references/plugins.md](references/plugins.md#in-house-plugins-and-modules).

### 8. npm and Vite

See [references/frontend-deps.md](references/frontend-deps.md). Patch/minor first (`ddev npm update`), majors one at a time, each followed by `ddev npm run build` and `ddev npm run lint:scss`.

### 9. Verify

All gates must pass before merging:

- `ddev craft project-config/check` clean; `ddev npm run build` succeeds; `ddev npm run lint:scss` clean
- Deprecation warnings reviewed (Utilities → Deprecation Warnings); new ones fixed or listed in the plan
- Every entry type renders: open the homepage, one page per entry type, one channel detail and the 404 page; check `storage/logs/` for new errors
- Forms: submit one Formie form per form type on the dev site
- If the `craft-building` skill is installed, run its `scripts/lint_conventions.py`
- Lighthouse mobile on the homepage if the frontend build or layout changed (budget in the Craft conventions §13)

### 10. Deploy

Merge, then deploy per `AGENTS.md`. The production sequence is `composer install --no-dev` → `php craft up --interactive=0` → frontend build (wherever the project builds `web/dist/`) → cache refresh (Blitz and/or Cloudflare, see plugins.md). Afterwards, smoke-test production: homepage, a form, the control panel login.

If a deploy breaks: check out the previous commit, `composer install`, and restore the automatic backup from `storage/backups/` only if migrations ran.

### 11. Feature adoption and client report

- Compare the new release notes with [references/feature-radar.md](references/feature-radar.md). For each relevant new feature, write a proposal (what, why, impact on the conventions, effort). **Do not implement proposals during an update run.** Update the radar file in this skill repo when you learn something new.
- Write the client report in the client's language using [references/client-report.md](references/client-report.md): only author-facing changes and security in plain words, no package names.
- **Lessons**: if something in this run would change what the *next* run does, add one line under `## Lessons` in the project's `AGENTS.md` (for example "Formie templates are overridden in templates/formie: diff them on every Formie update"). Nothing else gets logged: no "all went fine", no summaries. Read the Lessons section in step 1 of every run.

## Rules

- Never update on production or staging directly; never run `composer update` there.
- One concern per commit: a security fix is never mixed with a feature adoption. Messages are one line in the EC git conventions (`chore(deps): update …`; see update-runbook.md).
- A failing gate is a stop, not a warning. Report what failed and what you tried.
- Abandoned packages and plugins without Craft 6 support go into the report as risks, with an alternative when one exists.

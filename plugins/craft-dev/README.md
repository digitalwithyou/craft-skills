# craft-dev

Developer skills for Craft CMS 5, optimised for DWY client projects. Works in Claude Code and Codex.

- **craft-maintaining**: updates Craft, plugins (Formie, Blitz, SEOmatic, …), in-house plugins and modules, and npm/Vite dependencies inside DDEV. It follows a fixed sequence (inventory report, changelog review, plan, backup, grouped updates, verification gates, deploy), then writes feature-adoption proposals and a client report. Script: `scripts/update_report.py`.
- **craft-building**: templates in the atomic 00–04 layers, builder blocks, sections, fields, globals, SCSS/BEM, vanilla JS, i18n, SEO, accessibility and performance, plus project onboarding (AGENTS.md, MCP setup) and migrations. Script: `scripts/lint_conventions.py`.

Install in Claude Code with `claude plugin install craft-dev@dwy-craft` after `claude plugin marketplace add digitalwithyou/craft-skills`. In Codex, copy the `skills/` folders to `~/.agents/skills/`.

In Claude Code the plugin also adds a guard hook (`hooks/guard.py`): it denies composer/npm/npx/craft commands that bypass DDEV and asks before hand edits to `config/project/*.yaml`. It is silent otherwise.

Requirements: DDEV, Python 3 on the host (standard library only), Craft 5.12+ for MCP features.

The conventions spec is bundled as reference files, generated from `spec/CRAFT-CONVENTIONS.md` in the source repository.

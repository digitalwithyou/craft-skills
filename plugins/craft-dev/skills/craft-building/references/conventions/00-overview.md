<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. -->

# Craft CMS 5 Conventions — Structure, Naming & Way of Working

This document is the target-state specification for Craft CMS projects. It is written for an AI coding agent (or a developer) tasked with bringing an existing project in line with this structure.

**Usage scenarios:**

1. **Craft 4 → Craft 5 upgrade + restructure.** Run the official Craft upgrade first, then follow the Migration Playbook (§14) to restructure toward this spec.
2. **Custom-built PHP CMS → Craft CMS 5.** Follow the Migration Playbook from step 1; everything else in this document is the destination.
3. **New project.** Scaffold directly to this spec.

Rules in this document use MUST / never deliberately. When an existing project conflicts with this spec, the spec wins unless the user says otherwise.

## Files

- `01-stack-and-tooling.md`
- `02-templates.md`
- `03-scss.md`
- `04-javascript.md`
- `05-content-model.md`
- `06-i18n-seo-a11y.md`
- `07-performance.md`
- `08-migration-playbook.md`
- `09-recipes-and-anti-patterns.md`

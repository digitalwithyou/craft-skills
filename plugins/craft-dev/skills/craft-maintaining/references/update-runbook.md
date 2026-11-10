# Update runbook

## Contents

- Plan template
- Composer: grouping and order
- Craft minor updates
- Security advisories
- PHP and database versions
- Troubleshooting

## Plan template

```markdown
# Updates YYYY-MM-DD: <project>

Report: storage/updates-report.md (not committed)

## Security
| Package | From → To | Advisory | Action |

## Craft
| From → To | Breaking notes | Required actions (resave, config, templates) |

## Plugins
| Plugin | From → To | Kind | Notes / required actions |

## In-house plugins and modules
| Package | Change needed | Reason |

## npm
| Package | From → To | Kind | Notes |

## Needs approval
- <major bumps, PHP/DB changes, breaking changes>

## Risks
- <abandoned packages, plugins without Craft 6 support, alternatives>

## Feature proposals (not part of this run)
- <feature> → <proposal> (see feature-radar.md)
```

## Composer: grouping and order

1. Security fixes, each on its own commit.
2. `craftcms/cms` alone (with `-W` so its dependencies follow).
3. First-party plugins (`craftcms/ckeditor`, …).
4. Third-party plugins one vendor at a time (`verbb/*`, `putyourlightson/*`, `nystudio107/*`).
5. Everything else.

For each group:

```bash
ddev composer update <package(s)> -W
ddev craft up --interactive=0          # migrations + project config apply
ddev craft project-config/check        # 5.12+: confirms YAML and DB agree
git add composer.json composer.lock config/project
git commit -m "chore(deps): update <group> to <version>"   # format: see "Commit messages" below
```

Craft writes caret constraints (`^1.2.3`) into `composer.json` when it changes requirements itself (5.9+). Keep caret constraints; if a project still has exact pins from the old `craft update` behaviour, convert them to `^` deliberately in a separate commit.

## Craft minor updates

- Step through minors one at a time (5.10 → 5.11 → 5.12) when jumping more than one, so migrations and notes stay readable.
- Read the "Note" and "Warning" blocks at the top of each release: they list resave commands (for example `ddev craft resave/entries --section=… --update-search-index`) and behaviour changes.
- After 5.12: `config/mcp.php` and `config/oauth.php` become available. Don't enable MCP servers during an update run; that's a feature adoption (see feature-radar.md).

## Security advisories

- Sources: the GHSA list on the Craft release, GitHub advisories for plugins, the Craft Console notifications.
- A security update may skip the normal monthly cadence: branch, update just that package, verify, deploy the same day.
- Note the advisory ID in the commit subject (for example `chore(deps): update craftcms/cms to 5.12.1 (GHSA-xxxx-xxxx-xxxx)`) and the severity in the client report.

## PHP and database versions

- PHP changes touch three places: `.ddev/config.yaml` (`php_version`), `composer.json` `config.platform.php`, and the production server (Ploi). They must match; ask before changing any of them.
- Check the Craft requirement for the target version and every plugin's PHP constraint first.

## Commit messages

Follow the project's `## Git` section in `AGENTS.md` (EC git conventions): one line, `<type>(<scope>): <subject>`, imperative, lowercase, no period, at most 100 characters. No body or footer.

| Change | Header |
|---|---|
| Composer/npm update | `chore(deps): update craftcms/cms to 5.12.1` |
| Security update | `chore(deps): update craftcms/cms to 5.12.1 (GHSA-xxxx-xxxx-xxxx)` |
| Fix for a deprecation in an in-house plugin | `fix(<plugin-handle>): replace renderElements with Template::render` |
| Config change required by an update | `chore(config): enable origin verification` |
| Major update with breaking changes | `chore(deps): update verbb/formie to 3.0.0 (breaking: template overrides)` |

## Troubleshooting

- **Composer conflict**: run `ddev composer why-not <package> <version>` and report the blocking package instead of forcing.
- **Half-applied update** (vendor partially updated): `ddev composer install`, then `ddev craft up`.
- **Project config conflict after update**: `ddev craft project-config/diff`, decide which side is right, never hand-edit YAML except mechanical renames you immediately apply and verify.
- **Restore**: `ddev snapshot restore pre-updates-YYYYMMDD`.

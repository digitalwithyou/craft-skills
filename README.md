# Craft skills

Agent skills for Craft CMS 5, optimised for DWY client projects. They work with **Claude** and with **ChatGPT**: the skills use the open Agent Skills format (`SKILL.md`), and the Craft connection is Craft's own MCP server (5.12+).

| Plugin | For | Skills |
|---|---|---|
| `craft-dev` | developers | `craft-maintaining`: updates of Craft, plugins, in-house plugins/modules and npm/Vite, deploys, feature adoption, client reports · `craft-building`: templates, schema, front-end, project setup, migrations |
| `craft-content` | editors and clients | `craft-brand-discovery`: voice, visual and content strategy guides · `craft-preparing-pages`: pages and sections as drafts via Craft's MCP server, NL source with EN/FR |

The dev skills expect the conventions in `spec/CRAFT-CONVENTIONS.md`: atomic 00–04 template layers, one `_routing.twig`, `pageBuilder` blocks, `common*` fields, Sass/BEM, vanilla JS, Vite and DDEV. The content skills work on any Craft 5.12+ site and use its block catalog.

Project knowledge never lives in this repo. Each project keeps its own `AGENTS.md`, `docs/brand/`, `docs/content/` and `docs/ai/instructions.md`; Craft's MCP server sends the last one to every connected assistant. Setup: [project-setup.md](plugins/craft-dev/skills/craft-building/references/project-setup.md).

## Install for developers

**Claude Code**

```bash
claude plugin marketplace add digitalwithyou/craft-skills
claude plugin install craft-dev@dwy-craft
claude plugin install craft-content@dwy-craft
```

**Codex**: Codex reads skills from `.agents/skills` in a repo or `~/.agents/skills` for your user. Copy the skill folders there:

```bash
git clone https://github.com/digitalwithyou/craft-skills.git ~/src/craft-skills
mkdir -p ~/.agents/skills
cp -R ~/src/craft-skills/plugins/*/skills/* ~/.agents/skills/
```

Pull and copy again to update.

## Install for clients: Claude or ChatGPT

Clients use the assistant they already have. Both need the `craft-content` skills and a connection to their site.

| | Claude (claude.ai, Claude Desktop) | ChatGPT |
|---|---|---|
| Skills | Customize → Plugins → Add marketplace → `digitalwithyou/craft-skills`, install `craft-content`. Or upload the skill zips under Customize → Skills. | Skills → Create → Upload from your computer, one zip per skill. |
| Site connection | Custom connector per environment, URL `https://<site>/admin/mcp`, sign in with the client's "(AI)" Craft account | Developer mode → create an app per environment with the same URL, OAuth, same account |
| Creating drafts in Craft | Yes | Business, Enterprise and Edu workspaces. Plus/Pro connections are read-only: discovery, briefs and copy work, drafts are entered by hand |

Download the zips from the releases, or build them with `tools/package.sh`.

Example requests (either assistant):

- "Voer een merkontdekking uit voor onze website."
- "Bereid een nieuwe pagina 'Renovatie rijwoning' voor, eerst op staging."
- "De klant keurde de staging-versie goed, zet ze als concept op productie."

## What costs extra, and when

The skills stay lean by default. Extra checks only run where a mistake is expensive:

| Mechanism | Runs when | Cost | Why |
|---|---|---|---|
| DDEV guard hook (Claude Code) | every shell command and file edit in a DDEV Craft project | none unless it blocks (silent script, ~50 ms) | host-side composer/npm breaks vendor/node_modules; hand-edited project config breaks deploys |
| Fast path (pages) | small edits, factual updates | saves time: no brief, no approval stops | a changed opening hour doesn't need a content strategy |
| Independent review (pages) | new pages/sections or >300 words, and only with subagents | one extra agent call per page type | a fresh reviewer catches the writer's own habits and AI phrasing |
| Parallel changelogs (updates) | more than ~5 packages, subagents available | more calls, but the changelogs stay out of the main context | faster, and the main session stays focused on the plan |
| Parallel research (discovery) | three or more independent sources | one call per source | sources researched separately don't blur together |
| Source tags in brand guides | always | a few words per claim | interpretations aren't mistaken for client positions |
| Voice learnings, project lessons | only when a correction would change the next run | one table row | the same correction isn't needed twice |

Nothing runs in the background, nothing is logged "just in case", and chat-only setups (claude.ai, ChatGPT) skip the subagent steps and use the checklists instead.

## Safety model

- Content skills write drafts only, confirm the environment via `ENVIRONMENT:` in the MCP instructions, and never touch schema, globals or live content.
- Craft enforces it: assistants act as a Craft user in an "AI drafts" group without "Save entries" permission (Craft Pro). On Solo sites the guard is procedural only.
- Dev skills never run composer/npm on the host, never update on staging/production, and stop for approval on majors.

## Maintaining this repo

- Edit `spec/CRAFT-CONVENTIONS.md`, then run `python3 tools/split_spec.py`: it regenerates the reference copies inside the skills.
- `tools/package.sh` builds `dist/` with one zip per plugin and per skill.
- Bump `version` in each plugin's `.claude-plugin/plugin.json` on release.
- `plugins/craft-dev/skills/craft-maintaining/references/feature-radar.md` tracks new Craft features; update its verification line.
- Scenarios for evals: `evals/README.md`.
- Commit messages follow the [EC git conventions](https://ec.europa.eu/component-library/v1.15.0/eu/docs/conventions/git/): `<type>(<scope>): <subject>` with type feat, fix, docs, style, refactor, perf, test or chore; one line only (no body or footer), imperative, lowercase, no period, at most 100 characters. Scopes in this repo: `craft-dev`, `craft-content`, a skill name, `spec`, `tools`.

## Credits and inspiration

- Craft's built-in MCP server (5.12+).
- Wikipedia "Signs of AI writing" and the humanizer skill (blader/humanizer) for the AI-tell patterns, rewritten per language.
- Anthropic's knowledge-work-plugins `brand-voice` framework for the voice guide structure.
- michtio/craftcms-claude-skills for the idea of mirroring builder rules in review checklists.

MIT licensed.

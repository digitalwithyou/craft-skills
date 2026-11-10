---
name: craft-brand-discovery
description: Runs brand and content discovery for a website: researches the organization, interviews the client about purpose, audiences, positioning, voice and visual identity, and writes a voice guide, visual guide, content strategy, NL/EN/FR glossary and a condensed AI brief for the Craft CMS MCP server. Use when a site has no brand or voice guide yet, before preparing pages for a new client, or when asked to define, document or refresh a brand voice, tone of voice, style guide or content strategy.
---

# Brand and content discovery

Goal: written guides that let anyone (a person or an AI assistant) write and design content that sounds and looks like this organization. Discovery comes before page work; the `craft-preparing-pages` skill depends on its output.

Work in this order. Don't write guides from assumptions: every claim in a guide traces back to research, the client's words or an approved example.

```
- [ ] 1. Research: what already exists
- [ ] 2. Interview: fill the gaps (in rounds, not one long list)
- [ ] 3. Calibrate: show voice samples, let the client pick
- [ ] 4. Write the guides
- [ ] 5. Review with the client; record open questions
- [ ] 6. Deliver (repo files or documents) and the condensed AI brief
```

## 1. Research

Before asking anything, collect what exists so the interview only covers gaps. When there are three or more independent sources (the site, shared material, two or more competitors) and your tool can run subagents, research them in parallel: one subagent per source, each returning at most ~200 words in the summary format below. Otherwise go through them one by one.

- The current website (every main page, the About and Contact pages, product/service pages). If the Craft MCP connector is available, read the `pages` structure and a sample of entries; otherwise use web fetch.
- Existing brand material the client shares: brand book, logo files, presentations, brochures, job ads, social profiles, Figma or Sketch files.
- Two or three competitors or peers the client names (or that rank for their main services): how they position themselves, what they all say (so this client can say something else).

Write a short research summary: what the organization does, who it serves, recurring claims, current voice (with three quoted sentences from their own material), visual identity as found, inconsistencies.

## 2. Interview

Use [references/interview.md](references/interview.md). Ask in rounds of 3–5 questions, grouped by topic, and adapt follow-ups to the answers. Prefer questions that produce evidence ("what do customers say when they recommend you?") over abstract ones ("what are your values?"). Record the client's own words; they become copy material.

## 3. Calibrate the voice

Voice adjectives mean different things to different people, so calibrate with examples:

1. Take one real paragraph from their current site (or a typical service description).
2. Rewrite it in Dutch in 2–3 clearly different voices that fit the interview answers (for example: warm-informal `je`, factual-expert `u`, bold-short).
3. Ask which one is closest, and what to change. Repeat once with the refined version.
4. The approved paragraph becomes the reference sample in the voice guide.

## 4. Write the guides

Use the templates in [references/guide-templates.md](references/guide-templates.md):

- `docs/brand/voice.md`: personality, voice attributes on spectrums, `u`/`je`, tone by context, words to use and avoid, approved samples per language, a do/don't table.
- `docs/brand/visual.md`: logo use, colors with hex and contrast pairs, typography, photography direction, illustration and icon style, what to avoid. Include enough detail for generating visuals in style.
- `docs/content/strategy.md`: purpose of the site, audiences and their top tasks, key messages and proof points, primary actions, site structure (current and proposed), content priorities.
- `docs/content/glossary.md`: product and service names, preferred terms NL → EN → FR, words never to use.
- `docs/ai/instructions.md`: the condensed brief served by the Craft MCP server (≤ ~1,000 words). Template in the same reference file.

Tag every claim in the guides with where it comes from, so nobody mistakes your interpretation for the client's position:

- `[client]`: the client said or approved it
- `[found: <source>]`: seen in their site or material
- `[inferred]`: your interpretation; it stays **To confirm** until the client confirms it

Keep an "Open questions" list at the end of each guide. Create an empty `docs/brand/voice-learnings.md` from the template; the page skill fills it as the client corrects drafts.

## 5. Review

Send the guides (or a summary plus the voice sample) to the client, then apply the feedback. Approval of the voice sample matters more than approval of every adjective.

## 6. Deliver

- **In a project repo** (Claude Code, Codex): write the files at the paths above and tell the developer to commit them; `config/mcp.php` loads `docs/ai/instructions.md` (see the craft-building skill, project-setup.md).
- **Without a repo** (claude.ai, Claude Desktop, ChatGPT): produce the guides as documents and the AI brief as one text block, and tell the client to send them to their developer so they can be added to the site's MCP instructions.

## Rules

- Never invent facts, figures, customers, awards or quotes. A missing proof point is an open question, not something to fill in.
- Dutch (Belgium) is the source language; EN and FR sections of the glossary and samples are adaptations, approved separately.
- Sensitive business details (prices, margins, internal names) only go into the guides if the client agrees, since the AI brief is shared with every MCP client.

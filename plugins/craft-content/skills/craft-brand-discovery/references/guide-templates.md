# Guide templates

## Contents

- voice.md
- visual.md
- strategy.md
- glossary.md
- voice-learnings.md
- ai/instructions.md

## voice.md

```markdown
# Voice — <organization>

Status: draft | approved <date>

## Personality
<2–3 sentences: who we are when we talk.>

## Voice attributes
| Attribute | Where we sit | Means | Doesn't mean |
|---|---|---|---|
| Formal ↔ casual | 2/5 casual | short sentences, `je` | slang, emoji |
| Expert ↔ accessible | … | … | … |
| Serious ↔ playful | … | … | … |
| Modest ↔ confident | … | … | … |

## Address
- NL: u | je (per audience if different)
- EN: British | American; FR: vous

## Tone by context
| Context | Tone shift |
|---|---|
| Homepage, campaign | … |
| Service pages | … |
| Errors, forms, legal | … |
| Vacancies | … |

## Words
Use: <their own words from the interview>
Avoid: <their dislikes + generic clichés relevant to the sector>

## Approved samples
### NL (reference)
<the calibrated paragraph>
### EN / FR
<adapted versions, once approved>

## Do / don't
| Do | Don't |
|---|---|

## Open questions
- …
```

## visual.md

```markdown
# Visual identity — <organization>

## Logo
Files, variants, clear space, minimum size, don'ts.

## Colors
| Token | Hex | Use | Text on it (contrast ratio) |
|---|---|---|---|
| primary | #… | … | white 7.1:1 ✔ AA |

## Typography
Families, weights in use, web font source, fallback.

## Photography
Subjects, framing, light, people (real staff/customers, consent), what to avoid. Sources available.

## Illustration and icons
Style (line weight, corners, fill, colors), existing sets, examples. Icons are inline SVG with currentColor.

## Generating visuals
Prompt-ready description of the style (palette, line, texture, composition), reference files, what must never be generated (people presented as staff or customers, products, logos of others).

## Open questions
```

## strategy.md

```markdown
# Content strategy — <site>

## Purpose
One outcome that matters most, plus secondary outcomes.

## Audiences
| Audience | Top tasks | Knows | Hesitates because | Language(s) |

## Key messages and proof
| Message | Proof (only verified) |

## Primary actions
Per audience: the action and where it happens (form, phone, shop).

## Structure
Current sitemap → proposed sitemap (pages structure, channels), main navigation, footer.

## Priorities
Which pages first, what's missing, what to remove or merge.

## Open questions
```

## glossary.md

```markdown
# Glossary — <organization>

| NL (source) | EN | FR | Note |
|---|---|---|---|
| <product name> | (unchanged) | (unchanged) | never translated |

## Never use
| Term | Why | Use instead |
```

## voice-learnings.md

Corrections the client made to drafts, waiting to become rules. Write an entry only if it changes how the next page is written.

```markdown
# Voice learnings — <organization>

Promote an entry into voice.md when it's seen on 2+ pages or the client states it as a rule, then delete it here.

## Learnings
| Date | Page | Correction (before → after) | Therefore (next time) | Seen |
|---|---|---|---|---|
| 2026-11-10 | /diensten/renovatie | "ontzorgen" → "wij regelen de vergunning" | name the concrete task instead of "ontzorgen" | 1 |

## Tensions (contradict voice.md; the client decides)
| Date | Voice guide says | Client correction | Status |
|---|---|---|---|
```

## ai/instructions.md

Condensed brief, ≤ ~1,000 words, served by Craft's MCP server to every connected assistant. It repeats only what an assistant needs on every task; details stay in the full guides.

```markdown
# <Site> — instructions for AI assistants

## Rules
- Never publish, delete or change live content: create drafts only.
- Dutch (Belgium) is the source language; EN and FR are adaptations.
- Never invent facts, numbers, quotes, customers or people.

## About
<3 lines: what the organization does, for whom, main action on the site.>

## Voice
- <5–8 bullets>
- Address: NL <u|je>, FR vous, EN <British|American>
- Avoid: <short list>

## Content model
<copy from the craft-building project-setup.md template>

## Block catalog
| Block | Use it for | Don't use it for | Fields |
```

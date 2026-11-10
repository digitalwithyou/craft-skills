# Page brief and page types

## Contents

- Brief template
- Placing the page in the site
- Page types: what each must answer

## Brief template

```markdown
# Brief: <working title>

- Environment: staging | production (drafts)
- Type: <page type from the list below>
- Purpose: <one sentence: what this page must achieve>
- Audience: <who, what they already know, what they hesitate about>
- Their question or task: <in their words>
- Primary action: <one: call, form, book, buy, apply, read on>; secondary: <optional>
- Key message: <one sentence the visitor should remember>
- Proof: <facts that support the message: verified only, or TE BEVESTIGEN>
- Place in the site: parent <URI>, slug nl/en/fr, in main navigation: yes/no (under …)
- Reached from: <pages that will link here, search queries, campaigns>
- Links out: <where the visitor goes next>
- SEO intent: <main search query per language, if relevant>
- Success: <how we'll know it works: form submissions, fewer calls about X>
- Open questions
```

## Placing the page in the site

- Check the existing `pages` tree before adding anything: maybe the content belongs on an existing page (merge, don't duplicate).
- Keep navigation shallow: a visitor should reach any important page within two clicks of the homepage. More than 7 items in a navigation group is a signal to regroup.
- URL = structure: the parent determines the URI (`/diensten/renovatie`). Slugs are short, lowercase, in the site's language, without stop words when clarity allows (`renovatie-rijwoning`, not `onze-renovatie-van-rijwoningen`).
- Navigation is a global set: propose the change in the report; don't edit globals.
- Channel content (articles, cases, vacancies) goes in its channel, not in `pages`.

## Page types: what each must answer

The block names follow the Craft conventions (`pageBlock…`). Always use the site's actual block catalog.

| Type | Visitor's question | Must have | Typical blocks |
|---|---|---|---|
| Homepage | Am I in the right place, and where do I go? | what you do + for whom in one line, the 3–5 main paths, proof, primary action | hero, `pageBlockCards` (paths), `pageBlockLogoSlider` or proof, `pageBlockCta` |
| Service / product | Can they solve my problem, how, and what does it cost or take? | problem → approach → result, scope, process or steps, proof (case, numbers), FAQ for objections, one action | hero, `pageBlockRichText`, `pageBlockGrid` (steps/benefits), `pageBlockMedia`, `pageBlockFaq`, `pageBlockCta` |
| Overview (services, cases, articles) | Which one is for me? | one-line intro, filterable or grouped list, clear card labels | `pageBlockHeading`, `pageBlockOverview<X>` / `pageBlockCards` |
| About | Can I trust them? | why the organization exists, real people and places, history only if relevant, proof | `pageBlockRichText`, `pageBlockMedia`, `pageBlockGrid` |
| Contact | How do I reach them, and what happens next? | channels with response times, address and opening hours, form, what to prepare | `pageBlockRichText`, form block, map/media |
| Landing / campaign | Is this offer for me, and how do I get it? | one offer, one action, no navigation detours, proof close to the action | hero, `pageBlockGrid`, `pageBlockFaq`, `pageBlockCta`/form |
| Article / news | What's new or useful, and is it worth my time? | the news or answer in the first paragraph, date, author, related links | article builder blocks |
| Case | Did it work for someone like me? | client situation → what was done → measurable result → quote (real, approved) | case builder blocks |
| Vacancy | Is this job for me, and how do I apply? | role in one line, tasks, profile, offer (concrete), process, contact person | `pageBlockRichText`, `pageBlockGrid`, `pageBlockCta` |
| FAQ | Where's the answer to my question? | questions in the visitor's words, grouped, short direct answers with links | `pageBlockFaq` |
| Legal (privacy, terms, cookies) | What do they do with my data, what are the rules? | client-supplied or lawyer-approved text only | `pageBlockRichText` |

For legal pages: never write the legal content. Structure it and format supplied text only.

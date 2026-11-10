# Mapping content to blocks

## Where the catalog comes from

1. The block catalog in the `info.get` instructions (preferred: it says what each block is *for*).
2. The editor manual pages, if the project has them (`modules/manual/content/<lang>/blocks/`).
3. The builder Matrix field's entry types and their field layouts (read via the schema tools) for field names, required fields, limits and dropdown options.

Write down for each candidate block: purpose, fields (handle, type, required, limits), options (layout dropdowns), and how it renders when a field is empty (in the conventions: the markup is omitted).

## Outline table

Present the outline as a table in reading order:

| # | Section (what the visitor gets) | Block | Fields → content | Assets |
|---|---|---|---|---|
| 1 | What we do, for whom | hero `heroText` | heading, text, commonLink | — |
| 2 | Three reasons, with proof | `pageBlockGrid` | items[3]: heading, text, commonIcon | icons: …, … |
| 3 | Common questions | `pageBlockFaq` | items[5]: question, answer | — |
| 4 | Next step | `pageBlockSharedBlock` | sharedBlocks: "CTA offerte" | — |

## Rules

- **Content first, block second.** Decide what the visitor needs, then pick the block. Never pad a block's fields to make it look full: empty optional fields render nothing, which is correct.
- **Use blocks for what they are.** A FAQ block for questions and answers, cards for parallel items that link somewhere, a grid for parallel items without their own page. No hacks (a card grid with one card as a "highlight", a heading block used as a paragraph).
- **Shared blocks for repeated fragments.** If the same CTA or banner exists in `sharedBlocks`, insert it with the shared-block block instead of copying its content. If a fragment will be reused on several pages, propose a new shared block in the report.
- **One primary action per page**, usually at the end and optionally in the hero. Link fields carry their own label: write the label ("Vraag een offerte aan"), never leave it to the fallback ("Lees meer").
- **Spacers sparingly.** Use the spacer block only where the design needs a deliberate break, not between every block.
- **Headings form an outline.** One h1 (usually the hero or page title); sections descend without skipping levels. Where a block has a heading-level option, set it to fit the outline.
- **Rich text tiers.** Respect what each CKEditor config allows (basic, simple, full); don't paste headings into a field that doesn't support them.
- **Lists of items** (cards, grid, FAQ): keep items parallel in length and structure; 3–6 items is usually right, and odd counts are fine.

## Block request (when nothing fits)

```markdown
## Block request: <name by what it is, e.g. "timeline">

- Needed for: <page, section>
- Shows: <what the visitor sees>
- Fields: <field, type, required, limits>
- Why existing blocks don't fit: <specific>
- Used meanwhile: <closest honest alternative>
```

The developer builds it with the `craft-building` skill (entry type `pageBlock<Name>`, named by what it is, not where it's used).

# Translating NL → EN and FR

Dutch is written and approved first. EN and FR are **adaptations**: same facts, same structure and blocks, native phrasing. A reader should not be able to tell which language was the original.

## Process

1. Read the glossary (`docs/content/glossary.md` or the instructions): fixed terms, product names that never change, words to avoid.
2. Translate per block, keeping the outline. Don't add or remove claims; if something only makes sense for one audience (for example a Flanders-only service area), flag it instead of silently changing it.
3. Adapt what must change: examples, idioms, place names, units and formats, search terms (people search differently per language: write the SEO title for the phrase *they* use).
4. Localize every slug and every link label; internal links point to the same-language version of the target page.
5. Re-run the language's checklist ([writing-en.md](writing-en.md), [writing-fr.md](writing-fr.md)).
6. Present EN and FR for approval when the client has reviewers for those languages; otherwise mark them "machine-adapted, not reviewed" in the report.

## In Craft

- Each language is a site. Write the translation to the same draft for the `en` and `fr` sites after the `nl` site is filled.
- Respect each field's translation method: a field that isn't translatable shares its value across sites. Don't overwrite it from another language (check the field settings via the schema tools; if unsure, ask).
- Matrix/builder blocks: depending on the field's propagation settings, blocks may be shared across sites or separate. If blocks are shared, only translatable fields inside them differ per site; if separate, recreate the same block sequence per site.
- Assets: alt text per site if the volume's alt text is translatable.
- UI strings (buttons in templates, form labels in `translations/*/site.php`) are developer territory. If one is missing or wrong, report it; don't work around it in content.

## When the source changes

If the Dutch copy changes after translation, update EN and FR in the same pass and list what changed. Never leave languages out of sync in a draft handed over for review.

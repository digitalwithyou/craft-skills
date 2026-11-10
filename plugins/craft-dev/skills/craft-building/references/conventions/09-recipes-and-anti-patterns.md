<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## 15. Recipes & definition of done

### 15.1 New page-builder block

1. **CP**: create the entry type `pageBlock<Name>` (reusing `common*` fields), add it to the `pageBuilder` Matrix under the right group. Commit the YAML.
2. **Adapter**: `templates/03_organisms/page-builder/blocks/_pageBlock<Name>.twig` — thin field→param mapping with eager loading, delegating `with { … } only`.
3. **Molecule**: `templates/02_molecules/<name>/_<name>.twig` + `_<name>.scss` following §6 and §8.
4. **JS (if interactive)**: `<Name>.js` in the same folder, registered in the `site.js` map under a `js-<name>` hook class.

**Definition of done** — check every box:

- [ ] Entry type handle `pageBlock<Name>`, named by what it is, added to `pageBuilder` with a group
- [ ] Adapter is the only file reading `block.*`; eager loads relations
- [ ] Molecule has the docblock, `attributes` hash, `classes` param; all includes `only`
- [ ] Every optional field guarded — empty content renders nothing, no placeholder copy
- [ ] All strings through `|t('site')`, keys added to every `translations/*/site.php`
- [ ] SCSS scoped to the block class, chained BEM, lint-clean (`ddev npm run lint:scss`)
- [ ] Mobile first, grid/flex layout, no floats/`!important`; CSS used over JS where possible (§8.3)
- [ ] Semantic HTML (§12.1); keyboard-operable with visible focus; readable contrast (§12.2)
- [ ] Images through the `image` atom: webp, sized, sharp 2x srcset, lazy unless LCP (§13.2)
- [ ] JS (if any): class file + registry entry + `data-*` config, no `js-*` styling
- [ ] Project Config YAML committed
- [ ] Editor manual: `modules/manual/content/{nl,en}/blocks/<slug>.md` (with `block: pageBlock<Name>`) and `modules/manual/samples/pageBlock<Name>.php`, and `ddev craft manual/check` passes (`docs/manual.md`)

### 15.2 New icon

Create `01_atoms/icon-<name>/_icon-<name>.twig` with the inline `<svg viewBox fill="currentColor">`. If CMS-selectable, add `<name>` to the icon Dropdown options. Done — dynamic resolution picks it up.

### 15.3 New section / entry type

CP: section + entry type (template `04_templates/_routing.twig`, uriFormat per site) → add the `{% case %}` in `_routing.twig` → create `04_templates/<kebab-name>/_<kebab-name>.twig` composing organisms → commit YAML. If it's a channel, also create its `page<X>Overview` page entry type and overview block/template.

### 15.4 New shared field

Check the existing `common*` fields first — reuse beats creation. If genuinely new and generic: handle `common<Name>`, generic label, no per-type instructions baked in. Commit YAML.

## 16. Anti-patterns — never do these

- **No Singles.** Pages live in the `pages` structure; settings live in Globals.
- **No hardcoded or default copy** in blocks/molecules — no `block.field ?? "Some text"`. Empty ⇒ omit markup. (Sole exception: the translated CTA-label fallback for empty Link fields.)
- **No single-purpose block naming** — a block is never "the homepage X section".
- **No framework JS** — no React/Vue/Alpine/jQuery. Vanilla ES classes only.
- **No physical CSS properties** — logical only (`padding-inline-start`, not `padding-left`).
- **No floats for layout, no `!important`, no clearfix** — grid/flex and correct specificity.
- **No desktop-first CSS** — base styles are mobile; `min-width` queries only.
- **No JS for what CSS can do** — sticky, scroll, accordions, transitions, state styling are CSS jobs (§8.3).
- **No unsized or non-webp content images, no `<img>` outside the `image` atom** — CLS and blurry retina output are both bugs.
- **No icon fonts or raster icons** — icons are inline SVG atoms (§7.2).
- **No element queries inside loops (N+1), no unlimited overview queries** — eager-load and `.limit()` (§13.1).
- **No click handlers on `<div>`s, no `outline: none` without a replacement, no skipped heading levels.**
- **No flat BEM in nesting** — `&__item { &__label }`, never a re-declared `.block__item__label`.
- **No label+url field pairs** — use Link fields.
- **No globals/`entry` reads inside molecules or atoms** — explicit params only.
- **No `{% include %}` without `only`** (layout-level fundamentals excepted).
- **No manual SCSS import manifest** — the glob in `site.js` is the manifest.
- **No undocumented component templates** — every one starts with the §6 docblock.
- **No styling `js-*` classes, no JS bound to BEM classes.**
- **No mass-rewriting legacy code in an unrelated PR** — migrate folder by folder.

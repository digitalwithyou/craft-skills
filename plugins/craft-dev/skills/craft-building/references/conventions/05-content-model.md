<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## 10. Craft content model

### 10.1 Sections — no singles, a Pages structure

**Never create Singles.** The content model is:

- **`pages` (structure)** — the home of every page on the site, including the homepage (`uriFormat: '{ parent.uri != "__home__" ? parent.uri }/{slug}'`, home entry uses `__home__`). Nesting gives URL hierarchy for free. Template: `04_templates/_routing.twig`.
- **Channels/structures only for genuinely different content**: `articles`, `cases`, `news`, `services`, … and data-only sections like `team` (team members). Each gets its own entry type + `{% case %}` in `_routing.twig`; overview pages are `pages` entries (`pageArticleOverview`, …), not singles.
- **`sharedBlocks` (structure)** — predefined reusable blocks (§10.4).

What used to be a Single (contact page, about page) is a `pages` entry — almost always `pageGeneric`. Site-wide *settings* that used to live on singles belong in Globals (§10.6).

### 10.2 Entry types & builders

Naming is strict and uniform:

- Page entry types start with `page`: **`pageGeneric`** (the workhorse — the type used to create most pages), `pageHome` (only when the homepage layout truly differs), `page<X>Overview` for channel overview pages.
- Builder block entry types are `<builder-prefix>Block<Name>`: `pageBlockMedia`, `pageBlockRichText`, `pageBlockCards`, `articleBlockQuote`, `caseBlockMedia`, … The block adapter template filename equals the handle: `blocks/_pageBlockMedia.twig`.
- Name blocks by **what they are**, never by where they're used: `work-section`, `logo-slider` — not `homepage-clients`.

**Builders are Matrix fields**: `pageBuilder` (on every page type — the body of the page), `articleBuilder`, `caseBuilder`. Settings: card view (`defaultIndexViewMode: cards`), and a `group` label per entry type so the CP block picker is organized (e.g. *Basic* / *Lists & Grids* / *Structures* / *Forms*).

A healthy `pageBuilder` starter set: `pageBlockHeading`, `pageBlockRichText`, `pageBlockMedia`, `pageBlockCards`, `pageBlockGrid`, `pageBlockLogoSlider`, `pageBlockFaq`, `pageBlockCta`, `pageBlockNewsletterForm`, `pageBlockOverview<X>`, `pageBlockSpacer`, `pageBlockSharedBlock`.

### 10.3 Fields — share aggressively, prefix `common`

- **Share fields whenever it makes sense.** One `heading` concept = one field reused across dozens of entry types, not per-type duplicates.
- **Shared generic fields get the `common` prefix and a generic name**: `commonText`, `commonTextMultiline`, `commonImage`, `commonImages`, `commonLogos`, `commonLink`, `commonLightswitch`, `commonIcon`, `commonEmail`, `commonCode`, … Non-`common` handles are reserved for genuinely specific fields (`articleBody`, `seoRobots`).
- **Link fields over label+url pairs.** A native Craft Link field carries `.label` and `.url` in one field — use it for every CTA. The **one sanctioned content fallback** in the whole system: a translated default label when a Link field's label is empty:

  ```twig
  {% set ctaLabel = (block.commonLink.label ?? null) ?: ('Read more'|t('site')) %}
  ```

- **Few CKEditor configs, as tiers.** 3–5 configs total, named by editorial affordance: `commonRichTextBasic` (bold/italic) → `commonRichTextSimple` (+ links, lists) → `commonRichTextFull` (+ headings, media, nested entries), plus `commonHeadline` (single-line, marks only). Settings live inline in the field YAML. Nested-entry rendering goes through `partialTemplatesPath('01_atoms/rich-text')` → `templates/01_atoms/rich-text/entry/<type>.twig`.

### 10.4 Shared blocks

A `sharedBlocks` **structure** holds predefined blocks that appear on multiple pages (a CTA used on ten pages, edited in one entry). Each `sharedBlock` entry's body is the **same `pageBuilder` Matrix**. In the page builder, a `pageBlockSharedBlock` entry type holds an Entries field (`sharedBlocks`) sourced only from that section. Rendering is a two-file hop that **recurses back into the page builder**:

```twig
{# 03_organisms/page-builder/blocks/_pageBlockSharedBlock.twig #}
{% include "02_molecules/page-block-shared-block/_page-block-shared-block" with {
    sharedBlocks: block.sharedBlocks.all(),
} only %}
```

```twig
{#
    Page block: Shared block

    @param {array[Entry]} sharedBlocks
#}

{% for sharedBlock in sharedBlocks %}
    {% include "03_organisms/page-builder/_page-builder" with {
        blocks: sharedBlock.pageBuilder.eagerly().all(),
    } only %}
{% endfor %}
```

Because it re-enters `_page-builder.twig` with a different `blocks` array (the `blocks ?? entry.pageBuilder` contract from §5.5), the shared block needs **zero dedicated templates** and every block type is automatically shareable.

### 10.5 Navigation

- Navigation is **globals-driven**: a `navigation` (or `header`) global set with Matrix fields (`mainMenu`, optionally `topNavigation`), editable by the client.
- Nav item entry types stay few by being **polymorphic**: a `type` Dropdown (`link` | `section`) with `elementCondition` rules on the field layout, so the CP shows either a single `commonLink` or a group label + nested `subitems` Matrix. Prefer this over one entry type per nav flavor.
- **Include the most-used structures in the main navigation** as section groups whose sublinks point at entries in `pages`/`cases`/`articles` — the nav mirrors the site's primary structures rather than a hand-maintained flat list.
- Query the nav **once** in `variables.twig`, stash on `_globals`, read it in both `navigation-main` and `site-footer` (§5.3).
- A small Twig extension helper `isActiveNavItem(linkfield)` (current path vs. the Link field's element URI, prefix-matched for sub-pages) keeps active states out of the templates.

### 10.6 Globals — site-wide settings

Globals replace settings-singles. Standard set (create what applies):

`navigation`, `companyInfo` (address, email, telephone), `socialMedia` (matrix of channels), `header` (behavior preferences), `footer` (CTA-band matrix), `seo` (defaults, og-image), `tracking`, `newsletter`, `legal`, `notFound`, `serverError`, `rss`.

With `preloadSingles()` on, templates read them by handle without passing — but **only** in `variables.twig`, organisms, and adapters (§6 rule 7).

### 10.7 Assets

- **Default filesystem**: `uploads` (`craft\fs\Local`, `@webroot/uploads`) for editorial and design assets.
- **Volumes as subpaths on it**: `images`, `videos`, `logos` — plus `symbols` or `illustrations` only when the design includes those. A new asset *category* is a volume on an existing filesystem.
- **User uploads on separate storage, preferably where no scripts can run**: files uploaded by visitors (front-end forms) go on their own filesystem, never in `@webroot/uploads`. Use object storage (an S3-compatible bucket served from its own domain): an uploaded script can't execute there, and the storage scales independently of the web server. Only when a project can't use object storage: a local filesystem outside the webroot, served without PHP execution.
- **More filesystems when the storage differs**: besides user uploads, for example private files or large media. Configure path and URL through environment variables, and give files that must stay private a filesystem without public URLs.
- **Named image transforms** per ratio/size (`sixteentonine_768x432`, `square_1200`, …) plus `openGraphImage` (1200×630 crop). The `image` atom applies transforms + webp + `srcset`; templates never call `.getUrl()` with inline transform hashes.

### 10.8 Project Config workflow

`config/project/*.yaml` is the source of truth. Make schema changes in the CP (dev only, `ALLOW_ADMIN_CHANGES=true`), let Craft write the YAML, commit it. Other environments have admin changes disabled and sync with `ddev craft project-config/apply`. Never hand-edit YAML except for mechanical renames you immediately apply and verify.

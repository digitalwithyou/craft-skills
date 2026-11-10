# Plugin integration in templates

## Formie

- Forms are rendered through a builder block (for example `pageBlockForm` with a Formie field), adapter → molecule, like every other block. The molecule receives the form element as a param and renders it with `craft.formie.renderForm(form)` (or the project's custom rendering).
- Style Formie output in the molecule's SCSS, scoped to the block class. Don't load Formie's default CSS when the project styles forms itself (form settings → "Output CSS"/"Output theme").
- Field labels and messages come from Formie (content). UI strings around the form still go through `|t('site')`.
- Keep the conventions' `form-field` atom for non-Formie forms (newsletter, search).
- File upload fields: point them at a dedicated user-uploads volume on the separate user-uploads filesystem (conventions §10.7), never at the editorial `uploads` volumes. Restrict allowed file types and size in the field settings.
- Accessibility: check that labels, error messages (`aria-describedby`) and focus on error work after styling.

## Blitz

- Pages are cached as static HTML. Anything per-visitor (CSRF tokens, cookie consent state, language suggestions, logged-in state) must be client-side or use Blitz dynamic content (`craft.blitz.csrfInput()`, `craft.blitz.includeDynamic(...)`).
- Don't use `{% cache %}` and Blitz on the same fragment without a reason; Blitz already caches the page.
- Element queries in templates are tracked for cache invalidation; avoid raw DB queries in templates.

## Cloudflare

- HTML caching rules must bypass `/admin*`, `/actions/*`, `/.well-known/*`, preview requests (`token`/`x-craft-preview` query parameters) and any form endpoints.
- Assets in `web/dist/` are hashed: long cache lifetimes are safe.

## SEOmatic

- When present, SEOmatic replaces `00_fundamentals/meta/_seo.twig`. Keep the `hreflang` logic consistent with the language switcher (§12).
- Per-entry SEO uses an SEOmatic field (Content SEO), not `common*` fields.
- Without SEOmatic: the `seo` global holds defaults; per-entry overrides live in the entry type's SEO fields (a Content Block field is a good fit, see feature-radar in craft-maintaining).

## In-house plugins (cookie banner, first-visit language selection)

- Both must work on cached HTML: decisions happen in the browser (`localStorage`/cookie + JS), never by server-side per-visitor rendering.
- Language selection: suggest, don't force-redirect bots; keep `hreflang` and canonical intact.
- Tracking (`meta/_tracking.twig`) loads only after consent and stays last in `<body>`.

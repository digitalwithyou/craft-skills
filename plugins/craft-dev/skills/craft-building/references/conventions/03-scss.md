<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## 8. SCSS conventions

### 8.1 Stylelint config (enforced via pre-commit)

`.stylelintrc.json`:

```json
{
  "extends": [
    "stylelint-config-standard-scss"
  ],
  "plugins": [
    "stylelint-order",
    "stylelint-use-logical"
  ],
  "rules": {
    "order/properties-alphabetical-order": true,

    "csstools/use-logical": "always",

    "declaration-property-value-disallowed-list": {
      "/^padding-(top|right|bottom|left)$/": ["/.*/"],
      "/^margin-(top|right|bottom|left)$/": ["/.*/"],
      "/^border-(top|right|bottom|left)(-.*)?$/": ["/.*/"],
      "/^(top|right|bottom|left)$/": ["/.*/"],
      "text-align": ["left", "right"]
    },

    "max-nesting-depth": 5,
    "selector-max-compound-selectors": 4,

    "selector-class-pattern": [
      "^[a-z][a-z0-9]*(-[a-z0-9]+)*(__[a-z0-9]+(-[a-z0-9]+)*)*(--[a-z0-9]+(-[a-z0-9]+)*)?$",
      {
        "message": "Class names should follow chained-BEM: .block__element__sub--modifier",
        "resolveNestedSelectors": true
      }
    ],

    "no-descending-specificity": null,
    "rule-empty-line-before": ["always", {
      "except": ["first-nested"],
      "ignore": ["after-comment"]
    }],

    "scss/selector-no-redundant-nesting-selector": true,

    "color-function-notation": null,
    "alpha-value-notation": null,
    "hue-degree-notation": null,
    "media-feature-range-notation": null
  },
  "ignoreFiles": [
    "node_modules/**",
    "vendor/**",
    "web/dist/**",
    "storage/**"
  ]
}
```

### 8.2 The rules in prose

- **Chained BEM via SCSS nesting.** Elements nest under elements: `&__item { &__emoji { … } }` compiles to `.block__item__emoji` — not flat `.block__emoji`. Twig class names must match the chained output. Modifiers: `&--large`.
- **Alphabetical property order** inside every rule.
- **Logical properties only**, no exceptions: `inline-size`/`block-size`, `max-inline-size`, `padding-inline-*`/`padding-block-*`, `margin-inline`/`margin-block`, `inset-inline-*`, `border-block-*`, `text-align: start/end`. `stylelint --fix` rewrites physical properties automatically.
- **Design tokens as CSS custom properties** — `var(--color-ink)`, `var(--font-display)`, `var(--s-sec-y)` — never SCSS variables in component files. SCSS variables are only for compile-time needs (breakpoints in `@media` are the common case: `@use '../../00_config/breakpoints-config' as *;`).
- `rem` for typography, `clamp()` for fluid sizes, `text-wrap: balance` on headlines / `pretty` on long-form copy.
- Formatting: 4-space indent, single blank line between sibling rules, no blank line before a first-nested rule.
- One SCSS file per component, scoped to its block class. No global component styles outside `00_fundamentals`.

### 8.3 Modern CSS

Write CSS as it is in the current decade — this is a hard requirement, not a preference:

- **Layout with CSS Grid and Flexbox.** Grid for two-dimensional layout and page/section structure, flex for one-dimensional alignment. **Never floats** for layout, never absolute-positioning hacks where grid/flex does the job, no clearfix utilities.
- **No `!important`.** If specificity forces it, the selector structure is wrong — fix the nesting/order instead.
- **Mobile first.** The unqueried base styles are the small-screen styles; enhance upward with `@media (min-width: …)` only. Never write desktop-default styles overridden back down with `max-width` queries.
- **Prefer intrinsic/fluid sizing over breakpoints**: `clamp()`, `minmax()`, `auto-fit`/`auto-fill`, `aspect-ratio`, `gap`, container-relative units. A component that only works at specific widths is a bug.
- **CSS over JavaScript, always.** If CSS can do it, CSS does it: sticky headers (`position: sticky`), smooth scrolling (`scroll-behavior`), scroll snapping, accordions (`<details>`), simple carousels (scroll snap), transitions/animations, auto-numbering (counters, §8.4), `:hover`/`:focus-visible`/`:has()` state styling. JS is reserved for genuine behavior (fetching, complex state, focus management).
- Use modern selectors and features freely (`:has()`, `:is()`/`:where()`, `@supports` for progressive enhancement); animate only `transform` and `opacity`, and wrap non-essential motion in `@media (prefers-reduced-motion: no-preference)`.

### 8.4 Token files (`templates/00_config/`)

- **`_colors-config.scss`** — two layers: SCSS `$vars` (compile-time mirror) → `:root { --color-x: #{$color-x}; }`, then semantic aliases (`--color-text`, `--color-background`, `--color-border`). If the design has themes, a `html[data-theme="dark"]` block overrides only the themeable tokens, and theme-stable tokens (e.g. `--color-slab*` for always-dark bands) stay put.
- **`_fonts-config.scss`** — font stacks (`--font-display`, `--font-text`, `--font-mono`), a fluid type scale (`--fs-display` … `--fs-meta`, `clamp()`-based), and a density scale for spacing (`--s-hero-y`, `--s-sec-y`, `--s-block`, `--gutter`). Section/hero padding always uses the density tokens — no ad-hoc px.
- **`_breakpoints-config.scss`** — SCSS breakpoint variables + `$max-width`.

A trick worth reusing: CMS-free auto-numbering with CSS counters (`body { counter-reset: section; }` + `.section-label { counter-increment: section; }` + `content: counter(section, decimal-leading-zero)`) — the CMS stores only labels, order and numbering stay correct automatically.

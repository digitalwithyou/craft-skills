<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. Do not edit this copy; edit the master and regenerate. -->

## 9. JavaScript conventions

### 9.1 `site.js` — the single entry

The prescribed shape — a registry map, one boot loop, zero per-component boilerplate:

```js
import.meta.glob('./**/*.scss', { eager: true });

import LanguageSwitcher from './02_molecules/language-switcher/LanguageSwitcher';
import NavigationMain from './02_molecules/navigation-main/NavigationMain';
import ThemeToggle from './01_atoms/theme-toggle/ThemeToggle';
import PageBlockLogoSlider from './02_molecules/page-block-logo-slider/PageBlockLogoSlider';

/**
 * Selector → component class. One entry per interactive component.
 * Every selector is a `js-*` hook class, never a styling class.
 */
const components = new Map([
    ['.js-language-switcher', LanguageSwitcher],
    ['.js-navigation-main', NavigationMain],
    ['.js-theme-toggle', ThemeToggle],
    ['.js-page-block-logo-slider', PageBlockLogoSlider],
]);

document.addEventListener('DOMContentLoaded', () => {
    for (const [selector, Component] of components) {
        document.querySelectorAll(selector).forEach((element) => new Component(element));
    }
});
```

Adding an interactive component = one import + one Map entry.

### 9.2 Module rules

- **One default-export ES class per file**, PascalCase filename, co-located in the component's folder (§5.2). No frameworks, no global scripts.
- **Constructor takes the root element** and must no-op safely (guard against missing children). The registry only instantiates when the selector matches, so absence on a page costs nothing.
- **`js-*` hook classes** are the only JS↔DOM contract on the root; inside the component prefer `[data-*]` selectors so BEM renames never break behavior. Never style a `js-*` class; never bind JS to a BEM class.
- **Configuration via `data-*` attributes** written by the Twig template — scalars as plain attributes (`data-marquee-speed="40"`), complex config as JSON (`data-presets='{{ presets|json_encode }}'`). The class reads `element.dataset` with documented defaults. No inline `<script>` config.
- The Twig side sets both in the `attributes` hash:

  ```twig
  {% set attributes = {
      "class": ["logo-slider", "js-page-block-logo-slider"]|merge(classes ?? []),
      "data-speed": speed ?? 40,
  } %}
  ```

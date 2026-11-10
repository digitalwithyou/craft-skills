# npm and Vite updates

The frontend stack in the Craft conventions: Vite + `vite-plugin-restart`, Sass, Stylelint (`stylelint-config-standard-scss`, `stylelint-order`, `stylelint-use-logical`), husky, lint-staged, wired to Craft via `nystudio107/craft-vite`. No frameworks.

## Order

1. `ddev npm outdated` (the update report already lists it).
2. Patch and minor: `ddev npm update`, then build and lint.
3. Majors one at a time, each on its own commit: `ddev npm install <package>@<major> --save-dev`.

After every step:

```bash
ddev npm run build
ddev npm run lint:scss
```

## Majors that need care

- **Vite**: read the migration guide for the version. Check `vite.config.mjs` (`build.target`, `rollupOptions`, `server.origin`/`allowedHosts`), the manifest path in `config/vite.php` (`@webroot/dist/.vite/manifest.json`), and that `craft-vite` supports the new manifest format. Test HMR in DDEV (`ddev npm run dev`, edit an SCSS file) and the production build.
- **Sass**: deprecations (for example `@import`, global functions) surface as build warnings; fix them in the component files, don't silence them.
- **Stylelint and its plugins**: a new major can add or rename rules. Run `ddev npm run lint:scss`; when the new version reports new violations, fix them with `lint:scss:fix` where safe and review the diff. Keep `.stylelintrc.json` in line with conventions §8.1.
- **husky / lint-staged**: after a major, run `ddev npm install` so `prepare` re-wires the hook, then make a test commit that touches an SCSS file.

## Rules

- Commit `package.json` and `package-lock.json` together.
- `web/dist/` is gitignored; never commit build output.
- No new runtime dependencies during an update run.

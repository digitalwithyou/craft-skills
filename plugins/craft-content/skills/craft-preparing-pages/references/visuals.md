# Visuals and assets

## Order of preference

1. **Existing assets** on the site that fit (search the volumes by title and filename first).
2. **The client's own photos**: real people, places, work. These build the most trust; ask for them in the report.
3. **Commissioned photography**: write a shot list (subject, setting, orientation, which block and transform).
4. **Licensed stock**: only for generic context (a city, a material), never presented as the client's team, customers or work.
5. **Generated visuals**: icons, diagrams, patterns and illustrations in the brand style (below).

Never generate or fake: people presented as staff, customers or testimonials; the client's products, premises or projects; logos of other companies; certificates or awards.

## Generating visuals

Read `docs/brand/visual.md` first (colors, line style, corners, illustration style). Then:

| Visual | How |
|---|---|
| Icons | Draw as SVG directly: single color, `fill="currentColor"` (or `stroke="currentColor"` for line icons), a `viewBox`, no width/height, no editor metadata, consistent grid (24×24) and stroke width with the existing set. On sites that follow the Craft conventions, icons are template files (`01_atoms/icon-<name>/`), so a new icon is a developer request: deliver the SVG with the request. |
| Diagrams (process steps, timelines, simple schemas) | SVG with brand colors and fonts available on the site; text kept minimal and also present in the page copy (accessibility, translation). |
| Patterns, shapes, backgrounds | SVG; decorative (empty alt). |
| Illustrations and compositions | Figma when the Figma connector is available: work in the client's Figma file or library so the designer can refine it, then export SVG or PNG. Sketch files: ask the designer for exports. |
| Photos | Not generated (see the never-list). |

Show generated visuals to the user before using them; keep the source file (SVG, Figma link) with the delivery.

## Specs per asset

For each asset in the plan:

- Block and field it goes in; volume (`images`, `logos`, `videos`, `illustrations`, `symbols`)
- Orientation and minimum size: at least 2× the largest named transform it's used in (the Craft conventions render 1×/2× srcsets; small sources look soft on retina)
- Filename: lowercase, hyphens, descriptive
- Alt text per language, or "decorative"
- Focal point when the transform crops (faces, product)
- Credit/license note for stock

## Upload

Craft's MCP server creates assets only from public HTTPS URLs. Otherwise deliver files with their specs and ask the user to upload them in the control panel, then link them in the draft (see environments-and-safety.md).

## Video

Prefer embeds the site supports (check the block catalog). Every video needs captions and a short text summary in the page. Never autoplay with sound.

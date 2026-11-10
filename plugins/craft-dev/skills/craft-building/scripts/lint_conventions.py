#!/usr/bin/env python3
"""Check a Craft project against the Craft conventions (spec/CRAFT-CONVENTIONS.md).

Runs on the host with the Python 3 standard library only (no ddev needed),
because it only reads files: templates/, translations/ and config/project/.

Usage:
    python3 lint_conventions.py [PROJECT_ROOT] [--only CHECK[,CHECK...]] [--warnings-as-errors]

Exit code: 0 when there are no errors, 1 when errors were found, 2 on bad usage.
Stylelint covers SCSS formatting and logical properties; this script covers the
rules stylelint cannot see (Twig structure, routing, adapters, translations).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Result collection
# ---------------------------------------------------------------------------


@dataclass
class Finding:
    level: str  # "error" or "warning"
    check: str
    path: str
    line: int
    message: str


FINDINGS: list[Finding] = []


def report(level: str, check: str, path: Path | str, line: int, message: str) -> None:
    FINDINGS.append(Finding(level, check, str(path), line, message))


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TWIG_COMMENT = re.compile(r"\{#.*?#\}", re.DOTALL)
COMPONENT_LAYERS = ("01_atoms", "02_molecules", "03_organisms", "04_templates")
DOCBLOCK_KINDS = ("Atom:", "Molecule:", "Organism:", "Template:", "Page block:")


def strip_comments(text: str) -> str:
    """Blank out Twig comments but keep newlines so line numbers stay correct."""
    return TWIG_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def rel(project: Path, path: Path) -> str:
    return str(path.relative_to(project))


def kebab(handle: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "-", handle).lower()


def is_adapter(parts: tuple[str, ...]) -> bool:
    return "blocks" in parts


def is_exempt_from_docblock(parts: tuple[str, ...], name: str) -> bool:
    if is_adapter(parts):
        return True  # thin field->param adapters; the molecule carries the docs
    if any(p.startswith("icon-") for p in parts):
        return True  # icon atoms are bare inline SVG
    if "rich-text" in parts and "entry" in parts:
        return True  # CKEditor nested-entry partials
    if name in ("_routing.twig", "_head.twig"):
        return True
    return False


# ---------------------------------------------------------------------------
# Checks on Twig templates
# ---------------------------------------------------------------------------

INCLUDE_TAG = re.compile(r"\{%-?\s*include\b(.*?)-?%\}", re.DOTALL)
BLOCK_READ = re.compile(r"\bblock\.[A-Za-z_]")
ENTRY_READ = re.compile(r"\bentry\.[A-Za-z_]")
GLOBALS_READ = re.compile(r"\b_globals\b")
IMG_TAG = re.compile(r"<img\b", re.IGNORECASE)
ROOT_CLASS_STRING = re.compile(r"\{#\s*Output\s*#\}\s*<(\w+)\s+class=\"", re.DOTALL)


def check_twig(project: Path, templates: Path) -> None:
    for path in sorted(templates.rglob("*.twig")):
        relative = path.relative_to(templates)
        parts = relative.parts
        layer = parts[0] if parts else ""
        raw = path.read_text(encoding="utf-8", errors="replace")
        code = strip_comments(raw)
        shown = rel(project, path)

        # Rule 1: docblock first (components only).
        if layer in COMPONENT_LAYERS and path.name.startswith("_") and not is_exempt_from_docblock(parts[:-1], path.name):
            head = raw.lstrip()
            level = "warning" if layer == "04_templates" else "error"
            if not head.startswith("{#"):
                report(level, "docblock", shown, 1, "Component must start with a {# Atom:/Molecule:/Organism:/Template: … #} docblock (§6 rule 1).")
            else:
                first_block = head[: head.find("#}") + 2]
                if not any(kind in first_block for kind in DOCBLOCK_KINDS):
                    report("warning", "docblock", shown, 1, "Docblock does not name the layer (Atom:/Molecule:/Organism:/Template:).")

        # Rule 2/4: Variables/Output sections and attr() on the root.
        if layer in ("01_atoms", "02_molecules") and not is_exempt_from_docblock(parts[:-1], path.name):
            if "{# Output #}" not in raw:
                report("warning", "sections", shown, 1, "Missing '{# Output #}' section marker (§6).")
            match = ROOT_CLASS_STRING.search(raw)
            if match:
                report("error", "root-attr", shown, line_of(raw, match.start()), "Root element uses a hand-written class string; render it with attr(attributes) (§6 rule 4).")

        # Rule 6: includes use `with { … } only`.
        if layer not in ("00_layouts", "00_config", "00_fundamentals") and layer != "04_templates":
            for match in INCLUDE_TAG.finditer(code):
                args = match.group(1)
                if "/blocks/_" in args or "blocks/_\"" in args:
                    continue  # dispatcher -> adapter hop passes `block` implicitly by design
                if "00_fundamentals" in args:
                    continue  # layout-level fundamentals are exempt
                if not re.search(r"\bonly\b", args):
                    report("warning", "include-only", shown, line_of(code, match.start()), "Include without `only` leaks ambient context (§6 rule 6).")

        # Rule 7: molecules and atoms take explicit params only.
        if layer in ("01_atoms", "02_molecules"):
            for pattern, what in ((BLOCK_READ, "block.*"), (ENTRY_READ, "entry.*")):
                for match in pattern.finditer(code):
                    report("error", "explicit-params", shown, line_of(code, match.start()), f"{what} read inside an atom/molecule; resolve it in the adapter or organism (§6 rule 7).")
            for match in GLOBALS_READ.finditer(code):
                report("warning", "explicit-params", shown, line_of(code, match.start()), "_globals read inside an atom/molecule; pass the data in as a param unless this is a documented exception (§6 rule 7).")

        # Adapters are the only place block.* may be read; flag organisms outside blocks/.
        if layer == "03_organisms" and not is_adapter(parts[:-1]):
            for match in BLOCK_READ.finditer(code):
                snippet = code[match.start(): match.start() + 12]
                if snippet.startswith("block.type"):
                    continue  # the dispatcher switches on block.type
                report("warning", "adapter-only", shown, line_of(code, match.start()), "block.* read outside a blocks/ adapter (§5.5).")

        # Images only through the image atom.
        if not (layer == "01_atoms" and len(parts) > 1 and parts[1] == "image"):
            if layer != "00_mails":
                for match in IMG_TAG.finditer(code):
                    report("error", "image-atom", shown, line_of(code, match.start()), "<img> outside the image atom (§13.2, §16).")

        # Icon atoms: inline SVG, currentColor, no fixed size.
        if any(p.startswith("icon-") for p in parts[:-1]):
            svg = re.search(r"<svg\b[^>]*>", raw, re.IGNORECASE | re.DOTALL)
            if not svg:
                report("error", "icon", shown, 1, "Icon atom contains no inline <svg> (§7.2).")
            else:
                tag = svg.group(0)
                if re.search(r"\s(width|height)=", tag):
                    report("warning", "icon", shown, line_of(raw, svg.start()), "Icon <svg> has a fixed width/height; size it with CSS (§7.2).")
                if "viewBox" not in tag:
                    report("error", "icon", shown, line_of(raw, svg.start()), "Icon <svg> has no viewBox (§7.2).")
                if "currentColor" not in raw:
                    report("warning", "icon", shown, 1, "Icon does not use currentColor, so it cannot inherit color (§7.2).")


# ---------------------------------------------------------------------------
# Checks on SCSS that stylelint does not cover
# ---------------------------------------------------------------------------


def check_scss(project: Path, templates: Path) -> None:
    for path in sorted(templates.rglob("*.scss")):
        text = path.read_text(encoding="utf-8", errors="replace")
        shown = rel(project, path)
        code = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.DOTALL)
        code = re.sub(r"//[^\n]*", "", code)
        for match in re.finditer(r"!important", code):
            report("error", "scss", shown, line_of(code, match.start()), "!important is banned; fix specificity instead (§8.3).")
        for match in re.finditer(r"\bfloat\s*:", code):
            report("warning", "scss", shown, line_of(code, match.start()), "float used; layout must use grid/flex (§8.3).")
        for match in re.finditer(r"@media[^{]*\bmax-width\b", code):
            report("warning", "scss", shown, line_of(code, match.start()), "max-width media query; write mobile-first with min-width (§8.3).")
        is_config = "00_config" in path.parts or "00_fundamentals" in path.parts
        if not is_config:
            for match in re.finditer(r"^\s*\$[\w-]+\s*:", code, re.MULTILINE):
                report("warning", "scss", shown, line_of(code, match.start()), "SCSS variable declared in a component; use CSS custom properties for tokens (§8.2).")


# ---------------------------------------------------------------------------
# Project Config: routing coverage and builder adapters
# ---------------------------------------------------------------------------

UID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def handle_and_uid(path: Path) -> tuple[str, str] | None:
    match = re.match(rf"^(.+?)--({UID})\.yaml$", path.name)
    return (match.group(1), match.group(2)) if match else None


def yaml_list_uids(text: str, key: str) -> list[str]:
    """Return UIDs listed under `key:` (strings or `- uid: …` items), stdlib only."""
    match = re.search(rf"^(\s*){re.escape(key)}:\s*\n", text, re.MULTILINE)
    if not match:
        return []
    indent = len(match.group(1))
    uids: list[str] = []
    for line in text[match.end():].splitlines():
        if line.strip() and (len(line) - len(line.lstrip())) <= indent and not line.lstrip().startswith("-"):
            break
        found = re.search(UID, line)
        if found and (line.lstrip().startswith("-") or "uid:" in line):
            uids.append(found.group(0))
    return uids


def check_project_config(project: Path, templates: Path) -> None:
    config = project / "config" / "project"
    if not config.is_dir():
        report("warning", "project-config", "config/project", 0, "No config/project directory found; skipped routing and adapter checks.")
        return

    entry_types: dict[str, str] = {}
    for path in (config / "entryTypes").glob("*.yaml"):
        parsed = handle_and_uid(path)
        if parsed:
            entry_types[parsed[1]] = parsed[0]

    # Routing: every entry type of a section with URLs needs a {% case %}.
    routing = templates / "04_templates" / "_routing.twig"
    routed: set[str] = set()
    if routing.is_file():
        code = strip_comments(routing.read_text(encoding="utf-8"))
        for case in re.finditer(r"\{%-?\s*case\s+(.*?)-?%\}", code, re.DOTALL):
            routed.update(re.findall(r"[\"']([^\"']+)[\"']", case.group(1)))
    else:
        report("error", "routing", "templates/04_templates/_routing.twig", 0, "Missing _routing.twig (§5.4).")

    for path in sorted((config / "sections").glob("*.yaml")):
        parsed = handle_and_uid(path)
        if not parsed:
            continue
        text = path.read_text(encoding="utf-8")
        if not re.search(r"hasUrls:\s*true", text):
            continue  # data-only sections (team, sharedBlocks) are not routed
        for uid in yaml_list_uids(text, "entryTypes"):
            handle = entry_types.get(uid)
            if handle and handle not in routed:
                report("error", "routing", rel(project, path), 0, f"Entry type '{handle}' of section '{parsed[0]}' has URLs but no {{% case \"{handle}\" %}} in _routing.twig (§5.4).")
        if "_routing" not in text and "template:" in text:
            report("warning", "routing", rel(project, path), 0, f"Section '{parsed[0]}' template is not 04_templates/_routing.twig (§5.4).")

    # Builders: every entry type in a Matrix field needs an adapter when the
    # organism has a blocks/ folder (page-builder, article-builder, hero, …).
    for path in sorted((config / "fields").glob("*.yaml")):
        parsed = handle_and_uid(path)
        if not parsed:
            continue
        text = path.read_text(encoding="utf-8")
        if "craft\\fields\\Matrix" not in text:
            continue
        blocks_dir = templates / "03_organisms" / kebab(parsed[0]) / "blocks"
        if not blocks_dir.is_dir():
            continue
        for uid in yaml_list_uids(text, "entryTypes"):
            handle = entry_types.get(uid)
            if handle and not (blocks_dir / f"_{handle}.twig").is_file():
                report("error", "adapter", rel(project, blocks_dir), 0, f"Matrix '{parsed[0]}' allows '{handle}' but blocks/_{handle}.twig is missing (§5.5, §15.1).")


# ---------------------------------------------------------------------------
# Translations: every |t('site') key exists in every language
# ---------------------------------------------------------------------------

T_KEY = re.compile(r"([\"'])((?:(?!\1).)+)\1\s*\|\s*t\(\s*[\"']site[\"']")


def check_translations(project: Path, templates: Path) -> None:
    folder = project / "translations"
    languages = sorted(p for p in folder.glob("*/site.php")) if folder.is_dir() else []
    if not languages:
        report("warning", "translations", "translations", 0, "No translations/<lang>/site.php files found (§11).")
        return
    defined: dict[str, set[str]] = {}
    for php in languages:
        text = php.read_text(encoding="utf-8", errors="replace")
        defined[php.parent.name] = set(m.group(2) for m in re.finditer(r"([\"'])((?:(?!\1).)+)\1\s*=>", text))

    used: dict[str, tuple[str, int]] = {}
    for path in templates.rglob("*.twig"):
        code = strip_comments(path.read_text(encoding="utf-8", errors="replace"))
        for match in T_KEY.finditer(code):
            used.setdefault(match.group(2), (rel(project, path), line_of(code, match.start())))

    for key, (where, line) in sorted(used.items()):
        missing = [lang for lang, keys in defined.items() if key not in keys]
        if missing:
            report("error", "translations", where, line, f"Key '{key}' missing in: {', '.join(missing)} (§11, §15.1).")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

CHECKS = {
    "twig": check_twig,
    "scss": check_scss,
    "project-config": check_project_config,
    "translations": check_translations,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", nargs="?", default=".", help="Craft project root (default: current directory)")
    parser.add_argument("--only", help="Comma-separated subset of checks: " + ", ".join(CHECKS))
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    templates = project / "templates"
    if not templates.is_dir():
        print(f"error: {templates} not found; pass the Craft project root.", file=sys.stderr)
        return 2

    selected = list(CHECKS)
    if args.only:
        selected = [c.strip() for c in args.only.split(",") if c.strip()]
        unknown = [c for c in selected if c not in CHECKS]
        if unknown:
            print(f"error: unknown check(s): {', '.join(unknown)}", file=sys.stderr)
            return 2

    for name in selected:
        CHECKS[name](project, templates)

    if args.warnings_as_errors:
        for finding in FINDINGS:
            finding.level = "error"

    errors = [f for f in FINDINGS if f.level == "error"]
    warnings = [f for f in FINDINGS if f.level == "warning"]
    for finding in sorted(FINDINGS, key=lambda f: (f.level != "error", f.path, f.line)):
        location = f"{finding.path}:{finding.line}" if finding.line else finding.path
        print(f"{finding.level.upper():7} [{finding.check}] {location} — {finding.message}")
    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) across checks: {', '.join(selected)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

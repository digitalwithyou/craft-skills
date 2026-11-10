#!/usr/bin/env python3
"""Split spec/CRAFT-CONVENTIONS.md into the reference files the skills load.

The master spec stays the single source of truth. Edit the master, then run:

    python3 tools/split_spec.py

Every generated file starts with a "generated" banner so nobody edits the copies.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "spec" / "CRAFT-CONVENTIONS.md"

# Output file -> list of top-level section numbers ("## N. Title") it contains.
GROUPS: dict[str, list[int]] = {
    "01-stack-and-tooling.md": [1, 2, 3, 4],
    "02-templates.md": [5, 6, 7],
    "03-scss.md": [8],
    "04-javascript.md": [9],
    "05-content-model.md": [10],
    "06-i18n-seo-a11y.md": [11, 12],
    "07-performance.md": [13],
    "08-migration-playbook.md": [14],
    "09-recipes-and-anti-patterns.md": [15, 16],
}

# Destination folders and which generated files each one receives.
TARGETS: dict[Path, list[str]] = {
    ROOT / "plugins/craft-dev/skills/craft-building/references/conventions": list(GROUPS),
    ROOT / "plugins/craft-content/skills/craft-preparing-pages/references/conventions": [
        "05-content-model.md",
    ],
}

HEADING = re.compile(r"^## (\d+)\. ", re.MULTILINE)


def split_sections(text: str) -> tuple[str, dict[int, str]]:
    """Return the preamble and a map of section number -> section markdown."""
    matches = list(HEADING.finditer(text))
    if not matches:
        sys.exit(f"No '## N. Title' headings found in {SPEC}")
    preamble = text[: matches[0].start()].rstrip().rstrip("-").rstrip()
    sections: dict[int, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.start():end].rstrip()
        # Drop the horizontal rule that separates sections in the master.
        body = re.sub(r"\n-{3,}\s*$", "", body).rstrip()
        sections[int(match.group(1))] = body + "\n"
    return preamble, sections


def main() -> None:
    text = SPEC.read_text(encoding="utf-8")
    preamble, sections = split_sections(text)

    expected = {n for numbers in GROUPS.values() for n in numbers}
    missing = sorted(set(sections) - expected)
    if missing:
        sys.exit(f"Sections {missing} are not assigned to any output file in GROUPS.")

    rendered: dict[str, str] = {}
    for filename, numbers in GROUPS.items():
        parts = [sections[n] for n in numbers if n in sections]
        banner = (
            "<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. "
            "Do not edit this copy; edit the master and regenerate. -->\n\n"
        )
        body = "\n".join(parts)
        if body.count("\n") > 100:
            titles = re.findall(r"^#{2,3} (.+)$", body, re.MULTILINE)
            body = "## Contents\n\n" + "\n".join(f"- {t}" for t in titles) + "\n\n" + body
        rendered[filename] = banner + body

    # The overview file carries the spec preamble (purpose and usage scenarios).
    rendered["00-overview.md"] = (
        "<!-- Generated from spec/CRAFT-CONVENTIONS.md by tools/split_spec.py. -->\n\n"
        + preamble
        + "\n\n## Files\n\n"
        + "\n".join(f"- `{name}`" for name in GROUPS)
        + "\n"
    )

    for folder, files in TARGETS.items():
        folder.mkdir(parents=True, exist_ok=True)
        wanted = files + (["00-overview.md"] if files == list(GROUPS) else [])
        for name in wanted:
            (folder / name).write_text(rendered[name], encoding="utf-8")
            print(f"wrote {folder.relative_to(ROOT)}/{name}")


if __name__ == "__main__":
    main()

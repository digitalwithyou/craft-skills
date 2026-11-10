#!/usr/bin/env python3
"""Inventory everything that can be updated in a Craft project.

Runs on the host and shells into DDEV for composer/npm, per the Craft conventions
rule that tooling only runs inside DDEV. Python 3 standard library only.

Usage:
    python3 update_report.py [PROJECT_ROOT] [--out FILE] [--no-npm] [--no-composer]

Writes a Markdown report (stdout by default) with:
  - Craft, PHP and DDEV versions
  - outdated Composer packages, split into patch / minor / major, abandoned flagged
  - outdated npm packages, same split
  - in-house plugins and modules (local path repositories) and their Craft constraints
  - Craft 6 readiness signals found in templates and PHP
The report is an input for the plan; it never changes anything.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

COMMAND_TIMEOUT = 300  # composer outdated can be slow on cold caches


def run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run a command and return (exit code, stdout, stderr) without raising."""
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=COMMAND_TIMEOUT)
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "", f"timed out after {COMMAND_TIMEOUT}s: {' '.join(cmd)}"


def parse_version(value: str) -> tuple[int, ...] | None:
    match = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", value or "")
    if not match:
        return None
    return tuple(int(part or 0) for part in match.groups())


def bump_kind(current: str, latest: str) -> str:
    """Classify an update as major, minor or patch (Composer/npm semver style)."""
    a, b = parse_version(current), parse_version(latest)
    if not a or not b:
        return "unknown"
    if b[0] != a[0]:
        return "major"
    # 0.x packages treat minor bumps as breaking.
    if a[0] == 0 and b[1] != a[1]:
        return "major"
    if b[1] != a[1]:
        return "minor"
    return "patch"


def load_json(text: str) -> object | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start > 0:
            try:
                return json.loads(text[start:])
            except json.JSONDecodeError:
                return None
        return None


# ---------------------------------------------------------------------------
# Sections of the report
# ---------------------------------------------------------------------------


def section_versions(project: Path) -> list[str]:
    lines = ["## Versions", ""]
    lock = project / "composer.lock"
    craft_version = "unknown"
    if lock.is_file():
        data = load_json(lock.read_text(encoding="utf-8")) or {}
        for package in data.get("packages", []):
            if package.get("name") == "craftcms/cms":
                craft_version = package.get("version", "unknown")
    lines.append(f"- Craft CMS (composer.lock): **{craft_version}**")

    ddev_config = project / ".ddev" / "config.yaml"
    if ddev_config.is_file():
        text = ddev_config.read_text(encoding="utf-8")
        php = re.search(r"php_version:\s*[\"']?([\d.]+)", text)
        db = re.search(r"database:\s*\n\s*type:\s*(\w+)\s*\n\s*version:\s*[\"']?([\d.]+)", text)
        lines.append(f"- PHP (DDEV): {php.group(1) if php else 'unknown'}")
        if db:
            lines.append(f"- Database (DDEV): {db.group(1)} {db.group(2)}")
    composer_json = project / "composer.json"
    if composer_json.is_file():
        data = load_json(composer_json.read_text(encoding="utf-8")) or {}
        platform = data.get("config", {}).get("platform", {}).get("php")
        if platform:
            lines.append(f"- composer.json platform PHP: {platform} (production PHP must match)")
    lines.append("")
    return lines


def section_composer(project: Path) -> list[str]:
    lines = ["## Composer packages (direct)", ""]
    code, out, err = run(["ddev", "composer", "outdated", "--direct", "--format=json"], project)
    data = load_json(out)
    if not isinstance(data, dict):
        lines += [f"Could not read `ddev composer outdated` (exit {code}): {err.strip()[:300]}", ""]
        return lines
    packages = data.get("installed", [])
    if not packages:
        return lines + ["All direct Composer packages are up to date.", ""]
    rows = []
    for package in packages:
        kind = bump_kind(package.get("version", ""), package.get("latest", ""))
        abandoned = package.get("abandoned")
        note = ""
        if abandoned:
            note = f"ABANDONED → {abandoned}" if isinstance(abandoned, str) else "ABANDONED"
        rows.append((kind, package.get("name", "?"), package.get("version", "?"), package.get("latest", "?"), note))
    order = {"major": 0, "minor": 1, "patch": 2, "unknown": 3}
    rows.sort(key=lambda r: (order.get(r[0], 9), r[1]))
    lines += ["| Kind | Package | Installed | Latest | Note |", "|---|---|---|---|---|"]
    lines += [f"| {k} | `{n}` | {v} | {l} | {note} |" for k, n, v, l, note in rows]
    lines.append("")
    return lines


def section_npm(project: Path) -> list[str]:
    lines = ["## npm packages", ""]
    if not (project / "package.json").is_file():
        return lines + ["No package.json.", ""]
    # npm outdated exits 1 when something is outdated; that is not an error here.
    code, out, err = run(["ddev", "npm", "outdated", "--json"], project)
    data = load_json(out) if out.strip() else {}
    if data is None:
        return lines + [f"Could not read `ddev npm outdated` (exit {code}): {err.strip()[:300]}", ""]
    if not data:
        return lines + ["All npm packages are up to date.", ""]
    rows = []
    for name, info in data.items():
        if isinstance(info, list):  # workspaces return a list per package
            info = info[0]
        kind = bump_kind(info.get("current", ""), info.get("latest", ""))
        rows.append((kind, name, info.get("current", "?"), info.get("wanted", "?"), info.get("latest", "?")))
    order = {"major": 0, "minor": 1, "patch": 2, "unknown": 3}
    rows.sort(key=lambda r: (order.get(r[0], 9), r[1]))
    lines += ["| Kind | Package | Current | Wanted | Latest |", "|---|---|---|---|---|"]
    lines += [f"| {k} | `{n}` | {c} | {w} | {l} |" for k, n, c, w, l in rows]
    lines.append("")
    return lines


def section_inhouse(project: Path) -> list[str]:
    lines = ["## In-house plugins and modules", ""]
    composer_json = project / "composer.json"
    data = load_json(composer_json.read_text(encoding="utf-8")) if composer_json.is_file() else {}
    repos = [r for r in (data or {}).get("repositories", []) if isinstance(r, dict) and r.get("type") == "path"]
    if not repos:
        lines.append("No local path repositories in composer.json.")
    for repo in repos:
        path = project / repo.get("url", "")
        manifest = path / "composer.json"
        if not manifest.is_file():
            lines.append(f"- `{repo.get('url')}`: composer.json missing")
            continue
        info = load_json(manifest.read_text(encoding="utf-8")) or {}
        craft = info.get("require", {}).get("craftcms/cms", "not declared")
        version = info.get("version", "no version key")
        ready = "yes" if re.search(r"\^6|\|\|\s*\^?6|>=\s*5", craft) else "no"
        lines.append(f"- `{info.get('name', repo.get('url'))}` ({repo.get('url')}): craftcms/cms `{craft}`, version `{version}`, allows Craft 6: {ready}")
    modules = project / "modules"
    if modules.is_dir():
        names = sorted(p.name for p in modules.iterdir() if p.is_dir())
        if names:
            lines.append(f"- Modules in `modules/`: {', '.join(names)}")
    lines.append("")
    return lines


CRAFT6_SIGNALS = [
    ("templates", "*.twig", r"\bcraft\.app\b", "`craft.app` in Twig (deprecated in Craft 6 in favour of facades)"),
    ("templates", "*.twig", r"\bcraft\.globalSets\b", "`craft.globalSets` queries (global sets are slated for removal)"),
    ("templates", "*.twig", r"\bcraft\.categories\b", "`craft.categories` queries (categories are slated for removal)"),
    ("templates", "*.twig", r"\bcraft\.tags\b", "`craft.tags` queries (tags are slated for removal)"),
    ("modules", "*.php", r"Craft::\$app", "`Craft::$app` in modules (works via the Yii 2 adapter, review before Craft 6)"),
    ("plugins", "*.php", r"Craft::\$app", "`Craft::$app` in in-house plugins (review before Craft 6)"),
]


def section_craft6(project: Path) -> list[str]:
    lines = ["## Craft 6 readiness signals", ""]
    found = False
    for folder, pattern, regex, label in CRAFT6_SIGNALS:
        base = project / folder
        if not base.is_dir():
            continue
        hits = 0
        files = 0
        for path in base.rglob(pattern):
            if "vendor" in path.parts or "node_modules" in path.parts:
                continue
            count = len(re.findall(regex, path.read_text(encoding="utf-8", errors="replace")))
            if count:
                hits += count
                files += 1
        if hits:
            found = True
            lines.append(f"- {label}: {hits} occurrence(s) in {files} file(s)")
    config = project / "config" / "project"
    if config.is_dir():
        for kind in ("globalSets", "categoryGroups", "tagGroups"):
            count = len(list((config / kind).glob("*.yaml"))) if (config / kind).is_dir() else 0
            if count:
                found = True
                lines.append(f"- Project config has {count} `{kind}` (the conventions keep Globals for now; track Craft 6 support)")
    if not found:
        lines.append("No signals found.")
    lines.append("")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("project", nargs="?", default=".")
    parser.add_argument("--out", help="Write the report to this file instead of stdout")
    parser.add_argument("--no-npm", action="store_true")
    parser.add_argument("--no-composer", action="store_true")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    if not (project / "composer.json").is_file():
        print(f"error: {project} has no composer.json; pass the Craft project root.", file=sys.stderr)
        return 2
    if shutil.which("ddev") is None and not (args.no_npm and args.no_composer):
        print("error: ddev is not on PATH. Start from the host where DDEV is installed, or pass --no-npm --no-composer.", file=sys.stderr)
        return 2

    report = [f"# Update report: {project.name} ({date.today().isoformat()})", ""]
    report += section_versions(project)
    if not args.no_composer:
        report += section_composer(project)
    if not args.no_npm:
        report += section_npm(project)
    report += section_inhouse(project)
    report += section_craft6(project)
    report += [
        "## Next steps",
        "",
        "Read the changelog of every package above between the installed and latest version,",
        "classify each change (security / breaking / feature / fix) and write the plan before updating.",
        "",
    ]
    text = "\n".join(report)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

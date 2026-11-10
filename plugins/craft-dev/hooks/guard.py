#!/usr/bin/env python3
"""PreToolUse guard for Craft projects that run in DDEV (Claude Code plugin hook).

Deterministic enforcement of two rules that are expensive to break:
  1. Bash: composer / npm / npx / yarn / pnpm / php craft / ./craft must run through `ddev`.
     Running them on the host uses the wrong PHP/Node version and can corrupt vendor/ or
     node_modules/. Denied, with the ddev-prefixed command as the reason. Heredoc bodies and
     quoted text (commit messages, file contents) are data and never checked.
  2. Edit/Write on config/project/*.yaml: Project Config is written by Craft, not by hand.
     Not blocked (mechanical renames are allowed by the conventions), but the user is asked.

Silent (exit 0, no output) for everything else, so it adds no tokens to normal work.
Only acts inside a DDEV Craft project: a directory with .ddev/config.yaml and a `craft` file.
Standard library only; any internal error lets the call through (never block on a bug).
"""

from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path

HOST_TOOLS = {"composer", "npm", "npx", "yarn", "pnpm"}
SEPARATORS = ("&&", "||", ";", "|", "\n")
# `<<EOF`, `<<-'EOF'`, `<< "EOF"`; not the here-string `<<<`.
HEREDOC_START = re.compile(r"(?<!<)<<(-?)(?!<)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
ENV_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PREFIXES = {"sudo", "time", "nice", "command", "exec"}


def find_project_root(start: Path) -> Path | None:
    """Walk up from start to the first directory that looks like a DDEV Craft project."""
    for directory in [start, *start.parents]:
        if (directory / ".ddev" / "config.yaml").is_file() and (directory / "craft").is_file():
            return directory
    return None


def first_words(segment: str) -> list[str]:
    try:
        words = shlex.split(segment, posix=True)
    except ValueError:
        words = segment.split()
    while words and (ENV_ASSIGNMENT.match(words[0]) or words[0] in PREFIXES):
        words.pop(0)
    return words


def strip_heredoc_bodies(command: str) -> str:
    """Drop heredoc bodies: they are data (a commit message, a file), not commands."""
    kept: list[str] = []
    pending: list[tuple[str, bool]] = []  # (delimiter, strip leading tabs) in order of appearance
    for line in command.split("\n"):
        if pending:
            delimiter, strip_tabs = pending[0]
            if (line.lstrip("\t") if strip_tabs else line) == delimiter:
                pending.pop(0)
            continue
        kept.append(line)
        pending.extend((m.group(3), m.group(1) == "-") for m in HEREDOC_START.finditer(line))
    return "\n".join(kept)


def command_segments(command: str) -> list[str]:
    """Split on &&, ||, ;, | and newlines, but not inside quotes or after a backslash."""
    segments: list[str] = []
    current: list[str] = []
    quote = ""
    i = 0
    while i < len(command):
        char = command[i]
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            elif char == "\\" and quote == '"' and i + 1 < len(command):
                current.append(command[i + 1])
                i += 1
        elif char in "'\"":
            quote = char
            current.append(char)
        elif char == "\\" and i + 1 < len(command):
            current.append(char + command[i + 1])
            i += 1
        else:
            separator = next((s for s in SEPARATORS if command.startswith(s, i)), None)
            if separator:
                segments.append("".join(current))
                current = []
                i += len(separator)
                continue
            current.append(char)
        i += 1
    segments.append("".join(current))
    return segments


def host_tool_violation(command: str) -> str | None:
    """Return the offending segment when a tool runs on the host instead of in DDEV."""
    for raw in command_segments(strip_heredoc_bodies(command)):
        words = first_words(raw.strip())
        if not words:
            continue
        head = words[0]
        if head == "ddev":
            continue
        if Path(head).name in HOST_TOOLS:
            return " ".join(words)
        if Path(head).name.startswith("php") and len(words) > 1 and Path(words[1]).name == "craft":
            return " ".join(words)
        if head in ("./craft", "craft") or head.endswith("/craft"):
            return " ".join(words)
    return None


def ddev_equivalent(segment: str) -> str:
    words = segment.split()
    if words and Path(words[0]).name.startswith("php") and len(words) > 1:
        words = words[1:]  # "php craft x" -> "craft x"
    if words and words[0].endswith("craft"):
        words[0] = "craft"
    return "ddev " + " ".join(words)


def decide(payload: dict) -> dict | None:
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = Path(payload.get("cwd") or ".")

    if tool == "Bash":
        if find_project_root(cwd) is None:
            return None
        offending = host_tool_violation(tool_input.get("command", ""))
        if offending:
            return {
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"This is a DDEV project: run `{ddev_equivalent(offending)}` instead of `{offending}` "
                    "(tooling only runs inside DDEV)."
                ),
            }
        return None

    if tool in ("Edit", "Write", "MultiEdit"):
        file_path = tool_input.get("file_path", "")
        if not file_path:
            return None
        path = Path(file_path)
        if not path.is_absolute():
            path = cwd / path
        root = find_project_root(path.parent)
        if root is None:
            return None
        try:
            relative = path.resolve().relative_to(root.resolve())
        except ValueError:
            return None
        if relative.parts[:2] == ("config", "project") and path.suffix in (".yaml", ".yml"):
            return {
                "permissionDecision": "ask",
                "permissionDecisionReason": (
                    "Project Config YAML is written by Craft. Hand edits are only for mechanical renames "
                    "that are applied and verified right away (`ddev craft project-config/apply`, then `project-config/check`)."
                ),
            }
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        decision = decide(payload)
    except Exception:  # never block on a bug in the guard itself
        return 0
    if decision:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", **decision}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

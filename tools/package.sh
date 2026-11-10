#!/usr/bin/env bash
# Build upload packages into dist/:
#   - one zip per skill (Claude: Customize > Skills > Upload; ChatGPT: Skills > Create > Upload from your computer)
#   - one zip per plugin (Claude Desktop / Cowork "Upload plugin", or Claude org marketplaces)
# Regenerates the conventions reference files from spec/ first, so packages never ship stale copies.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist="$root/dist"

python3 "$root/tools/split_spec.py" >/dev/null
rm -rf "$dist"
mkdir -p "$dist/skills" "$dist/plugins"

for plugin_dir in "$root"/plugins/*/; do
    plugin="$(basename "$plugin_dir")"
    # Plugin zip: the plugin root must be the top of the archive.
    (cd "$plugin_dir" && zip -qr "$dist/plugins/$plugin.zip" . -x '*.DS_Store' '*__pycache__*')
    for skill_dir in "$plugin_dir"skills/*/; do
        skill="$(basename "$skill_dir")"
        # Skill zip: the skill folder (named like the skill) is the top of the archive.
        (cd "$plugin_dir/skills" && zip -qr "$dist/skills/$skill.zip" "$skill" -x '*.DS_Store' '*__pycache__*')
    done
done

echo "Packages in $dist:"
find "$dist" -name '*.zip' | sed "s|$root/||" | sort

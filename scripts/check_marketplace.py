"""Check that the Claude Code marketplace lists exactly the plugins under plugins/.

`claude plugin validate .` checks that each listed source is a valid plugin, but not that
every plugin folder is listed. A folder left out of marketplace.json is never installable,
so this check fails the build instead. It uses only the standard library.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def main() -> int:
    """Print each mismatch and return 1 if there is any."""
    folders = {
        manifest.parents[1].name: json.loads(manifest.read_text())["name"]
        for manifest in sorted((ROOT / "plugins").glob("*/.claude-plugin/plugin.json"))
    }
    listed = {
        entry["source"].removeprefix("./plugins/"): entry["name"]
        for entry in json.loads(MARKETPLACE.read_text())["plugins"]
        if isinstance(entry.get("source"), str)
    }
    errors = [
        f"plugins/{folder}/ is not listed in .claude-plugin/marketplace.json"
        for folder in folders.keys() - listed.keys()
    ]
    errors += [
        f"marketplace entry {name!r} points at ./plugins/{folder}, which has no plugin.json"
        for folder, name in listed.items()
        if folder not in folders
    ]
    errors += [
        f"marketplace entry {listed[f]!r} and plugins/{f}/ plugin.json name {folders[f]!r} differ"
        for f in folders.keys() & listed.keys()
        if listed[f] != folders[f]
    ]
    for error in sorted(errors):
        print(error, file=sys.stderr)
    if not errors:
        print(f"marketplace lists every plugin: {', '.join(sorted(folders))}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

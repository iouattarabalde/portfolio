#!/usr/bin/env python3
"""
bump_css_version.py

Auto-syncs the style.css?v=N cache-buster across index.html and project.html
whenever style.css changes, so this manual step (documented as a reminder
comment in index.html) can't be forgotten. Aug 2026.

Takes the higher of the two files' current version numbers (self-healing if
they'd ever drifted apart), adds 1, and writes that back into both files.

Run from the repo root:
    python3 scripts/bump_css_version.py
"""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["index.html", "project.html"]
PATTERN = re.compile(r'(style\.css\?v=)(\d+)')


def main():
    versions = {}
    contents = {}

    for name in FILES:
        path = os.path.join(REPO_ROOT, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        match = PATTERN.search(text)
        if not match:
            print(f"ERROR: no style.css?v=N reference found in {name}")
            sys.exit(1)
        contents[name] = text
        versions[name] = int(match.group(2))

    old_max = max(versions.values())
    new_v = old_max + 1

    if versions["index.html"] == versions["project.html"] == new_v - 1:
        pass  # normal case, both already in sync one behind

    for name in FILES:
        new_text = PATTERN.sub(rf'\g<1>{new_v}', contents[name])
        with open(os.path.join(REPO_ROOT, name), "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"{name}: v={versions[name]} -> v={new_v}")


if __name__ == "__main__":
    main()

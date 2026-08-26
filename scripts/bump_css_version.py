#!/usr/bin/env python3
"""
bump_css_version.py

Auto-syncs the style.css?v=N cache-buster across every page that links the
shared stylesheet, whenever style.css changes, so this manual step (documented
as a reminder comment in index.html) can't be forgotten. Aug 2026.

Takes the highest version currently found across those files (self-healing if
they've drifted apart), adds 1, and writes that back into all of them.

admin/index.html is in the list too, as of Aug 2026 — it links the same
stylesheet (as ../style.css?v=N) but was originally left out, so it silently
drifted 13 versions behind index/project and could serve admins a stale
cached stylesheet indefinitely. The regex matches the "style.css?v=N" tail of
that relative path unchanged, so no special-casing is needed for it.

Run from the repo root:
    python3 scripts/bump_css_version.py
"""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["index.html", "project.html", "admin/index.html"]
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

    new_v = max(versions.values()) + 1

    for name in FILES:
        new_text = PATTERN.sub(rf'\g<1>{new_v}', contents[name])
        with open(os.path.join(REPO_ROOT, name), "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"{name}: v={versions[name]} -> v={new_v}")


if __name__ == "__main__":
    main()

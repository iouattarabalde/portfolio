#!/usr/bin/env python3
"""
bump_asset_versions.py

Auto-syncs the ?v=N cache-buster on every shared asset the pages link, whenever
one of those assets changes, so this manual step (documented as a reminder
comment in index.html) can't be forgotten. Aug 2026; extended from style.css
alone to site.js and i18n.js as well in Sept 2026.

Takes the highest version currently found anywhere across those files (self-
healing if they've drifted apart), adds 1, and writes that back onto every
asset in all of them. One shared number rather than one per asset: it makes a
drifted file obvious at a glance, and the cost of the coupling is that a CSS
edit also re-downloads the two scripts once, which is not worth a counter each
to avoid.

The scripts were added because they and the HTML that loads them were all
unversioned, so a visitor mid-deploy could hold a new page against a cached
older site.js and call into functions that didn't exist yet. project.html had
grown a defensive typeof check around exactly that. A versioned URL is a URL the
browser has never seen, so the set can no longer come apart. i18n.js is quieter
about failing than site.js — it falls back to its built-in default strings — but
a stale copy of it serves stale labels, which is worse for being invisible.

admin/index.html is in the list too, as of Aug 2026 — it links the same assets
(as ../style.css?v=N) but was originally left out, so it silently drifted 13
versions behind index/project and could serve admins a stale cached stylesheet
indefinitely. The regex matches the "style.css?v=N" tail of that relative path
unchanged, so no special-casing is needed for it.

Run from the repo root:
    python3 scripts/bump_asset_versions.py
"""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["index.html", "project.html", "admin/index.html"]
# Every page links every one of these, so a missing reference below is a real
# error rather than something to skip over.
ASSETS = ["style.css", "site.js", "i18n.js"]
PATTERN = re.compile(r'(%s)(\?v=)(\d+)' % "|".join(re.escape(a) for a in ASSETS))


def main():
    contents = {}
    found = {}

    for name in FILES:
        path = os.path.join(REPO_ROOT, name)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        seen = {m.group(1): int(m.group(3)) for m in PATTERN.finditer(text)}
        missing = [asset for asset in ASSETS if asset not in seen]
        if missing:
            print(f"ERROR: no {', '.join(m + '?v=N' for m in missing)} reference found in {name}")
            sys.exit(1)
        contents[name] = text
        found[name] = seen

    new_v = max(v for seen in found.values() for v in seen.values()) + 1

    for name in FILES:
        new_text = PATTERN.sub(rf'\g<1>\g<2>{new_v}', contents[name])
        with open(os.path.join(REPO_ROOT, name), "w", encoding="utf-8") as f:
            f.write(new_text)
        was = ", ".join(f"{asset} v={found[name][asset]}" for asset in ASSETS)
        print(f"{name}: {was} -> v={new_v}")


if __name__ == "__main__":
    main()

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

The file list is DISCOVERED, not hardcoded, as of Sept 2026. It used to be a
literal list, and admin/index.html was left out of it when that page was added,
so it silently drifted 13 versions behind index/project and served admins a
stale cached stylesheet for weeks. Adding privacy/ and terms/ would have
repeated that exactly, so the list is now every .html in the repo that already
carries an asset?v=N reference. A new page is covered the moment it links a
versioned asset, which is the only moment it needs to be. The regex matches the
"style.css?v=N" tail regardless of how deep the relative path is, so a page in a
subfolder needs no special casing.

Run from the repo root:
    python3 scripts/bump_asset_versions.py
"""
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Every page that links these links all of them, so a page carrying some but not
# all is a real error rather than something to skip over.
ASSETS = ["style.css", "site.js", "i18n.js"]

# Versioned identically, but only on the pages that actually read it, so absence
# is not an error the way it is for the three above — privacy/ and terms/ carry
# the shared assets and no project data at all.
#
# Added Sept 2026. data/projects.json is what the admin rewrites on every save,
# and it was the one input to the work grid and the galleries with no cache-buster
# on it: GitHub Pages serves it with max-age=600 and gives no way to set a header,
# so for ten minutes after a save every visitor kept the old gallery, and an iOS
# tab restored from the back/forward cache never re-ran the fetch at all and could
# hold it indefinitely. Stale data there is worse than a stale stylesheet, because
# a save that removes a still leaves the old copy pointing at files that now 404.
# Both the <link rel=preload> and the fetch() carry the number and are rewritten
# together — they have to stay byte-identical or the preload stops matching the
# request it exists to warm, and the page pays for two fetches instead of one.
# data/settings.json is the same story on a smaller file — the contact photo and
# the two bios, index.html only.
#
# data/strings.json is here for its PRELOADS only. Nothing fetches it from a page:
# i18n.js builds that URL itself and carries its own ?v= onto it, so the fetched URL
# is busted by i18n.js's number without anything here. The preloads in index.html and
# project.html do sit in the HTML though, and have to move on the same counter or they
# stop matching the request they exist to warm.
OPTIONAL_ASSETS = ["data/projects.json", "data/settings.json", "data/strings.json"]

VERSIONED = ASSETS + OPTIONAL_ASSETS
PATTERN = re.compile(r'(%s)(\?v=)(\d+)' % "|".join(re.escape(a) for a in VERSIONED))
SKIP_DIRS = {".git", "node_modules", ".github"}


def discover():
    """Every .html under the repo that already references a versioned asset.

    Discovery rather than a literal list: see the note in the module docstring
    about admin/index.html drifting 13 versions behind because it was forgotten.
    Pages with no asset?v=N reference at all (the generated project/ share pages)
    are simply not found, which is correct — they link nothing to bust.
    """
    out = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            full = os.path.join(dirpath, fn)
            with open(full, encoding="utf-8") as f:
                if PATTERN.search(f.read()):
                    out.append(os.path.relpath(full, REPO_ROOT))
    if not out:
        print("ERROR: no page references a versioned asset; refusing to run")
        sys.exit(1)
    return sorted(out)


def main():
    contents = {}
    found = {}
    files = discover()
    print(f"Pages found: {', '.join(files)}")

    for name in files:
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

    for name in files:
        new_text = PATTERN.sub(rf'\g<1>\g<2>{new_v}', contents[name])
        with open(os.path.join(REPO_ROOT, name), "w", encoding="utf-8") as f:
            f.write(new_text)
        was = ", ".join(f"{asset} v={found[name][asset]}"
                        for asset in VERSIONED if asset in found[name])
        print(f"{name}: {was} -> v={new_v}")


if __name__ == "__main__":
    main()

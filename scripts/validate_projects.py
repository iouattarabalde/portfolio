#!/usr/bin/env python3
"""
validate_projects.py

Structural + referential integrity check for data/projects.json, run as the
first step of the share-pages workflow so a bad reference (missing thumbnail,
missing gallery image, duplicate id, unknown type) fails the CI job loudly
with a clear message instead of either crashing generate_share_pages.py with
a raw traceback, or silently shipping a broken reference (this is exactly
how assets/og-image.jpg went missing for a while — Aug 2026).

Exit code 0 = clean, non-zero = at least one problem found (listed on stdout).

Run from the repo root:
    python3 scripts/validate_projects.py
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_JSON = os.path.join(REPO_ROOT, "data", "projects.json")
STRINGS_JSON = os.path.join(REPO_ROOT, "data", "strings.json")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")


def fail(errors):
    print(f"projects.json validation FAILED — {len(errors)} problem(s):\n")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)


def main():
    errors = []

    if not os.path.exists(PROJECTS_JSON):
        fail([f"{PROJECTS_JSON} does not exist"])

    with open(PROJECTS_JSON, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            fail([f"data/projects.json is not valid JSON: {e}"])

    projects = data.get("projects")
    if not isinstance(projects, list) or not projects:
        fail(["data/projects.json has no non-empty 'projects' list"])

    # Valid project types come from data/strings.json ("types" key), the
    # actual source of truth the admin's "Textes du site" panel edits —
    # not a hardcoded list, since types are addable/removable there.
    valid_types = set()
    if os.path.exists(STRINGS_JSON):
        with open(STRINGS_JSON, encoding="utf-8") as f:
            strings_data = json.load(f)
        valid_types = set(strings_data.get("types", {}).keys())
    if not valid_types:
        errors.append("data/strings.json has no 'types' — can't validate project types against it")

    seen_ids = set()

    for i, p in enumerate(projects):
        label = p.get("id") or f"[projects[{i}], no id]"

        pid = p.get("id")
        if not pid or not isinstance(pid, str):
            errors.append(f"{label}: missing or invalid 'id'")
        elif pid in seen_ids:
            errors.append(f"{label}: duplicate id '{pid}'")
        else:
            seen_ids.add(pid)

        if not p.get("title"):
            errors.append(f"{label}: missing 'title'")

        ptype = p.get("type")
        if not ptype:
            errors.append(f"{label}: missing 'type'")
        elif valid_types and ptype not in valid_types:
            errors.append(f"{label}: type '{ptype}' not in data/strings.json types ({sorted(valid_types)})")

        thumb = p.get("thumbnail")
        if not thumb:
            errors.append(f"{label}: missing 'thumbnail'")
        else:
            thumb_path = os.path.join(ASSETS_DIR, thumb)
            if not os.path.isfile(thumb_path):
                errors.append(f"{label}: thumbnail file not found: assets/{thumb}")

        gallery = p.get("gallery")
        if not isinstance(gallery, list) or not gallery:
            errors.append(f"{label}: 'gallery' is missing or empty")
        else:
            for j, item in enumerate(gallery):
                fn = item.get("filename") if isinstance(item, dict) else None
                if not fn:
                    errors.append(f"{label}: gallery[{j}] missing 'filename'")
                    continue
                gallery_path = os.path.join(ASSETS_DIR, fn)
                if not os.path.isfile(gallery_path):
                    errors.append(f"{label}: gallery file not found: assets/{fn}")

    if errors:
        fail(errors)

    print(f"projects.json OK — {len(projects)} projects, {len(seen_ids)} unique ids, all referenced files present.")


if __name__ == "__main__":
    main()

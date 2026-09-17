#!/usr/bin/env python3
"""
backfill_gallery_dimensions.py

Stamps each gallery entry in data/projects.json with the still's true pixel
dimensions, as "w" and "h". Sept 2026.

Why this exists
---------------
The lightbox pins its frame to the gallery's aspect-ratio bounds rather than
resizing per still (see .lightbox-content img in style.css and
measureGalleryRatios() in project.html). That needs each still's real ratio.

Measuring it off the grid tiles at runtime doesn't work: a tile is a -640 or
-1280 variant, and resizing to a round width rounds the height. A 1920x1080
still becomes 640x358 or 640x359 depending on the rounding, which is half a
percent off 16:9 — enough that the pinned frame sits three or four pixels proud
of the photo instead of hugging it, in every project, including the ones that
only ever use one ratio. The palette strip, which is sized to the frame,
inherits that error.

So the dimensions are recorded once, from the originals, and read straight out
of projects.json. The admin does the same for every still uploaded from now on
(prepareOriginal() in admin/index.html); this covers everything committed
before that existed.

Dimensions are read from the JPEG's own SOF header rather than by decoding the
image, so this needs no third-party library and does not depend on Pillow being
installed, unlike generate_image_variants.py.

Idempotent: an entry whose w/h already match the file on disk is left alone.
Safe to re-run, and worth re-running after a still is replaced outside the
admin.

projects.json is rewritten in the same compact form the admin commits it in
(JSON.stringify with no indent, no ASCII escaping, no trailing newline), so a
backfill doesn't show up as a whole-file reformat in the diff.

Run from the repo root:
    python3 scripts/backfill_gallery_dimensions.py
    python3 scripts/backfill_gallery_dimensions.py --dry-run
"""
import argparse
import json
import os
import struct
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_JSON = os.path.join(REPO_ROOT, "data", "projects.json")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

# Start-of-frame markers. Any of these carries the dimensions; the rest of the
# JPEG's segments are skipped by their own length field.
SOF_MARKERS = {
    0xC0, 0xC1, 0xC2, 0xC3,
    0xC5, 0xC6, 0xC7,
    0xC9, 0xCA, 0xCB,
    0xCD, 0xCE, 0xCF,
}
# Standalone markers: SOI, EOI and the restart markers carry no length field.
STANDALONE = {0xD8, 0xD9} | set(range(0xD0, 0xD8))


def jpeg_size(path):
    """(width, height) from a JPEG's SOF header, or None if it can't be read."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError:
        return None
    if len(data) < 4 or data[0] != 0xFF or data[1] != 0xD8:
        return None  # not a JPEG
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:      # padding between segments
            i += 1
            continue
        marker = data[i + 1]
        if marker in SOF_MARKERS:
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        if marker in STANDALONE:
            i += 2
            continue
        i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="report what would change without writing")
    args = parser.parse_args()

    with open(PROJECTS_JSON, encoding="utf-8") as handle:
        data = json.load(handle)

    stamped = corrected = unchanged = 0
    unreadable = []

    for project in data.get("projects", []):
        for entry in project.get("gallery", []):
            filename = entry.get("filename")
            if not filename:
                continue
            size = jpeg_size(os.path.join(ASSETS_DIR, filename))
            if not size:
                unreadable.append(filename)
                continue
            width, height = size
            if entry.get("w") == width and entry.get("h") == height:
                unchanged += 1
                continue
            if entry.get("w") or entry.get("h"):
                corrected += 1
                print(f"  corrected {filename}: "
                      f"{entry.get('w')}x{entry.get('h')} -> {width}x{height}")
            else:
                stamped += 1
            entry["w"] = width
            entry["h"] = height

    for filename in unreadable:
        print(f"  UNREADABLE {filename}", file=sys.stderr)

    print(f"{stamped} stamped, {corrected} corrected, {unchanged} already current, "
          f"{len(unreadable)} unreadable")

    if args.dry_run:
        print("dry run: data/projects.json not written")
        return 0
    if not (stamped or corrected):
        print("nothing to write")
        return 1 if unreadable else 0

    # Matches the admin's own JSON.stringify(next): compact, UTF-8, no trailing newline.
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    with open(PROJECTS_JSON, "w", encoding="utf-8") as handle:
        handle.write(text)
    print(f"wrote data/projects.json ({len(text.encode('utf-8'))} bytes)")
    return 1 if unreadable else 0


if __name__ == "__main__":
    sys.exit(main())

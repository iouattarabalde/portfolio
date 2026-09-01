#!/usr/bin/env python3
"""
generate_image_variants.py

Builds the responsive variants the project gallery serves via srcset, and converts
every gallery still to progressive JPEG. Sept 2026.

Why this exists
---------------
Gallery stills are uploaded at 1920px wide (admin/index.html's compressImage), and the
project page used to serve that single file at every size. A three-column grid on a
1440px display shows each still about 476px wide, so the browser was downloading roughly
sixteen times the pixels it painted — 10MB for the heaviest project's 24 stills, which is
8-16 seconds on a normal 4G connection. That, plus `loading="lazy"` starting each fetch at
the same moment the tile's reveal animation began, is why stills appeared to load
sporadically or not at all: the animation always finished first and the photo arrived
afterwards, if it arrived before you scrolled past.

Two outputs per still:

  <name>-640.jpg   for phones, and for a 3-up grid below roughly 640px of viewport
  <name>-1280.jpg  for the common desktop case (476px slot on a 2x display = 952px)

The untouched original stays as the 1920w entry in the srcset, for very wide or very
high-density displays, and is what the lightbox enlarges.

Both variant files are always written, even for a source narrower than the target width —
in that case the variant is simply a copy at the source's own width, never an upscale.
That matters because project.html builds the srcset from the filename pattern without
checking what exists, and a srcset candidate that 404s doesn't fall back to src: the image
just fails to display. Always writing both is what keeps that from being possible. The
admin's uploadVariants() behaves the same way for the same reason.

Progressive
-----------
Baseline JPEGs paint top-to-bottom as bytes arrive, which is why a half-loaded still
showed as a thin horizontal band of photo above black. Progressive ones come up whole and
soft, then sharpen.

The originals are converted with quality='keep', which reuses the file's existing
quantization tables instead of requantizing — the pixels are not re-encoded, so there is
no generation loss from running this, and no penalty for running it again later. The
variants are resized and therefore have to be encoded properly; VARIANT_QUALITY is what
they get.

Idempotent: a variant that already exists and is newer than its source is left alone, and
an original that is already progressive is not rewritten. Safe to re-run after adding
projects — it only does the missing work.

Run from the repo root:
    python3 scripts/generate_image_variants.py
    python3 scripts/generate_image_variants.py --dry-run
"""
import argparse
import json
import os
import sys

try:
    from PIL import Image, ImageFile
except ImportError:
    sys.exit(
        "Pillow is required.\n"
        "  python3 -m venv .venv && .venv/bin/pip install Pillow\n"
        "  .venv/bin/python scripts/generate_image_variants.py"
    )

# A few of the stills are large enough that Pillow's default guard trips on them.
ImageFile.LOAD_TRUNCATED_IMAGES = False

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO_ROOT, "assets")
PROJECTS_JSON = os.path.join(REPO_ROOT, "data", "projects.json")

# Widths the gallery's srcset offers below the original. Keep in sync with the srcset
# built in project.html's gallery template.
VARIANT_WIDTHS = (640, 1280)
VARIANT_QUALITY = 82  # resized output is re-encoded, so this is a real quality choice


def variant_path(src_path, width):
    """assets/foo/bar.jpg + 640 -> assets/foo/bar-640.jpg"""
    stem, ext = os.path.splitext(src_path)
    return f"{stem}-{width}{ext}"


def is_progressive(path):
    with Image.open(path) as im:
        return bool(im.info.get("progressive") or im.info.get("progression"))


def gallery_stills():
    """Every still referenced by a project's gallery, in projects.json order."""
    with open(PROJECTS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    seen = set()
    for project in data["projects"]:
        for item in project.get("gallery", []):
            name = item["filename"] if isinstance(item, dict) else item
            if name in seen:
                continue
            seen.add(name)
            yield os.path.join(ASSETS, name)


def process(src_path, dry_run):
    """Returns (variants_written, bytes_added, original_converted)."""
    written = 0
    added = 0
    converted = False

    # Progressive conversion FIRST, variants second, and the order is load-bearing:
    # rewriting the original bumps its mtime, so doing it last would leave every variant
    # looking staler than its source and a re-run would regenerate all 1440 of them every
    # time. Converting first means the variants written below are always the newer files.
    if not is_progressive(src_path):
        converted = True
        if not dry_run:
            before = os.path.getsize(src_path)
            with Image.open(src_path) as im:
                # quality='keep' reuses the file's own quantization tables; see the note
                # at the top of this file.
                im.save(src_path, "JPEG", quality="keep", progressive=True, optimize=True)
            added += os.path.getsize(src_path) - before

    with Image.open(src_path) as im:
        src_w = im.width
        for width in VARIANT_WIDTHS:
            out = variant_path(src_path, width)
            if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src_path):
                continue
            if dry_run:
                written += 1
                continue
            # Never upscale: a source already narrower than the target is written out at
            # its own width rather than skipped, so the file the srcset names always
            # exists. See the note at the top on why a missing candidate is fatal.
            target_w = min(width, src_w)
            resized = im.convert("RGB").resize(
                (target_w, round(im.height * target_w / src_w)), Image.LANCZOS
            )
            resized.save(out, "JPEG", quality=VARIANT_QUALITY, progressive=True, optimize=True)
            written += 1
            added += os.path.getsize(out)

    return written, added, converted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report what would change, write nothing")
    args = parser.parse_args()

    stills = list(gallery_stills())
    missing = [p for p in stills if not os.path.exists(p)]
    for p in missing:
        print(f"  MISSING {os.path.relpath(p, REPO_ROOT)}", file=sys.stderr)

    total_written = 0
    total_added = 0
    total_converted = 0
    processed = 0

    for path in stills:
        if not os.path.exists(path):
            continue
        try:
            written, added, converted = process(path, args.dry_run)
        except Exception as exc:  # a single unreadable file shouldn't abort the batch
            print(f"  FAILED {os.path.relpath(path, REPO_ROOT)}: {exc}", file=sys.stderr)
            continue
        total_written += written
        total_added += added
        total_converted += converted
        processed += 1
        if processed % 100 == 0:
            print(f"  ...{processed}/{len(stills)}")

    verb = "would write" if args.dry_run else "wrote"
    print(f"\n{processed} stills scanned, {len(missing)} missing")
    print(f"{verb} {total_written} variants; {total_converted} originals converted to progressive")
    if not args.dry_run:
        print(f"net change on disk: {total_added / 1048576:+.1f} MB")


if __name__ == "__main__":
    main()

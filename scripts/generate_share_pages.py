#!/usr/bin/env python3
"""
generate_share_pages.py

Regenerates the per-project Open Graph share shells (project/<slug>.html)
and their OG images (assets/og/<slug>.jpg) from data/projects.json.

Why this exists: project.html is a single dynamic template that reads its
content client-side via ?project=<slug>. Crawlers that build link previews
(Slack, iMessage, LinkedIn, Facebook, Discord) don't execute JS, so they only
ever see project.html's generic fallback <meta> tags, regardless of which
project was actually linked. These generated shells give each project its
own static, crawler-readable card, then redirect real visitors instantly to
the real interactive page. Added Aug 2026.

Run from the repo root:
    pip install pillow --break-system-packages
    python3 generate_share_pages.py

Regenerate any time data/projects.json changes (new project, retitled
project, new client credit, or a re-cropped cover thumbnail) — nothing here
runs automatically yet. See README.md for the manual steps, or ask Claude to
run this and commit the result.
"""
import json
import os
import html
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_JSON = os.path.join(REPO_ROOT, "data", "projects.json")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
OG_OUT_DIR = os.path.join(ASSETS_DIR, "og")
SHARE_OUT_DIR = os.path.join(REPO_ROOT, "project")

TARGET_W, TARGET_H = 1200, 630
TARGET_RATIO = TARGET_W / TARGET_H

TYPE_LABELS_EN = {
    "AD": "Advertising",
    "MV": "Music Video",
    "FILM": "Film",
    "TV": "TV",
}

SHARE_TEMPLATE = """<!DOCTYPE html>
<!--
  Auto-generated share shell for project "{slug}" — DO NOT hand-edit.
  Regenerate with generate_share_pages.py after any change to data/projects.json.
  Purpose: static per-project Open Graph card for crawlers that don't run JS
  (Slack, iMessage, LinkedIn, Facebook, Discord...), since project.html reads
  its content client-side from ?project= and crawlers only ever see the
  generic fallback tags baked into project.html itself.
  Real visitors are redirected instantly to the interactive page.
-->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_esc} — Ismael OB</title>
<meta http-equiv="refresh" content="0; url=https://ismaelob.com/project.html?project={slug}">
<link rel="icon" type="image/svg+xml" href="../assets/favicon.svg">
<meta property="og:type" content="website">
<meta property="og:url" content="https://ismaelob.com/project/{slug}.html">
<meta property="og:title" content="{title_esc} — Ismael OB">
<meta property="og:description" content="{desc_esc}">
<meta property="og:image" content="https://ismaelob.com/assets/og/{slug}.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary_large_image">
<script>location.replace('https://ismaelob.com/project.html?project={slug}');</script>
</head>
<body>
<p><a href="https://ismaelob.com/project.html?project={slug}">{title_esc} — Ismael OB</a></p>
</body>
</html>
"""


def parse_focus(focus_str):
    if not focus_str:
        return (0.5, 0.5)
    parts = focus_str.replace("%", "").split()
    return (float(parts[0]) / 100, float(parts[1]) / 100)


def crop_to_ratio(im, fx, fy):
    w, h = im.size
    src_ratio = w / h
    if src_ratio > TARGET_RATIO:
        new_w = int(h * TARGET_RATIO)
        left = max(0, min(int(fx * w - new_w / 2), w - new_w))
        box = (left, 0, left + new_w, h)
    else:
        new_h = int(w / TARGET_RATIO)
        top = max(0, min(int(fy * h - new_h / 2), h - new_h))
        box = (0, top, w, top + new_h)
    return im.crop(box).resize((TARGET_W, TARGET_H), Image.LANCZOS)


def build_description(project):
    type_label = TYPE_LABELS_EN.get(project["type"], project["type"])
    client = (project.get("client") or "").strip()
    artist = (project.get("artist") or "").strip()
    if client:
        return f"{type_label} for {client} — color grading by Ismael OB, Montreal-based colorist."
    if artist:
        return f"{type_label} — {artist} — color grading by Ismael OB, Montreal-based colorist."
    return f"{type_label} — color grading by Ismael OB, Montreal-based colorist."


def main():
    with open(PROJECTS_JSON) as f:
        data = json.load(f)

    os.makedirs(OG_OUT_DIR, exist_ok=True)
    os.makedirs(SHARE_OUT_DIR, exist_ok=True)

    for project in data["projects"]:
        slug = project["id"]

        # OG image: crop the project's own cover thumbnail using its saved
        # focal point (same one used for the homepage grid), so the share
        # card frames the same subject the site already shows.
        cover_path = os.path.join(ASSETS_DIR, project["thumbnail"])
        im = Image.open(cover_path).convert("RGB")
        fx, fy = parse_focus(project.get("thumbnailFocus"))
        cropped = crop_to_ratio(im, fx, fy)
        cropped.save(os.path.join(OG_OUT_DIR, f"{slug}.jpg"), quality=85)

        # Share shell HTML
        html_out = SHARE_TEMPLATE.format(
            slug=slug,
            title_esc=html.escape(project["title"]),
            desc_esc=html.escape(build_description(project)),
        )
        with open(os.path.join(SHARE_OUT_DIR, f"{slug}.html"), "w") as f:
            f.write(html_out)

    print(f"Generated {len(data['projects'])} share pages + OG images.")


if __name__ == "__main__":
    main()

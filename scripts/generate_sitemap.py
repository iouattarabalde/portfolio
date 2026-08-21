#!/usr/bin/env python3
"""
generate_sitemap.py

Generates sitemap.xml from data/projects.json so Google can index each
project as its own URL instead of only ever seeing the single index.html
(the work grid is rendered client-side, so a crawler that doesn't render JS
sees nothing but the homepage shell).

Points at the real interactive pages (project.html?project=<slug>), not the
project/<slug>.html OG share shells — those exist purely so link-preview
crawlers (Slack, iMessage...) get correct per-project cards without
executing JS, which is a different problem than search indexing. Google
generally renders JS well enough now to index project.html's real content
directly, and a direct URL is more reliable than counting on a redirect
chain being followed and consolidated correctly.

Run from the repo root:
    python3 scripts/generate_sitemap.py
"""
import json
import os
from xml.sax.saxutils import escape

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_JSON = os.path.join(REPO_ROOT, "data", "projects.json")
SITEMAP_OUT = os.path.join(REPO_ROOT, "sitemap.xml")

BASE_URL = "https://ismaelob.com"


def url_entry(loc, changefreq, priority):
    return (
        "  <url>\n"
        f"    <loc>{escape(loc)}</loc>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>\n"
    )


def main():
    with open(PROJECTS_JSON, encoding="utf-8") as f:
        data = json.load(f)

    entries = [
        url_entry(f"{BASE_URL}/", "weekly", "1.0"),
        url_entry(f"{BASE_URL}/colors.html", "weekly", "0.6"),
    ]

    for project in data["projects"]:
        loc = f"{BASE_URL}/project.html?project={project['id']}"
        entries.append(url_entry(loc, "monthly", "0.8"))

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(entries)
        + "</urlset>\n"
    )

    with open(SITEMAP_OUT, "w", encoding="utf-8") as f:
        f.write(xml)

    print(f"sitemap.xml written with {len(entries)} URLs.")


if __name__ == "__main__":
    main()

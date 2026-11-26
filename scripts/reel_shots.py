#!/usr/bin/env python3
"""
reel_shots.py

First detection of the homepage reel's cuts, for the caption that names the current
project while the reel plays (Nov 2026).

Writes data/reel.json: one entry per shot, its start time in seconds and the project it
comes from (null = no caption). After that first pass, cuts and projects are edited in
the admin, Reel tab, on a timeline with the video, and published from there. This script
is only needed again when the reel itself changes (scripts/encode_reel.py).

It refuses to replace cuts that are already in data/reel.json, since those may have been
corrected by hand in the admin. --redetect replaces them with a fresh detection: projects
are kept for every shot that still starts on the same frame, the rest come back empty.

Cuts are found with ffmpeg's scene score above --threshold (0.3). That catches clear
cuts and misses some between similar-looking shots (on the 2026 reel, 29 of 94); those
are added in the admin with « Couper ici ». Lowering the threshold doesn't help much:
real cuts scored as low as 0.13 while light flicker inside one shot reached 0.30.

Usage:
    python3 scripts/reel_shots.py [--video video/reel.mp4] [--threshold 0.3] [--redetect]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REEL_JSON = os.path.join(REPO_ROOT, "data", "reel.json")
FPS = 24
NOTE = ("Which project each shot of video/reel.mp4 comes from, for the caption on the homepage "
        "reel. Cuts and projects are edited in the admin, Reel tab; scripts/reel_shots.py only "
        "makes the first detection. start is in seconds; project is an id from "
        "data/projects.json, or null for no caption.")


def detect_cuts(video, threshold):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-an",
         "-vf", f"scale=320:-1,select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("ffmpeg failed:\n" + out.stderr[-2000:])
    return [float(t) for t in re.findall(r"pts_time:([0-9.]+)", out.stderr)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default=os.path.join(REPO_ROOT, "video", "reel.mp4"))
    ap.add_argument("--threshold", type=float, default=0.3)
    ap.add_argument("--redetect", action="store_true",
                    help="replace the cuts already in data/reel.json")
    args = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found (brew install ffmpeg)")

    old = []
    if os.path.exists(REEL_JSON):
        with open(REEL_JSON, encoding="utf-8") as f:
            old = json.load(f).get("shots", [])
    if old and not args.redetect:
        sys.exit(f"data/reel.json already has {len(old)} shots, maybe corrected in the admin. "
                 "Edit them there, or pass --redetect to replace them.")

    frame = lambda t: round(t * FPS)
    labels = {frame(s["start"]): s["project"] for s in old if s.get("project")}
    starts = sorted({0} | {frame(t) for t in detect_cuts(args.video, args.threshold)})
    shots = [{"n": n, "start": round(k / FPS, 3), "project": labels.get(k)} for n, k in enumerate(starts)]

    text = json.dumps({"_note": NOTE, "shots": shots}, indent=2, ensure_ascii=False)
    # one shot per line, the same layout the admin writes
    text = re.sub(r'\{\n\s+"n": (\d+),\n\s+"start": ([\d.]+),\n\s+"project": (null|"[^"]*")\n\s+\}',
                  r'{ "n": \1, "start": \2, "project": \3 }', text)
    with open(REEL_JSON, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    kept = sum(1 for s in shots if s["project"])
    print(f"wrote data/reel.json: {len(shots)} shots, {kept} projects kept")


if __name__ == "__main__":
    main()

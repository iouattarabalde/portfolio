#!/usr/bin/env python3
"""
encode_reel.py

Compresses a high-quality hero-reel master (ProRes/DNxHR/whatever) into the two
web files the homepage serves, plus the poster frame:

    video/reel.av1.mp4   AV1 10-bit, primary source for modern browsers
    video/reel.mp4       H.264 8-bit, fallback for Safari <=16 / iOS <=16
    assets/hero-poster.jpg   frame 0 of the cut

WHY TWO FILES
-------------
The 2026 reel is grain-dominated and genuinely expensive to encode. Measured on
IOB_DEMO_REELS_v2_PR422HQ.mov (1080p24, 3:11), sampling three points:

    x264 CRF 23 tune film ...  7.3 Mbps  -> ~166 MB   (what the grain actually wants)
    AV1  CRF 30 10-bit ......  2.2 Mbps  -> ~50 MB
    AV1  CRF 35 10-bit ......  1.2 Mbps  -> ~27 MB

GitHub rejects any single file over 100 MB, so x264 alone physically cannot hold
this texture -- the pre-2026 reel shipped at 3.7 Mbps, roughly half what CRF 23
wants, which is why grain on the old site was mush. AV1 is a ~3x win on this
content and is the only reason the quality target fits. H.264 stays purely as a
compatibility floor for the ~5% of browsers that can't decode AV1.

Film-grain SYNTHESIS was tested and rejected: on this footage it saved nothing
measurable (1153 vs 1174 kbps) and would substitute synthetic grain for the real
grain structure. We encode the real grain. No synthesis, no denoise by default.

HOW THE CRF IS CHOSEN
---------------------
Not hardcoded. Phase 1 samples three points of the actual file at two CRFs,
fits log(bitrate) = a - k*CRF through them, and solves for the CRF that lands on
the size target. A grainier or cleaner cut therefore gets a different CRF
automatically. The result is clamped to CRF_CLAMP and refused if it falls
outside -- a solve that far off means the assumptions don't hold.

TWO PHASES, WITH A HUMAN GATE
-----------------------------
Phase 1 (~8 min, unattended) probes, solves the CRF, encodes a short excerpt of
the GRAINIEST section at the solved CRF and +/-2, pulls matched stills against
the master, and serves a 1:1 A/B review page on localhost.

Phase 2 runs only after a CRF is picked (in the page, or via --pick). It does
the full encode, writes the three files into the working tree, and stops.
It deliberately does NOT commit or push -- that stays a deliberate human action.

Usage:
    python3 scripts/encode_reel.py --file "D:/path/to/master.mov"
    python3 scripts/encode_reel.py --watch          # process the drop folder
    python3 scripts/encode_reel.py --file X --pick 29   # skip the review gate
    python3 scripts/encode_reel.py --file X --dry-run   # phase 1 analysis only
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

# Where a new master gets dropped. Two folders are watched, in this order:
#
#   1. A local disk folder -- fastest, nothing can half-sync underneath it.
#   2. A Google Drive folder -- this is the "from any machine" route. The masters
#      are already exported to Drive, so dropping one from a laptop or phone via
#      drive.google.com puts it here with no upload UI to build and no size cap.
#
# Drive materializes files progressively, so a watcher pointed there can see a
# file long before its bytes exist. is_file_settled() handles exactly that: it
# waits for the size to stop moving and refuses unmaterialized placeholders.
DROP_DIRS = [
    Path(os.environ.get("REEL_DROP_DIR", r"E:\_reel-dropbox")),
    Path(os.environ.get("REEL_DRIVE_DIR",
                        r"G:\My Drive\Color Grading\Demos\_to-web")),
]

# Published to the repo so admin/ can show status from any machine. Deliberately
# tiny and free of local paths -- the repo is public, so only basenames go in it.
STATUS_FILE = REPO_ROOT / "data" / "reel-status.json"

VIDEO_EXTS = {".mov", ".mp4", ".mxf", ".m4v", ".avi", ".mkv"}

# Size targets. AV1 is the file almost everyone actually downloads, so it
# carries the quality. Both must clear GitHub's hard limit with room to spare.
TARGET_AV1_MB = 60
TARGET_H264_MB = 60
HARD_LIMIT_MB = 100          # GitHub rejects any blob above this, full stop.

AUDIO_BITRATE_K = 192        # matches what the site has always shipped
AV1_PRESET = 4               # ~23 min for a 3-minute 1080p24 reel on 8 cores
CRF_CLAMP = (24, 38)

# Phase 1 sampling. Samples MUST use the same preset as the final encode or the
# bitrate fit doesn't transfer.
#
# Six points, not three. Measured on the 2026 reel: with three points the mean was
# dominated by a single very grainy sample (4830 kbps against 1102 and 830 at the
# other two), which pushed the whole-file estimate ~44% high -- CRF 27 was projected
# at 79 MB and actually landed at 54.7 MB. Wider coverage cuts that outlier's weight.
#
# Two residual biases both push the estimate HIGH, and are left alone deliberately:
# every short sample pays for its own keyframe, which a real 240-frame GOP amortizes;
# and solving below the probed range extrapolates the curve. Over-estimating means
# the solver picks a LOWER CRF (higher quality) than strictly needed to hit the
# target, and produces a file under the size aimed for -- the safe direction on both
# counts. The hard <100 MB check in verify() is what actually guards the GitHub
# limit; these numbers are for choosing, not for guaranteeing.
SAMPLE_SECONDS = 5
SAMPLE_POINTS = (0.08, 0.24, 0.40, 0.56, 0.72, 0.88)
PROBE_CRFS = (30, 35)
SHOOTOUT_SECONDS = 12
REVIEW_PORT = 8765
REVIEW_TIMEOUT_H = 6

OUT_AV1 = REPO_ROOT / "video" / "reel.av1.mp4"
OUT_H264 = REPO_ROOT / "video" / "reel.mp4"
OUT_POSTER = REPO_ROOT / "assets" / "hero-poster.jpg"
POSTER_TARGET_KB = 140


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


# --------------------------------------------------------------------------
# ffmpeg discovery
# --------------------------------------------------------------------------

def find_tool(name):
    """
    There is no system ffmpeg on this machine; the only build available is the
    one bundled with Shutter Encoder. Env var wins, then PATH, then the known
    install path -- so this keeps working if Shutter Encoder moves or a real
    ffmpeg gets installed later.
    """
    env = os.environ.get(f"{name.upper()}_BIN")
    if env and Path(env).exists():
        return env
    on_path = shutil.which(name)
    if on_path:
        return on_path
    bundled = Path(r"C:\Program Files\Shutter Encoder\Library") / f"{name}.exe"
    if bundled.exists():
        return str(bundled)
    sys.exit(
        f"ERROR: could not find {name}.\n"
        f"  Looked at: ${name.upper()}_BIN, PATH, and {bundled}\n"
        f"  Install ffmpeg or set {name.upper()}_BIN to its full path."
    )


FFMPEG = find_tool("ffmpeg")
FFPROBE = find_tool("ffprobe")


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", **kw)


# --------------------------------------------------------------------------
# Probing
# --------------------------------------------------------------------------

def probe(path):
    r = run([FFPROBE, "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)])
    if r.returncode != 0:
        sys.exit(f"ERROR: ffprobe could not read {path}\n{r.stderr.strip()}")
    data = json.loads(r.stdout)

    video = next((s for s in data["streams"] if s.get("codec_type") == "video"), None)
    audio = next((s for s in data["streams"] if s.get("codec_type") == "audio"), None)
    if video is None:
        sys.exit(f"ERROR: {path} has no video stream.")

    num, den = (video.get("r_frame_rate") or "24/1").split("/")
    fps = float(num) / float(den) if float(den) else 24.0

    return {
        "path": str(path),
        "duration": float(data["format"]["duration"]),
        "size": int(data["format"]["size"]),
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": fps,
        "codec": video.get("codec_name"),
        "profile": video.get("profile"),
        "pix_fmt": video.get("pix_fmt"),
        "color_primaries": video.get("color_primaries"),
        "color_transfer": video.get("color_transfer"),
        "color_space": video.get("color_space"),
        "color_range": video.get("color_range"),
        "has_audio": audio is not None,
        "audio_codec": audio.get("codec_name") if audio else None,
        "audio_channels": audio.get("channels") if audio else None,
    }


def validate(info):
    """
    Scope is the hero reel specifically: a 16:9 frame in a padding-top:56.25%
    box. Anything else is very likely a mis-drop, so say so loudly rather than
    quietly publishing a letterboxed reel.
    """
    w, h = info["width"], info["height"]
    ratio = w / h
    if abs(ratio - 16 / 9) > 0.02:
        log(f"WARNING: source is {w}x{h} (ratio {ratio:.3f}), not 16:9. "
            f"The hero frame is a 16:9 box -- this will letterbox or crop.")
    if not info["has_audio"]:
        log("WARNING: source has no audio track. The site's unmute button "
            "will do nothing.")
    if w > 1920 or h > 1080:
        log(f"Source is {w}x{h}; will downscale to 1920 wide with lanczos.")
    return w > 1920 or h > 1080


def vfilter(info, needs_scale, pix_fmt):
    parts = []
    if needs_scale:
        parts.append("scale=1920:-2:flags=lanczos")
    parts.append(f"format={pix_fmt}")
    return ",".join(parts)


def color_flags(info):
    """
    The master is tv-range Rec.709 and the outgoing file has always been tagged
    that way. An untagged MP4 gets interpreted inconsistently across browsers,
    which shifts the grade -- for a colorist's reel that is the one regression
    that must never happen. Carry the source's tags through, defaulting to 709.
    """
    return [
        "-color_primaries", info.get("color_primaries") or "bt709",
        "-color_trc", info.get("color_transfer") or "bt709",
        "-colorspace", info.get("color_space") or "bt709",
        "-color_range", info.get("color_range") or "tv",
    ]


# --------------------------------------------------------------------------
# Phase 1: solve the CRF from the file itself
# --------------------------------------------------------------------------

VIDEO_KB_RE = re.compile(r"video:\s*(\d+)\s*kB")


def measure_kbps(src, info, needs_scale, start, seconds, crf):
    """
    Encode a slice and throw the packets away (-f null). ffmpeg still reports
    the encoded payload in its final 'video:NkB' line, so this measures real
    encoder output without writing anything to disk.
    """
    cmd = [FFMPEG, "-hide_banner", "-nostats",
           "-ss", str(start), "-t", str(seconds), "-i", str(src),
           "-map", "0:v:0", "-an", "-sn", "-dn",
           "-vf", vfilter(info, needs_scale, "yuv420p10le"),
           "-c:v", "libsvtav1", "-preset", str(AV1_PRESET), "-crf", str(crf),
           "-svtav1-params", "tune=0:scd=1:keyint=240",
           "-f", "null", "-"]
    r = run(cmd)
    m = VIDEO_KB_RE.search(r.stderr)
    if not m:
        sys.exit(f"ERROR: could not measure encoder output at CRF {crf}.\n"
                 f"{r.stderr.strip()[-1500:]}")
    return int(m.group(1)) * 8 / seconds  # kB over N s -> kbps


def solve_crf(src, info, needs_scale):
    dur = info["duration"]
    points = [round(dur * p, 2) for p in SAMPLE_POINTS]

    measurements = {}
    for crf in PROBE_CRFS:
        vals = []
        for p in points:
            kbps = measure_kbps(src, info, needs_scale, p, SAMPLE_SECONDS, crf)
            vals.append(kbps)
            log(f"  probe CRF {crf} @ {p:>7.1f}s : {kbps:8.0f} kbps")
        measurements[crf] = vals
        log(f"  -> CRF {crf} mean: {sum(vals) / len(vals):.0f} kbps")

    lo_crf, hi_crf = PROBE_CRFS
    b_lo = sum(measurements[lo_crf]) / len(measurements[lo_crf])
    b_hi = sum(measurements[hi_crf]) / len(measurements[hi_crf])

    # Bitrate falls off near-exponentially with CRF: ln(b) = a - k*CRF
    k = (math.log(b_lo) - math.log(b_hi)) / (hi_crf - lo_crf)
    a = math.log(b_lo) + k * lo_crf

    target_total_kbps = (TARGET_AV1_MB * 1024 * 1024 * 8) / dur / 1000
    target_video_kbps = target_total_kbps - AUDIO_BITRATE_K
    if target_video_kbps <= 0:
        sys.exit(f"ERROR: target of {TARGET_AV1_MB} MB is too small to fit "
                 f"{AUDIO_BITRATE_K}k of audio across {dur:.0f}s.")

    solved = (a - math.log(target_video_kbps)) / k
    crf = int(round(solved))

    log(f"  fit: ln(bitrate) = {a:.3f} - {k:.4f}*CRF")
    log(f"  target {TARGET_AV1_MB} MB -> {target_video_kbps:.0f} kbps video "
        f"-> CRF {solved:.2f} (rounded {crf})")

    if not (CRF_CLAMP[0] <= crf <= CRF_CLAMP[1]):
        sys.exit(
            f"ERROR: solved CRF {crf} is outside the sane range {CRF_CLAMP}.\n"
            f"  This usually means the source is unlike a normal graded reel\n"
            f"  (near-static, or extraordinarily noisy). Encode it by hand and\n"
            f"  check the result before trusting a number this far out."
        )

    # The grainiest sample is the honest place to JUDGE grain, but a terrible
    # place to MEASURE size from -- see project_mb().
    worst_idx = max(range(len(points)), key=lambda i: measurements[lo_crf][i])
    return crf, points[worst_idx], {"a": a, "k": k}


# --------------------------------------------------------------------------
# Phase 1: shootout + stills
# --------------------------------------------------------------------------

def encode_excerpt(src, info, needs_scale, start, crf, dest):
    cmd = [FFMPEG, "-hide_banner", "-nostats", "-y",
           "-ss", str(start), "-t", str(SHOOTOUT_SECONDS), "-i", str(src),
           "-map", "0:v:0", "-an", "-sn", "-dn",
           "-vf", vfilter(info, needs_scale, "yuv420p10le"),
           "-c:v", "libsvtav1", "-preset", str(AV1_PRESET), "-crf", str(crf),
           "-svtav1-params", "tune=0:scd=1:keyint=240",
           *color_flags(info),
           "-movflags", "+faststart", str(dest)]
    r = run(cmd)
    if r.returncode != 0:
        sys.exit(f"ERROR: shootout encode failed at CRF {crf}.\n"
                 f"{r.stderr.strip()[-1500:]}")
    return dest.stat().st_size


def grab_still(src, at_seconds, dest, vf=None):
    """
    Input-side -ss with accurate_seek. The master is all-intra (ProRes), so this
    is exact there; for the inter-coded candidates ffmpeg decodes forward to the
    requested frame, so it lands on the same picture either way.
    """
    cmd = [FFMPEG, "-hide_banner", "-nostats", "-y",
           "-accurate_seek", "-ss", str(at_seconds), "-i", str(src),
           "-frames:v", "1"]
    if vf:
        cmd += ["-vf", vf]
    cmd += [str(dest)]
    r = run(cmd)
    if r.returncode != 0 or not dest.exists():
        sys.exit(f"ERROR: could not extract still at {at_seconds}s from {src}\n"
                 f"{r.stderr.strip()[-800:]}")


def project_mb(fit, crf, duration):
    """
    Full-reel size for a CRF, from the fit across the WHOLE file.

    Deliberately NOT extrapolated from the shootout excerpt: that excerpt is
    chosen to be the grainiest stretch of the reel precisely because it is the
    hardest to encode, so scaling its bitrate across the full duration
    overstates the result badly (on the 2026 reel, ~88 MB predicted against
    ~64 MB actual). Judge grain on the excerpt; size on the fit.
    """
    kbps = math.exp(fit["a"] - fit["k"] * crf)
    return ((kbps + AUDIO_BITRATE_K) * 1000 * duration / 8) / (1024 * 1024)


def run_shootout(src, info, needs_scale, crf, worst_start, work, fit):
    crfs = [crf - 2, crf, crf + 2]
    dur = info["duration"]
    start = max(0.0, min(worst_start, dur - SHOOTOUT_SECONDS - 0.1))

    candidates = []
    for c in crfs:
        dest = work / f"cand_crf{c}.mp4"
        log(f"  encoding {SHOOTOUT_SECONDS}s excerpt at CRF {c} ...")
        size = encode_excerpt(src, info, needs_scale, start, c, dest)
        kbps = size * 8 / SHOOTOUT_SECONDS / 1000
        projected_mb = project_mb(fit, c, dur)
        candidates.append({"crf": c, "file": dest.name,
                           "kbps": round(kbps), "projected_mb": round(projected_mb, 1)})
        log(f"    CRF {c}: {kbps:.0f} kbps on the grainiest section "
            f"-> ~{projected_mb:.1f} MB projected full reel")

    # Three frames spread through the excerpt, same picture from every source.
    offsets = [SHOOTOUT_SECONDS * f for f in (0.25, 0.55, 0.85)]
    frames = []
    for i, off in enumerate(offsets):
        ref = work / f"frame{i}_source.png"
        grab_still(src, start + off, ref,
                   vf=("scale=1920:-2:flags=lanczos" if needs_scale else None))
        entry = {"index": i, "source": ref.name, "candidates": {}}
        for c in crfs:
            out = work / f"frame{i}_crf{c}.png"
            grab_still(work / f"cand_crf{c}.mp4", off, out)
            entry["candidates"][str(c)] = out.name
        frames.append(entry)
        log(f"  stills for frame {i + 1}/{len(offsets)} extracted")

    return {"crfs": crfs, "recommended": crf, "excerpt_start": round(start, 2),
            "candidates": candidates, "frames": frames}


# --------------------------------------------------------------------------
# Phase 1: the review page
# --------------------------------------------------------------------------

REVIEW_HTML = """<!doctype html>
<meta charset="utf-8">
<title>Reel grain review</title>
<style>
  :root { color-scheme: dark; }
  body { margin:0; background:#0c0c0c; color:#eee;
         font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }
  header { padding:14px 18px; border-bottom:1px solid #262626; }
  h1 { margin:0 0 4px; font-size:15px; font-weight:600; letter-spacing:.01em; }
  .sub { color:#8a8a8a; font-size:12.5px; }
  .bar { display:flex; gap:8px; flex-wrap:wrap; align-items:center;
         padding:12px 18px; border-bottom:1px solid #262626; }
  .bar .spacer { flex:1; }
  button { font:inherit; padding:7px 13px; border-radius:7px; cursor:pointer;
           border:1px solid #3a3a3a; background:#1a1a1a; color:#ddd; }
  button:hover { border-color:#585858; }
  button.on { background:#eee; color:#111; border-color:#eee; font-weight:600; }
  .pick { border-color:#2f6f4f; background:#16281f; color:#9fe3c0; }
  .pick:hover { background:#1d3a2b; }
  #stage { position:relative; overflow:hidden; height:calc(100vh - 165px);
           background:#000; cursor:grab; }
  #stage.drag { cursor:grabbing; }
  #stage img { position:absolute; top:0; left:0; max-width:none;
               image-rendering:pixelated; display:none;
               transform-origin:0 0; user-select:none; -webkit-user-drag:none; }
  #stage img.show { display:block; }
  .hint { padding:9px 18px; color:#7a7a7a; font-size:12px;
          border-top:1px solid #262626; }
  kbd { background:#1e1e1e; border:1px solid #3a3a3a; border-radius:4px;
        padding:1px 5px; font-size:11px; }
</style>
<header>
  <h1>Grain review &mdash; pick a CRF</h1>
  <div class="sub">__SUB__</div>
</header>
<div class="bar">
  <span style="color:#8a8a8a">Layer:</span>
  <span id="layers"></span>
  <span style="color:#8a8a8a; margin-left:14px">Frame:</span>
  <span id="frames"></span>
  <span class="spacer"></span>
  <span style="color:#8a8a8a">Encode with:</span>
  <span id="picks"></span>
</div>
<div id="stage"></div>
<div class="hint">
  Viewing at 1:1. Drag to pan. Press <kbd>1</kbd>&ndash;<kbd>4</kbd> to switch
  layer, <kbd>&larr;</kbd>/<kbd>&rarr;</kbd> for frames, <kbd>Space</kbd> to
  flip against the source. Layers sit in the same position so grain differences
  read as a straight A/B rather than a side-by-side.
</div>
<script>
const DATA = __DATA__;
const stage = document.getElementById('stage');
let frame = 0, layer = 0, prevLayer = 1, ox = 0, oy = 0;

const layerDefs = [{key:'source', label:'ProRes source'}].concat(
  DATA.crfs.map(c => ({key:String(c), label:'CRF ' + c})));

const imgs = {};
DATA.frames.forEach((f, fi) => {
  layerDefs.forEach((ld, li) => {
    const im = new Image();
    im.src = li === 0 ? f.source : f.candidates[ld.key];
    im.dataset.f = fi; im.dataset.l = li;
    stage.appendChild(im);
    imgs[fi + ':' + li] = im;
  });
});

function render() {
  Object.values(imgs).forEach(im => im.classList.remove('show'));
  const im = imgs[frame + ':' + layer];
  if (im) im.classList.add('show');
  Object.values(imgs).forEach(i => i.style.transform =
    'translate(' + ox + 'px,' + oy + 'px)');
  [...document.querySelectorAll('#layers button')].forEach((b, i) =>
    b.classList.toggle('on', i === layer));
  [...document.querySelectorAll('#frames button')].forEach((b, i) =>
    b.classList.toggle('on', i === frame));
}

const lw = document.getElementById('layers');
layerDefs.forEach((ld, i) => {
  const b = document.createElement('button');
  b.textContent = ld.label;
  b.onclick = () => { prevLayer = layer; layer = i; render(); };
  lw.appendChild(b);
});

const fw = document.getElementById('frames');
DATA.frames.forEach((f, i) => {
  const b = document.createElement('button');
  b.textContent = String(i + 1);
  b.onclick = () => { frame = i; render(); };
  fw.appendChild(b);
});

const pw = document.getElementById('picks');
DATA.candidates.forEach(c => {
  const b = document.createElement('button');
  b.className = 'pick';
  b.innerHTML = 'CRF ' + c.crf + ' &middot; ~' + c.projected_mb + ' MB' +
                (c.crf === DATA.recommended ? ' &middot; suggested' : '');
  b.onclick = () => {
    if (!confirm('Encode the full reel at CRF ' + c.crf +
                 '?\\nProjected ~' + c.projected_mb + ' MB. Takes ~25 min.')) return;
    fetch('/pick', {method:'POST', headers:{'Content-Type':'application/json'},
                    body: JSON.stringify({crf: c.crf})})
      .then(() => { document.body.innerHTML =
        '<header><h1>CRF ' + c.crf + ' selected</h1><div class="sub">' +
        'Encoding now &mdash; watch the terminal or the log. You can close this tab.' +
        '</div></header>'; });
  };
  pw.appendChild(b);
});

let dragging = false, sx = 0, sy = 0;
stage.addEventListener('mousedown', e => {
  dragging = true; sx = e.clientX - ox; sy = e.clientY - oy;
  stage.classList.add('drag');
});
addEventListener('mousemove', e => {
  if (!dragging) return;
  ox = e.clientX - sx; oy = e.clientY - sy; render();
});
addEventListener('mouseup', () => { dragging = false; stage.classList.remove('drag'); });
addEventListener('keydown', e => {
  if (e.key >= '1' && e.key <= String(layerDefs.length)) {
    prevLayer = layer; layer = +e.key - 1; render();
  } else if (e.key === 'ArrowRight') {
    frame = (frame + 1) % DATA.frames.length; render();
  } else if (e.key === 'ArrowLeft') {
    frame = (frame - 1 + DATA.frames.length) % DATA.frames.length; render();
  } else if (e.key === ' ') {
    e.preventDefault();
    const t = layer; layer = (layer === 0 ? (prevLayer || 1) : 0);
    prevLayer = t; render();
  }
});

// Centre on the middle of the frame rather than the top-left corner, so the
// first thing shown is subject matter instead of an edge.
addEventListener('load', () => {
  const im = imgs['0:0'];
  if (im && im.naturalWidth) {
    ox = Math.min(0, (stage.clientWidth - im.naturalWidth) / 2);
    oy = Math.min(0, (stage.clientHeight - im.naturalHeight) / 2);
  }
  render();
});
render();
</script>
"""


class ReviewServer(HTTPServer):
    picked = None
    allow_reuse_address = True


def serve_review(work, shootout, subtitle):
    data = json.dumps({
        "crfs": shootout["crfs"],
        "recommended": shootout["recommended"],
        "candidates": shootout["candidates"],
        "frames": shootout["frames"],
    })
    html = REVIEW_HTML.replace("__DATA__", data).replace("__SUB__", subtitle)
    (work / "index.html").write_text(html, encoding="utf-8")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            name = self.path.lstrip("/").split("?")[0] or "index.html"
            f = work / name
            if not f.exists() or not f.resolve().is_relative_to(work.resolve()):
                self.send_error(404)
                return
            ctype = {"html": "text/html", "png": "image/png",
                     "mp4": "video/mp4"}.get(name.rsplit(".", 1)[-1],
                                             "application/octet-stream")
            body = f.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            self.server.picked = int(payload.get("crf"))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

    srv = ReviewServer(("127.0.0.1", REVIEW_PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    url = f"http://127.0.0.1:{REVIEW_PORT}/"
    log("")
    log(f"  REVIEW READY -> {url}")
    log(f"  Or skip the browser:  --pick <crf>   (candidates in {work})")
    log("")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    deadline = time.time() + REVIEW_TIMEOUT_H * 3600
    while srv.picked is None and time.time() < deadline:
        time.sleep(0.5)
    srv.shutdown()

    if srv.picked is None:
        log(f"  No pick within {REVIEW_TIMEOUT_H}h -- stopping. "
            f"Re-run with --pick <crf> to continue.")
        return None
    log(f"  CRF {srv.picked} selected.")
    return srv.picked


# --------------------------------------------------------------------------
# Phase 2: the real encodes
# --------------------------------------------------------------------------

def encode_av1(src, info, needs_scale, crf, dest):
    cmd = [FFMPEG, "-hide_banner", "-y", "-i", str(src),
           "-map", "0:v:0"]
    if info["has_audio"]:
        cmd += ["-map", "0:a:0"]
    cmd += [
        "-vf", vfilter(info, needs_scale, "yuv420p10le"),
        "-c:v", "libsvtav1", "-preset", str(AV1_PRESET), "-crf", str(crf),
        "-svtav1-params", "tune=0:scd=1:keyint=240",
        *color_flags(info),
    ]
    if info["has_audio"]:
        # The mix is a creative choice (-12.1 LUFS on the 2026 reel). Re-encode
        # it, never normalize it.
        cmd += ["-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_K}k", "-ac", "2", "-ar", "48000"]
    cmd += ["-movflags", "+faststart", str(dest)]

    log(f"  AV1 preset {AV1_PRESET} CRF {crf} -- expect ~25 min, please wait ...")
    r = run(cmd)
    if r.returncode != 0:
        sys.exit(f"ERROR: AV1 encode failed.\n{r.stderr.strip()[-2000:]}")


def encode_h264(src, info, needs_scale, dest, work):
    """
    2-pass ABR rather than CRF: this file has a hard 100 MB ceiling it must not
    cross, and only ABR gives a predictable size. tune=film with deblock -1,-1
    and aq-mode 3 are the grain-retention levers available at a bitrate this
    far below what the content wants.
    """
    dur = info["duration"]
    total_kbps = (TARGET_H264_MB * 1024 * 1024 * 8) / dur / 1000
    vkbps = int(total_kbps - (AUDIO_BITRATE_K if info["has_audio"] else 0))

    common = [
        "-vf", vfilter(info, needs_scale, "yuv420p"),
        "-c:v", "libx264", "-preset", "veryslow",
        "-profile:v", "high", "-level", "4.0",
        "-b:v", f"{vkbps}k",
        "-maxrate", f"{int(vkbps * 1.65)}k", "-bufsize", f"{int(vkbps * 3.3)}k",
        "-tune", "film",
        "-x264-params",
        "aq-mode=3:aq-strength=1.0:psy-rd=1.0,0.15:deblock=-1,-1:"
        "ref=5:bframes=4:me=umh:subme=9:trellis=2",
        "-pix_fmt", "yuv420p",
    ]
    passlog = str(work / "x264pass")

    log(f"  H.264 fallback, 2-pass ABR at {vkbps}k (target {TARGET_H264_MB} MB) ...")
    # -f null, not "-f mp4 NUL": the mp4 muxer needs seekable output to write its
    # moov atom, and NUL isn't seekable. Pass 1 only exists to produce the stats
    # file, so discarding the packets outright is both correct and faster.
    r1 = run([FFMPEG, "-hide_banner", "-y", "-i", str(src), "-map", "0:v:0",
              "-an", "-sn", "-dn", *common,
              "-pass", "1", "-passlogfile", passlog, "-f", "null", os.devnull])
    if r1.returncode != 0:
        sys.exit(f"ERROR: x264 pass 1 failed.\n{r1.stderr.strip()[-2000:]}")

    cmd = [FFMPEG, "-hide_banner", "-y", "-i", str(src), "-map", "0:v:0"]
    if info["has_audio"]:
        cmd += ["-map", "0:a:0"]
    cmd += [*common, "-pass", "2", "-passlogfile", passlog, *color_flags(info)]
    if info["has_audio"]:
        cmd += ["-c:a", "aac", "-b:a", f"{AUDIO_BITRATE_K}k", "-ac", "2", "-ar", "48000"]
    cmd += ["-movflags", "+faststart", str(dest)]

    r2 = run(cmd)
    if r2.returncode != 0:
        sys.exit(f"ERROR: x264 pass 2 failed.\n{r2.stderr.strip()[-2000:]}")


def make_poster(src, info, needs_scale, dest):
    """
    Frame 0 exactly. The homepage paints this as the <video> poster and eases it
    from grayscale to colour on 'loadeddata' (style.css #reel-video.is-ready), so
    it has to be the first frame of the cut -- any other frame makes the handoff
    from poster to playback visibly jump.
    """
    sel = "select=eq(n\\,0)"
    scale = "scale=1920:-2:flags=lanczos," if needs_scale else ""
    for q in (2, 3, 4, 5, 6, 7):
        r = run([FFMPEG, "-hide_banner", "-nostats", "-y", "-i", str(src),
                 "-vf", f"{sel},{scale}format=yuv420p",
                 "-frames:v", "1", "-q:v", str(q), str(dest)])
        if r.returncode != 0:
            sys.exit(f"ERROR: poster extraction failed.\n{r.stderr.strip()[-1200:]}")
        kb = dest.stat().st_size / 1024
        if kb <= POSTER_TARGET_KB:
            log(f"  poster: frame 0 at -q:v {q}, {kb:.0f} KB")
            return
    log(f"  poster: frame 0, {dest.stat().st_size / 1024:.0f} KB "
        f"(above the {POSTER_TARGET_KB} KB target, kept anyway)")


# --------------------------------------------------------------------------
# Output verification
# --------------------------------------------------------------------------

def has_faststart(path):
    """moov must precede mdat or progressive playback stalls until fully buffered."""
    head = path.read_bytes()[:65536]
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    return moov != -1 and (mdat == -1 or moov < mdat)


def verify(path, info):
    problems = []
    mb = path.stat().st_size / (1024 * 1024)
    if mb >= HARD_LIMIT_MB:
        problems.append(f"{mb:.1f} MB exceeds GitHub's {HARD_LIMIT_MB} MB hard "
                        f"limit -- git push would be rejected outright")
    if not has_faststart(path):
        problems.append("moov atom is not at the head (faststart missing)")

    got = probe(path)
    if abs(got["duration"] - info["duration"]) > 0.5:
        problems.append(f"duration {got['duration']:.2f}s != source "
                        f"{info['duration']:.2f}s")
    for key in ("color_primaries", "color_transfer", "color_space"):
        if got.get(key) != (info.get(key) or "bt709"):
            problems.append(f"{key} is {got.get(key)!r}, expected "
                            f"{info.get(key) or 'bt709'!r}")
    if info["has_audio"] and not got["has_audio"]:
        problems.append("audio track missing from output")

    log(f"  {path.name}: {mb:.1f} MB, {got['width']}x{got['height']}, "
        f"{got['duration']:.2f}s, {got['codec']}"
        + (f" + {got['audio_codec']}" if got["has_audio"] else " (no audio)"))
    for p in problems:
        log(f"    !! {p}")
    return problems


def av1_codec_string(path):
    """
    The <source type=...> codec string must match or Safari silently skips AV1
    and drops to the H.264 fallback. Derive it from the file instead of guessing.
    """
    r = run([FFPROBE, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=profile,level,bits_per_raw_sample",
             "-of", "json", str(path)])
    try:
        s = json.loads(r.stdout)["streams"][0]
        prof = {"Main": 0, "High": 1, "Professional": 2}.get(s.get("profile"), 0)
        lvl = int(s.get("level") or 8)
        depth = int(s.get("bits_per_raw_sample") or 10)
        return f"av01.{prof}.{lvl:02d}M.{depth:02d}"
    except Exception:
        return "av01.0.08M.10"


# --------------------------------------------------------------------------
# Drop-folder plumbing
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# Published status -- what admin/ reads
# --------------------------------------------------------------------------
#
# The encode runs on one desktop, but the admin page is opened from anywhere.
# The only channel between them that costs nothing and needs no server is the
# repo itself, so the pipeline publishes a small JSON and pushes just that file.
#
# Nothing here is secret, but the repo IS public: store basenames only, never
# full local paths, and never the drop folders' locations.

STATUS_STATES = (
    "idle",            # nothing to do
    "waiting_settle",  # file seen, still copying/syncing
    "probing",         # sampling the file to solve the CRF
    "awaiting_review", # grain A/B is up, waiting on a human
    "encoding",        # full AV1 + H.264 pass
    "verifying",       # size / faststart / colour checks
    "done",
    "failed",
)


def read_status():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def write_status(state=None, detail=None, source=None, queue=None,
                 current=None, publish=False):
    """
    Merge-and-write. Every field is optional so callers can update just the one
    thing that changed without having to restate the rest.
    """
    st = read_status()
    st["heartbeat"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    job = st.setdefault("job", {})
    if state is not None:
        if state not in STATUS_STATES:
            raise ValueError(f"unknown status state {state!r}")
        if job.get("state") != state:
            job["since"] = st["heartbeat"]
        job["state"] = state
    if detail is not None:
        job["detail"] = detail
    if source is not None:
        job["source"] = Path(source).name   # basename only: public repo
    if queue is not None:
        st["queue"] = [Path(q).name for q in queue]
    if current is not None:
        st["current"] = current

    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATUS_FILE.write_text(json.dumps(st, indent=2) + chr(10), encoding="utf-8")
    if publish:
        publish_status()
    return st


def publish_status():
    """
    Commit and push ONLY data/reel-status.json.

    Scoped to that one path on purpose. The encoded reel is never auto-committed
    -- that stays a deliberate human action -- but the status file is useless
    unless it actually reaches GitHub, since the whole point is reading it from
    another machine. [skip ci] keeps it from waking the cache-buster workflow.
    """
    rel = str(STATUS_FILE.relative_to(REPO_ROOT)).replace("\\", "/")
    try:
        r = run(["git", "-C", str(REPO_ROOT), "status", "--porcelain", "--", rel])
        if not r.stdout.strip():
            return  # nothing changed, don't make an empty commit
        run(["git", "-C", str(REPO_ROOT), "add", "--", rel])
        run(["git", "-C", str(REPO_ROOT), "commit", "-m",
             "Reel pipeline status [skip ci]", "--", rel])
        # --autostash so a working tree mid-encode (new mp4s sitting unstaged)
        # never blocks the rebase.
        run(["git", "-C", str(REPO_ROOT), "pull", "--rebase", "--autostash",
             "origin", "main"])
        push = run(["git", "-C", str(REPO_ROOT), "push", "origin", "main"])
        if push.returncode != 0:
            log(f"  (status push failed, continuing: "
                f"{push.stderr.strip().splitlines()[-1] if push.stderr.strip() else '?'})")
    except Exception as e:
        # Status publishing must never take the encode down with it.
        log(f"  (status publish skipped: {e})")


def describe_current():
    """Facts about the reel as it now stands on disk, for the admin panel."""
    out = {}
    for key, path in (("av1", OUT_AV1), ("h264", OUT_H264), ("poster", OUT_POSTER)):
        if path.exists():
            out[key] = {"name": path.name,
                        "mb": round(path.stat().st_size / (1024 * 1024), 1)}
    if OUT_AV1.exists():
        try:
            v = probe(OUT_AV1)
            out["width"] = v["width"]
            out["height"] = v["height"]
            out["duration"] = round(v["duration"], 2)
            out["fps"] = round(v["fps"], 3)
        except SystemExit:
            pass
    return out


STATE_FILE = Path(__file__).resolve().parent / ".reel_state.json"
LOCK_FILE = Path(tempfile.gettempdir()) / "encode_reel.lock"


def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"processed": {}}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def is_file_settled(path, quiet_seconds=30, poll=5):
    """
    A 4 GB master takes a while to copy or sync. Wait until the size stops
    moving before touching it, and refuse cloud placeholders outright -- on
    Google Drive an unmaterialized file reports its full size but has no bytes
    behind it, which would produce a silently truncated encode.
    """
    FILE_ATTRIBUTE_OFFLINE = 0x1000
    FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000
    try:
        attrs = path.stat().st_file_attributes
        if attrs & (FILE_ATTRIBUTE_OFFLINE | FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS):
            log(f"  {path.name} is a cloud placeholder, not downloaded. Skipping.")
            return False
    except AttributeError:
        pass

    last, stable = -1, 0
    while stable < quiet_seconds:
        size = path.stat().st_size
        if size == last and size > 0:
            stable += poll
        else:
            stable, last = 0, size
        time.sleep(poll)
    return True


def acquire_lock():
    """A full run spans several 5-minute watcher ticks; only one may be live."""
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            r = run(["tasklist", "/FI", f"PID eq {pid}", "/NH"])
            if str(pid) in r.stdout:
                log(f"Another run is already active (pid {pid}). Exiting.")
                return False
            log(f"Clearing stale lock from dead pid {pid}.")
        except Exception:
            pass
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def release_lock():
    try:
        LOCK_FILE.unlink()
    except FileNotFoundError:
        pass


def scan_drops():
    """
    Every unprocessed master across all drop folders, oldest first.

    Missing folders are skipped quietly rather than treated as an error: the
    Drive folder in particular is only present when Drive is mounted, and a
    laptop-less week shouldn't fill the log with complaints.
    """
    state = load_state()
    found = []
    for d in DROP_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.iterdir(), key=lambda x: x.stat().st_mtime):
            if not f.is_file() or f.suffix.lower() not in VIDEO_EXTS:
                continue
            if f"{f.name}:{f.stat().st_size}" in state["processed"]:
                continue
            found.append(f)
    return found


def find_dropped():
    pending = scan_drops()
    if not pending:
        if not any(d.exists() for d in DROP_DIRS):
            log("No drop folder exists yet. Run watch_reel_dropbox.ps1 -Setup, "
                "or set REEL_DROP_DIR / REEL_DRIVE_DIR.")
        return None
    # The first is what we work on; the rest are reported as queued so the admin
    # panel can show that something is stacked up behind the current job.
    write_status(queue=[f.name for f in pending[1:]])
    return pending[0]


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def process(src, pick=None, dry_run=False):
    src = Path(src)
    if not src.exists():
        sys.exit(f"ERROR: {src} does not exist.")

    log(f"Source: {src}")
    info = probe(src)
    log(f"  {info['codec']} {info['profile']} {info['width']}x{info['height']} "
        f"@ {info['fps']:.3f}fps, {info['duration']:.2f}s, {info['pix_fmt']}, "
        f"{info['size'] / (1024 ** 3):.2f} GB")
    log(f"  colour: {info['color_primaries']}/{info['color_transfer']}/"
        f"{info['color_space']} {info['color_range']}")
    needs_scale = validate(info)

    work = Path(tempfile.mkdtemp(prefix="reel_encode_"))
    log(f"  work dir: {work}")
    keep_work = False   # only set when something failed and the files are evidence

    try:
        if pick is None:
            log("")
            log("Phase 1 -- solving CRF from the file itself")
            write_status(state="probing", source=src,
                         detail="Analyse du grain et calcul du CRF", publish=True)
            crf, worst, fit = solve_crf(src, info, needs_scale)
            if dry_run:
                log(f"\nDry run: would encode at CRF {crf}. Stopping.")
                return
            log("")
            log(f"Phase 1 -- grain shootout at CRF {crf - 2}/{crf}/{crf + 2} "
                f"on the grainiest section ({worst:.0f}s)")
            write_status(detail=f"Comparatif de grain a CRF {crf-2}/{crf}/{crf+2}")
            shootout = run_shootout(src, info, needs_scale, crf, worst, work, fit)
            subtitle = (f"{src.name} &middot; {info['width']}x{info['height']} "
                        f"&middot; {info['duration']:.0f}s &middot; excerpt from "
                        f"{shootout['excerpt_start']:.0f}s (grainiest section)")
            write_status(state="awaiting_review",
                         detail=f"En attente de ton choix de CRF "
                                f"(http://127.0.0.1:{REVIEW_PORT}/)", publish=True)
            pick = serve_review(work, shootout, subtitle)
            if pick is None:
                write_status(state="idle", detail="Revue expiree sans choix",
                             publish=True)
                return

        log("")
        log(f"Phase 2 -- full encode at CRF {pick}")
        write_status(state="encoding", source=src,
                     detail=f"Encodage complet a CRF {pick} (~25 min)", publish=True)
        OUT_AV1.parent.mkdir(parents=True, exist_ok=True)
        OUT_POSTER.parent.mkdir(parents=True, exist_ok=True)

        tmp_av1 = work / "reel.av1.mp4"
        tmp_h264 = work / "reel.mp4"
        tmp_poster = work / "hero-poster.jpg"

        t0 = time.time()
        encode_av1(src, info, needs_scale, pick, tmp_av1)
        log(f"  AV1 done in {(time.time() - t0) / 60:.1f} min")

        t0 = time.time()
        encode_h264(src, info, needs_scale, tmp_h264, work)
        log(f"  H.264 done in {(time.time() - t0) / 60:.1f} min")

        make_poster(src, info, needs_scale, tmp_poster)

        log("")
        log("Verifying outputs")
        write_status(state="verifying",
                     detail="Verification taille / faststart / couleur")
        problems = verify(tmp_av1, info) + verify(tmp_h264, info)
        if problems:
            keep_work = True
            log("")
            log("REFUSING to stage -- fix the above and re-run. "
                f"Files left in {work}")
            write_status(state="failed", detail="; ".join(problems), publish=True)
            return

        shutil.move(str(tmp_av1), str(OUT_AV1))
        shutil.move(str(tmp_h264), str(OUT_H264))
        shutil.move(str(tmp_poster), str(OUT_POSTER))

        log("")
        log("Staged into the working tree:")
        for p in (OUT_AV1, OUT_H264, OUT_POSTER):
            log(f"  {p.relative_to(REPO_ROOT)}  "
                f"{p.stat().st_size / (1024 * 1024):.1f} MB")
        log("")
        log(f"AV1 codec string for index.html: {av1_codec_string(OUT_AV1)}")
        log("")
        log("Not committed. Review the files, then commit and push yourself.")
        write_status(state="done", current=describe_current(),
                     detail=f"Encode a CRF {pick}. A relire puis commiter.",
                     publish=True)

    except BaseException as e:
        keep_work = True    # crashed or interrupted -- leave the evidence
        try:
            write_status(state="failed", detail=f"{type(e).__name__}: {e}"[:300],
                         publish=True)
        except Exception:
            pass
        raise
    finally:
        # Keep the work dir ONLY on failure. The earlier "keep if any *.mp4 is
        # present" test was always true, because the three shootout excerpts are
        # themselves .mp4 -- so every run leaked ~126 MB of stills and excerpts
        # into %TEMP% forever.
        if work.exists():
            if keep_work:
                log(f"  work files kept for inspection: {work}")
            else:
                shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="Encode the hero reel for the web.")
    ap.add_argument("--file", help="master to encode")
    ap.add_argument("--watch", action="store_true",
                    help="process the next unhandled file in the drop folder")
    ap.add_argument("--pick", type=int, help="skip the review gate, use this CRF")
    ap.add_argument("--dry-run", action="store_true",
                    help="phase 1 analysis only, no encoding")
    args = ap.parse_args()

    if not args.file and not args.watch:
        ap.error("give --file <master> or --watch")

    if not acquire_lock():
        return
    try:
        if args.watch:
            src = find_dropped()
            if src is None:
                # Still touch the status file: its heartbeat is how the admin
                # panel tells "nothing queued" apart from "this desktop is
                # asleep and your drop is going nowhere".
                write_status(state="idle", detail="Rien en attente",
                             queue=[], current=describe_current(), publish=True)
                log("Nothing new in the drop folders.")
                return
            log(f"Found {src.name}; waiting for it to finish copying ...")
            write_status(state="waiting_settle", source=src,
                         detail="Copie/synchronisation en cours", publish=True)
            if not is_file_settled(src):
                write_status(state="idle",
                             detail=f"{src.name} pas encore disponible "
                                    f"(fichier cloud non telecharge)", publish=True)
                return
            process(src, pick=args.pick)
            state = load_state()
            state["processed"][f"{src.name}:{src.stat().st_size}"] = {
                "at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "path": str(src),
            }
            save_state(state)
        else:
            process(args.file, pick=args.pick, dry_run=args.dry_run)
    finally:
        release_lock()


if __name__ == "__main__":
    main()

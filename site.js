// site.js — behaviours shared by index.html, project.html and admin/index.html.
//
// Created Aug 2026 to stop copy-pasting the same code into three pages. Before this,
// the accent-colour cycle below existed as three verbatim ~45-line copies, the HTML
// escaper as three near-copies that had drifted apart, and the language toggle and
// design-settings loader as two copies each. Fixing any one of them meant remembering
// to fix the others, which is exactly how admin/index.html ended up 13 stylesheet
// versions behind at one point.
//
// Loaded from <head> on every page (before i18n.js), as a plain parser-blocking script:
// the accent cycle needs to start before first paint, and everything else just needs to
// be defined before the body-bottom scripts run. Root pages load "site.js";
// admin/index.html loads "../site.js".

// ---------------------------------------------------------------------------
// Accent colour cycle — self-starting, no DOM needed.
//
// Continuously cycles --accent (Red -> Yellow -> Green -> Cyan -> Blue -> Magenta ->
// Red), one full loop every 60s, from a random starting point per page load.
//
// This is the SECOND implementation. The first tried to do it entirely in CSS: an
// animated number (--accent-hue) fed live into oklch()'s hue argument, then redesigned
// into --accent itself being a @property-registered <color> animated through literal
// colour keyframes. Both were spec-valid CSS, and both broke .wordmark span's colour in
// real browser testing anyway (it rendered solid white — --accent was going invalid and
// falling through to the inherited page text colour). Animating a colour-typed custom
// property proved too inconsistently supported in practice to keep trusting, so this
// version drops CSS animation entirely and computes the exact oklch(65% 0.09 hue) ->
// sRGB hex value in JS, setting --accent via style.setProperty() — the same mechanism
// the original static 3-colour picker used with zero issues, just re-run continuously.
//
// The oklch->sRGB maths and the 65%/0.09 L/C choice are the ones verified earlier for
// contrast: worst case 5.46:1 against --bg across the full hue circle, comfortably
// clearing WCAG AA's 4.5:1. style.css's plain #8A9A5B is the pre-JS fallback, so if this
// file fails to load the site simply stays olive.
(function () {
  var CYCLE_MS = 60000; // full 360° loop duration
  var L = 0.65, C = 0.09; // oklch lightness/chroma — perceptually uniform brightness across every hue, unlike hsl()
  var html = document.documentElement;
  var startOffset = Math.random() * CYCLE_MS; // randomizes where in the loop this page load begins

  function oklchToHex(hueDeg) {
    var h = hueDeg * Math.PI / 180;
    var a = C * Math.cos(h);
    var b = C * Math.sin(h);
    var l_ = L + 0.3963377774 * a + 0.2158037573 * b;
    var m_ = L - 0.1055613458 * a - 0.0638541728 * b;
    var s_ = L - 0.0894841775 * a - 1.2914855480 * b;
    var l = l_ * l_ * l_, m = m_ * m_ * m_, s = s_ * s_ * s_;
    var r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s;
    var g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s;
    var bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s;
    function toSrgb(c) {
      c = Math.max(0, Math.min(1, c));
      return c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
    }
    function hex2(c) {
      var n = Math.round(toSrgb(c) * 255).toString(16);
      return n.length === 1 ? '0' + n : n;
    }
    return '#' + hex2(r) + hex2(g) + hex2(bl);
  }

  var UPDATE_INTERVAL_MS = 120; // ~8x/sec — imperceptibly different from every frame for a 60s cycle, but ~8x less work (each update triggers a style recalc everywhere --accent is used)
  var lastUpdate = -Infinity;

  function tick(now) {
    if (now - lastUpdate >= UPDATE_INTERVAL_MS) {
      var elapsed = (now + startOffset) % CYCLE_MS;
      html.style.setProperty('--accent', oklchToHex((elapsed / CYCLE_MS) * 360));
      lastUpdate = now;
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
})();

// ---------------------------------------------------------------------------
// Escapes a value before it's interpolated into generated HTML.
//
// Titles, client and crew names come from data/projects.json (written by the admin), so
// they're ordinary human text, not hostile input — but they're still not HTML. Four
// DP/director fields already contain "&" ("Sandra Coppola & Juliette Gosselin" and
// friends), and a straight double quote in any title would end an attribute early and
// corrupt the rest of the markup. Covers both attribute values and text content.
function esc(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ---------------------------------------------------------------------------
// Runs updateFn as a same-document View Transition where supported, otherwise just runs
// it — used for the work-grid filter crossfade (index.html) and the lightbox's
// still-to-still crossfade (project.html).
//
// Temporarily adds .same-doc-transition to <body> for the duration; see the CSS rule of
// the same name in style.css for why. Short version: the nav's own view-transition-name
// otherwise pulls it into the browser's view-transition top layer, which paints above
// everything regardless of z-index, so it visibly pops over whatever is transitioning.
// That bug first showed up in the lightbox crossfade and is solved here once for every
// same-document transition rather than per feature.
// Both .ready and .finished REJECT whenever the browser skips the animation rather than
// running it — a hidden tab, or simply a second click arriving while the first transition
// is still going. (prefers-reduced-motion was listed here too until Aug 2026; it doesn't
// belong, which is the whole reason for the check below.) The DOM update itself still happens in every
// one of those cases, so there's nothing to recover from; but each rejection with no
// handler attached logs "InvalidStateError: Transition was aborted because of invalid
// state" to the console, and .ready is easy to miss because this function otherwise never
// touches it. Both are swallowed explicitly. Catching before .finally() also guarantees
// the cleanup still runs, which is the part that actually matters.
// onDone, when given, runs once the transition has finished (or immediately when there
// was no transition to run) — for cleanup that must not happen while the browser is
// still animating, such as releasing a view-transition-name back to another element.
function withViewTransition(updateFn, onDone) {
  // The comment above already treated prefers-reduced-motion as a case where the browser
  // skips the animation and only the DOM update lands. It isn't: nothing in the API
  // consults that preference, so these transitions were in fact animating for users who
  // asked them not to. Skipping here rather than per caller covers every same-document
  // transition at once (work-grid filter, lightbox open/close/navigate), and matches how
  // the rest of the site's motion is gated in style.css's prefers-reduced-motion block.
  const stillMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!document.startViewTransition || stillMotion) {
    updateFn();
    if (onDone) onDone();
    return;
  }
  document.body.classList.add('same-doc-transition');
  const transition = document.startViewTransition(updateFn);
  transition.ready.catch(() => {});
  transition.finished
    .catch(() => {})
    .finally(() => {
      document.body.classList.remove('same-doc-transition');
      if (onDone) onDone();
    });
}

// ---------------------------------------------------------------------------
// Wires the FR/EN toggle: restores the remembered choice, keeps the button label
// showing the language you'd switch TO (not the current one), and persists every change.
//
// English is the default; French is only applied if it was remembered. onChange runs
// after each switch so a page can re-render whatever it builds in JS and would otherwise
// keep stale labels — the work grid and filter bar on index.html, the credits' type
// acronym on project.html. No-ops if the page has no toggle (admin/index.html is
// French-only), so it's safe to call unconditionally.
function initLangToggle(onChange) {
  const btn = document.getElementById('lang-toggle');
  if (!btn) return;
  const body = document.body;

  if (localStorage.getItem('iob-lang') === 'fr') body.classList.add('lang-fr');

  const isFr = () => body.classList.contains('lang-fr');
  const syncButton = () => { btn.textContent = isFr() ? 'EN' : 'FR'; };
  syncButton();

  btn.addEventListener('click', () => {
    body.classList.toggle('lang-fr');
    localStorage.setItem('iob-lang', isFr() ? 'fr' : 'en');
    document.documentElement.lang = isFr() ? 'fr' : 'en';
    syncButton();
    if (onChange) onChange(isFr());
  });
}

// ---------------------------------------------------------------------------
// Applies the admin-editable visual settings (Design tab -> data/design.json) on top of
// style.css's defaults: reel halo intensity/size/falloff, grain level, background colour.
//
// Silently no-ops if the file doesn't exist yet (first use, before any admin save) —
// the CSS defaults in :root already match this file's own defaults exactly, so a missing
// file is indistinguishable from a saved default. The halo variables are inert on pages
// with no reel (project.html), so all five are applied everywhere rather than
// maintaining a per-page subset that has to be kept in sync by hand.
function applyDesignSettings() {
  return fetch('data/design.json')
    .then((r) => r.json())
    .then((d) => {
      const root = document.documentElement.style;
      if (d.haloIntensity != null) root.setProperty('--halo-intensity', d.haloIntensity);
      if (d.haloSize != null) root.setProperty('--halo-size', d.haloSize);
      if (d.haloFalloff != null) root.setProperty('--halo-falloff', d.haloFalloff);
      if (d.grainLevel != null) root.setProperty('--grain-level', d.grainLevel);
      if (d.bg) root.setProperty('--bg', d.bg);
    })
    .catch(() => {});
}

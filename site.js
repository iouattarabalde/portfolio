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
// it — used by the lightbox's open, close and still-to-still crossfades (project.html).
// index.html's work-grid filter used this too until Sept 2026, when the crossfade it
// brings with it turned out to be the wrong motion for that change; see
// withInfoBarSlide() there for what replaced it.
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
  // transition at once (lightbox open/close/navigate), and matches how
  // the rest of the site's motion is gated in style.css's prefers-reduced-motion block.
  const stillMotion = prefersReducedMotion();
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
// Does this visitor ask the system to keep motion to a minimum?
//
// Read live on every call rather than cached once: the setting can be toggled
// mid-session, and every caller is either a one-off init or a user interaction, so
// re-querying costs nothing next to the risk of acting on a stale answer.
function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

// ---------------------------------------------------------------------------
// Scroll-triggered entrance reveals — the single mechanism behind every "lifts and
// fades in as you reach it" on the public pages: work cards and filter chips, the
// contact block, project gallery stills, the credits and the next-project card.
//
// This replaces a load-triggered @keyframes entrance (card-enter) that ran on every
// card the moment the grid rendered. On every viewport the hero fills the screen, so
// the whole grid finished animating below the fold roughly a second before anyone
// scrolled to it, and the site read as completely static from the fold down. It only
// ever looked alive on phones by accident: there the grid renders after
// data/projects.json resolves, so on a slower connection the visitor was already
// scrolling when the cards landed and caught the stagger by chance. Nothing about it
// was ever device-specific — there is no width-gated animation CSS anywhere.
//
// Elements opt in with a data-reveal attribute. The hidden "before" state is scoped to
// .js-reveal on <html>, set immediately below at parse time, which is the safety gate:
// if this file ever fails to load, the class is never added, nothing is hidden, and the
// pages render plainly — the same progressive-enhancement stance the accent cycle takes
// with its olive fallback.
//
// Why a @keyframes animation applied by a class, rather than a CSS transition: an
// earlier scroll-reveal here was built as a transition and abandoned after two rounds of
// fixes (a requestAnimationFrame deferral, then a forced reflow via offsetHeight). A
// transition needs the browser to have already painted the "before" state to animate
// FROM, and these elements are created by innerHTML and observed in the same task, so
// that paint hasn't happened yet. A @keyframes animation starts on its own clock the
// instant `animation` applies to an element, so there is no race to lose. Same
// reasoning as the hero's own entrance in style.css, which is why that one always
// worked while the transition version never did.
document.documentElement.classList.add('js-reveal');

var revealObserver = null;
var revealTiming = null;

// The stagger's two numbers live in style.css with the rest of the motion tokens; this
// reads them once so there's still only one place to tune them. parseFloat handles the
// "55ms" unit, and each falls back to its authored value if the property is ever missing.
function getRevealTiming() {
  if (revealTiming) return revealTiming;
  var cs = getComputedStyle(document.documentElement);
  function num(name, fallback) {
    var v = parseFloat(cs.getPropertyValue(name));
    return isFinite(v) && v > 0 ? v : fallback;
  }
  revealTiming = { step: num('--reveal-stagger', 55), budget: num('--reveal-window', 500) };
  return revealTiming;
}

function getRevealObserver() {
  if (revealObserver) return revealObserver;
  revealObserver = new IntersectionObserver(function (entries, observer) {
    // Stagger across whatever crossed the line together, in document order — not by
    // each element's index within the full list. A grid of 32 cards enters a row at a
    // time, so this gives row 8 exactly the same rhythm as row 1. The hand-written
    // nth-child ladder this replaces had to cap its delays at 12 steps to stop late
    // cards trailing ever further behind, which meant everything past the cap started
    // simultaneously — the stagger died halfway down the grid.
    // Anything sitting entirely above the root counts as arrived too. The huge top
    // rootMargin below means that's normally reported as intersecting anyway; this is
    // the backstop for a document taller than that margin, where the guaranteed initial
    // observation is the only callback such an element will ever get.
    //
    // The isConnected check first, though, is what keeps the rest of this honest.
    // Re-rendering the work grid or a gallery replaces every card via innerHTML, and the
    // observer goes on watching the elements that were thrown away — it delivers one
    // last entry for each. Those entries have a zero-sized rect and, worse,
    // compareDocumentPosition() is implementation-defined for a disconnected node, so
    // they sorted arbitrarily among the real ones below: after a filter change the eight
    // surviving cards came out numbered 0, 1, 2, 16, 17, 18, 19, 20 with the filter bar
    // wedged in at 15, and a batch of 13 was counted as 44, squeezing the step from 55ms
    // to 11.63ms. Dropping them here fixes the ordering and the count at once, and
    // unobserving stops them being reported again.
    var arrived = entries.filter(function (e) {
      if (!e.target.isConnected) {
        observer.unobserve(e.target); // thrown away by a re-render; stop watching it
        return false;
      }
      // Already claimed by a wave started elsewhere (revealBatch marks it and unobserves
      // it, but an entry queued a frame earlier can still land here afterwards).
      if (e.target.hasAttribute('data-revealing')) return false;
      return e.isIntersecting ||
        (e.rootBounds && e.boundingClientRect.bottom <= e.rootBounds.top);
    });
    arrived.sort(function (a, b) {
      return (a.target.compareDocumentPosition(b.target) & Node.DOCUMENT_POSITION_FOLLOWING) ? -1 : 1;
    });
    revealBatch(arrived.map(function (e) { return e.target; }));
  }, {
    // The negative bottom margin pulls the trigger line up off the viewport edge, so an
    // element starts moving just before it would otherwise be properly in view and is
    // already settling by the time it reads.
    //
    // The enormous TOP margin is load-bearing, not a typo. An observer only reports a
    // change in intersection, so an element that goes from below the viewport to above
    // it between two frames — a hash link to #contact, a reload partway down, one hard
    // flick — is never reported at all, and would stay at opacity 0 forever. Growing the
    // root upward past any realistic page height means "above the viewport" is always
    // an intersecting state, so being scrolled past reveals an element instead of
    // stranding it. threshold stays near zero on purpose: crossing the line at all is
    // the signal, not how much of a very tall element shows.
    rootMargin: '9999px 0px -12% 0px',
    threshold: 0.05
  });
  return revealObserver;
}

// Lifts a set of elements into place as one staggered wave, in the order given.
//
// The observer above feeds this whatever crossed the trigger line together, one grid row
// at a time in the usual case. The project page also calls it directly, to open with a
// fixed three rows of stills rather than however many happen to clear the fold — see the
// opening wave at the bottom of project.html.
//
// Claiming each element with data-revealing the moment its wave starts is what keeps
// those two paths from fighting. A manually revealed element is skipped by the observer
// and by observeReveals(), so nothing can be handed a second --reveal-index part-way
// through its animation, which would restart the lift.
//
// A batch is usually one row of a grid, but it can be far larger — a reload partway down
// the page, a hash link, one hard flick, or the project page's own opening wave can land
// a dozen tiles at once. At a flat 55ms each the last one would wait over a second, which
// is the same trailing-off the old nth-child ladder tried to solve by capping its delays
// (and which made everything past the cap start simultaneously instead). Narrowing the
// step so the whole batch fits a fixed budget keeps it a real wave at every size.
function revealBatch(els) {
  var batch = [];
  Array.prototype.forEach.call(els, function (el) {
    if (!el || !el.isConnected || el.hasAttribute('data-revealing')) return;
    el.setAttribute('data-revealing', '');
    if (revealObserver) revealObserver.unobserve(el); // reveals once, then stops being watched
    batch.push(el);
  });
  if (!batch.length) return;
  // Direct callers can reach this without going through observeReveals()' own check.
  if (prefersReducedMotion()) {
    batch.forEach(function (el) { el.classList.add('is-revealed'); });
    return;
  }
  var timing = getRevealTiming();
  var step = batch.length > 1
    ? Math.min(timing.step, timing.budget / (batch.length - 1))
    : timing.step;
  step = Math.round(step * 100) / 100; // keeps the inline style readable; sub-10us is not a timing anyone can perceive
  batch.forEach(function (el, i) {
    // Hold the lift until the tile's own image can actually be painted. Without this the
    // two are on independent clocks and the animation always wins: a 700ms lift against a
    // photo still arriving over the network means an empty box slides into place and the
    // picture appears afterwards, which is what made the project galleries look like they
    // were loading at random. Elements with no image of their own (the filter bar, the
    // credits block) resolve immediately.
    whenPaintable(el.querySelector('img'), function () {
      el.style.setProperty('--reveal-index', i);
      el.style.setProperty('--reveal-stagger', step + 'ms');
      el.classList.add('is-revealed');
    });
  });
}

// Runs cb once img is ready to paint, or immediately when there is no img.
//
// decode() rather than the load event alone: load fires when the bytes are in, but the
// decode can still happen on the first paint, which is exactly when the reveal animation
// is starting and is the worst moment to spend it. Waiting for decode means the first
// frame of the lift already has pixels.
//
// Every failure path still calls cb. A broken image, a decode that rejects, or a request
// that stalls without ever firing load or error would otherwise leave the tile parked at
// opacity 0 for good — a blank grid is bad, an invisible one is worse. The timeout is the
// backstop for that last case and should never normally fire.
var PAINT_TIMEOUT_MS = 4000;

function whenPaintable(img, cb) {
  if (!img) { cb(); return; }
  var fired = false;
  function fire() {
    if (fired) return;
    fired = true;
    cb();
  }
  function decodeThenFire() {
    if (!img.decode) { fire(); return; }
    img.decode().then(fire, fire);
  }
  if (img.complete && img.naturalWidth) {
    decodeThenFire();
  } else {
    img.addEventListener('load', decodeThenFire, { once: true });
    img.addEventListener('error', fire, { once: true });
  }
  setTimeout(fire, PAINT_TIMEOUT_MS);
}

// Starts watching every not-yet-revealed [data-reveal] inside root (the whole document
// by default). Safe to call repeatedly and safe on pages with no such elements at all —
// admin/index.html shares this file and has none.
function observeReveals(root) {
  var scope = root || document;
  var targets = scope.querySelectorAll('[data-reveal]:not(.is-revealed):not([data-revealing])');
  if (!targets.length) return;
  // No observer is created at all for these two cases, rather than creating one and
  // letting the CSS render it inert — the same approach the hero parallax in index.html
  // takes with prefers-reduced-motion.
  if (!('IntersectionObserver' in window) || prefersReducedMotion()) {
    revealNow(scope);
    return;
  }
  var observer = getRevealObserver();
  Array.prototype.forEach.call(targets, function (el) { observer.observe(el); });
}

// Marks everything inside root as revealed straight away. Used by the fallbacks above;
// the reduced-motion rule in style.css is what keeps this from animating for the people
// who asked it not to.
function revealNow(root) {
  var scope = root || document;
  Array.prototype.forEach.call(
    scope.querySelectorAll('[data-reveal]:not(.is-revealed):not([data-revealing])'),
    function (el) { el.classList.add('is-revealed'); }
  );
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

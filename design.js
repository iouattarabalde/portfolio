// design.js — applies data/design.json on top of the stylesheet as CSS custom properties.
//
// How it fits together:
//   - style.css consumes a small set of variables (--wg-cols, --card-ratio, --photo-w, ...)
//     with fallbacks equal to the shipped design, so a missing/partial design.json (or this
//     script failing) always degrades to the original look.
//   - Every control exists in a desktop and a mobile flavour ("-m" suffix). The responsive
//     breakpoints themselves stay in style.css; this file only supplies values.
//   - The admin's Design panel edits the same object and live-previews it by posting
//     { type: 'iob-design-preview', design } into an iframe of the site — hence the
//     message listener below. Values are sanitized here (colors, numeric ranges, ratio
//     whitelist), so neither a hand-edited design.json nor a message can inject CSS.
//   - Last applied values are cached in localStorage and re-applied synchronously on load,
//     before the async fetch of design.json, to avoid a flash of the default design.

const IOB_DESIGN_DEFAULTS = {
  colors: { accent: '#8A9A5B', bg: '#0C0C0C', fg: '#ECECE6', line: '#232320', bgRaised: '#131311', fgDim: '#8C8C86' },
  typography: {
    bodySize: { desktop: 15, mobile: 15 },
    leading: 1.6,
    titleScale: { desktop: 1, mobile: 1 },
    cardTitleSize: 14,
    trackingScale: 1
  },
  grid: {
    columns: { desktop: 4, mobile: 2 },
    gap: { desktop: 1, mobile: 1 },
    cardRatio: { desktop: '16 / 9', mobile: '1 / 1' },
    cardPadding: { desktop: 14, mobile: 10 },
    hoverZoom: 1.04,
    hoverZoomMs: 500,
    scrimOpacity: 1
  },
  hero: { reelScale: 100, bracketsOpacity: 0.7 },
  layout: { sectionPadY: { desktop: 56, mobile: 28 }, sidePad: { desktop: 48, mobile: 20 }, bioMaxWidth: 52 },
  gallery: { columns: { desktop: 3, mobile: 2 }, gap: { desktop: 1, mobile: 1 } },
  nav: { padY: 20, autoHide: false },
  contact: { photoWidth: { desktop: 440, mobile: 320 } }
};

const IOB_CARD_RATIOS = ['21 / 9', '16 / 9', '3 / 2', '4 / 3', '1 / 1', '4 / 5'];

function iobColor(v, fallback) {
  return (typeof v === 'string' && /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(v)) ? v : fallback;
}
function iobNum(v, min, max, fallback) {
  const n = parseFloat(v);
  return Number.isFinite(n) ? Math.min(max, Math.max(min, n)) : fallback;
}
function iobRatio(v, fallback) {
  return IOB_CARD_RATIOS.includes(v) ? v : fallback;
}

// Merges a (possibly partial) design object over the defaults, sanitizes every value,
// and returns the flat map of CSS variables to set. Unknown keys are simply ignored.
function iobDesignVars(d) {
  d = d || {};
  const D = IOB_DESIGN_DEFAULTS;
  const c = d.colors || {}, t = (d.typography || {}), g = d.grid || {}, ct = d.contact || {};
  const h = d.hero || {}, lay = d.layout || {}, gal = d.gallery || {}, nav = d.nav || {};
  const bs = t.bodySize || {}, ts = t.titleScale || {};
  const cols = g.columns || {}, gap = g.gap || {}, ratio = g.cardRatio || {}, cpad = g.cardPadding || {};
  const sy = lay.sectionPadY || {}, sx = lay.sidePad || {};
  const gcols = gal.columns || {}, ggap = gal.gap || {};
  const pw = ct.photoWidth || {};
  return {
    // Couleurs
    '--accent':      iobColor(c.accent, D.colors.accent),
    '--bg':          iobColor(c.bg, D.colors.bg),
    '--fg':          iobColor(c.fg, D.colors.fg),
    '--line':        iobColor(c.line, D.colors.line),
    '--bg-raised':   iobColor(c.bgRaised, D.colors.bgRaised),
    '--fg-dim':      iobColor(c.fgDim, D.colors.fgDim),
    // Typographie
    '--body-size':   iobNum(bs.desktop, 11, 22, D.typography.bodySize.desktop) + 'px',
    '--body-size-m': iobNum(bs.mobile, 11, 22, D.typography.bodySize.mobile) + 'px',
    '--leading':     String(iobNum(t.leading, 1.2, 2.2, D.typography.leading)),
    '--title-scale':   String(iobNum(ts.desktop, 0.6, 1.6, D.typography.titleScale.desktop)),
    '--title-scale-m': String(iobNum(ts.mobile, 0.6, 1.6, D.typography.titleScale.mobile)),
    '--card-title':  iobNum(t.cardTitleSize, 10, 22, D.typography.cardTitleSize) + 'px',
    '--tracking':    String(iobNum(t.trackingScale, 0.3, 2, D.typography.trackingScale)),
    // Grille projets
    '--wg-cols':     String(Math.round(iobNum(cols.desktop, 1, 6, D.grid.columns.desktop))),
    '--wg-cols-m':   String(Math.round(iobNum(cols.mobile, 1, 3, D.grid.columns.mobile))),
    '--wg-gap':      iobNum(gap.desktop, 0, 48, D.grid.gap.desktop) + 'px',
    '--wg-gap-m':    iobNum(gap.mobile, 0, 48, D.grid.gap.mobile) + 'px',
    '--card-ratio':  iobRatio(ratio.desktop, D.grid.cardRatio.desktop),
    '--card-ratio-m': iobRatio(ratio.mobile, D.grid.cardRatio.mobile),
    '--card-pad':    iobNum(cpad.desktop, 4, 32, D.grid.cardPadding.desktop) + 'px',
    '--card-pad-m':  iobNum(cpad.mobile, 4, 32, D.grid.cardPadding.mobile) + 'px',
    '--zoom':        String(iobNum(g.hoverZoom, 1, 1.2, D.grid.hoverZoom)),
    '--zoom-dur':    Math.round(iobNum(g.hoverZoomMs, 100, 1500, D.grid.hoverZoomMs)) + 'ms',
    '--scrim':       String(iobNum(g.scrimOpacity, 0, 1, D.grid.scrimOpacity)),
    // Hero
    '--reel-scale':  String(iobNum(h.reelScale, 50, 100, D.hero.reelScale) / 100),
    '--brackets-o':  String(iobNum(h.bracketsOpacity, 0, 1, D.hero.bracketsOpacity)),
    // Mise en page
    '--sect-y':      iobNum(sy.desktop, 24, 140, D.layout.sectionPadY.desktop) + 'px',
    '--sect-y-m':    iobNum(sy.mobile, 12, 80, D.layout.sectionPadY.mobile) + 'px',
    '--pad-x':       iobNum(sx.desktop, 16, 120, D.layout.sidePad.desktop) + 'px',
    '--pad-x-m':     iobNum(sx.mobile, 8, 48, D.layout.sidePad.mobile) + 'px',
    '--bio-w':       Math.round(iobNum(lay.bioMaxWidth, 30, 90, D.layout.bioMaxWidth)) + 'ch',
    // Galerie (page projet)
    '--gal-cols':    String(Math.round(iobNum(gcols.desktop, 1, 4, D.gallery.columns.desktop))),
    '--gal-cols-m':  String(Math.round(iobNum(gcols.mobile, 1, 3, D.gallery.columns.mobile))),
    '--gal-gap':     iobNum(ggap.desktop, 0, 48, D.gallery.gap.desktop) + 'px',
    '--gal-gap-m':   iobNum(ggap.mobile, 0, 48, D.gallery.gap.mobile) + 'px',
    // Nav
    '--nav-pad':     iobNum(nav.padY, 8, 40, D.nav.padY) + 'px'
  };
}

// Nav auto-hide: slides the nav away when scrolling down past the fold, back at any
// upward scroll. Behavioral (not a CSS value), so managed here, idempotently — apply
// can run many times (live preview) without stacking listeners.
let iobNavHideHandler = null;
function iobSetNavAutoHide(on) {
  if (on && !iobNavHideHandler) {
    let lastY = window.scrollY;
    iobNavHideHandler = () => {
      const y = window.scrollY;
      document.documentElement.classList.toggle('nav-hidden', y > lastY && y > 120);
      lastY = y;
    };
    window.addEventListener('scroll', iobNavHideHandler, { passive: true });
  } else if (!on && iobNavHideHandler) {
    window.removeEventListener('scroll', iobNavHideHandler);
    iobNavHideHandler = null;
    document.documentElement.classList.remove('nav-hidden');
  }
}

function iobApplyDesign(design) {
  const vars = iobDesignVars(design);
  for (const [k, v] of Object.entries(vars)) {
    document.documentElement.style.setProperty(k, v);
  }
  iobSetNavAutoHide(!!(design && design.nav && design.nav.autoHide));
  // Nudge anything that sizes itself in JS from these values (the hero's sizeReel
  // listens to resize and reads --reel-scale).
  window.dispatchEvent(new Event('resize'));
  return vars;
}

// The admin sets window.IOB_ADMIN before including this file: it only needs the defaults
// and iobDesignVars() for its form — no fetching, no applying to the admin page itself.
if (!window.IOB_ADMIN) {
  // 1. Instant re-apply of the last known design (avoids the flash on repeat visits).
  try {
    const cached = localStorage.getItem('iob-design-cache');
    if (cached) iobApplyDesign(JSON.parse(cached));
  } catch (e) { /* corrupt cache: ignore, the fetch below fixes it */ }

  // 2. Fresh copy from the repo. 404 (file never saved yet) = shipped defaults.
  fetch('data/design.json')
    .then(r => r.ok ? r.json() : null)
    .then(design => {
      if (!design) return;
      iobApplyDesign(design);
      try { localStorage.setItem('iob-design-cache', JSON.stringify(design)); } catch (e) {}
    })
    .catch(() => {});

  // 3. Live preview channel for the admin's Design panel (same-origin only).
  window.addEventListener('message', (e) => {
    if (e.origin !== location.origin) return;
    if (e.data && e.data.type === 'iob-design-preview') iobApplyDesign(e.data.design);
  });
}

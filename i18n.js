// i18n.js — shared across index.html, project.html, privacy/, terms/ and admin/index.html.
//
// The site is English only (Oct 2026); it was bilingual FR/EN before. Everything editable
// from the admin's Réglages → Avancé section lives in data/strings.json: general UI copy
// (nav labels, headings, credit labels) plus the project type labels. The constants below
// are the fallback defaults, used if that fetch fails or a key is missing, so the site
// never shows blank text even if something goes wrong.
//
// Usage: call loadI18n() once per page (it fetches and caches the result), await it,
// then call applyStrings() to fill in every element tagged with data-key, and use
// projectTypeLabel() wherever a project type needs to be displayed.

const DEFAULT_STRINGS = {
  'nav.eyebrow': 'Colorist',
  'nav.work': 'Projects',
  'nav.contact': 'Contact',

  'work.heading': 'Projects',
  'work.filter_all': 'All',

  'contact.heading': 'Available for your next project.',
  'contact.email_label': 'Email',
  'contact.top': 'Back to top',
  'contact.privacy': 'Privacy',
  'contact.terms': 'Terms of use',

  'project.back': 'Back to projects',
  'project.type_label': 'Type',
  'project.client_label': 'Client',
  'project.director_label': 'Director',
  'project.dp_label': 'DP',
  'project.artist_label': 'Artist',
  'project.next_label': 'Next project',
  'project.not_found_eyebrow': 'Not found',
  'project.not_found_heading': "This project doesn't exist.",

  'lightbox.close': 'Close'
};

// Code (what data/projects.json stores) -> label shown on the cards, the filter, the footer
// and the project credits. Narrative replaced FILM and TV in Oct 2026.
const DEFAULT_TYPES = {
  AD: 'Commercial',
  MV: 'Music Video',
  NARRATIVE: 'Narrative'
};

// Live copies, overwritten by loadI18n() once data/strings.json has loaded successfully.
// Kept as separate mutable variables (not just reading DEFAULT_* directly) so an edit
// made in the admin takes effect without needing any other code to change.
let STRINGS = Object.assign({}, DEFAULT_STRINGS);
let PROJECT_TYPES = Object.assign({}, DEFAULT_TYPES);

let _i18nPromise = null; // cached so several callers on the same page share one fetch

// Resolved against this script's own URL rather than the page's (Sept 2026). The pages in
// a subfolder (privacy/, terms/) load ../i18n.js, and a page-relative 'data/strings.json'
// sent them to /privacy/data/strings.json — a 404 on every visit, after which their
// labels quietly fell back to the defaults above, ignoring anything edited in the admin.
const SELF_URL = new URL(document.currentScript ? document.currentScript.src : location.href);

// ...and carrying this script's own ?v= across onto the data file, so the strings get the
// cache-busting the rest of the site already had (Sept 2026). data/strings.json is rewritten
// by the admin, and was fetched at a bare URL that GitHub Pages serves with max-age=600 and
// no way to set a header — so an edited label kept its old value for ten minutes, and on an
// iOS tab restored from the back/forward cache the fetch never re-ran at all.
//
// The version is taken from this script's src rather than passed in from the page, because
// every page already loads i18n.js?v=N and that number is already bumped in CI. There is
// nothing to add to a page, nothing for a new page to forget, and the two can't drift: the
// strings are busted by definition whenever i18n.js is. The preloads in index.html and
// project.html carry the same ?v= (they're in the bump script's OPTIONAL_ASSETS, moved by
// the same counter) so they still match the request they exist to warm — change one of
// these without the other and the page quietly pays for two fetches.
//
// A relative reference does not inherit its base's query, so resolving against SELF_URL
// gives a clean data/strings.json and the v below is the only thing on it. If
// document.currentScript is unavailable the fallback is location.href, which carries no
// version — the URL is then simply unbusted, as it was before this change.
const STRINGS_URL = (() => {
  const url = new URL('data/strings.json', SELF_URL);
  const v = SELF_URL.searchParams.get('v');
  if (v) url.searchParams.set('v', v);
  return url.href;
})();

// Fetches data/strings.json and merges it over the defaults (a key missing from the
// file — e.g. a brand new one added later that hasn't been edited yet — just falls
// back to its default rather than disappearing). Safe to call more than once per page.
function loadI18n() {
  if (_i18nPromise) return _i18nPromise;
  _i18nPromise = fetch(STRINGS_URL)
    .then((r) => r.json())
    .then((data) => {
      if (data.strings) STRINGS = Object.assign({}, DEFAULT_STRINGS, data.strings);
      if (data.types) PROJECT_TYPES = Object.assign({}, DEFAULT_TYPES, data.types);
    })
    .catch((err) => {
      console.error('Impossible de charger data/strings.json, valeurs par défaut utilisées:', err);
    });
  return _i18nPromise;
}

// Fills every element tagged data-key="..." with the matching STRINGS entry. Call once
// per page, after loadI18n() resolves.
function applyStrings() {
  document.querySelectorAll('[data-key]').forEach((el) => {
    const text = STRINGS[el.dataset.key];
    if (typeof text === 'string' && text) el.textContent = text;
  });
}

function projectTypeLabel(code) {
  const label = PROJECT_TYPES[code];
  return typeof label === 'string' && label ? label : (code || '');
}

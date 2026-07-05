// i18n.js — shared across index.html, project.html, intake-form.html, and admin/index.html.
//
// Everything editable from the admin's "Textes du site" panel lives in data/strings.json:
// general UI copy (nav labels, headings, form labels) plus project type acronyms/labels.
// The constants below are the fallback defaults, used if that fetch fails or a key is
// missing, so the site never shows blank text even if something goes wrong.
//
// Usage: call loadI18n() once per page (it fetches and caches the result), await it,
// then call applyStrings() to fill in every element tagged with data-key, and use
// projectTypeAcronym()/projectTypeLabel() wherever a project type needs to be displayed.

const DEFAULT_STRINGS = {
  'nav.eyebrow': { fr: 'Coloriste', en: 'Colorist' },
  'nav.work': { fr: 'Projets', en: 'Projects' },
  'nav.info': { fr: 'Info', en: 'Info' },
  'nav.contact': { fr: 'Contact', en: 'Contact' },

  'work.heading': { fr: 'Projets', en: 'Projects' },
  'work.filter_all': { fr: 'Tous', en: 'All' },

  'contact.heading': { fr: 'Disponible pour vos prochains projets.', en: 'Available for your next project.' },
  'contact.email_label': { fr: 'Courriel', en: 'Email' },
  'contact.location_label': { fr: 'Localisation', en: 'Location' },

  'project.back': { fr: 'Retour aux travaux', en: 'Back to work' },
  'project.type_label': { fr: 'Type', en: 'Type' },
  'project.director_label': { fr: 'Réalisation', en: 'Director' },
  'project.dp_label': { fr: 'Image', en: 'DP' },
  'project.artist_label': { fr: 'Artiste', en: 'Artist' },
  'project.not_found_eyebrow': { fr: 'Introuvable', en: 'Not found' },
  'project.not_found_heading': { fr: "Ce projet n'existe pas ou plus.", en: "This project doesn't exist." },

  'lightbox.close': { fr: 'Fermer', en: 'Close' },

  'intake.eyebrow': { fr: 'Nouveau projet', en: 'New project' },
  'intake.heading': { fr: 'Parlons de votre projet', en: 'Tell me about your project' },
  'intake.subheading': { fr: 'Quelques informations pour démarrer, on précise le reste ensemble par la suite.', en: "A few details to get started, we'll figure out the rest together." },
  'intake.name_label': { fr: 'Nom', en: 'Name' },
  'intake.email_label': { fr: 'Courriel', en: 'Email' },
  'intake.type_label': { fr: 'Type de projet', en: 'Project type' },
  'intake.description_label': { fr: 'Décris ton projet', en: 'Describe your project' },
  'intake.description_placeholder': { fr: 'Caméra, logiciel de montage, livrables, VFX... tout ce qui aide à comprendre le projet.', en: 'Camera, editing software, deliverables, VFX... anything that helps understand the project.' },
  'intake.date_label': { fr: 'Date de livraison souhaitée', en: 'Desired delivery date' },
  'intake.submit': { fr: 'Envoyer', en: 'Send' }
};

const DEFAULT_TYPES = {
  AD:   { enAcronym: 'AD',   frAcronym: 'PUB',  enLabel: 'Advertising', frLabel: 'Publicité' },
  MV:   { enAcronym: 'MV',   frAcronym: 'CLIP', enLabel: 'Music Video', frLabel: 'Vidéoclip' },
  FILM: { enAcronym: 'FILM', frAcronym: 'FILM', enLabel: 'Film',        frLabel: 'Film' },
  TV:   { enAcronym: 'TV',   frAcronym: 'TV',   enLabel: 'TV',          frLabel: 'Série' }
};

// Live copies, overwritten by loadI18n() once data/strings.json has loaded successfully.
// Kept as separate mutable variables (not just reading DEFAULT_* directly) so an edit
// made in the admin takes effect without needing any other code to change.
let STRINGS = Object.assign({}, DEFAULT_STRINGS);
let PROJECT_TYPES = Object.assign({}, DEFAULT_TYPES);

let _i18nPromise = null; // cached so several callers on the same page share one fetch

// Fetches data/strings.json and merges it over the defaults (a key missing from the
// file — e.g. a brand new one added later that hasn't been edited yet — just falls
// back to its default rather than disappearing). Safe to call more than once per page.
function loadI18n() {
  if (_i18nPromise) return _i18nPromise;
  _i18nPromise = fetch('data/strings.json')
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

// Fills every element tagged data-key="..." with the matching STRINGS entry, using
// whichever of data-fr/data-en is also present on that same element to pick fr vs en
// — the same pairing pattern already used for the language toggle everywhere on the
// site. Call once per page, after loadI18n() resolves.
function applyStrings() {
  document.querySelectorAll('[data-key]').forEach((el) => {
    const entry = STRINGS[el.dataset.key];
    if (!entry) return;
    if (el.hasAttribute('data-fr') && entry.fr) el.textContent = entry.fr;
    else if (el.hasAttribute('data-en') && entry.en) el.textContent = entry.en;
  });
  // Placeholder text (e.g. the intake form's textarea) can't live in a data-fr/data-en
  // span since it's an attribute, not content — data-placeholder-key elements get their
  // data-fr-placeholder/data-en-placeholder attributes updated instead.
  document.querySelectorAll('[data-placeholder-key]').forEach((el) => {
    const entry = STRINGS[el.dataset.placeholderKey];
    if (!entry) return;
    if (entry.fr) el.dataset.frPlaceholder = entry.fr;
    if (entry.en) el.dataset.enPlaceholder = entry.en;
  });
}

function projectTypeAcronym(code, isFr) {
  const t = PROJECT_TYPES[code];
  if (!t) return code || '';
  return isFr ? t.frAcronym : t.enAcronym;
}

function projectTypeLabel(code, isFr) {
  const t = PROJECT_TYPES[code];
  if (!t) return code || '';
  return isFr ? t.frLabel : t.enLabel;
}

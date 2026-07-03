// Catégories de type de projet, communes à tout le site.
// Clé = code canonique stocké dans data/projects.json et les formulaires.
//
// Loaded via <script src="types.js"> on index.html, project.html, intake-form.html,
// and admin/index.html. Used for: the type tag on work-grid cards, the Type field on
// project pages, the Project Type <select> on the intake form, and the type shown in
// each project row in the admin dashboard.
const PROJECT_TYPES = {
  AD:   { enAcronym: 'AD',   frAcronym: 'PUB',  enLabel: 'Advertising', frLabel: 'Publicité' },
  MV:   { enAcronym: 'MV',   frAcronym: 'CLIP', enLabel: 'Music Video', frLabel: 'Vidéoclip' },
  FILM: { enAcronym: 'FILM', frAcronym: 'FILM', enLabel: 'Film',        frLabel: 'Film' },
  TV:   { enAcronym: 'TV',   frAcronym: 'TV',   enLabel: 'TV',          frLabel: 'Série' },
  WEB:  { enAcronym: 'WEB',  frAcronym: 'WEB',  enLabel: 'Web',         frLabel: 'Web' }
};

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

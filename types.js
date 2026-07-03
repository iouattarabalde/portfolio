// Catégories de type de projet, communes à tout le site.
// Clé = code canonique stocké dans data/projects.json et les formulaires.
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

# ismaelob.com

Portfolio d'Ismael OB, coloriste basé à Montréal. Site statique, hébergé sur GitHub Pages,
sans build step ni dépendances npm — tout ce qui n'est pas HTML/CSS/JS maison (polices,
ffmpeg.wasm) est chargé depuis un CDN au moment de l'exécution.

## Structure

| Fichier / dossier | Rôle |
|---|---|
| `index.html` | Page principale : hero reel, grille de travaux (construite dynamiquement depuis `data/projects.json`), section contact |
| `project.html` | Gabarit unique pour tous les projets. Se remplit via l'URL `project.html?project=<id>`, lit `data/projects.json` |
| `data/projects.json` | Source de vérité pour tous les projets : titre, type, réalisation, DP, vignette, galerie ordonnée |
| `data/settings.json` | Coordonnées éditables : courriel, localisation (FR/EN), disponibilité (FR/EN), Instagram |
| `data/strings.json` | **Tous les autres textes du site** : libellés de navigation, titres, textes de formulaire (bilingue FR/EN), et les acronymes/libellés de chaque type de projet |
| `i18n.js` | Charge `data/strings.json`, avec des valeurs par défaut intégrées en repli. Fournit `applyStrings()` (remplit tout élément `data-key`) et `projectTypeAcronym()`/`projectTypeLabel()`. Partagé par toutes les pages, y compris l'admin |
| `intake-form.html` | Formulaire "Contact" (5 champs), envoie par mailto, pas de backend |
| `admin/index.html` | Outil d'auto-gestion — voir section dédiée plus bas |
| `style.css` | Feuille de style partagée, versionnée en cache-buster (`?v=7`, actuellement) |
| `video/reel.mp4` | Reel auto-hébergé |
| `assets/` | Stills et vignettes des projets |
| `.nojekyll`, `robots.txt`, `CNAME` | Housekeeping GitHub Pages (désactive Jekyll, bloque l'indexation de `/admin/`, domaine custom) |

## Navigation

**Work** → `#work` · **Info** → `#contact` · **Contact** → `intake-form.html`
(le libellé "Contact" pointe vers le formulaire, pas vers la section coordonnées, qui elle s'appelle "Info")

## Catégories de projet

| | EN | FR |
|---|---|---|
| Advertising | AD | PUB |
| Music Video | MV | CLIP |
| Film | FILM | FILM |
| TV | TV | Série |
| Web | WEB | WEB |

Le code canonique (AD/MV/FILM/TV/WEB) est ce qui est stocké dans `data/projects.json` ;
l'acronyme et le libellé affichés changent selon la langue active, via `data/strings.json`
(section "types"). Éditables dans l'admin, sous "Textes du site → Types de projet".

## Pages projet

Galerie de stills en haut (cliquables pour agrandir en lightbox), infos condensées en bas
(Type, Réalisation, DP seulement — pas de Client/Année/Étalonnage, puisque l'étalonnage
est toujours Ismael OB).

**Règles à respecter pour chaque projet** (imposées structurellement dans l'admin) :
- Le nombre de stills doit toujours être un multiple de 3 (aligné sur la grille 3 colonnes)
- La vignette de la page d'accueil doit être une image distincte, absente de la galerie

## Bilinguisme et textes éditables

Anglais par défaut, français activé via le bouton FR/EN (mémorisé en `localStorage`,
partagé entre les pages). Tout le texte du site — navigation, titres, étiquettes de
formulaire, types de projet — vient de `data/strings.json` et est éditable dans l'admin
sous "Textes du site", sans toucher au code.

Mécanique : chaque élément bilingue dans le HTML a une paire `<span data-fr data-key="...">`
/ `<span data-en data-key="...">`. Au chargement, `applyStrings()` (dans `i18n.js`) va
chercher la valeur correspondante dans `data/strings.json` et remplit les deux spans ; le
CSS n'affiche que celui qui correspond à la langue active. Si `data/strings.json` est
absent ou qu'une clé manque, les valeurs par défaut intégrées à `i18n.js` prennent le relais
— le site ne se retrouve jamais avec du texte vide.

Ajouter un nouveau texte bilingue quelque part sur le site demande trois choses : une entrée
dans `DEFAULT_STRINGS` (`i18n.js`), la même entrée dans `data/strings.json`, et les deux
`<span data-key="...">` dans le HTML. Pour qu'il soit aussi éditable dans l'admin, ajouter
une ligne dans `STRING_GROUPS` (`admin/index.html`).

## Admin (`ismaelob.com/admin/`)

Outil d'auto-gestion, non listé dans la nav, non indexé (`robots.txt`). Communique
directement avec l'API GitHub depuis le navigateur (token collé une fois, gardé en
`localStorage`), donc chaque sauvegarde commit directement dans le repo — le site se
met à jour tout seul via GitHub Pages, en général en moins d'une minute.

Permet de :
- Modifier tous les textes du site — coordonnées, navigation, titres, formulaire, et les
  acronymes/libellés de chaque type de projet, en français et en anglais
- Ajouter / modifier / supprimer des projets (titre, type, réalisation, DP)
- Rechercher/filtrer la liste de projets par titre ou type
- Ouvrir un projet sur le site en direct depuis sa ligne ("Voir")
- Glisser-déposer pour réordonner les projets sur la page d'accueil (sauvegarde automatique)
- Uploader des images, compressées automatiquement (canvas, 1920px max, JPEG qualité 0.85)
- Glisser-déposer pour réordonner la galerie d'un projet
- Remplacer le reel principal — compression vidéo H.264 dans le navigateur via ffmpeg.wasm
  (version mono-thread `core-st`, seule à fonctionner sur GitHub Pages sans les en-têtes
  serveur COOP/COEP qu'on ne peut pas y configurer ; plus lente qu'un ffmpeg normal,
  peut prendre plusieurs minutes selon la longueur du fichier)
- Annuler le dernier changement sur les projets (relit l'historique Git de `projects.json`
  et republie la version précédente comme nouveau commit — ne touche pas aux images)

Pas de bouton "dupliquer" un projet — volontairement retiré, "+ Nouveau projet" suffit.

## Ajouter/modifier un projet

Le plus simple : `ismaelob.com/admin/`. Sinon, éditer `data/projects.json` à la main et
ajouter les images dans `assets/`.

## Historique

Le site utilisait auparavant une page HTML statique dupliquée par projet
(`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` +
gabarit unique) pour permettre l'auto-gestion via `admin/`. Le fichier `types.js` (types
de projet seulement) a ensuite été remplacé par `i18n.js`, qui couvre tous les textes du
site via `data/strings.json`.

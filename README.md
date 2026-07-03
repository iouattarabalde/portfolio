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
| `data/settings.json` | Coordonnées éditables : courriel, localisation (FR/EN), disponibilité (FR/EN), Instagram — lues par la section contact de `index.html` et par le mailto d'`intake-form.html` |
| `types.js` | Mapping bilingue des types de projet (AD/PUB, MV/CLIP, FILM, TV/Série, WEB), partagé par toutes les pages |
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
l'acronyme et le libellé affichés changent selon la langue active, via `types.js`.

## Pages projet

Galerie de stills en haut (cliquables pour agrandir en lightbox), infos condensées en bas
(Type, Réalisation, DP seulement — pas de Client/Année/Étalonnage, puisque l'étalonnage
est toujours Ismael OB).

**Règles à respecter pour chaque projet** (imposées structurellement dans l'admin) :
- Le nombre de stills doit toujours être un multiple de 3 (aligné sur la grille 3 colonnes)
- La vignette de la page d'accueil doit être une image distincte, absente de la galerie

## Bilinguisme

Anglais par défaut, français activé via le bouton FR/EN (mémorisé en `localStorage`,
partagé entre les pages). Tout le texte statique est écrit deux fois inline
(`<span data-fr>`/`<span data-en>`, voir le commentaire en haut de `style.css`) ; le texte
généré dynamiquement (types de projet, formulaire) est géré en JS pour la même raison.

## Admin (`ismaelob.com/admin/`)

Outil d'auto-gestion, non listé dans la nav, non indexé (`robots.txt`). Communique
directement avec l'API GitHub depuis le navigateur (token collé une fois, gardé en
`localStorage`), donc chaque sauvegarde commit directement dans le repo — le site se
met à jour tout seul via GitHub Pages, en général en moins d'une minute.

Permet de :
- Modifier les coordonnées du site (courriel, localisation, disponibilité, Instagram)
- Ajouter / modifier / supprimer des projets (titre, type, réalisation, DP)
- Dupliquer un projet existant (réutilise ses images telles quelles, à ajuster ensuite)
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

## Ajouter/modifier un projet

Le plus simple : `ismaelob.com/admin/`. Sinon, éditer `data/projects.json` à la main et
ajouter les images dans `assets/`.

## Historique

Le site utilisait auparavant une page HTML statique dupliquée par projet
(`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` +
gabarit unique) pour permettre l'auto-gestion via `admin/`.

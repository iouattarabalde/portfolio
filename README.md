# ismaelob.com

Portfolio d'Ismael OB, coloriste basé à Montréal. Site statique, hébergé sur GitHub Pages,
sans build step ni dépendances npm — tout ce qui n'est pas HTML/CSS/JS maison (les polices)
est chargé depuis un CDN au moment de l'exécution.

## Structure

| Fichier / dossier | Rôle |
|---|---|
| `index.html` | Page principale : hero reel, filtre de catégories + grille de travaux (construits dynamiquement depuis `data/projects.json`), section contact |
| `project.html` | Gabarit unique pour tous les projets. Se remplit via l'URL `project.html?project=<id>`, lit `data/projects.json` |
| `data/projects.json` | Source de vérité pour tous les projets : titre, type, réalisation, DP, vignette, galerie ordonnée |
| `data/settings.json` | Coordonnées éditables : courriel, localisation (FR/EN), disponibilité (FR/EN), Instagram |
| `data/strings.json` | **Tous les autres textes du site** : libellés de navigation, titres, textes de la page projet (bilingue FR/EN), et les acronymes/libellés de chaque type de projet |
| `i18n.js` | Charge `data/strings.json`, avec des valeurs par défaut intégrées en repli. Fournit `applyStrings()` (remplit tout élément `data-key`) et `projectTypeAcronym()`/`projectTypeLabel()`. Partagé par toutes les pages, y compris l'admin |
| `admin/index.html` | Outil d'auto-gestion — voir section dédiée plus bas |
| `style.css` | Feuille de style partagée, versionnée en cache-buster (`?v=N` — bumper ce numéro sur les 3 pages qui la chargent à chaque édition, sinon certains navigateurs gardent l'ancienne feuille en cache) |
| `video/reel.mp4` | Reel auto-hébergé |
| `assets/` | Stills et vignettes des projets |
| `.nojekyll`, `robots.txt`, `CNAME` | Housekeeping GitHub Pages (désactive Jekyll, bloque l'indexation de `/admin/`, domaine custom) |

## Navigation

**Projects** → `#work` · **Contact** → `#contact`

Le reel vit uniquement en hero sur la page d'accueil (une page dédiée a été essayée puis
retirée : jugée sans utilité par rapport au hero). Boutons superposés au reel : son et
plein écran (sur iPhone, le plein écran passe par le lecteur natif de Safari, seul
mécanisme disponible).

Pas de page de formulaire distincte : le lien "Contact" pointe directement vers la
section coordonnées de la page d'accueil (email, localisation, Instagram, photo, bio).
Un ancien formulaire (`intake-form.html`) a été retiré : sans backend, il ne faisait que
construire un lien `mailto:`, sans réel avantage sur un lien courriel direct.

## Catégories de projet

Liste actuelle (éditable dans l'admin, sous "Textes du site → Types de projet") :

| | EN | FR |
|---|---|---|
| Advertising | AD | PUB |
| Music Video | MV | CLIP |
| Film | FILM | FILM |
| TV | TV | Série |

Le code canonique est ce qui est stocké dans `data/projects.json` ; l'acronyme et le
libellé affichés changent selon la langue active, via `data/strings.json` (section
"types"). Un type peut être ajouté/retiré à tout moment dans l'admin — la liste des
catégories sur la page d'accueil (filtre) se régénère automatiquement à partir de
cette même source, jamais besoin de la toucher séparément.
Avant de retirer un type déjà utilisé par un projet existant, le réassigner d'abord
(sinon son acronyme s'affiche tel quel, sans traduction, sur ce projet).

## Filtre de catégories (page d'accueil)

Sous le titre "Projects", la liste des catégories est cliquable : "All"/"Tous" affiche
tout, chaque catégorie filtre la grille sur ce type. Généré en JS (`renderCategoryFilter`
dans `index.html`) à partir des mêmes types de projet, pas de configuration séparée.

## Pages projet

Galerie de stills en haut (cliquables pour agrandir en lightbox), infos condensées en bas
(Type, Client pour les publicités, Artiste pour les vidéoclips, Réalisation, DP — pas
d'Année ni d'Étalonnage, puisque l'étalonnage est toujours Ismael OB). Les champs Client
et Artiste sont conditionnels : l'admin ne les montre que pour le type concerné (AD ou MV),
et le site ne les affiche que s'ils sont remplis, sur la vignette (au-dessus du titre) comme
dans les crédits.

**Lightbox** : flèches à l'écran + flèches du clavier (←/→) pour naviguer entre les stills,
boucle entre la première et la dernière image. Le curseur reste normal partout dans le
lightbox sauf sur les boutons cliquables (Close, flèches).

**Règles à respecter pour chaque projet** (imposées structurellement dans l'admin) :
- Le nombre de stills doit toujours être un multiple de 3 (aligné sur la grille 3 colonnes)
- La vignette de la page d'accueil doit être une image distincte, absente de la galerie

**Note sur les fichiers orphelins** : retirer une image de la galerie d'un projet dans
l'admin (ou supprimer un projet entier) ne supprime pas le fichier de `assets/`, seulement
la référence dans `projects.json`. Ces fichiers orphelins sont inoffensifs mais s'accumulent
avec le temps ; un ménage occasionnel (comparer `assets/` aux fichiers réellement référencés
dans `projects.json`) permet de les retirer.

## Bilinguisme et textes éditables

Anglais par défaut, français activé via le bouton FR/EN (mémorisé en `localStorage`,
partagé entre les pages). Tout le texte du site — navigation, titres, étiquettes de
types de projet — vient de `data/strings.json` et est éditable dans l'admin
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
une ligne dans `STRING_GROUPS` (`admin/index.html`). Les deux fichiers doivent rester en
miroir exact (mêmes clés des deux côtés) — un désalignement ne casse rien visuellement
(repli silencieux sur la valeur par défaut ou absence du champ dans l'admin) mais vaut la
peine d'être vérifié après une modification de la liste des textes.

## Admin (`ismaelob.com/admin/`)

Outil d'auto-gestion, non listé dans la nav, non indexé (`robots.txt`). Communique
directement avec l'API GitHub depuis le navigateur (token collé une fois, gardé en
`localStorage`), donc chaque sauvegarde commit directement dans le repo — le site se
met à jour tout seul via GitHub Pages, en général en moins d'une minute.

Section "Projets" en premier sur la page (ajout, recherche, réordonnancement), "Textes
du site" ensuite. Largeur du tableau de bord : 1400px sur desktop.

Permet de :
- Ajouter / modifier / supprimer des projets (titre, type, réalisation, DP)
- Rechercher/filtrer la liste de projets par titre ou type
- Ouvrir un projet sur le site en direct depuis sa ligne ("Voir")
- Glisser-déposer pour réordonner les projets sur la page d'accueil (sauvegarde automatique)
- Uploader des images, compressées automatiquement (canvas, 1920px max, JPEG qualité 0.85)
- Glisser-déposer pour réordonner la galerie d'un projet
- Modifier tous les textes du site — coordonnées, navigation, titres, et les
  acronymes/libellés de chaque type de projet, en français et en anglais
- Annuler le dernier changement sur les projets (relit l'historique Git de `projects.json`
  et republie la version précédente comme nouveau commit — ne touche pas aux images)

Pas de bouton "dupliquer" un projet — volontairement retiré, "+ Nouveau projet" suffit.

**Le reel principal (`video/reel.mp4`) ne se change pas depuis l'admin.** Une tentative avec
ffmpeg.wasm (compression dans le navigateur) a été faite puis retirée : sa seule variante
compatible avec GitHub Pages (mono-thread, sans les en-têtes serveur COOP/COEP qu'on ne peut
pas y configurer) ne peut pas tourner dans un thread séparé, donc elle gèle l'onglet le temps
du traitement, sans limite fiable au-delà de quelques dizaines de MB. Pour remplacer le reel,
envoyer le fichier vidéo à Claude par le chat, qui le compresse avec un vrai ffmpeg côté
serveur et le publie directement.

## Ajouter/modifier un projet

Le plus simple : `ismaelob.com/admin/`. Sinon, éditer `data/projects.json` à la main et
ajouter les images dans `assets/`.

## À savoir sur le déploiement

Uploader beaucoup d'images d'un coup (un nouveau projet avec sa galerie complète, par
exemple) crée autant de commits rapprochés, un par fichier. GitHub Pages a parfois du mal
à suivre et un déploiement échoue silencieusement (le site reste sur l'ancienne version).
Si un changement récent n'apparaît pas après une minute ou deux, ce n'est généralement pas
un problème de données, un nouveau commit (n'importe lequel) suffit à relancer un
déploiement propre.

## Design du site (panneau admin)

L'admin est organisé en trois onglets (Projets, Textes du site, Design), onglet actif
mémorisé entre les visites. L'onglet "Design" édite `data/design.json`, que `design.js` (chargé
par `index.html` et `project.html`) applique en variables CSS par-dessus `style.css`.
Contrôles : couleurs (accent, fond, texte, texte secondaire, bordures, fond des panneaux),
typographie (taille du texte, taille des titres, titres de vignettes, interligne,
espacement des lettres), hero (hauteur du reel, coins du cadre), grille projets (colonnes,
espacement, ratio, padding, zoom au survol et sa durée, intensité du dégradé), galerie de
la page projet (colonnes, espacement), mise en page (espacement vertical des sections,
marges latérales, largeur de la bio), nav (hauteur, masquage au défilement) et largeur de
la photo de contact. Les contrôles responsifs ont une valeur desktop et une valeur mobile. L'aperçu est le vrai site en iframe, pleine largeur en haut de l'onglet (72vh),
mis à jour en direct via postMessage; les contrôles suivent en colonnes CSS dessous;
rien n'est publié avant "Enregistrer le design".

Points d'architecture : les breakpoints restent dans `style.css` (le JSON ne fournit que
des valeurs); chaque `var()` a un fallback égal au design d'origine, donc site intact si
`design.json` est absent ou si `design.js` échoue; toutes les valeurs sont validées dans
`design.js` (couleurs par regex, nombres bornés, ratios sur liste blanche) — impossible
d'injecter du CSS par le JSON ou par postMessage. `design.js` a son propre cache-buster
(`?v=1`) : le bumper à chaque édition du fichier. Le dernier design appliqué est mis en
cache localStorage pour éviter un flash au chargement.

## Carte de partage et favicon

`assets/og-image.jpg` (1200x630, recadré depuis un still de projet) est l'aperçu affiché
quand ismaelob.com est partagé (iMessage, LinkedIn, Slack). Pour le changer, remplacer le
fichier, mêmes dimensions. Les balises Open Graph sont dans le `<head>` de `index.html` et
`project.html` (carte générique sur les pages projet : les crawlers n'exécutent pas de JS,
donc pas de carte par projet possible sur un hébergement statique). `assets/favicon.svg`
reprend les tokens du site (fond `--bg`, monogramme `--accent`).

## Historique

Le site utilisait auparavant une page HTML statique dupliquée par projet
(`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` +
gabarit unique) pour permettre l'auto-gestion via `admin/`. Le fichier `types.js` (types
de projet seulement) a ensuite été remplacé par `i18n.js`, qui couvre tous les textes du
site via `data/strings.json`.

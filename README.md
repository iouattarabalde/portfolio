# ismaelob.com

Portfolio d'Ismael OB, coloriste basé à Montréal. Site statique, hébergé sur GitHub Pages,
sans build step ni dépendances npm — tout ce qui n'est pas HTML/CSS/JS maison (les polices)
est chargé depuis un CDN au moment de l'exécution.

## Tâches courantes — par où commencer

99 % du travail quotidien se fait dans `ismaelob.com/admin/`, pas dans le code. Ce tableau
dit où aller pour chaque tâche ; le reste du README explique le "pourquoi" en détail pour
les cas qui sortent de l'admin.

| Je veux… | Où | Note |
|---|---|---|
| Ajouter un nouveau projet | Admin → Projets → **+ Nouveau projet** | Nombre de stills = multiple de 3 |
| Modifier titre / type / réalisation / DP d'un projet | Admin → Projets → cliquer le projet | |
| Réordonner les projets sur la page d'accueil | Admin → Projets, glisser-déposer | Sauvegarde automatique |
| Réordonner ou retirer des images dans un projet | Admin → ouvrir le projet, glisser-déposer | Retirer une image ne supprime pas le fichier, voir "fichiers orphelins" plus bas |
| Recadrer/repositionner une vignette (le sujet est mal centré sur la grille) | Admin → ouvrir le projet → clique/glisse sur la vignette | Ne coupe pas l'image, ça déplace juste le point de focus utilisé pour les deux formats du site (16:9 desktop, 1:1 mobile) |
| Annuler ma dernière modif de projet | Admin → Projets → bouton **Annuler** | Ne touche pas aux images uploadées |
| Changer courriel / localisation / dispo / Instagram / bio / photo de contact | Admin → Coordonnées | |
| Changer un texte du site (nav, titres, étiquettes) | Admin → Textes du site | |
| Ajouter ou retirer un type de projet (AD, MV, etc.) | Admin → Textes du site → Types de projet | Réassigner les projets existants avant de retirer un type déjà utilisé |
| Vérifier le rendu mobile avant de publier | Admin → Design → bascule Desktop/Mobile | L'aperçu reflète aussi tes réglages non enregistrés (halo, grain, fond) |
| Ajuster l'intensité/taille/étalement du halo du reel, le grain, ou la couleur de fond | Admin → Design → curseurs en haut de l'onglet | Rien ne se publie tant que tu n'as pas cliqué Enregistrer ; Réinitialiser remet les valeurs par défaut dans l'aperçu (sans publier) |
| Mon changement n'apparaît pas sur le site en ligne | Attendre 1-2 min | Si ça persiste, tout petit changement (n'importe lequel) relance un déploiement propre |
| Remplacer le reel principal (vidéo hero) | **Pas dans l'admin** | Envoyer le fichier vidéo à Claude par le chat — nécessite un vrai réencodage |
| Changer la photo de partage (aperçu quand le lien est partagé) | **Pas dans l'admin** | Remplacer `assets/og-image.jpg` via l'éditeur de fichiers GitHub (voir plus bas), même nom, mêmes dimensions 1200×630 |
| Changer polices / mise en page | Verrouillé, pas d'éditeur admin | Demander à Claude |
| Ajouter un tout nouveau texte bilingue à un endroit du site qui n'en a pas encore | Touche 3 fichiers différents | Demander à Claude |

### Modifier un fichier directement sur GitHub, sans coder

Pour les rares cas ci-dessus marqués "pas dans l'admin" mais qui sont un simple remplacement
de fichier (comme `og-image.jpg` ou le favicon) :

1. Aller sur `github.com/iouattarabalde/portfolio`, ouvrir le dossier concerné (ex. `assets/`)
2. Cliquer le fichier à remplacer, puis l'icône crayon (éditer) ou "Upload files" en haut du dossier pour en glisser un nouveau avec **exactement le même nom**
3. En bas de page, laisser le message de commit par défaut (ou une courte description) et cliquer **Commit changes**
4. Le site se met à jour tout seul en 1-2 minutes, comme après une sauvegarde admin

Ça fonctionne pour n'importe quel fichier remplacé à l'identique (même nom, même dossier).
Dès qu'il faut *modifier du code* (pas juste remplacer un fichier), retour à Claude.

### Petit lexique

- **Commit** : un point de sauvegarde dans l'historique du repo. Chaque sauvegarde admin,
  ou chaque modif via l'éditeur GitHub, en crée un.
- **Repo** (dépôt) : le dossier de projet complet sur GitHub, avec tout son historique.
- **Déploiement** : le moment où GitHub Pages republie le site à partir du dernier commit.
  Automatique, prend en général moins d'une minute, parfois deux.
- **Cache-buster** (`?v=62`) : le `?v=N` à la fin des liens vers `style.css`. Force les
  navigateurs à retélécharger la feuille de style plutôt que de garder une vieille version
  en mémoire. Concerne seulement le code, jamais l'admin.
- **JSON** : le format des fichiers `data/*.json`. C'est le contenu du site (projets, textes,
  coordonnées) séparé du code qui l'affiche — l'admin lit et écrit ces fichiers pour vous.

---

## Structure

| Fichier / dossier | Rôle |
|---|---|
| `index.html` | Page principale : hero reel, filtre de catégories + grille de travaux (construits dynamiquement depuis `data/projects.json`), section contact |
| `project.html` | Gabarit unique pour tous les projets. Se remplit via l'URL `project.html?project=<id>`, lit `data/projects.json` |
| `data/projects.json` | Source de vérité pour tous les projets : titre, type, réalisation, DP, vignette, galerie ordonnée |
| `data/settings.json` | Coordonnées éditables : courriel, localisation (FR/EN), disponibilité (FR/EN), Instagram |
| `data/design.json` | Réglages visuels éditables depuis Admin → Design : intensité/taille/étalement du halo du reel, niveau de grain, couleur de fond. Absent = valeurs par défaut (identiques aux valeurs codées dans `style.css`) |
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

**Règles à respecter pour chaque projet** (encouragées par l'interface de l'admin, mais pas
bloquées à l'enregistrement) :
- Le nombre de stills doit toujours être un multiple de 3 (aligné sur la grille 3 colonnes) —
  un avertissement coloré s'affiche sous la galerie si ce n'est pas le cas, mais ça n'empêche
  pas de cliquer Enregistrer
- La vignette de la page d'accueil doit être une image distincte, absente de la galerie —
  simple convention portée par des champs d'upload séparés dans l'admin, rien ne vérifie
  activement qu'elles diffèrent

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

## Aperçu et réglages visuels (onglet Design de l'admin)

L'admin est organisé en trois onglets (Projets, Textes du site, Design), onglet actif
mémorisé entre les visites. L'onglet "Design" a eu un premier panneau d'édition visuelle
complet (couleurs, typographie, grille, mise en page, etc., persistées dans `data/design.json`
via un fichier `design.js`), retiré le 9 juillet 2026 : trop chargé pour l'usage réel, jugé plus
overwhelming qu'utile.

Un panneau plus ciblé l'a remplacé depuis (Aug 2026) : curseurs pour l'intensité, la taille et
l'étalement du halo du reel, le niveau de grain (anti-banding), et un sélecteur de couleur de
fond. Les changements s'appliquent en direct dans l'aperçu (le vrai site en iframe, bascule
Desktop/Mobile qui réduit l'iframe à 390px de large pour déclencher les mêmes media queries
qu'un vrai téléphone) sans rien publier. Seul un clic sur **Enregistrer** écrit dans
`data/design.json` ; **Réinitialiser** remet les valeurs par défaut dans l'aperçu, sans publier
non plus.

Les propriétés de mise en page plus larges (colonnes de grille, ratio des vignettes,
espacements, typographie, etc.) restent hors de portée de ce panneau : `style.css` garde
l'infrastructure de l'ancien éditeur complet pour elles (`var(--nom, valeur-d-origine)` plutôt
qu'une valeur en dur), mais rien ne les définit actuellement, donc leur repli fait toujours foi
et le rendu de mise en page reste strictement identique à avant — c'est noté dans le CSS même,
en cas de besoin futur d'un éditeur plus ciblé pour celles-ci aussi.

## Carte de partage et favicon

`assets/og-image.jpg` (1200x630, recadré depuis un still de projet) est l'aperçu affiché
quand ismaelob.com est partagé (iMessage, LinkedIn, Slack). Pour le changer, remplacer le
fichier, mêmes dimensions. Les balises Open Graph sont dans le `<head>` de `index.html` et
`project.html` (carte générique sur les pages projet : les crawlers n'exécutent pas de JS,
donc pas de carte par projet possible sur un hébergement statique). `assets/favicon.svg`
reprend les tokens du site (fond `--bg`, monogramme `--accent`).

## Vidéo du reel

`video/reel.mp4` (desktop, 1080p, ~3.5 Mbps, ~82 MB) et `video/reel-mobile.mp4` (mobile,
même résolution 1080p, ~1.6 Mbps, ~39 MB) : deux fichiers servis via `<source media="...">`
dans le tag `<video>` du hero (`index.html`). Le navigateur choisit une fois au chargement
selon la largeur de viewport à ce moment (seuil 700px, cohérent avec le reste du site) —
pas de changement à la volée si on redimensionne ou tourne l'écran. Les deux gardent la
piste audio (le reel démarre muet par défaut sur les deux, comme l'exige l'autoplay
navigateur; le bouton son active un vrai son sur mobile comme sur desktop).

Retranscodés le 9 juillet 2026 à partir du vrai master (`Portfolio.mov`, H.264 1080p 16
Mbps, fourni par Ismael) — remplace une première passe qui repartait par erreur d'une
version déjà compressée du reel.

Pour retranscoder : découper la source en segments de ~50s (`ffmpeg -f segment
-segment_time 50`), encoder chaque segment séparément pour rester sous la limite de temps
d'un appel d'outil, puis concaténer (`ffmpeg -f concat`). Toujours repartir du master
d'origine si disponible plutôt que d'une version déjà compressée : réencoder à partir d'un
fichier déjà compressé ne restitue pas le détail perdu, ça réduit seulement les artefacts.

## Historique

Le site utilisait auparavant une page HTML statique dupliquée par projet
(`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` +
gabarit unique) pour permettre l'auto-gestion via `admin/`. Le fichier `types.js` (types
de projet seulement) a ensuite été remplacé par `i18n.js`, qui couvre tous les textes du
site via `data/strings.json`.

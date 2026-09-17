# ismaelob.com

Portfolio d'Ismael OB, coloriste basé à Montréal. Site statique, hébergé sur GitHub Pages,
sans build step ni dépendances npm, et sans ressource externe : même les polices sont servies
par le site lui-même (dossier `fonts/`, depuis septembre 2026).

## Tâches courantes — par où commencer

99 % du travail quotidien se fait dans `ismaelob.com/admin/`, pas dans le code. Ce tableau
dit où aller pour chaque tâche ; le reste du README explique le "pourquoi" en détail pour
les cas qui sortent de l'admin.

| Je veux… | Où | Note |
|---|---|---|
| Ajouter un nouveau projet | Admin → Projets → **+ Nouveau projet** | Entre 9 et 30 stills, idéalement un multiple de 3 |
| Modifier titre / type / réalisation / DP d'un projet | Admin → Projets → cliquer le projet | |
| Réordonner les projets sur la page d'accueil | Admin → Projets, glisser une carte (au doigt : appui long) | Enregistré tout seul dès que tu arrêtes de bouger les cartes, en un seul commit ; **Annuler** dans la notification remet l'ordre d'avant |
| Ajouter, réordonner, remplacer ou retirer des images dans un projet | Admin → ouvrir le projet ; glisser des fichiers depuis le Finder sur la galerie, glisser les images pour réordonner, boutons sur chaque image | Les fichiers retirés ou remplacés sont effacés du dépôt au même enregistrement, avec leurs variantes |
| Recadrer/repositionner une vignette (le sujet est mal centré sur la grille) | Admin → ouvrir le projet → clique/glisse sur la vignette | Ne coupe pas l'image, ça déplace juste le point de focus utilisé pour les deux formats du site (16:9 desktop, 1:1 mobile) |
| Supprimer un projet | Admin → ouvrir le projet → **Supprimer le projet** | Pas de confirmation : **Annuler** dans la notification pendant 6 secondes, la suppression n'est faite qu'après |
| Utiliser une image de la galerie comme vignette | Admin → ouvrir le projet → bouton « Définir comme vignette » sur l'image | L'image quitte la galerie (une vignette n'est pas aussi dans sa galerie) |
| Changer courriel / localisation / dispo / Instagram / photo / bio de contact | Admin → Réglages | La bio est de nouveau affichée sur le site depuis la refonte de septembre 2026 |
| Changer un texte du site (nav, titres, étiquettes) | Admin → Réglages → Avancé | |
| Ajouter ou retirer un type de projet (AD, MV, etc.) | Admin → Réglages → Avancé → Types de projet | Réassigner les projets existants avant de retirer un type déjà utilisé |
| Savoir si une modification est en ligne | L'étiquette à côté de « Admin » | « Publication… » puis « En ligne ✓ » quand le site sert la nouvelle version |
| Ajuster le halo du reel, le grain ou la couleur de fond | **Pas dans l'admin** (depuis sept. 2026) | Variables `--halo-*`, `--grain-level` et `--bg` en tête de `style.css` — demander à Claude |
| Mon changement n'apparaît pas sur le site en ligne | Attendre 1-2 min | Si ça persiste, tout petit changement (n'importe lequel) relance un déploiement propre |
| Remplacer le reel principal (vidéo hero) | Terminal sur le Mac : `python3 scripts/encode_reel.py --file "master.mov"` | Ouvre une page pour choisir le grain, encode, met à jour `index.html`, puis demande avant de commit et push. Voir "Vidéo du reel" |
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
  ou chaque modif via l'éditeur GitHub, en crée **un seul**, quel que soit le nombre de
  fichiers touchés — enregistrer un projet de 12 stills, c'est un commit, pas 37.
- **Repo** (dépôt) : le dossier de projet complet sur GitHub, avec tout son historique.
- **Déploiement** : le moment où GitHub Pages republie le site à partir du dernier commit.
  Automatique, prend en général moins d'une minute, parfois deux.
- **Cache-buster** (`?v=105`) : le `?v=N` à la fin des liens vers `style.css`, `site.js` et
  `i18n.js`. Force les navigateurs à retélécharger la feuille de style et les scripts plutôt
  que de garder une vieille version en mémoire. Un seul numéro partagé par les trois fichiers,
  incrémenté automatiquement dès que l'un d'eux change, sur les trois pages qui les chargent
  (accueil, projet, admin) — voir "Automatisations" plus bas. Rien à faire à la main.
- **JSON** : le format des fichiers `data/*.json`. C'est le contenu du site (projets, textes,
  coordonnées) séparé du code qui l'affiche — l'admin lit et écrit ces fichiers pour vous.

---

## Structure

| Fichier / dossier | Rôle |
|---|---|
| `index.html` | Page principale : hero reel, filtre de catégories + grille de travaux (construits dynamiquement depuis `data/projects.json`), barre d'infos au survol, section contact |
| `project.html` | Gabarit unique pour tous les projets. Se remplit via l'URL `project.html?project=<id>`, lit `data/projects.json` |
| `data/projects.json` | Source de vérité pour tous les projets : titre, type, réalisation, DP, vignette, galerie ordonnée |
| `data/settings.json` | Coordonnées éditables : courriel, localisation (FR/EN), disponibilité (FR/EN), Instagram |
| `data/strings.json` | **Tous les autres textes du site** : libellés de navigation, titres, textes de la page projet (bilingue FR/EN), et les acronymes/libellés de chaque type de projet |
| `i18n.js` | Charge `data/strings.json`, avec des valeurs par défaut intégrées en repli. Fournit `applyStrings()` (remplit tout élément `data-key`) et `projectTypeAcronym()`/`projectTypeLabel()`. Partagé par toutes les pages, y compris l'admin. Versionné en cache-buster (`?v=N`), sur le même numéro que `style.css` et `site.js` |
| `site.js` | Comportements partagés par les trois pages (Aug 2026) : le cycle de couleur d'accent, `esc()` (échappe le texte injecté en HTML), `withViewTransition()` et `initLangToggle()`. Chacun existait auparavant en deux ou trois copies recopiées à la main. Versionné en cache-buster (`?v=N`) comme `style.css` et `i18n.js`, sur le même numéro |
| `admin/index.html` | Outil d'auto-gestion — voir section dédiée plus bas |
| `style.css` | Feuille de style partagée, versionnée en cache-buster (`?v=N`, le même numéro que `site.js` et `i18n.js`). L'incrément se fait tout seul sur les 3 pages qui la chargent à chaque modification — voir "Automatisations" |
| `video/reel.av1.mp4` | Reel auto-hébergé, **source principale** (AV1 10 bits — voir "Vidéo du reel") |
| `video/reel.mp4` | Même reel en H.264, filet de compatibilité pour Safari ≤16 / iOS ≤16 |
| `assets/` | Stills et vignettes des projets |
| `fonts/` | Les deux polices du site (Space Grotesk, IBM Plex Mono) en WOFF2, sous-ensembles latin et latin-ext, licence SIL OFL. Déclarées dans `style.css` (section « Typefaces »). Servies depuis le site plutôt que Google Fonts depuis septembre 2026 : une connexion de moins au premier chargement, et plus aucun décalage du texte quand la police arrive. Pour remplacer une police, changer aussi le nom du fichier (ces fichiers n'ont pas de cache-buster) |
| `assets/og/` | **Généré**, ne pas éditer à la main : une image de partage 1200×630 par projet |
| `project/` | **Généré**, ne pas éditer à la main : une coquille HTML par projet, qui porte les balises Open Graph que les crawlers lisent puis redirige vers la vraie page |
| `scripts/` | Scripts Python lancés par les automatisations : validation de `projects.json`, génération des coquilles de partage + du sitemap, incrément des cache-busters. Contient aussi deux scripts lancés à la main sur le Mac et pas dans la CI : l'encodage du reel (`encode_reel.py`) et le rattrapage des dimensions de stills (`backfill_gallery_dimensions.py`, idempotent — à relancer si une image est remplacée hors admin) |
| `.github/workflows/` | Les deux automatisations elles-mêmes — voir "Automatisations" plus bas |
| `sitemap.xml` | **Généré** à partir de `projects.json` |
| `.nojekyll`, `robots.txt`, `CNAME`, `favicon.ico` | Housekeeping GitHub Pages (désactive Jekyll, bloque l'indexation de `/admin/`, domaine custom, favicon de repli) |

## Navigation

**Projects** → `#work` · **Contact** → `#contact`

Le reel vit uniquement en hero sur la page d'accueil (une page dédiée a été essayée puis
retirée : jugée sans utilité par rapport au hero). Boutons superposés au reel : son et
plein écran (sur iPhone, le plein écran passe par le lecteur natif de Safari, seul
mécanisme disponible).

Pas de page de formulaire distincte : le lien "Contact" pointe directement vers la
section coordonnées de la page d'accueil. Depuis la refonte de septembre 2026, elle est
sur deux colonnes — tout le texte (titre, bio, courriel/Instagram, localisation et
disponibilité) d'un côté, la photo de l'autre — le tout limité à 1120px de large et
centré. Elle occupait toute la largeur de l'écran auparavant, ce qui laissait un grand
vide au milieu sur les grands écrans. Sous 700px, la photo passe sous le texte. La bio y
est de nouveau affichée après avoir été retirée en août 2026 ; le champ était resté
modifiable dans l'admin entre-temps.

Cliquer « Contact » (ou « Projets ») amène la section pile sous la barre de navigation :
son bord supérieur est aligné sur le bas de la barre, ni plus haut ni plus bas. La hauteur
de la barre est mesurée en JS et publiée dans `--nav-h` (elle bouge avec le chargement de
la police et le zoom du navigateur) ; `#contact` a aussi une hauteur minimale d'un écran
moins cette barre, sinon — étant la dernière section — la page se termine avant d'avoir pu
la faire monter jusque-là, et l'atterrissage dépendrait de la hauteur de la fenêtre.

La section porte aussi le pied de page du site (il n'y avait aucun `<footer>` avant) :
mention de copyright, liens vers les catégories de projets (ils appliquent le même filtre
que la barre au-dessus de la grille, puis remontent à celle-ci) et un lien "Haut de page".
Cette barre est limitée à la même largeur que les colonnes : la mention de copyright
commence donc juste sous le titre. Elle ne se termine pas au même endroit que la barre de
navigation — les deux alignements sont incompatibles, et c'est l'alignement sur le texte
qui a été retenu (voir la note dans `style.css`, section Contact).
Pas de bascule FR/EN dans le pied de page : la barre de navigation est collante et reste
visible, la sienne est donc déjà à portée de clic.

Un ancien formulaire (`intake-form.html`) a été retiré : sans backend, il ne faisait que
construire un lien `mailto:`, sans réel avantage sur un lien courriel direct.

**Retour aux projets** (sept. 2026) : sur une page projet, « ← Retour aux projets » et le lien
« Projets » de la barre de navigation reviennent en arrière dans l'historique quand la grille
y est déjà (même après plusieurs « Projet suivant »), au lieu de recharger l'accueil. La page
revient telle qu'elle a été quittée : même position dans la grille, reel au même endroit. Si
la grille n'est pas dans l'historique (lien partagé, nouvel onglet), le lien se comporte
normalement. Voir `initBackToGrid()` dans `site.js`.

## Zones tactiles

Tous les contrôles des pages publiques (navigation, bascule FR/EN, filtres de la grille,
liens courriel/Instagram, pied de page, boutons de la visionneuse) ont une zone cliquable
d'au moins 44x44px, sans que rien ne bouge visuellement : un `::before` invisible et
centré agrandit la zone autour du contrôle. Voir la section « Touch targets » à la fin de
`style.css`. Attention en ajoutant un libellé court (type de projet, lien de pied de
page) : plus le texte est court, plus sa zone déborde, et c'est ce qui peut faire se
chevaucher deux cibles voisines. L'admin n'est pas concernée (outil privé, non tactile).

Conséquence pour les catégories du pied de page : sous 480px, elles affichent les
acronymes (AD/PUB, MV/CLIP…) au lieu des libellés complets, sinon la rangée ne tient pas
sur une ligne une fois les zones tactiles agrandies. Les deux versions sont dans le HTML
et c'est le CSS qui choisit — rien à faire côté JS lors d'une rotation d'écran.
L'espacement de cette rangée diffère selon la langue (30px en anglais, 24px en français) :
les acronymes n'ont pas la même longueur, donc ni le minimum (ne pas faire se chevaucher
deux cibles) ni le maximum (tenir sur une ligne) ne tombent au même endroit. Le tableau
des valeurs est dans `style.css` — à recalculer si un acronyme change dans l'admin.

## Animations et fluidité (sept. 2026)

Toutes les durées et courbes d'animation sont des variables en tête de `style.css` (`--dur-*`,
`--ease-*`, `--reveal-*`). Quelques règles tiennent le site fluide et sont faciles à défaire
sans le savoir :

- **Couleur d'accent** : mise à jour 4 fois par seconde, et jamais pendant un défilement.
  Chaque changement oblige le navigateur à recalculer le style de toute la page (~4 ms sur un
  MacBook, davantage sur un téléphone). Voir `site.js`.
- **Parallaxe du reel** : animation CSS liée au défilement là où le navigateur la supporte, donc
  parfaitement synchronisée avec le scroll ; l'ancienne version JS ne sert plus que de repli.
- **Survol** : les effets de survol ne s'appliquent qu'aux appareils qui ont un vrai survol
  (souris, trackpad). Sur écran tactile, ils restaient « collés » après un tap.
- **Appui** : chaque bouton réagit dès qu'on appuie (léger enfoncement, ou atténuation pour les
  liens texte). Les vignettes ne s'enfoncent qu'à la souris : au doigt, presque chaque
  défilement commence sur une vignette.
- **Lightbox et changements de page** : durées et courbes propres au site plutôt que celles par
  défaut du navigateur (section « Timing for every view transition » de `style.css`).
- **Apparition au défilement** : 560 ms, 12 px de montée, décalage de 40 ms entre éléments.

Pour les visiteurs qui ont activé « Réduire les animations » dans leur système, les apparitions,
la parallaxe, les zooms, les glissements du filtre et les transitions du lightbox sont
désactivés. Restent le léger retour d'appui sur les boutons et les gestes au doigt, qui
suivent toujours le doigt mais changent d'image ou se referment sans animation.

## Catégories de projet

Liste actuelle (éditable dans l'admin, sous « Réglages → Avancé → Types de projet ») :

| Code | Acronyme EN / FR | Libellé EN / FR |
|---|---|---|
| `AD` | AD / PUB | Commercial / Publicité |
| `MV` | MV / CLIP | Music Video / Vidéoclip |
| `FILM` | FILM / FILM | Film / Film |
| `TV` | TV / TV | TV / Série |

(L'acronyme est ce qui s'affiche sur les vignettes ; le libellé est ce qui s'affiche dans
le filtre de la page d'accueil.)

Le code canonique est ce qui est stocké dans `data/projects.json` ; l'acronyme et le
libellé affichés changent selon la langue active, via `data/strings.json` (section
"types"). Un type peut être ajouté/retiré à tout moment dans l'admin — la liste des
catégories sur la page d'accueil (filtre) se régénère automatiquement à partir de
cette même source, jamais besoin de la toucher séparément.
Avant de retirer un type déjà utilisé par un projet existant, le réassigner d'abord
(sinon son acronyme s'affiche tel quel, sans traduction, sur ce projet).

## Grille de travaux (page d'accueil)

**Filtre de catégories** : une ligne de catégories séparées par des `/`, alignée à droite
juste au-dessus de la grille. "All"/"Tous" affiche tout, chaque catégorie filtre la grille
sur ce type. Il n'y a plus de titre "Projects" visible au-dessus depuis la refonte d'août
2026 — la ligne de filtres tient lieu d'en-tête à elle seule (le titre existe toujours dans
le HTML, masqué, pour les lecteurs d'écran et les moteurs de recherche). Généré en JS
(`renderCategoryFilter` dans `index.html`) à partir des mêmes types de projet, pas de
configuration séparée.

**Changer de filtre ou de langue** (sept. 2026) : la grille est construite une seule fois.
Un filtre masque les vignettes qui ne correspondent pas ; celles qui restent glissent vers leur
nouvelle place, celles qui partent s'estompent, et les nouvelles apparaissent en fondu. La
bascule FR/EN ne fait que réécrire les étiquettes. Avant, les deux reconstruisaient toute la
grille, qui disparaissait et réapparaissait d'un bloc.

**Barre d'infos** (Aug 2026, ordinateur seulement) : survoler une vignette assombrit
légèrement toutes les autres et affiche son type, son titre, ses crédits et sa position
(`06 / 32`) dans une barre noire fixée en bas de la grille. Elle remplace la légende qui
s'affichait auparavant sur la vignette elle-même. Sur tablette et téléphone, où il n'y a pas
de survol possible, cette barre n'existe pas : chaque vignette porte sa propre légende en
permanence, par-dessus un dégradé sombre.

## Pages projet

Galerie de stills en haut (cliquables pour agrandir en lightbox), infos condensées en bas
(Type, Client pour les publicités, Artiste pour les vidéoclips, Réalisation, DP — pas
d'Année ni d'Étalonnage, puisque l'étalonnage est toujours Ismael OB). Les champs Client
et Artiste sont conditionnels : l'admin ne les montre que pour le type concerné (AD ou MV),
et le site ne les affiche que s'ils sont remplis, sur la vignette (au-dessus du titre) comme
dans les crédits.

**Lightbox** : flèches à l'écran + flèches du clavier (←/→) pour naviguer entre les stills,
boucle entre la première et la dernière image. Le curseur reste normal partout dans le
lightbox sauf sur les boutons cliquables (Close, flèches). La page derrière ne défile plus
pendant que le lightbox est ouvert (sept. 2026).

Au doigt (sept. 2026), l'image suit le geste : glisser sur le côté passe à l'image voisine (ou
revient en place si le geste est trop court), glisser vers le bas referme le lightbox et
l'image rétrécit jusqu'à sa vignette, comme dans l'app Photos.

**Formats d'image mélangés** (sept. 2026) : la grille des stills ne bouge pas, quel que soit
le format des images. Chaque tuile est une boîte 16:9 fixe (carrée sous 700px) remplie en
`object-fit: cover`, donc un still 4:3 perd 25% de sa hauteur au recadrage et un 2.39 perd 26%
de sa largeur — mais l'alignement reste parfait. Contrairement à la vignette d'accueil, les
tuiles de galerie n'ont pas de point focal réglable : le recadrage est toujours centré.

Le lightbox, lui, montre chaque image entière (`object-fit: contain`). Son cadre est **fixé
par projet** et non par image : il est calculé à partir du format le plus large et du format
le plus haut de la galerie, chaque dimension prise séparément. Aucune image n'est donc réduite
par rapport à avant, mais le cadre et la bande de palette cessent de changer de taille d'une
flèche à l'autre. Dans un projet à format unique — c'est le cas des 32 projets actuels — le
cadre épouse l'image exactement, comme avant.

Cela repose sur les dimensions réelles (`w` / `h`) stockées pour chaque entrée de galerie dans
`projects.json` : l'admin les inscrit à l'upload, et `scripts/backfill_gallery_dimensions.py`
les a rattrapées une fois pour les 711 stills antérieurs. Elles ne peuvent pas être mesurées
sur les tuiles à l'affichage, parce qu'une tuile est une variante -640/-1280 dont le
redimensionnement arrondit la hauteur (1920x1080 devient 640x358 ou 640x359, soit un demi
pour cent d'écart) — assez pour que le cadre flotte de trois ou quatre pixels autour de
l'image. Une entrée sans `w`/`h` retombe sur la mesure des tuiles.

**Ouverture instantanée** (sept. 2026, Chrome et Edge) : survoler une vignette de la grille
ou la carte « Projet suivant » prépare la page projet en arrière-plan, et le clic l'affiche
aussitôt. Les autres navigateurs ignorent simplement la règle (`<script type="speculationrules">`
dans `index.html` et `project.html`).

**Projet suivant** (Aug 2026) : carte cliquable en bas de page, à droite des crédits (empilée
sous les crédits et alignée à droite sur mobile), pour sauter directement au projet suivant
sans repasser par la grille. "Suivant" = l'entrée suivante dans l'ordre de `projects.json`
(le même ordre que la grille et que le glisser-déposer de l'admin), boucle au premier projet
après le dernier. Disparaît si un seul projet existe au total. Rien à configurer dans
l'admin — entièrement dérivé de `projects.json`, comme la grille elle-même.

**Règles à respecter pour chaque projet** :
- **Bloquant** : entre 9 et 30 stills dans la galerie. En dehors de cette plage, l'admin
  refuse d'enregistrer et surligne le champ en rouge. Le site lui-même se limite à 32 projets
  au total, refusés de la même façon sur "+ Nouveau projet"
- **Simple avertissement** : le nombre de stills devrait aussi être un multiple de 3 (aligné
  sur la grille 3 colonnes). Un message coloré s'affiche sous la galerie si ce n'est pas le
  cas, mais l'enregistrement passe quand même
- **Convention non vérifiée** : la vignette de la page d'accueil doit être une image
  distincte, absente de la galerie — portée par des champs d'upload séparés dans l'admin,
  mais rien ne vérifie activement qu'elles diffèrent

**Note sur les fichiers orphelins** : retirer, remplacer ou déplacer une image, changer une
vignette ou supprimer un projet efface les fichiers concernés (et leurs variantes) dans le
même commit que le `projects.json` qui cesse de les référencer. Il ne se crée donc plus de
fichiers orphelins. Ce n'était pas le cas avant septembre 2026 : en août ils représentaient
669 fichiers et 122 MB. Le bouton **Nettoyer** qui faisait le ménage a été retiré en septembre
2026 — il n'avait plus rien à trouver, et une de ses deux utilisations avait effacé 1567
images encore servies par le site (restaurées depuis l'historique).

## Bilinguisme et textes éditables

Anglais par défaut, français activé via le bouton FR/EN (mémorisé en `localStorage`,
partagé entre les pages). Tout le texte du site — navigation, titres, étiquettes de
types de projet — vient de `data/strings.json` et est éditable dans l'admin
sous « Réglages → Avancé », sans toucher au code.

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

Une sauvegarde = **un commit**, qui regroupe tout ce qu'elle touche : la vignette, les
stills et leurs variantes responsives, `projects.json`, et les stills retirés. C'est
atomique — le commit atterrit en entier ou pas du tout, donc le dépôt ne peut jamais se
retrouver avec une image sans l'entrée qui la référence, ni l'inverse. (Jusqu'en
septembre 2026 l'admin passait par l'API Contents, qui n'écrit qu'un fichier par commit :
une soirée de curation produisait plus de deux cents commits. Voir le commentaire en tête
de la couche d'écriture dans `admin/index.html`.)

Deux onglets depuis septembre 2026, **Projets** et **Réglages**, après un tri fait sur
l'historique Git (ce qui servait vraiment) : la recherche, le tri, la vue liste, les flèches
↑/↓, le bouton d'annulation, **Nettoyer** et tout l'onglet **Design** ont été retirés.

**Projets** : une grille dans l'ordre de la page d'accueil. Cliquer une carte ouvre le
projet ; la petite flèche l'ouvre sur le site. Glisser une carte la déplace (au doigt : appui
long ; au clavier : Alt + flèches), et le nouvel ordre part en **un seul commit** quand les
cartes arrêtent de bouger — il en partait un par déplacement avant.

**L'éditeur de projet** occupe presque tout l'écran : détails et vignette à gauche, galerie à
droite, barre d'enregistrement toujours visible.
- Glisser des images depuis le Finder sur la galerie pour les ajouter, ou sur la vignette pour
  la remplacer.
- Chaque image est préparée dès qu'elle est ajoutée (une petite roue tourne sur la vignette) :
  **Enregistrer** n'a plus qu'à envoyer.
- **Un JPEG déjà prêt pour le web est envoyé tel quel**, sans recompression : 1920px de large
  au plus et 700 Ko au plus pour un still (1200px et 400 Ko pour une vignette). Les autres
  fichiers sont redimensionnés (JPEG qualité 0.9). Les variantes -640/-1280 sont toujours
  générées.
- Boutons sur chaque image : **Remplacer** (même position), **Définir comme vignette**,
  **Retirer** (avec Annuler).
- ⌘S enregistre, Échap ferme. Quitter avec des changements non enregistrés demande
  confirmation, y compris en fermant l'onglet.

**Réglages** : coordonnées en haut, types de projet et libellés du site repliés sous
« Avancé ». Un seul bouton Enregistrer, qui indique s'il reste quelque chose à enregistrer.

**Plusieurs appareils** : l'admin peut être ouvert sur le Mac et le téléphone en même temps
sans que l'un efface le travail de l'autre. Chaque enregistrement de projets est rejoué sur
la version de `projects.json` présente au moment du commit ; si le projet ouvert (ou les
réglages) a changé ailleurs entre-temps, l'admin demande avant de remplacer. En revenant sur
un onglet resté ouvert, la grille se met à jour toute seule.

**Publication** : l'étiquette à côté du titre suit chaque enregistrement jusqu'à ce que le site
en ligne serve la nouvelle version (« Publication… » puis « En ligne ✓ »).

**Token** : utiliser un token *fine-grained* limité au dépôt `portfolio`, permission
« Contents : Read and write » seulement (l'écran de connexion explique comment). Un token
classique (`ghp_…`) donne accès à tous les dépôts du compte ; l'admin le signale en bas de page.

Pas de bouton "dupliquer" un projet — volontairement retiré, "+ Nouveau projet" suffit.

**Le reel principal ne se change pas depuis l'admin**, et ce n'est pas un oubli. Trois
raisons qui se cumulent :

- Une tentative avec ffmpeg.wasm (compression dans le navigateur) a été faite puis retirée :
  sa seule variante compatible avec GitHub Pages (mono-thread, sans les en-têtes COOP/COEP
  qu'on ne peut pas y configurer) ne peut pas tourner dans un thread séparé, donc elle gèle
  l'onglet, sans limite fiable au-delà de quelques dizaines de MB.
- L'admin écrit **tout** via l'API Contents de GitHub, qui passe en base64 et plafonne autour
  de 100 MB. Un master ProRes de 4 Go ne peut tout simplement pas transiter par là.
- L'encodage prend une vingtaine de minutes de CPU. C'est un vrai calcul, pas une tâche de
  navigateur.

Le remplacement se fait donc **en local, sur le Mac, là où le master et le processeur sont
déjà** : une commande, voir "Vidéo du reel".

## Ajouter/modifier un projet

Le plus simple : `ismaelob.com/admin/`. Sinon, éditer `data/projects.json` à la main et
ajouter les images dans `assets/`.

## À savoir sur le déploiement

Uploader beaucoup d'images d'un coup (un nouveau projet avec sa galerie complète, par
exemple) ne produit plus qu'un seul commit, donc un seul déploiement. Avant, chaque
fichier partait dans son propre commit et la rafale faisait parfois échouer un
déploiement silencieusement — le site restait sur l'ancienne version.

Si malgré tout un changement récent n'apparaît pas après une minute ou deux, ce n'est
généralement pas un problème de données : un nouveau commit (n'importe lequel) suffit à
relancer un déploiement propre.

## Automatisations

Deux robots tournent sur GitHub à chaque `push` sur `main`. Ce sont eux qui produisent les
commits signés **`github-actions[bot]`** dans l'historique — c'est normal, il n'y a rien à
faire quand ils apparaissent.

| Quand | Ce qui se passe |
|---|---|
| `data/projects.json` ou une image change (donc : à chaque sauvegarde de projet dans l'admin) | `projects.json` est d'abord validé (ids uniques, fichiers réellement présents) ; si c'est bon, les coquilles de partage `project/<slug>.html`, les images `assets/og/<slug>.jpg` et `sitemap.xml` sont régénérées et commitées |
| `style.css`, `site.js` **ou** `i18n.js` change | Le cache-buster `?v=N` — un seul numéro pour les trois fichiers — est incrémenté sur `index.html`, `project.html` **et** `admin/index.html`, puis commité |

Deux détails qui ont déjà causé des ennuis et sont maintenant réglés :

- L'admin avait été oublié dans l'incrément du cache-buster et avait dérivé de 13 versions,
  ce qui pouvait lui faire servir une vieille feuille de style pendant longtemps. Les trois
  pages sont désormais incrémentées ensemble, et le script se resynchronise tout seul si
  elles divergent à nouveau.
- `site.js` et `i18n.js` n'étaient pas versionnés du tout (Sept 2026). Pendant un
  déploiement, un visiteur pouvait donc se retrouver avec une page toute neuve et une
  ancienne copie des scripts en cache : appeler une fonction qui n'existait pas encore dans
  `site.js`, ou afficher les vieux libellés d'`i18n.js`. Les deux portent maintenant le même
  `?v=N` que `style.css`.
- Les deux robots écrivent dans le même dépôt. Un `push` qui touchait à la fois `style.css`
  et une image les lançait en parallèle et l'un des deux échouait. Ils sont maintenant mis
  en file l'un derrière l'autre, et réessaient en cas de collision.

La validation est un vrai garde-fou : si `projects.json` est cassé (deux projets avec le même
id, une image référencée qui n'existe pas), le robot s'arrête avant de générer quoi que ce
soit et le lien de partage des projets n'est pas régénéré à partir de données douteuses.

## Halo, grain et couleur de fond

Réglés dans `style.css`, en tête du fichier : `--halo-intensity`, `--halo-size`,
`--halo-falloff`, `--grain-level` et `--bg`. Ils se réglaient dans l'onglet Design de l'admin
(août 2026) et étaient chargés depuis `data/design.json` sur chaque page, après le premier
affichage — le grain et le halo changeaient donc visiblement une fraction de seconde après
l'ouverture d'une page, et les pages Confidentialité/Conditions ne les recevaient jamais
(chemin relatif erroné). L'onglet a été retiré en septembre 2026, une fois le rendu fixé ; les
valeurs qu'il avait enregistrées sont maintenant écrites dans `style.css` (halo 2 / 0.5 / 1,
grain 0.4) et s'appliquent dès la première image, sur toutes les pages.

Le grain est une texture appliquée uniformément sur toute la page (`.grain-overlay`), qui a
remplacé en août 2026 les correctifs anti-banding scopés au halo du reel et au bas de la
section Contact.

Les propriétés de mise en page plus larges (colonnes de grille, ratio des vignettes,
espacements, typographie, etc.) sont écrites directement dans `style.css`. Les variables
fantômes de l'ancien éditeur visuel complet ont été retirées en août 2026 ; `git show
0538c4d` remet l'indirection en place si un éditeur redevient utile un jour.

## Carte de partage et favicon

`assets/og-image.jpg` (1200x630, recadré depuis un still de projet) est l'aperçu affiché
quand ismaelob.com est partagé (iMessage, LinkedIn, Slack). Pour le changer, remplacer le
fichier, mêmes dimensions. Les balises Open Graph sont dans le `<head>` de `index.html` et
`project.html` (carte générique sur les pages projet : les crawlers n'exécutent pas de JS,
donc pas de carte par projet possible sur un hébergement statique). `assets/favicon.svg`
reprend les tokens du site (fond `--bg`, monogramme `--accent`).

## Vidéo du reel

Deux fichiers, servis au même endroit — le navigateur prend le **premier `<source>` qu'il
sait décoder** :

| Fichier | Codec | Pour qui |
|---|---|---|
| `video/reel.av1.mp4` | AV1 10 bits | Tout le monde ou presque (Chrome, Edge, Firefox, Safari 17+) |
| `video/reel.mp4` | H.264 8 bits | Uniquement Safari ≤16 / iOS ≤16, qui ne décodent pas l'AV1 |

Le poster `assets/hero-poster.jpg` est **l'image 0 du montage**, pas une image au hasard :
elle s'affiche en noir et blanc puis passe en couleur au chargement (`#reel-video.is-ready`
dans `style.css`). Si ce n'était pas exactement l'image de départ, le passage du poster à la
lecture ferait un saut visible.

Le reel démarre muet (l'autoplay l'exige dans tous les navigateurs) ; le bouton son active un
vrai son sur mobile comme sur ordinateur. Le mix n'est jamais normalisé au réencodage — c'est
un choix artistique, on le transporte tel quel.

Tant qu'il est muet, le reel se met en pause quand il sort de l'écran et reprend quand on
remonte (sept. 2026) : sinon le navigateur continue de décoder la vidéo pendant qu'on parcourt
la grille. Avec le son activé, il continue de jouer.

Sur téléphone en portrait, le hero s'ajuste à la hauteur du reel, avec la même marge latérale
que la navigation pour garder la forme de l'écran et le halo visibles : les filtres et la
première rangée de projets sont visibles dès l'arrivée.

### Pourquoi deux fichiers, et pourquoi de l'AV1

Le reel est une image à fort grain, et le grain est exactement ce qui compresse le plus mal.
Mesuré sur le master 2026 (échantillons à trois endroits du montage) :

| Encodeur | Réglage | Débit mesuré | Taille estimée |
|---|---|---|---|
| x264 | CRF 23, tune film | 7,3 Mbps | ~166 MB |
| **AV1 10 bits** | **CRF 30** | **2,2 Mbps** | **~50 MB** |
| AV1 10 bits | CRF 35 | 1,2 Mbps | ~27 MB |

GitHub refuse tout fichier de plus de 100 MB. Autrement dit : **en H.264 seul, il est
physiquement impossible de garder ce grain.** L'ancien reel partait à 3,7 Mbps, soit environ
la moitié de ce que le grain réclamait — c'est précisément pour ça qu'il bouillait.

L'AV1 transporte le *même grain réel* pour environ un tiers des bits. C'est la seule raison
pour laquelle l'objectif de qualité tient sous la limite de GitHub. Le H.264 ne reste là que
comme filet de compatibilité.

La **synthèse de grain** (AV1 `film-grain`) a été testée et écartée : sur cette image elle ne
faisait gagner à peu près rien (1153 contre 1174 kbps) et remplaçait le vrai grain par du
grain synthétique. On encode le vrai grain, sans synthèse et sans débruitage.

Effet secondaire agréable : la plupart des visiteurs téléchargent maintenant **moins** qu'avant
(~60 MB au lieu de 89), ce qui double à peu près la marge sous le plafond de bande passante de
GitHub Pages (~100 GB/mois).

### Remplacer le reel

Une commande, dans le Terminal du Mac, depuis le dossier du site :

```bash
python3 scripts/encode_reel.py --file "chemin/vers/master.mov"
```

Astuce : taper le début de la commande, puis glisser le master depuis le Finder dans la
fenêtre du Terminal colle son chemin complet.

Le master peut rester où il est, y compris dans Google Drive. Pour un fichier de plusieurs
Go, le rendre **disponible hors ligne** avant (clic droit dans le Finder) évite que l'analyse
attende le téléchargement.

Ce qui se passe ensuite :

1. Il analyse le fichier et **calcule le CRF tout seul** : il encode des échantillons à deux
   CRF, ajuste une courbe débit/CRF, et résout pour la taille visée. Un montage plus ou moins
   granuleux obtient donc automatiquement un réglage différent — rien n'est codé en dur.
2. Il encode un extrait court **de la section la plus granuleuse** à trois CRF, extrait des
   images fixes, et **ouvre une page de comparaison à 100 %** dans le navigateur
   (`http://127.0.0.1:8765`).
3. Tu regardes, tu cliques sur un CRF. C'est la seule décision de qualité demandée.
4. Il encode l'AV1 et le H.264 en entier, extrait le poster, vérifie tout, et dépose les trois
   fichiers dans le dépôt.
5. Il écrit la bonne chaîne `codecs="av01…"` dans `index.html`.
6. Il **demande** s'il doit commit et push sur `main`. Sans « oui » explicite, rien n'est
   publié : les fichiers restent dans le dossier pour relecture.

Compter **30 à 40 minutes** pour un reel de 3 minutes sur le MacBook (extrapolé d'un test
en septembre 2026, à confirmer au premier vrai encodage), dont une pause au milieu pour
choisir le CRF. Le script empêche la mise en veille automatique (`caffeinate`), mais il faut
garder le Mac branché, le capot ouvert, et la fenêtre du Terminal ouverte.

Vérifications automatiques avant dépôt : taille sous 100 MB, atome `moov` en tête
(`+faststart`, sans quoi la lecture progressive bloque), durée conforme à la source, balises
colorimétriques bt709/tv conservées, piste audio présente. Si quoi que ce soit cloche, il
refuse de déposer et laisse les fichiers dans son dossier de travail.

Options utiles :

```bash
python3 scripts/encode_reel.py --file X --dry-run    # analyse seule, rien n'est encodé
python3 scripts/encode_reel.py --file X --pick 29    # sauter la page de comparaison
```

Installation (une seule fois) : `brew install ffmpeg`. Le script vérifie au démarrage que
ffmpeg est là et qu'il contient les deux encodeurs nécessaires (`libsvtav1`, `libx264`).

Jusqu'en septembre 2026, l'encodage tournait sur un poste Windows via une tâche planifiée qui
surveillait un dossier Google Drive (`Demos/_to-web`), avec un onglet **Reel** dans l'admin
pour suivre l'avancement à distance. Tout ça est parti avec ce poste : le reel change à peu
près une fois par an, et une commande lancée devant la machine qui travaille suffit.

### Notes

- ffmpeg vient de Homebrew (`brew install ffmpeg`). Les variables `FFMPEG_BIN` et
  `FFPROBE_BIN` permettent de pointer vers un autre build.
- Toujours repartir du master d'origine, jamais d'une version déjà compressée : réencoder
  depuis un fichier compressé ne restitue pas le détail perdu, ça ne fait que lisser les
  artefacts.
- La chaîne `codecs="av01..."` dans `index.html` doit correspondre au fichier. Si elle est
  fausse, Safari ignore l'AV1 sans rien dire et bascule sur le H.264. Le script l'écrit
  lui-même dans `index.html` à la fin de chaque encodage.
- Chaque remplacement de reel laisse l'ancien fichier dans l'historique git pour toujours. Le
  dépôt grossit donc à chaque mise à jour ; à surveiller sur la durée.

## Historique

Le site utilisait auparavant une page HTML statique dupliquée par projet
(`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` +
gabarit unique) pour permettre l'auto-gestion via `admin/`. Le fichier `types.js` (types
de projet seulement) a ensuite été remplacé par `i18n.js`, qui couvre tous les textes du
site via `data/strings.json`.

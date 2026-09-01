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
| Ajouter un nouveau projet | Admin → Projets → **+ Nouveau projet** | Entre 9 et 30 stills, idéalement un multiple de 3 |
| Modifier titre / type / réalisation / DP d'un projet | Admin → Projets → cliquer le projet | |
| Réordonner les projets sur la page d'accueil | Admin → Projets, glisser-déposer | Sauvegarde automatique |
| Réordonner ou retirer des images dans un projet | Admin → ouvrir le projet, glisser-déposer | Retirer une image ne supprime pas le fichier ; le bouton **Nettoyer** (Admin → Projets) efface ceux qui ne servent plus, voir "fichiers orphelins" plus bas |
| Recadrer/repositionner une vignette (le sujet est mal centré sur la grille) | Admin → ouvrir le projet → clique/glisse sur la vignette | Ne coupe pas l'image, ça déplace juste le point de focus utilisé pour les deux formats du site (16:9 desktop, 1:1 mobile) |
| Annuler ma dernière modif de projet | Admin → Projets → bouton **Annuler** | Ne touche pas aux images uploadées |
| Changer courriel / localisation / dispo / Instagram / photo / bio de contact | Admin → Coordonnées | La bio est de nouveau affichée sur le site depuis la refonte de septembre 2026 |
| Changer un texte du site (nav, titres, étiquettes) | Admin → Textes du site | |
| Ajouter ou retirer un type de projet (AD, MV, etc.) | Admin → Textes du site → Types de projet | Réassigner les projets existants avant de retirer un type déjà utilisé |
| Vérifier le rendu mobile avant de publier | Admin → Design → bascule Desktop/Mobile | L'aperçu reflète aussi tes réglages non enregistrés (halo, grain, fond) |
| Ajuster l'intensité/taille/étalement du halo du reel, le grain (texture appliquée sur tout le site), ou la couleur de fond | Admin → Design → curseurs en haut de l'onglet | Rien ne se publie tant que tu n'as pas cliqué Enregistrer ; Réinitialiser remet les valeurs par défaut dans l'aperçu (sans publier) |
| Mon changement n'apparaît pas sur le site en ligne | Attendre 1-2 min | Si ça persiste, tout petit changement (n'importe lequel) relance un déploiement propre |
| Remplacer le reel principal (vidéo hero) | Déposer le fichier dans Drive → `Demos/_to-web` | Depuis n'importe quelle machine. Le pipeline s'occupe du reste et ouvre une page pour valider le grain sur le poste principal. Suivi dans Admin → onglet **Reel**. Voir "Vidéo du reel" |
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
- **Cache-buster** (`?v=105`) : le `?v=N` à la fin des liens vers `style.css`. Force les
  navigateurs à retélécharger la feuille de style plutôt que de garder une vieille version
  en mémoire. Incrémenté automatiquement à chaque modification de `style.css`, sur les trois
  pages qui la chargent (accueil, projet, admin) — voir "Automatisations" plus bas. Rien à
  faire à la main.
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
| `data/design.json` | Réglages visuels éditables depuis Admin → Design : intensité/taille/étalement du halo du reel, niveau de grain, couleur de fond. Absent = valeurs par défaut (identiques aux valeurs codées dans `style.css`) |
| `data/strings.json` | **Tous les autres textes du site** : libellés de navigation, titres, textes de la page projet (bilingue FR/EN), et les acronymes/libellés de chaque type de projet |
| `i18n.js` | Charge `data/strings.json`, avec des valeurs par défaut intégrées en repli. Fournit `applyStrings()` (remplit tout élément `data-key`) et `projectTypeAcronym()`/`projectTypeLabel()`. Partagé par toutes les pages, y compris l'admin |
| `site.js` | Comportements partagés par les trois pages (Aug 2026) : le cycle de couleur d'accent, `esc()` (échappe le texte injecté en HTML), `withViewTransition()`, `initLangToggle()` et `applyDesignSettings()`. Chacun existait auparavant en deux ou trois copies recopiées à la main |
| `admin/index.html` | Outil d'auto-gestion — voir section dédiée plus bas |
| `style.css` | Feuille de style partagée, versionnée en cache-buster (`?v=N`). L'incrément se fait tout seul sur les 3 pages qui la chargent à chaque modification — voir "Automatisations" |
| `video/reel.av1.mp4` | Reel auto-hébergé, **source principale** (AV1 10 bits — voir "Vidéo du reel") |
| `video/reel.mp4` | Même reel en H.264, filet de compatibilité pour Safari ≤16 / iOS ≤16 |
| `assets/` | Stills et vignettes des projets |
| `assets/og/` | **Généré**, ne pas éditer à la main : une image de partage 1200×630 par projet |
| `project/` | **Généré**, ne pas éditer à la main : une coquille HTML par projet, qui porte les balises Open Graph que les crawlers lisent puis redirige vers la vraie page |
| `scripts/` | Scripts Python lancés par les automatisations : validation de `projects.json`, génération des coquilles de partage + du sitemap, incrément du cache-buster. Contient aussi le pipeline d'encodage du reel (`encode_reel.py` + `watch_reel_dropbox.ps1`), qui tourne en local et pas dans la CI |
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

## Catégories de projet

Liste actuelle (éditable dans l'admin, sous "Textes du site → Types de projet") :

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
lightbox sauf sur les boutons cliquables (Close, flèches).

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

**Note sur les fichiers orphelins** : retirer une image de la galerie d'un projet dans
l'admin ne supprime pas le fichier de `assets/`, seulement la référence dans `projects.json`.
(Supprimer un projet entier, en revanche, efface bien ses images.) Ces fichiers orphelins
sont invisibles sur le site mais s'accumulent : en août 2026 ils représentaient 669 fichiers
et 122 MB, presque la moitié des images du repo, hérités des galeries ramenées à 30 stills.

Le bouton **Nettoyer** (Admin → Projets) fait le ménage : il compare `assets/` aux fichiers
réellement référencés dans `projects.json` et propose d'effacer le reste. À lancer de temps
en temps, surtout après avoir beaucoup retiré d'images.

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
- Uploader des images, compressées automatiquement (canvas, JPEG qualité 0.85, taille max
  selon l'usage : 1200px pour les vignettes de projet, 1920px pour les stills de galerie,
  800px pour la photo de contact — chacune n'est jamais affichée plus grande que ça)
- Glisser-déposer pour réordonner la galerie d'un projet
- Modifier tous les textes du site — coordonnées, navigation, titres, et les
  acronymes/libellés de chaque type de projet, en français et en anglais
- Annuler le dernier changement sur les projets (relit l'historique Git de `projects.json`
  et republie la version précédente comme nouveau commit — ne touche pas aux images)

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

Le remplacement se fait donc **en local, là où le master et le processeur sont déjà**. Le
transport, lui, passe par Google Drive : déposer le master dans `Demos/_to-web` depuis
n'importe quelle machine (drive.google.com marche depuis un téléphone), et le poste principal
le récupère tout seul. Pas d'interface d'envoi à construire, pas de limite de taille, et la
reprise sur coupure est gratuite.

L'onglet **Reel** de l'admin est la moitié consultable de ce dispositif : il montre où en est
le pipeline, ce qui est en file, et **si le poste d'encodage répond encore**. Voir
"Vidéo du reel".

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

## Automatisations

Deux robots tournent sur GitHub à chaque `push` sur `main`. Ce sont eux qui produisent les
commits signés **`github-actions[bot]`** dans l'historique — c'est normal, il n'y a rien à
faire quand ils apparaissent.

| Quand | Ce qui se passe |
|---|---|
| `data/projects.json` ou une image change (donc : à chaque sauvegarde de projet dans l'admin) | `projects.json` est d'abord validé (ids uniques, fichiers réellement présents) ; si c'est bon, les coquilles de partage `project/<slug>.html`, les images `assets/og/<slug>.jpg` et `sitemap.xml` sont régénérées et commitées |
| `style.css` change | Le cache-buster `?v=N` est incrémenté sur `index.html`, `project.html` **et** `admin/index.html`, puis commité |

Deux détails qui ont déjà causé des ennuis et sont maintenant réglés :

- L'admin avait été oublié dans l'incrément du cache-buster et avait dérivé de 13 versions,
  ce qui pouvait lui faire servir une vieille feuille de style pendant longtemps. Les trois
  pages sont désormais incrémentées ensemble, et le script se resynchronise tout seul si
  elles divergent à nouveau.
- Les deux robots écrivent dans le même dépôt. Un `push` qui touchait à la fois `style.css`
  et une image les lançait en parallèle et l'un des deux échouait. Ils sont maintenant mis
  en file l'un derrière l'autre, et réessaient en cas de collision.

La validation est un vrai garde-fou : si `projects.json` est cassé (deux projets avec le même
id, une image référencée qui n'existe pas), le robot s'arrête avant de générer quoi que ce
soit et le lien de partage des projets n'est pas régénéré à partir de données douteuses.

## Aperçu et réglages visuels (onglet Design de l'admin)

L'admin est organisé en trois onglets (Projets, Textes du site, Design), onglet actif
mémorisé entre les visites. L'onglet "Design" a eu un premier panneau d'édition visuelle
complet (couleurs, typographie, grille, mise en page, etc., persistées dans `data/design.json`
via un fichier `design.js`), retiré le 9 juillet 2026 : trop chargé pour l'usage réel, jugé plus
overwhelming qu'utile.

Un panneau plus ciblé l'a remplacé depuis (Aug 2026) : curseurs pour l'intensité, la taille et
l'étalement du halo du reel, le niveau de grain, et un sélecteur de couleur de fond. Les
changements s'appliquent en direct dans l'aperçu (le vrai site en iframe, bascule
Desktop/Mobile qui réduit l'iframe à 390px de large pour déclencher les mêmes media queries
qu'un vrai téléphone) sans rien publier. Seul un clic sur **Enregistrer** écrit dans
`data/design.json` ; **Réinitialiser** remet les valeurs par défaut dans l'aperçu, sans publier
non plus.

Le grain a changé de nature en cours de route (Aug 2026) : d'abord un correctif anti-banding
scopé au halo du reel (`.halo-dither`) et au bas de la section Contact (`.bottom-glow-noise`),
il est devenu une texture appliquée uniformément sur toute la page (`.grain-overlay`), visible
sur `index.html` et `project.html`. Le curseur va maintenant jusqu'à 2.0 (au lieu de 1.0) :
au-delà de 1.0, une seconde couche de la même texture se superpose (décalée d'une demi-tuile)
pour donner un vrai surplus de densité — une opacité CSS seule plafonne à 1.0 et n'aurait rien
donné sur la moitié supérieure du curseur sans ce détour.

Les propriétés de mise en page plus larges (colonnes de grille, ratio des vignettes,
espacements, typographie, etc.) restent hors de portée de ce panneau. `style.css` gardait
pour elles l'infrastructure de l'ancien éditeur complet — une trentaine de `var(--nom,
valeur-d-origine)` que plus rien ne définissait, donc le repli faisait toujours foi. Ces
variables fantômes ont été retirées en août 2026 et leurs valeurs écrites directement : le
rendu est identique (vérifié en comparant les styles calculés à 1440/900/680/390 px), mais
le CSS est nettement plus direct à lire. Si un éditeur visuel plus ciblé redevient utile un
jour, `git show 0538c4d` remet l'indirection en place.

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

**Déposer le master dans un dossier de dépôt, c'est tout.** Deux dossiers sont surveillés,
une tâche planifiée les regarde toutes les 5 minutes :

| Dossier | Quand |
|---|---|
| `E:\_reel-dropbox` | Depuis le poste principal. Disque local, rien ne peut se synchroniser à moitié dessous. |
| `Google Drive → Color Grading → Demos → _to-web` | **Depuis n'importe quelle machine**, y compris un téléphone, via [drive.google.com](https://drive.google.com). Aucune limite de taille, et l'envoi reprend tout seul s'il est coupé. |

(Chemins modifiables via `REEL_DROP_DIR` et `REEL_DRIVE_DIR`.)

**C'est le poste principal qui encode.** Un fichier déposé pendant qu'il est éteint attend
sans rien casser ; l'encodage démarre au prochain démarrage. L'onglet **Reel** de l'admin dit
lequel des deux est le cas — voir plus bas.

Ce qui se passe ensuite, sans rien faire :

1. Le pipeline attend que le fichier ait fini de se copier (un master ProRes fait plusieurs Go)
   et refuse les fichiers cloud non téléchargés.
2. Il analyse le fichier et **calcule le CRF tout seul** : il encode des échantillons à deux
   CRF, ajuste une courbe débit/CRF, et résout pour la taille visée. Un montage plus ou moins
   granuleux obtient donc automatiquement un réglage différent — rien n'est codé en dur.
3. Il encode un extrait court **de la section la plus granuleuse** à trois CRF, extrait des
   images fixes, et **ouvre une page de comparaison à 100 %** dans le navigateur.
4. Tu regardes, tu cliques sur un CRF. C'est la seule décision demandée.
5. Il encode l'AV1 et le H.264 en entier, extrait le poster, vérifie tout, et dépose les trois
   fichiers dans le dépôt.

Il **ne commit pas et ne pousse pas** le reel : tu relis, puis tu commit toi-même. La seule
chose qu'il publie tout seul est `data/reel-status.json`, un petit fichier d'état (voir juste
en dessous) — sans quoi l'admin n'aurait rien à lire.

### Suivre l'avancement depuis n'importe où — onglet « Reel » de l'admin

`ismaelob.com/admin/` → onglet **Reel**. En lecture seule : le fichier vidéo ne transite pas
par l'admin (l'API Contents de GitHub plafonne vers 100 Mo, un master ProRes fait plusieurs
Go — c'est tout l'intérêt de passer par Drive). L'onglet affiche :

- **Où en est le pipeline** : au repos, copie en cours, analyse, *attend ton choix de CRF*,
  encodage, vérification, terminé, échec.
- **La file d'attente**, si plusieurs masters sont déposés.
- **Le reel actuellement en ligne** : tailles AV1 / H.264 / poster, format, durée.
- **Un avertissement si le poste d'encodage ne répond plus.** C'est la partie qui compte le
  plus : sans ça, « rien en attente » et « le poste est éteint, ton fichier ne sera jamais
  traité » s'afficheraient exactement pareil — et c'est précisément la question qu'on se pose
  quand on dépose un fichier depuis un portable.

Le comparatif de grain, lui, s'ouvre sur le poste principal (`http://127.0.0.1:8765`) et
n'est pas accessible à distance. L'admin signale qu'il attend, mais le choix se fait devant
l'écran du poste — c'est un jugement sur du grain à 100 %, ça ne se délègue pas à un portable.

Vérifications automatiques avant dépôt : taille sous 100 MB, atome `moov` en tête
(`+faststart`, sans quoi la lecture progressive bloque), durée conforme à la source, balises
colorimétriques bt709/tv conservées, piste audio présente. Si quoi que ce soit cloche, il
refuse de déposer et laisse les fichiers dans son dossier de travail.

En ligne de commande, si besoin :

```bash
python scripts/encode_reel.py --file "chemin/vers/master.mov"   # manuel
python scripts/encode_reel.py --file X --dry-run                # analyse seule
python scripts/encode_reel.py --file X --pick 29                # sauter la validation
```

Installation de la tâche planifiée (une seule fois) :

```
powershell -ExecutionPolicy Bypass -File scripts\watch_reel_dropbox.ps1 -Setup
```

Journal : `scripts/reel-encode.log`. **C'est le seul retour d'une tâche planifiée** — c'est là
qu'il faut regarder si un encodage semble ne pas être parti.

### Notes

- ffmpeg n'est pas installé au niveau système ; le pipeline utilise celui fourni avec Shutter
  Encoder (`C:\Program Files\Shutter Encoder\Library`). La variable `FFMPEG_BIN` permet de
  pointer ailleurs.
- Toujours repartir du master d'origine, jamais d'une version déjà compressée : réencoder
  depuis un fichier compressé ne restitue pas le détail perdu, ça ne fait que lisser les
  artefacts.
- La chaîne `codecs="av01..."` dans `index.html` doit correspondre au fichier. Si elle est
  fausse, Safari ignore l'AV1 sans rien dire et bascule sur le H.264. Le script affiche la
  bonne chaîne à la fin de chaque encodage.
- Chaque remplacement de reel laisse l'ancien fichier dans l'historique git pour toujours. Le
  dépôt grossit donc à chaque mise à jour ; à surveiller sur la durée.

## Historique

Le site utilisait auparavant une page HTML statique dupliquée par projet
(`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` +
gabarit unique) pour permettre l'auto-gestion via `admin/`. Le fichier `types.js` (types
de projet seulement) a ensuite été remplacé par `i18n.js`, qui couvre tous les textes du
site via `data/strings.json`.

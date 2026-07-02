# ismaelob.com

Portfolio d'Ismael OB, coloriste basé à Montréal. Site statique, hébergé sur GitHub Pages.

## Structure
- `index.html` — page principale (hero reel + grille de travaux, construite dynamiquement depuis `data/projects.json` + contact)
- `project.html` — gabarit unique pour tous les projets. Se remplit via l'URL `project.html?project=<id>`, lit `data/projects.json`
- `data/projects.json` — source de vérité pour tous les projets (titre, type, réalisation, DP, vignette, galerie ordonnée)
- `intake-form.html` — formulaire d'intake client (envoie par mailto, pas de backend)
- `admin/index.html` — outil d'auto-gestion (ajouter/modifier/supprimer des projets, glisser-déposer pour l'ordre de la galerie et des projets, upload + compression d'images automatique). Écrit directement dans le repo via l'API GitHub. Non listé dans la nav, non indexé (`robots.txt`), accès direct par l'URL `ismaelob.com/admin/`. Demande le token GitHub au premier chargement (stocké seulement dans le navigateur utilisé)
- `style.css` — feuille de style partagée
- `video/` — reel auto-hébergé (`reel.mp4` + `poster.jpg`)
- `assets/` — stills et vignettes des projets

Pages projet : galerie de stills en haut (cliquables pour agrandir en lightbox), infos condensées en bas (Type, Réalisation, DP seulement, pas de Client/Année/Étalonnage puisque c'est toujours Ismael OB).

**Règle** : le nombre de stills par projet doit toujours être un multiple de 3 (aligné sur la grille 3 colonnes).

**Règle** : la vignette utilisée sur la page d'accueil doit être une image distincte, absente de la galerie de la page projet. L'admin l'impose structurellement (case d'upload séparée).

## Ajouter/modifier un projet
Le plus simple : `ismaelob.com/admin/`. Sinon, éditer `data/projects.json` à la main et ajouter les images dans `assets/`.

## Historique
Le site utilisait auparavant une page HTML statique dupliquée par projet (`project-01.html`, etc.). Passé à un modèle piloté par données (`data/projects.json` + gabarit unique) pour permettre l'auto-gestion via `admin/`.

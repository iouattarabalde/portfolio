# ismaelob.com

Portfolio d'Ismael OB, coloriste basé à Montréal. Site statique, hébergé sur GitHub Pages.

## Structure
- `index.html` — page principale (hero reel + grille de travaux + contact)
- `project.html` — gabarit à dupliquer pour chacun des projets restants (project-02.html, project-03.html, etc.)
- `project-01.html` — Fleur de Peau (premier projet complété)
- `intake-form.html` — formulaire d'intake client (envoie par mailto, pas de backend)
- `style.css` — feuille de style partagée
- `assets/` — stills et médias des projets

Pages projet : galerie de stills en haut (cliquables pour agrandir en lightbox), infos condensées en bas (Type, Réalisation, DP seulement, pas de Client/Année/Étalonnage puisque c'est toujours Ismael OB).

**Règle** : le nombre de stills par projet doit toujours être un multiple de 3 (aligné sur la grille 3 colonnes). Fleur de Peau en a 18.

## À faire
1. ~~Uploader le reel sur Vimeo~~ fait
2. Dupliquer `project.html` en `project-02.html` ... `project-12.html`, remplir titre/type/réalisation/DP et ajouter les stills en galerie
3. Ajouter les stills restants dans `assets/`
4. Mettre à jour les liens `href="project.html"` dans la grille de `index.html` vers chaque page projet au fur et à mesure

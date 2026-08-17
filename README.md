# nmary.net

Site vitrine de NMARY, consultant IT indépendant en Savoie.

Site statique : du HTML et une feuille de style, sans JavaScript, sans build,
sans dépendance. Hébergé par GitHub Pages, servi sur `www.nmary.net` via le
fichier `CNAME`. Pousser sur la branche par défaut déploie.

## Structure

```
index.html                      accueil
conseil-audit.html              ┐
accompagnement-technique.html   │ pages prestation, generees
developpement-logiciel.html     │ (voir tools/)
support.html                    ┘
mentions-legales.html           pages legales, noindex
cgv.html
assets/style.css                toute la mise en forme
assets/icons.svg                sprite SVG, symboles i-*
assets/fonts/                   Space Grotesk et DM Mono, auto-hebergees
assets/og.png                   image de partage
src/og-template.html            gabarit ayant servi a produire og.png
tools/gen-prestations.py        generateur des pages prestation
robots.txt, sitemap.xml, CNAME
```

## Lancer en local

```bash
python3 -m http.server 8000
```

Puis <http://localhost:8000>. Aucune installation n'est nécessaire.

## Régénérer les pages prestation

Les quatre pages prestation partagent la même structure : hero, `Le déroulé`,
une section propre à la page, `Facturation`, `Autres prestations`, contact.
Les maintenir à la main les ferait diverger, donc elles sont produites depuis
une source unique.

**Ne modifiez pas ces quatre fichiers `.html` directement**, ils seraient
écrasés. Le contenu vit dans la liste `PAGES` de `tools/gen-prestations.py`.

```bash
python3 tools/gen-prestations.py            # écrit les quatre pages
python3 tools/gen-prestations.py --check    # vérifie sans écrire
```

Le mode `--check` sort en erreur si une page versionnée ne correspond plus à
la source. Utile avant de committer, pour attraper une retouche faite à la
main par erreur.

Le script n'est pas une étape de build : sa sortie est du HTML statique
ordinaire, versionné comme le reste. On le relance seulement quand le contenu
change.

## Conventions

**Typographie**

- Pas de tiret cadratin ni demi-cadratin (`—`, `–`). Deux-points, virgule ou
  parenthèses à la place. Le générateur refuse de produire une page qui en
  contient.
- Espace insécable avant `: ; ! ?`, comme le veut l'usage français. Le
  générateur l'insère automatiquement dans les pages qu'il produit ; sur les
  autres pages, c'est à faire à la main.
- Texte en drapeau, jamais justifié.

**Mise en page**

- Les sections sont des bandes pleine largeur qui **alternent** entre `.band`
  (fond `#F7F5EF`) et `.band-alt` (fond `#F1EDE2`). Deux bandes de même teinte
  ne doivent jamais se suivre.
- Chaque section intermédiaire s'ouvre sur un en-tête centré `.sec-head` :
  une pastille `.sec-pill` puis un titre court `.sec-title`. Les hero, eux,
  restent alignés à gauche.
- Le contenu à l'intérieur d'une bande est plafonné autour de 620px et centré.

**Couleurs et contraste**

Tout texte doit atteindre le seuil WCAG AA de 4,5:1 sur son fond.

- Texte courant `#4A4632`, gris secondaire `#5F5B47`.
- Liens `#B8410C`, survol `#EA580C`. L'orange vif `#EA580C` ne sert que pour
  les icônes et les états de survol : sur les fonds crème il ne dépasse pas
  3,5:1 et ne convient pas au texte.
- N'utilisez jamais `#8A8564` ni `#9A9578` pour du texte sous 18px.

**Piège connu : ombres et `clip-path`**

Les cartes ont des coins biseautés via `clip-path`. Une `filter: drop-shadow`
posée sur le **même** élément est découpée par ce `clip-path` et n'apparaît
pas du tout. L'ombre est donc portée par le conteneur des cartes (`.grid`,
`.faq-list`, `.presta-more`, `.contact-grid`), dont l'opacité composite est
l'union des silhouettes. Une carte isolée doit être enveloppée dans un
`.card-shell`.

**Tarifs**

Le taux jour et la grille de segmentation client sont internes et ne doivent
jamais figurer sur le site. Seul le mode de facturation est public : travail
à la journée, nombre de jours annoncé avant de commencer.

## Déploiement

Aucune action particulière : GitHub Pages publie la branche par défaut.
Comptez une à deux minutes entre le `push` et la mise en ligne.

# Le plan de composition

**Intention :** dessiner une composition **avant qu'elle ne soit produite**, pour qu'une erreur de disposition coûte un plan et jamais une génération. Le plan est aussi ce qui se montre à l'opérateur pour valider une composition sans rien produire.

**S'applique** à toute composition posée sur une grille de cases : une planche de référence, l'image d'usage d'un sujet, la maquette du parc. **Ne couvre pas** le contenu graphique — le style, la lumière et la matière n'apparaissent jamais sur un plan.

## Ce qu'est un plan, et ce qu'il n'est pas

Un plan est **plat, vu de dessus**, jamais une perspective ni un rendu. Il dit peu, volontairement : quelles cases un sujet occupe, quel sujet c'est, et — pour ce qui se pose bout à bout — quelles cases se rejoignent. Rien d'autre. On lit un plan pour attraper une faute de disposition, et une faute s'attrape plus vite sur de l'aplat que sur un dessin.

Ce qui **ne se déduit pas** s'y déclare. En particulier, **le voisinage n'est pas la connexion** : deux clôtures peuvent se toucher sans se rejoindre. Un plan qui devinerait les connexions inventerait des raccords qui n'existent pas, et le moteur irait chercher la mauvaise pièce.

## Les deux fichiers

Un plan est un couple, au même nom, rangés côte à côte :

- **le `.json`, qui EST le plan** — la déclaration, seule source ; c'est lui qu'on modifie ;
- **le `.svg`, qui n'est qu'un rendu** — produit par l'outil, jamais édité à la main.

## Le format déclaratif

```json
{
  "format": "gatebeast-composition-plan",
  "version": 1,
  "title": "OB-010 — plan de composition de l'image d'usage",
  "grid": { "columns": 7, "rows": 7 },
  "default_cell": "transparent",
  "notes": ["une ligne de commentaire affichée sous le plan"],
  "cells": [
    { "column": 2, "row": 2, "subject": "OB-010", "joins": ["e", "s"] },
    { "column": 4, "row": 6, "subject": "BT-001", "columns": 16, "rows": 10 }
  ]
}
```

- **`grid`** — la taille du plan en cases.
- **`default_cell`** — ce que porte une case dont rien n'est déclaré : `transparent`, ou le code d'un sujet, par exemple `CH-001` pour une pelouse.
- **`cells`** — une entrée par sujet posé. `column` et `row` donnent son coin haut-gauche ; `columns` et `rows` son emprise, qui vaut une case si elle n'est pas dite ; `subject` son code d'inventaire ; `joins` les bords qu'il **rejoint réellement**, à la rose des vents, absent pour un sujet qui ne se raccorde à rien.

## Les contrôles, qui bloquent

Un plan dont un contrôle échoue **n'est pas écrit**. C'est tout l'intérêt : la faute s'arrête là.

- **Aucune case occupée deux fois** — deux sujets ne se superposent pas.
- **Aucune emprise hors de la grille.**
- **Toute connexion est déclarée des deux côtés** — si une case rejoint son voisin du nord, ce voisin rejoint son voisin du sud. Une connexion à sens unique est refusée.
- **Aucune connexion vers le vide** — on ne rejoint pas un bord derrière lequel il n'y a rien.
- **Aucune case déclarée deux fois.**

L'outil signale par ailleurs, sans bloquer, deux sujets différents qui se rejoignent — un chemin qui aboutit à un portillon est un cas réel, mais il mérite d'être vu.

## Ce que le rendu montre

Une case colorée par sujet occupé, un point noir fin au centre de chaque case qui porte un tracé, et une branche de ce point vers chaque bord rejoint. Deux cases connectées font se rejoindre leurs branches en une ligne continue ; deux cases voisines non connectées laissent un vide entre leurs points. Une légende ne nomme que ce qui est réellement présent, et les notes s'affichent sous le plan, avec le compte des formes obtenues et celles qui manquent.

## Comment on s'en sert

```
python3 scripts/build-composition-plan.py <chemin/du/plan.json>
```

Le SVG est écrit à côté du JSON, sous le même nom. Pour le regarder soi-même, un agent le convertit en image matricielle dans `local/` — il ne sait pas lire un SVG :

```
rsvg-convert -z 2 -o local/apercu.png <chemin/du/plan.svg>
```

## Où vivent les plans

Le plan se range **là où ira ce qu'il prépare** : le plan de l'image d'usage de la clôture est dans `assets/poc/cloture/`, à côté de l'image à venir. Un plan est versionné ; c'est une pièce du dossier, pas un brouillon.

## Ce que l'outil ne fait pas

Il ne connaît **ni les sujets ni leurs contraintes** : il vérifie la cohérence du plan, pas que `OB-010` existe ou qu'il a bien une pièce en angle. Ce contrôle-là appartient au référentiel des sujets, et se branchera ici quand celui-ci existera.

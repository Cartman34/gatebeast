# Les artefacts publiés — le registre des adresses

**Usage :** le registre de tout ce que le projet publie. **On l'ouvre AVANT toute publication**, sans exception, puis on liste les artefacts existants pour vérifier qu'il n'en manque aucun — ce
document peut être en retard, la liste réelle fait foi. On y republie, on n'y crée jamais d'adresse neuve pour un sujet qui en a déjà une.

**Intention :** une adresse non consignée est une adresse perdue, et le suivant en crée une de plus. C'est arrivé le 2026-08-06 : la maquette du parc a reçu une seconde adresse, et **les remarques que
l'opérateur y avait posées ont été perdues** — elles vivent dans le navigateur, attachées à la page qui les a reçues. Ce registre est un document à part, et non une section du suivi : le suivi dit où
en est le travail et se réécrit sans cesse, tandis qu'une adresse est durable et doit se trouver du premier coup.

**Un artefact, un sujet, plusieurs supports possibles.** Le même artefact peut être servi à plusieurs endroits — une page Claude aujourd'hui, une adresse chez le générateur ou un hébergement propre
demain. Chaque support porte son **identifiant** quand il en a un, parce que c'est lui qui permet de republier au bon endroit ; l'adresse complète, elle, se lit et se colle.

**Quatre états, et seuls ces quatre-là.** **Vivant** : on s'en sert, il se republie. **Archivé** : plus actif, mais consultable, et son adresse reste valable — archiver n'est pas supprimer. **Clos** :
son sujet est tranché, il ne bougera plus. **À ne pas rouvrir** : un doublon créé par erreur, sur lequel on ne republie jamais ; il reste inscrit jusqu'à ce que l'opérateur le supprime, et sa ligne
disparaît alors avec lui.

## Vivants

### Index des artefacts
La porte d'entrée vers tous les autres, bâtie sur ce registre. Produit par `artefacts/index/`. Ouvert le 2026-08-04.
- Artefact Claude · `cf3f2ac3-903c-43fb-ac91-c8e0129ab949` · https://claude.ai/code/artifact/cf3f2ac3-903c-43fb-ac91-c8e0129ab949

### Suivi des sprites
L'unique endroit où se lit l'état de la production. Produit par `artefacts/suivi-sprites/build.php` depuis le 2026-08-06 ; le constructeur Python reste en place, non supprimé, tant que la version PHP
n'a pas rattrapé tout ce qu'il faisait.
- Artefact Claude · `844640e3-8d10-47d5-b74d-aca74b99f63c` · https://claude.ai/code/artifact/844640e3-8d10-47d5-b74d-aca74b99f63c

### Le plan de composition du parc
Le plan déclaré case par case, avec la remarque par case. Produit par `artefacts/parc/build.php`. Ouvert le 2026-08-05.
- Artefact Claude · `5f9bb2af-9126-44e6-b953-59afb7ab4e28` · https://claude.ai/code/artifact/5f9bb2af-9126-44e6-b953-59afb7ab4e28

### La maquette du parc
La scène montée, trois tailles de case, navigation et remarque par case. Produit par `artefacts/parc/monter.php`. Republié le 2026-08-06. **D'autres maquettes viendront, chacune avec sa propre
adresse.**
- Artefact Claude · `1a5e7074-017e-40b3-9366-005ead586562` · https://claude.ai/code/artifact/1a5e7074-017e-40b3-9366-005ead586562

### Maquette Campagne
Le plan de composition et la maquette montée de la scène 32 × 24, en **deux sections repliables** sur une seule page, chacune gardant son état de pli d'une visite à l'autre et ses propres outils de
revue. Produite par `artefacts/scene/build.php`, à partir de `artefacts/parc/build.php` et `artefacts/parc/monter.php`, tous deux devenus génériques. Ouverte le 2026-08-06.
- Artefact Claude · `9c6cbb31-5f72-4db7-a8dc-237550866ce8` · https://claude.ai/code/artifact/9c6cbb31-5f72-4db7-a8dc-237550866ce8

### Plans de composition des sujets
Tout plan déclaré sous `assets/poc/`, par découverte automatique. Produit par `artefacts/plans-de-composition/`. Ouvert le 2026-08-04.
- Artefact Claude · `21dd8a3a-aea2-484d-9202-3749e24cb8b9` · https://claude.ai/code/artifact/21dd8a3a-aea2-484d-9202-3749e24cb8b9

### Audit de l'inventaire
Les écarts entre l'inventaire et les six planches, à arbitrer ligne par ligne. Produit par `artefacts/audit-inventaire/`. En attente d'arbitrage.
- Artefact Claude · `a15caa68-3b52-4cab-a92e-4b0829b172aa` · https://claude.ai/code/artifact/a15caa68-3b52-4cab-a92e-4b0829b172aa

## Archivés

### Tour de nettoyage
Trente et un éléments relevés, un verdict par ligne. Produit par `artefacts/nettoyage/`.
- Artefact Claude · `8598d3c2-a037-4edf-af42-f2fb4447498c` · https://claude.ai/code/artifact/8598d3c2-a037-4edf-af42-f2fb4447498c

### Planches de référence
Chaque planche du monde avec son rapport noté.
- Artefact Claude · `12a098f0-aecb-4326-8d4a-e60c80802413` · https://claude.ai/code/artifact/12a098f0-aecb-4326-8d4a-e60c80802413

### Calibration de l'échelle humaine
- Artefact Claude · `044dfac1-998d-4b36-87a5-639059ddba40` · https://claude.ai/code/artifact/044dfac1-998d-4b36-87a5-639059ddba40

## Clos

### Direction artistique
L'historique de la revue, jusqu'à la validation de la direction artistique.
- Artefact Claude · `f5b1e6f7-ad28-4f72-9c41-f0a2cdfd38c5` · https://claude.ai/code/artifact/f5b1e6f7-ad28-4f72-9c41-f0a2cdfd38c5

### Son
Les essais et le plafond constaté ; la synthèse est abandonnée.
- Artefact Claude · `e0c55e5f-f179-4ef7-9338-9d2b2cc341b8` · https://claude.ai/code/artifact/e0c55e5f-f179-4ef7-9338-9d2b2cc341b8

## À ne pas rouvrir

Aucun pour l'instant. Le doublon de la maquette, créé et neutralisé le 2026-08-06, a été supprimé par l'opérateur le jour même.

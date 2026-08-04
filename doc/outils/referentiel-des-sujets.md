# Le référentiel des sujets

**Intention :** dire, dans un fichier lisible par machine, tout ce qui se dessine — types, sujets,
variantes et représentations — pour que la génération, les plans de composition et le moteur de rendu
s'y réfèrent tous et jamais entre eux. Décrit à
[rendu-en-calques.md](../conception/referentiels/technique/rendu-en-calques.md) et
[sujets-et-variantes.md](../conception/referentiels/visuel/assets/sujets-et-variantes.md).

Remplace `assets/catalogue.json`, gelé : celui-ci était construit autour de l'image et ne savait porter
ni les types, ni les contraintes de passage, ni des représentations autres qu'une sprite.

## Les trois niveaux

- **types** — ce que porte le type : son calque d'affichage, le lot de variantes exigé de tous ses
  profils, les parties qui pointent, ses formes s'il s'assemble, ses garnitures s'il en a, et son
  passage par défaut.
- **sujets** — une entrée par profil réellement inscrit à l'inventaire : le code qui fait foi, le nom
  de profil, le type, l'emprise, la hauteur (`null` quand l'inventaire n'en donne pas), et ce que le
  sujet redéfinit du type (passage, notamment).
- **variantes**, sous chaque sujet — orientation, action, forme, garniture, directions — et sous
  chaque variante ses **représentations** : la sprite n'en est qu'une, un modèle en trois dimensions
  s'ajouterait à côté sans rien changer au reste.

Le fichier ne parle jamais d'images au premier plan : une variante est une posture, une représentation
en est une réalisation possible.

## Le passage — trois niveaux d'héritage

Le passage se déclare **côté par côté** (`n`, `e`, `s`, `w`), jamais déduit d'une forme. Par défaut,
tout sujet se traverse ; un type peut renverser ce défaut pour tous ses sujets (`passage_default`) ; un
sujet peut ensuite le redéfinir **case par case** de sa propre emprise (`passage.cells`), et ne porte
que ce qu'il redéfinit — ce qu'il ne mentionne pas garde la valeur du type.

## Ce qui n'entre pas au référentiel

**Rien ne se produit sans fiche** : un sujet sans code ni emprise à l'inventaire n'entre pas ici, même
si un fichier existe déjà sur le disque. Les sondes de capacité produites avant que la chaîne n'existe
(`HU-000`, `SOL-001`, `SP-001-1`) sont listées à part, sous `_hors_referentiel`, avec la raison précise
de leur absence — jamais un code ou une emprise fabriqués pour les y faire entrer. Leurs types, eux,
sont bien déclarés : un type n'a pas besoin d'un sujet produit pour exister.

## Le contrôleur

```
python3 scripts/check-sujets.py
```

Il **refuse** un fichier non conforme au modèle décidé (format, types inconnus, forme invalide, emprise
absente, garniture non déclarée par son type, etc.) et rend un code de sortie non nul, sans rien
corriger à sa place.

Sur un fichier conforme, il affiche :

- la **valeur résolue** du passage de chaque sujet, case par case, bord par bord, avec le niveau qui
  a tranché (`type <nom>` ou `sujet`) — sans quoi l'héritage à trois niveaux resterait invisible ;
- tout **code de sujet absent de l'inventaire** — une recherche du code dans les fiches de
  `doc/conception/referentiels/visuel/inventaire/` et `creatures-temoins.md` ;
- tout **fichier d'`assets/poc/` ou `assets/cutout/` qu'aucune variante ne réclame** dans ses
  représentations. Un maître n'est jamais lui-même une représentation — seule sa livraison en est
  une — donc un maître dont la livraison est bien réclamée reste signalé pour son propre compte : ce
  n'est pas une anomalie, c'est le rappel qu'il n'est pas la donnée que le référentiel consomme.

Il ne connaît ni les images ni les pixels : la conformité d'un fichier produit (emprise mesurée,
transparence, cadrage) reste le rôle de `check-asset.py`.

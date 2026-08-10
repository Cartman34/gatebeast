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
  profils, les parties qui pointent, ses formes s'il s'assemble, ses compositions s'il en a, et son
  passage par défaut.
- **sujets** — une entrée par profil réellement inscrit à l'inventaire : le code qui fait foi, le nom
  de profil, le type, l'emprise, la hauteur, et ce que le sujet redéfinit du type (passage, notamment).
  La hauteur est un élément obligatoire de la fiche ; elle vaut `null` tant que la fiche d'inventaire du
  sujet ne l'écrit pas encore — une fiche incomplète se complète, elle ne se comble pas : on ne
  l'invente jamais depuis le référentiel.
- **variantes**, sous chaque sujet — orientation, action, forme, et les axes propres au type comme la
  composition ou le portillon d'une clôture, directions, et éventuellement une redéfinition du passage
  propre à cette variante — et sous chaque variante ses
  **représentations** : la sprite n'en est qu'une, un modèle en trois dimensions s'ajouterait à côté
  sans rien changer au reste.

Le fichier ne parle jamais d'images au premier plan : une variante est une posture, une représentation
en est une réalisation possible.

## Le passage — trois niveaux d'héritage

Le passage se déclare **côté par côté** (`n`, `e`, `s`, `w`), jamais déduit d'une forme. Par défaut,
tout sujet se traverse ; un **type** peut renverser ce défaut pour tous ses sujets (`passage_default`) ;
un **sujet** peut ensuite le redéfinir **case par case** de sa propre emprise (`passage.cells`) ; une
**variante** peut à son tour le redéfinir, avec la même forme `passage.cells`, pour sa seule posture —
chaque niveau ne porte que ce qu'il redéfinit, ce qu'il ne mentionne pas garde la valeur du niveau
au-dessus (`sujets-et-variantes.md`, « trois niveaux »).

Exemple : `OB-010`, l'axe `portillon` de la clôture — sur le modèle exact de l'axe composition, restreint
aux deux formes de ligne (`shape-ns`, `shape-ew` ; les angles n'ont pas de portillon). Il porte trois
valeurs, en anglais américain comme `shape-ew` ou `posts-1` puisqu'elles s'écrivent dans l'adresse d'un
fichier (seul le nom de l'axe reste en français, en attendant la migration générale des clés) :
`gate-none`, le panneau fermé ordinaire, défaut jamais écrit dans l'adresse ; `gate-closed`, un portillon
qui ferme comme le reste de la clôture, sans aucune redéfinition de passage ; `gate-open`, qui laisse
entrer sur la case, en ouvrant les deux côtés que sa forme relie. C'est cet état qui porte tout l'intérêt
de l'axe — sans lui, une clôture ne pourrait jamais faire autre chose que fermer. Croisé avec les deux
sens de ligne, cela fait quatre variantes possibles ; une seule est produite, `shape-ew` avec
`portillon: gate-closed` (`OB-010_shape-ew-avec-portillon.png` montre le portillon fermé), les trois
autres n'ont pas de représentation. Aucune des quatre n'est dans le lot minimal, comme les autres valeurs
de composition.

## Ce qu'un tracé doit savoir faire, ce qu'il faut en dessiner

Les types `chemin` et `cours-d-eau` **pivotent** (`rotates: true`) : plats, sans volume, le moteur peut
tourner un même dessin pour obtenir les bords qu'il ne montre pas directement. Cela sépare deux notions
qu'une première version du référentiel confondait, ce qui a laissé `CH-019` avec seulement deux formes
déclarées — l'opérateur l'a signalé (« il manque tous les autres variants !! ») :

- **`lot_v0`** dit ce qu'il **faut dessiner** : les cinq dessins de base — extrémité (`shape-n`), ligne
  (`shape-ns`), angle (`shape-ne`), trois branches (`shape-nes`), croisement (`shape-nesw`).
- **`formes_couvertes_par_rotation`** dit ce qu'une case de ce type doit **savoir accepter** : les quinze
  combinaisons de bords possibles (`n`, `e`, `s`, `w`, `ns`, `ew`, `ne`, `es`, `sw`, `nw`, `nes`, `esw`,
  `nsw`, `new`, `nesw`). Elle ne se produit jamais telle quelle : chaque dessin du lot couvre lui-même
  toutes ses rotations (un angle sert aux quatre angles, une ligne aux deux lignes, etc.), donc les cinq
  dessins suffisent à couvrir les quinze configurations.

Confondre les deux a deux effets, opposés et également faux : croire qu'il faut produire quinze images
(dix seraient des doublons par rotation), ou déclarer seulement deux ou trois dessins et croire le tracé
complet alors qu'un embranchement ou un croisement n'a personne pour se dessiner. La clôture ne pivote
pas (`rotates: false`) : chaque combinaison de bords s'y dessine séparément, elle n'a donc pas ce second
champ — son lot reste ce qu'il est.

## Les représentations d'une variante — une seule version active

Une variante peut accumuler plusieurs représentations d'un même type au fil des reprises (une nouvelle
tentative de la même posture). Elles ne sont **jamais listées à égalité** : chaque représentation porte
un `statut`, soit `"courante"` — la dernière produite, c'est elle que le jeu et les planches affichent
— soit `"anterieure"` — une version remplacée, conservée pour l'historique et jamais supprimée
(`_intention` du fichier : « rien ne se jette »). Une variante ne porte **qu'une seule** représentation
`"courante"` par type ; les versions antérieures sont plafonnées à **trois au plus** conservées, la plus
ancienne au-delà de ce nombre sortant du fichier (jamais du disque).

## Le maître, l'image numérotée et les mesures — trois données que le débranchement du catalogue exigeait

Le champ `path` d'une représentation est son **livrable** (glossaire : « le maître exporté à la définition
de livraison ; il n'est ni rogné ni retouché ») — c'est ce que le jeu affiche. Trois autres champs
complètent la représentation, tous distincts du `statut` de version et du `verdict` :

- **`maitre`** — le chemin du **maître** (glossaire : « l'image telle que le générateur l'a rendue,
  conservée pour toujours »), sous `assets/poc/`. Sans lui, rien ne relie un livrable à ce dont il est
  issu : on ne peut ni le réexporter plus finement, ni prouver qu'il n'a pas été retouché depuis. Chaque
  maître déclaré a été vérifié présent sur le disque avant d'être écrit ici.
- **`numero_image`** — le rang de l'**image** au sens du glossaire : « un fichier d'une variante, numéroté
  `frame-01`, `frame-02`… Une posture fixe n'en a qu'un, une marche en a plusieurs. » **Ce n'est pas un
  numéro de version** : deux images d'une même marche sont deux images de la même variante, prises à des
  instants différents de la même posture animée ; deux tentatives du même dessin sont deux *versions* de
  la *même* image, départagées par `statut`. Confondre les deux mettrait une reprise et une image de
  marche dans la même colonne. Toutes les représentations actuelles portent `1` : aucun sujet inventorié
  n'a encore de posture animée à plusieurs images.
- **`mesures`** — ce que l'outil de contrôle relève sur le fichier produit à l'export : sa définition en
  pixels, sa bande de contact au sol, son point de pose, son rapport hauteur/largeur, sa transparence.
  C'est ce qui permet de confronter le produit à ce que la fiche annonçait. **Aucune mesure n'existe
  encore** : `check-asset.py`, qui sait lire les pixels, ne les écrit pas encore dans ce fichier — toutes
  les représentations portent donc `"mesures": null`, en attendant que ce branchement soit fait. Une
  valeur inventée ici serait pire qu'une case vide.

## Le verdict de l'opérateur — une autre donnée que le statut de version

Le `statut` dit la **place** d'une représentation dans son historique de production ; le `verdict` dit
son **jugement** — ce que l'opérateur en a pensé en la regardant. Les deux ne se confondent pas : une
représentation peut très bien être `"courante"` (la dernière produite, celle que tout le monde regarde)
et pourtant `"ecartee"` par l'opérateur, parce qu'aucune reprise n'a encore corrigé le défaut qu'il y a
vu. Confondre les deux effacerait cette situation, pourtant fréquente : le statut ne bouge qu'à la
prochaine production, le verdict peut tomber à tout moment sur ce qui existe déjà.

Le `verdict` porte l'une de ces valeurs : `"validee"`, `"a-reprendre"`, `"ecartee"` ; son absence signifie
que l'opérateur n'a pas encore regardé cette image précise. Une reprise produit une **nouvelle**
représentation, qui repart toujours sans verdict — le jugement porte sur l'image regardée, jamais sur la
variante en général. Quand il y a un verdict de reprise ou d'écart, un `commentaire_operateur` l'accompagne,
au mot près : c'est lui qui dit pourquoi, et c'est ce qui guide la correction de la fiche ou de la
consigne. Une représentation `"ecartee"` cesse d'être montrée mais n'est jamais supprimée, comme toute
image du dépôt (`_intention` du fichier).

Exemple : `OB-010`, variante `shape-ns` avec `composition: posts-1` a deux représentations produites
pour la même posture ; la seconde tentative (`OB-010_shape-ns_posts-1-v2.png`) est la plus récente et
porte `"statut": "courante"`, la première (`OB-010_shape-ns_posts-1.png`) devient `"anterieure"`.

## Ce qui n'entre pas au référentiel

**Rien ne se produit sans fiche** : un sujet sans code ni emprise à l'inventaire n'entre pas ici, même
si un fichier existe déjà sur le disque. Les sondes de capacité produites avant que la chaîne n'existe
(`SOL-001`, `SP-001-1`) sont listées à part, sous `_outside_referential`, avec la raison précise
de leur absence — jamais un code ou une emprise fabriqués pour les y faire entrer. Leurs types, eux,
sont bien déclarés : un type n'a pas besoin d'un sujet produit pour exister.

**`HU-000` n'en fait plus partie** : l'humain a depuis sa fiche à l'inventaire et sa place au référentiel, et son image y est réclamée par un variant. La clé s'appelle `_outside_referential`, en
anglais comme les autres — cette section la nommait `_hors_referentiel`, qui n'existe nulle part dans les données (relu le 2026-08-10).

## Le contrôleur

```
python3 scripts/check-subjects.py
```

Il **refuse** un fichier non conforme au modèle décidé (format, types inconnus, forme invalide, emprise
absente, composition non déclarée par son type, etc.) et rend un code de sortie non nul, sans rien
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

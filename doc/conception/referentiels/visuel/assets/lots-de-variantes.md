# Lots de variantes

**Intention :** dire, pour chaque **type** de sujet, **quelles images il faut et combien** — de sorte qu'une commande de production se calcule au lieu de se discuter, et que le coût d'un nouveau profil soit connu d'avance.

Ce document couvre le lot exigé par type, en cible et en v0, et les règles qui évitent de produire des images inutiles. Il exclut le vocabulaire et l'adressage ([sujets et variantes](sujets-et-variantes.md)), le contenu de chaque image ([inventaire](../inventaire/README.md)) et la fabrication ([chaîne de production](chaine-de-production.md)).

## Décisions

- **Le lot est exigé par le type, et vaut pour tous ses profils** — tout profil d'un type doit le même lot : ajouter un bouleau coûte exactement ce que coûte un chêne, et ce coût est connu avant de commander. Écarté : un lot décidé profil par profil (le coût d'une carte devient imprévisible).
- **Quatre orientations pour ce qui se tourne, jamais huit d'emblée** — `south`, `north`, `west`, `east` couvrent un déplacement au clavier et coûtent deux fois moins que huit. Les quatre trois-quarts existent dans le vocabulaire et se produiront si le jeu les demande. Écarté : huit orientations dès maintenant (double la production pour un gain que la caméra en plongée montre à peine) ; une orientation unique (le personnage marcherait de côté en nous regardant).
- **Aucune image ne s'obtient par symétrie** — `west` et `east` se produisent toutes les deux. Retourner une image inverserait le côté d'où vient la lumière, alors que le soleil arrive toujours du haut à gauche, sans exception ([visuel](../index.md)). Écarté : le miroir (économise une image et fausse toute la scène).
- **L'orientation est disponible pour tout sujet ; c'est le lot qui décide lesquelles on produit** — un sujet tourné d'un quart de tour reste **le même profil**, dans une autre orientation. Bâtiments, végétation et objets isolés n'en produisent qu'une seule parce que la carte les pose d'aplomb sur ses axes et que rien ne les fait tourner ; ceux qui s'assemblent le long du sol, eux, en produisent plusieurs. Écarté : traiter un sujet tourné comme un profil distinct (multiplie les codes pour une seule apparence, et le catalogue cesse de savoir qu'il s'agit de la même chose).
- **Un sujet qui s'assemble déclare ses formes** — une clôture, un chemin, un mur ne se dessinent pas d'une seule pièce : ils se posent bout à bout. Leur type déclare la liste des **formes** dont ils ont besoin — tronçon droit, coin, extrémité, embranchement, croisement, portillon —, et chaque forme se décline ensuite en orientations comme n'importe quel sujet. Un coin n'est pas un tronçon pivoté : c'est une autre forme. Écarté : un profil par forme (perd le fait que c'est la même clôture) ; se passer de la notion de forme (rien ne permet plus de commander un virage).
- **Ce qui est plat peut être pivoté par le rendu, ce qui a du volume doit être dessiné** — un chemin vu à la verticale est éclairé presque uniformément : le moteur peut le faire tourner, donc une seule image suffit par forme. Une clôture ou un mur se dressent : les faire pivoter mettrait le soleil du mauvais côté, en contradiction avec la lumière fixe de la direction artistique ([visuel](../index.md)). Leurs orientations se dessinent donc une à une. Écarté : pivoter tout ce qui se pose au sol (une clôture éclairée à l'envers se voit immédiatement).
- **Ce sous quoi on circule se livre en deux morceaux** — un grand arbre, un porche, une passerelle livrent une partie basse et une partie haute, déclarées au catalogue ([rendu en calques](../../technique/rendu-en-calques.md)). C'est une propriété du profil, décidée à son entrée à l'inventaire.
- **Un lot se complète, il ne se refait pas** — un profil livré avec sa seule vue de repos est utilisable, le repli faisant le reste ([sujets et variantes](sujets-et-variantes.md)) ; lui ajouter plus tard ses orientations, ses actions ou une pirouette est un pur ajout. C'est ce qui permet à la v0 d'être pauvre sans être un cul-de-sac.

## Les lots par type

L'action `idle` est la vue de repos : elle existe toujours, et l'image `orientation-south_action-idle_frame-01` — toutes directions au défaut — est la **vue principale** de tout profil — celle qui sert de référence visuelle à toutes les autres. Le nombre d'images d'une action animée appartient à l'action et se fixe au premier essai.

| Type | Lot cible | Lot v0 |
|---|---|---|
| sol | 1 variante, répétable bord à bord | 1 variante |
| chemin et cours d'eau | 5 dessins de tracé — extrémité, ligne, angle, trois branches, croisement —, le moteur obtenant les autres combinaisons de bords en pivotant : 1 image par dessin | 2 dessins : ligne, angle |
| clôture et mur | les combinaisons de bords utiles, **chacune dessinée séparément** puisqu'un volume ne se pivote pas | `shape-ns` et `shape-ew` (2), les quatre angles `shape-ne`, `shape-es`, `shape-sw`, `shape-nw` (4), le portillon dans ses deux sens (2) |
| végétation | 1 variante ; 2 morceaux si l'on passe dessous | 1 variante |
| bâtiment | 1 variante ; 2 morceaux si l'on passe dessous | 1 variante |
| objet | 1 variante | 1 variante |
| humain | 4 orientations × (`idle`, `walk`) | 4 orientations en `idle` |
| créature | 4 orientations × (`idle`, `walk`), puis les actions d'évènement | 4 orientations en `idle` |
| point de passage | une série d'images, l'ondulation étant sa nature même | 1 variante en `idle` |

## Questions ouvertes

- **Le nombre d'images d'une marche** — se fixera au premier essai d'animation, une fois qu'un profil aura ses quatre orientations. Bloque : rien aujourd'hui, la v0 n'anime pas.

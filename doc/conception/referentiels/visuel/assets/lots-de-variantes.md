# Lots de variantes

**Intention :** dire, pour chaque **type** de sujet, **quelles images il faut et combien** — de sorte qu'une commande de production se calcule au lieu de se discuter, et que le coût d'un nouveau profil soit connu d'avance.

Ce document couvre le lot exigé par type, en cible et en v0, et les règles qui évitent de produire des images inutiles. Il exclut le vocabulaire et l'adressage ([sujets et variantes](sujets-et-variantes.md)), le contenu de chaque image ([inventaire](../inventaire/README.md)) et la fabrication ([chaîne de production](chaine-de-production.md)).

## Décisions

- **Le lot est exigé par le type, et vaut pour tous ses profils** — tout profil d'un type doit le même lot : ajouter un bouleau coûte exactement ce que coûte un chêne, et ce coût est connu avant de commander. Écarté : un lot décidé profil par profil (le coût d'une carte devient imprévisible).
- **Quatre orientations pour ce qui se tourne, jamais huit d'emblée** — `south`, `north`, `west`, `east` couvrent un déplacement au clavier et coûtent deux fois moins que huit. Les quatre trois-quarts existent dans le vocabulaire et se produiront si le jeu les demande. Écarté : huit orientations dès maintenant (double la production pour un gain que la caméra en plongée montre à peine) ; une orientation unique (le personnage marcherait de côté en nous regardant).
- **Aucune image ne s'obtient par symétrie** — `west` et `east` se produisent toutes les deux. Retourner une image inverserait le côté d'où vient la lumière, alors que le soleil arrive toujours du haut à gauche, sans exception ([visuel](../index.md)). Écarté : le miroir (économise une image et fausse toute la scène).
- **Le décor immobile n'a qu'une variante** — végétation, bâtiments et objets sont vus sous une caméra fixe et posés d'aplomb sur les axes de la carte : leur orientation ne varie pas. Une construction tournée autrement est un **autre profil**, avec son propre code. Écarté : quatre orientations par bâtiment (quadruple le type le plus cher, pour des vues que la carte n'utilise jamais).
- **Les sols et les chemins sont les seuls que le rendu a le droit de tourner** — une matière vue à la verticale est éclairée presque uniformément : la faire pivoter ne déplace aucune ombre visible. On produit donc **une image par forme de raccord** et le moteur les oriente. La permission s'arrête là : un sujet en volume n'est jamais tourné par le rendu. Écarté : produire chaque raccord dans ses quatre orientations (quatre fois plus d'images pour un résultat identique).
- **Ce sous quoi on circule se livre en deux morceaux** — un grand arbre, un porche, une passerelle livrent une partie basse et une partie haute, déclarées au catalogue ([rendu en calques](../../technique/rendu-en-calques.md)). C'est une propriété du profil, décidée à son entrée à l'inventaire.
- **Un lot se complète, il ne se refait pas** — un profil livré avec sa seule vue de repos est utilisable, le repli faisant le reste ([sujets et variantes](sujets-et-variantes.md)) ; lui ajouter plus tard ses orientations, ses actions ou une pirouette est un pur ajout. C'est ce qui permet à la v0 d'être pauvre sans être un cul-de-sac.

## Les lots par type

L'action `idle` est la vue de repos : elle existe toujours, et l'image `orientation-south_action-idle_frame-01` — toutes directions au défaut — est la **vue principale** de tout profil — celle qui sert de référence visuelle à toutes les autres. Le nombre d'images d'une action animée appartient à l'action et se fixe au premier essai.

| Type | Lot cible | Lot v0 |
|---|---|---|
| sol | 1 variante, répétable bord à bord | 1 variante |
| chemin | 6 formes de raccord — pleine, droite, virage, embranchement, croisement, extrémité — orientées par le rendu | 2 formes : droite, virage |
| végétation | 1 variante ; 2 morceaux si l'on passe dessous | 1 variante |
| bâtiment | 1 variante ; 2 morceaux si l'on passe dessous | 1 variante |
| objet | 1 variante | 1 variante |
| humain | 4 orientations × (`idle`, `walk`) | 4 orientations en `idle` |
| créature | 4 orientations × (`idle`, `walk`), puis les actions d'évènement | 4 orientations en `idle` |
| point de passage | une série d'images, l'ondulation étant sa nature même | 1 variante en `idle` |

## Questions ouvertes

- **Le nombre d'images d'une marche** — se fixera au premier essai d'animation, une fois qu'un profil aura ses quatre orientations. Bloque : rien aujourd'hui, la v0 n'anime pas.

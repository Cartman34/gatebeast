# Les paramètres d'un sujet — la grille, fermée

**Usage :** ce que lit qui décrit un sujet, commande une image ou juge celle qui revient. Pour chaque type, la LISTE FERMÉE de ce qu'une fiche doit fixer. Ce qui n'y est pas fixé sera inventé par le
générateur, différemment à chaque appel, et le reproche qu'on lui fera n'aura aucun fondement.

**Intention :** les paramètres existaient dans les têtes et dans les reprises, jamais dans une liste. Chacun a donc été découvert par une image ratée : la caméra d'un bâtiment le 2026-08-12 après
trois versions, le sens d'une vue de profil le même jour après deux, l'usure d'une ferme absente alors que sa fiche la décrivait, la hauteur d'une clôture écrasée au ras du sol pendant cinq versions.
À chaque fois le paramètre existait, à chaque fois rien ne l'énumérait, à chaque fois on l'a payé en générations.

**LA GRILLE EST FERMÉE, ET C'EST TOUT SON INTÉRÊT.** La règle et sa raison vivent à la méthode commune (`~/projects/conceptions/methode/execution.md`, « Une liste est fermée, ou elle ne sert à
rien ») et ne se recopient pas ici. Ce qui est propre à ce document : un paramètre qui manque **s'ajoute ici**, daté, avec l'image qui l'a révélé — jamais dans une fiche, où il resterait invisible
aux autres sujets du même type.

**Ce qu'elle ne couvre pas :** le style, la caméra, le fond et le cadrage, qui sont les mêmes pour TOUT sujet et vivent dans le socle de la consigne (`scripts/asset_common.py`, `STYLE_FR`,
`RAPPEL_CAMERA_FR`, `CADRAGE_*`). Ce document ne dit que ce qui **varie d'un sujet à l'autre**.

## Les neuf paramètres communs — tout sujet les fixe

1. **L'emprise au sol**, en cases : ce que le sujet occupe au sol, contrat dans les deux sens.
2. **Le couvert**, en cases : ce que son volume surplombe, quand il déborde de l'emprise.
3. **La hauteur**, en `TY`, dans sa fourchette : ce qui distingue une herbe d'un chêne.
4. **La matière** : de quoi c'est fait, nommé — pierre, bois, tuile, feuillage, eau, poil.
5. **La couleur** : dite en mots, et rattachée à une image de référence quand il en existe une.
6. **Le rapport au sol** : posé dessus, planté dedans, creusé en retrait, ou passant au-dessus.
7. **Ce qui pousse à son pied** : herbe, mousse, rien — et « rien » se déclare, il ne s'omet pas.
8. **L'assemblage** : le sujet rejoint-il ses voisins, et par quels bords.
9. **Le passage** : franchissable ou non, et par où.

## Ce que chaque type fixe en plus — onze listes fermées

**`ground`** — trois paramètres : le grain de la surface ; le raccord bord à bord d'une case à la suivante ; la variation admise à l'intérieur d'une case.

**`path`** — quatre : la largeur du tracé dans sa case ; l'absence totale d'épaisseur et d'ombre portée, un chemin étant DANS le sol ; l'irrégularité de ses bords longs ; ce qui affleure à sa
surface — cailloux, traces de passage.

**`stream`** — cinq : la profondeur de son lit sous le terrain ; le sens et la marque du courant ; le traitement de la surface — rides, reflets ; la bordure de ses rives ; le raccord exact de l'eau
aux bords que la pièce relie.

**`bridge`** — cinq : la forme de son ouvrage — arche, tablier ; l'appareillage de sa pierre ; ses parapets, hauteur et couronnement ; ce qu'il enjambe, **et qui n'est pas dessiné** ; le raccord de
son tablier aux deux bords de la case.

**`fence`** — six : la hauteur des poteaux en fraction de case ; le nombre de lisses et leur position en hauteur ; l'espacement des poteaux ; le débord du poteau au-dessus de la lisse haute ; la
végétation au pied ; le portillon quand la variante en déclare un.

**`building`** — huit : le programme, c'est-à-dire ce qu'il abrite ; sa volumétrie — corps, ailes, toitures ; la pente et la couverture de ses toits ; ses ouvertures, porte et fenêtres, avec leur
taille en cases ; son échelle lue sur la porte ; ses matériaux de mur ; **son usure, deux niveaux, temps et nature** ([l'usure d'un bâtiment](usure-des-batiments.md)) ; ses abords immédiats — seuil,
bacs, appentis.

**`tree`** — cinq : la forme de sa couronne et sa densité ; le rapport entre la largeur de la couronne et celle du pied ; la forme du tronc et son évasement au sol ; la feuille, sa forme et ses deux
tons ; ce qu'il porte — fruits, fleurs, rien.

**`grove`** — cinq : le nombre d'arbres et leur recouvrement ; la bande de troncs nus visible, en fraction de la hauteur ; le sous-bois, plante par plante nommée ; l'aération de ce sous-bois et les
trouées d'ombre ; le raccord de la masse aux bords, pour que deux bosquets se rejoignent.

**`grass`** — quatre : la hauteur des brins ; leur port — dressés, arqués, retombants ; la densité de la touffe, qui est un axe de variante ; ce qui la ponctue — épis, fleurs, brins secs.

**`human`** — six : la morphologie et l'âge ; l'origine, carnation et cheveux ; le vêtement, pièce par pièce ; ce qu'il porte en main ou sur lui ; sa posture ; **ce qu'on voit de lui selon
l'orientation demandée**, qui est le paramètre le plus souvent manqué.

**`creature`** — six : l'espèce et sa silhouette ; sa taille en cases ; son pelage ou sa peau, matière et couleur ; ses traits distinctifs ; sa posture ; **ce qu'on voit d'elle selon l'orientation
demandée**. Sa rune n'en fait PAS partie : elle se trace au rendu, jamais dans la sprite.

## Comment on s'en sert

**UNE FICHE FIXE CHAQUE PARAMÈTRE DE SON TYPE, OU DÉCLARE QU'IL NE S'APPLIQUE PAS.** Le silence n'est pas une réponse : c'est lui qui laisse le générateur choisir, et c'est ce que ce document
supprime. Un paramètre qui vaut « rien » se dit — « aucun fruit », « rien à son pied ».

**LE CONTRÔLE LES COMPTE ET NOMME CE QUI MANQUE, SANS REFUSER** : `php scripts/check-subject-parameters.php`. Refuser bloquerait la production sur une fiche ancienne, alors que la production est ce
qui fait avancer le projet ; signaler la rend visible, et le manque se comble quand on touche à la fiche.

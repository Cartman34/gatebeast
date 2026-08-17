# La lumière — source unique de l'atelier

<!--
bloc: lumiere
groupe: La sprite et son rendu
titre: Lumière
niveau: common
apres: Caméra
gouverne: lumière, soleil, ombre, ombrage, éclairé, ciel
-->

**Usage :** ce fichier définit d'où vient la lumière et ce qu'elle fait. **C'est le seul endroit où la lumière est définie**, et aucun autre bloc n'a le droit
d'en parler.

**Intention :** la lumière vivait au milieu de la clause de caméra, sans lui appartenir — si bien que réécrire la caméra l'emportait avec elle, ce qui est
arrivé le 2026-08-17. Deux sujets dans une même section, c'est un sujet qu'on perd sans le voir. La caméra dit d'où l'on REGARDE, la lumière d'où l'on
ÉCLAIRE : deux choses, deux blocs.

## D'où vient la lumière

**Du NORD-OUEST et d'en haut**, ce qui se voit dans l'image comme une lumière venant du coin haut gauche. C'est la seule direction relative à l'image de toute
la consigne, et elle est donnée en cardinal d'abord — la caméra ayant l'azimut zéro, le nord-ouest tombe en haut à gauche et les deux formulations désignent le
même rayon.

**Jamais de la caméra.** Une lumière frontale supprime les ombres portées sur le sujet lui-même, et un sujet sans ombre est un sujet sans volume.

## Ce qu'elle fait — et DEUX CHOSES S'APPELLENT « OMBRE », QU'IL NE FAUT PAS CONFONDRE

**L'OMBRE PROPRE, SUR LE SUJET LUI-MÊME, EST VOULUE** : c'est elle qui donne le volume, et un sujet éclairé uniformément sur toute sa surface est un sujet plat.
Elle est sans danger parce que **la direction de la lumière est la même pour toutes les sprites du monde** — fixée ici, une fois : deux cents sujets dessinés au
même soleil s'assemblent sur une carte sans se contredire. Ce qui est exposé au ciel reçoit la lumière ; ce qu'une masse surplombe est plus sombre, et **les
faces tournées vers le sol restent lisibles** : on doit voir sous une couronne et sous un porche.

**L'OMBRE PORTÉE, SOUS LE SUJET, EST INTERDITE**, et c'est le détourage qui le dit, pas ce bloc. Une ombre cuite dans l'image tomberait sur les cases voisines
quoi qu'il y ait dessous, ne suivrait aucun relief, et se superposerait à celle du sujet d'à côté. C'est le moteur qui la pose, s'il la pose.

**Et la FORME de l'ombrage — les deux bandes claires — appartient au style, pas à la lumière.** Ce bloc dit d'où vient le soleil et ce qu'il éclaire ; comment
l'ombre est peinte est une décision de rendu. Elle était écrite aux deux endroits, ce qui est exactement la contradiction que cette organisation existe pour
supprimer.

**Aucun ciel n'est dessiné** : la sprite est détourée, il n'y a rien derrière elle. Le mot « horizon » appartient au bloc de la projection, où il nomme le
roulis nul de la caméra — il ne s'emploie pas ici, sous peine de désigner deux choses.

## Ce que la consigne en dit — et c'est ce texte-là, mot pour mot, qui part au générateur

```consigne
Lumière : soleil de fin de matinée venant du NORD-OUEST et d'en haut — ce qui se voit dans l'image comme une lumière
venant du coin haut gauche —, franc et clair, et de là SEULEMENT : jamais depuis le point de vue. Ce qui est exposé
au ciel reçoit la lumière ; ce qu'une masse surplombe est dans son ombre, et le reste franchement plus sombre — le
dessous d'une couronne, les branches sous le feuillage, l'intérieur d'un porche, le pied d'un mur. Un sujet éclairé
uniformément sur toute sa surface est un sujet sans volume. L'ombrage se fait en deux bandes claires, et les faces
tournées vers le sol restent lisibles. Aucun ciel n'est dessiné, et rien derrière le sujet.
```

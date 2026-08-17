# L'assise au sol et l'élévation — source unique de l'atelier

<!--
bloc: assise
groupe: Le sujet et ses mesures
titre: Assise au sol et élévation
niveau: parameters
apres: Dimensions de l'image
gouverne: 10 cases de profondeur; 8 TX; UNE CASE AU PLUS; 5,25; 10,5
-->

**Usage :** ce fichier définit ce que le sujet pose au sol, où il se pose, et ce qui monte au-dessus. **C'est le seul endroit où l'assise est fixée.**

**Intention :** c'est la chose la plus souvent manquée, et pour une raison précise — l'assise et le cadrage se contredisaient. Le cadrage exigeait « une marge
transparente tout autour » quand l'assise fixe le point de pose à la mesure, et le générateur suivait celle qu'il lisait en dernier. Une seule des deux décide,
et c'est celle-ci.

## Ce que le sujet pose, et où

**L'emprise au sol : un rectangle de 16 cases de large sur 10 cases de profondeur.** C'est le plan du bâtiment, pas sa silhouette : ce qu'il dresse peut être
plus étroit, jamais plus large.

**Le point de pose : le milieu de la base tombe à 8 TX du bord OUEST**, soit au milieu de la largeur. Décalé, le sujet empêche de poser quoi que ce soit à côté
de lui sur la carte.

**Un débord d'une case au plus** est toléré à la rangée SUD, pour que la matière se raccorde à ce qui l'entoure.

## Ce qui s'élève

Tout ce que le sujet dresse monte **au-dessus** de ce rectangle et occupe le reste de la hauteur de l'image. Un sujet entièrement contenu dans son rectangle au
sol, sans rien qui s'élève par-dessus, est un sujet écrasé — pas un sujet vu sous cette caméra.

**La tolérance d'une case ne s'applique QU'AU DÉBORD**, jamais au retrait. Elle a été lue comme une licence de dessiner plus étroit : les deux dernières images
sont sorties à 15,16 puis 14,20 TX de large pour 16 attendus, en s'octroyant presque une case de marge de chaque côté.

## Ce que la consigne en dit — et c'est ce texte-là, mot pour mot, qui part au générateur

```consigne
CE QUI TOUCHE LE SOL ET CE QUI S'ÉLÈVE. Le sujet POSE AU SOL un rectangle de 16 cases de large sur 10 cases de
profondeur : c'est le plan du bâtiment. Ce qu'il dresse peut être plus étroit que ce rectangle, jamais plus large.
LE POINT DE POSE EST UNE MESURE, PAS UNE IMPRESSION : le MILIEU DE LA BASE du sujet — le seuil du bâtiment, le pied
du tronc, le centre de la touffe — tombe à 8 TX du bord OUEST de l'image, soit au MILIEU de sa largeur.
LA BASE DU BÂTIMENT OCCUPE LA RANGÉE LA PLUS AU SUD DE SON EMPRISE : le pied du mur et le seuil y sont visibles, et
elle n'est laissée ni en sol nu ni en vide. Un débord d'UNE CASE AU PLUS y est toléré, pour que la matière se
raccorde à ce qui l'entoure.
CETTE TOLÉRANCE VAUT POUR CE QUI DÉPASSE, JAMAIS POUR CE QUI MANQUE : elle n'autorise en aucun cas à dessiner plus
étroit ou plus court que les dimensions annoncées.
CE QUE CELA DONNE COMME HAUTEUR À VISER, ET C'EST UN NOMBRE, PAS UNE IMPRESSION : les 10 cases de profondeur de
l'emprise occupent déjà 10 TY de l'image. Pour que le total tienne dans la fourchette annoncée plus haut, CE
BÂTIMENT SE DRESSE ENTRE 5,25 ET 10,5 MÈTRES, faîtage compris. Vise le milieu de cette fourchette, pas son bord.
TOUT CE QUE LE SUJET DRESSE — murs, toit, tronc, feuillage — MONTE AU-DESSUS de ce rectangle et occupe le reste de
la hauteur de l'image. Un sujet entièrement contenu dans son rectangle au sol, sans rien qui s'élève par-dessus, est
refusé : c'est un sujet écrasé, pas un sujet vu sous cette caméra.
```

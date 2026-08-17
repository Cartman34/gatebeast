# La projection — source unique de l'atelier

<!--
bloc: projection
groupe: La sprite et son rendu
titre: Caméra
niveau: common
gouverne: orthographique, parallèle, azimut, plongée, roulis, point de fuite, perspective, x_image, y_image, 96, 84, 48
-->

**Usage :** ce fichier définit la caméra, le repère et les échelles de l'atelier de génération. **C'est le seul endroit où la projection est définie**, et aucun
autre fichier de l'atelier n'a le droit de la redire, même autrement, même « pour rappel ». Ce qu'une consigne dit de la projection est assemblé d'ici.

**Comment ce fichier est fait, et tous les blocs de source sont faits pareil :** il porte l'explication — ce qui suit, destiné à un humain ou à un agent — **et
la clause exacte que le générateur lira**, en dernière section, dans un bloc de code. L'assembleur ne prend que ce bloc de code. Les deux vivent dans le même
fichier pour qu'on ne puisse pas corriger l'un en oubliant l'autre : c'est cela, la source unique.

**Ce que déclare son en-tête :** son `groupe` et son `titre` dans la consigne, son `niveau`, et surtout **ce qu'il `gouverne`** — la liste des mots dont il est
seul à avoir le droit de parler. `review-server/workshop/check-source.php` refuse qu'un autre bloc les emploie. C'est ce qui empêche mécaniquement la
contradiction, plutôt que la vigilance de celui qui écrit.

**ON NE GOUVERNE QUE CE QU'ON ÉNONCE, JAMAIS LE VOCABULAIRE PARTAGÉ.** `TX`, `TY` et les points cardinaux sont **définis** ici et **employés partout** — une
clause de dimensions doit pouvoir écrire « 16 TX de large », une clause d'usure « le pan OUEST ». Les gouverner reviendrait à interdire toute mesure et toute
direction dans le reste de la consigne. Ce bloc ne garde donc que ce que lui seul peut dire : les paramètres de la caméra, la formule, et ses trois nombres.

**Intention :** arrêter de se contredire. La projection a été décrite en prose, puis en deux égalités, puis en trois unités, à trois endroits qui ne disaient pas
la même chose — et chaque agent qui passait en inventait une quatrième pour combler ce qu'il croyait manquant. Une définition qui vit à un seul endroit ne peut
pas se contredire elle-même. **Il n'y a rien d'exotique ici** : c'est une plongée orthographique standard, et tout ce qui suit s'en déduit sans qu'aucune règle
supplémentaire soit inventée.

**Portée :** l'atelier seul. Le reste de l'application — `scripts/`, `doc/conception/`, la chaîne de production — n'est pas encore aligné là-dessus, et
**c'est voulu** : on définit d'abord, proprement et en un lieu, on applique ensuite. Aligner à moitié laisserait des reliquats partout et ramènerait exactement
les contradictions que ce fichier existe pour supprimer.

## La caméra, paramètre par paramètre

Une caméra se règle avec cinq paramètres, et les voici tous — aucun n'est laissé implicite, parce qu'un paramètre qu'on ne nomme pas est un paramètre que le
prochain lecteur invente.

**1. Le TYPE de projection : ORTHOGRAPHIQUE.** C'est le choix entre deux façons de mettre le monde à plat. Une caméra en **perspective** fait rétrécir ce qui est
loin — c'est l'œil humain, et les lignes y convergent vers un point de fuite. Une caméra **orthographique** ne fait rien rétrécir : c'est un plan d'architecte,
tout garde sa taille où qu'il soit. On prend l'orthographique parce que les sprites se posent sur une grille de cases : une case doit mesurer pareil au premier
plan et au fond, sinon elle ne se pose plus. **Orthographique et parallèle sont le même mot** — l'un dit la méthode, l'autre dit ce qu'elle préserve.

**2. L'AZIMUT : ZÉRO degré.** C'est la rotation de la caméra **autour de la verticale**, autrement dit vers où elle est tournée sur la boussole. À zéro, elle
regarde plein NORD : elle a le sud dans le dos et voit la face sud des choses. La conséquence tient en une ligne — **s'enfoncer vers le nord monte tout droit
dans l'image, sans partir de côté**. Un azimut non nul ferait dériver la profondeur en biais : c'est exactement ce qu'on appelle une vue isométrique, et c'est
ce qu'on ne veut pas.

**3. La PLONGÉE : SOIXANTE degrés au-dessus du plan du sol.** C'est de combien la caméra est levée au-dessus de l'horizon pour regarder vers le bas. À 0° on
serait de plain-pied et on ne verrait aucun dessus ; à 90° on serait à la verticale et on ne verrait aucune façade. À 60° on voit **largement le dessus** de ce
qui est posé au sol tout en gardant les façades lisibles. C'est ce seul angle qui fixe les deux nombres 84 et 48 de la formule plus bas.

**4. Le ROULIS : ZÉRO degré.** C'est l'inclinaison de la caméra sur le côté, celle qui ferait pencher tout le décor. À zéro, l'horizon est droit : une verticale
du monde est une verticale de l'image, et une ligne est-ouest est horizontale. Il est dit ici bien qu'il ne change jamais, parce que non dit il se devine.

**5. L'ÉCHELLE : 96 PIXELS pour un mètre est-ouest.** C'est la finesse de l'image, et c'est le seul paramètre qui n'a rien à voir avec l'angle. Les deux autres
échelles s'en déduisent par la plongée. **La position de la caméra, elle, n'est pas un paramètre** : en projection orthographique seule sa direction compte, la
reculer ou l'avancer ne change rien à l'image.

## Le repère du monde

Trois axes, en mètres, et **un mètre est une case** :

| Axe | Direction du monde | Point cardinal |
| --- | --- | --- |
| `X` | vers la droite | l'EST ; `-X` est l'OUEST |
| `Y` | vers le fond | le NORD ; `-Y` est le SUD |
| `Z` | vers le haut | la hauteur ; il n'a pas de point cardinal |

**Le SUD est le bord le plus proche de la caméra**, donc le bas de l'image ; le NORD est le plus lointain, donc le haut. La face SUD d'un sujet est celle que la
caméra voit. **Toute direction se dit avec ces quatre mots**, jamais en « gauche », « droite », « devant » ou « fond ».

## Comment un point du monde se dessine — et tout le reste en découle

Un point du monde `(X, Y, Z)`, en mètres, se dessine dans l'image à :

    x_image = 96 · X
    y_image = 84 · Y + 48 · Z          (vers le HAUT de l'image)

**D'où viennent ces trois nombres, et il n'y en a pas d'autres :**

- `96` est l'échelle de base : un mètre est-ouest occupe 96 pixels. La caméra ne raccourcit pas cet axe.
- `84 = 96 × sin 60°` — un mètre de profondeur au sol, vu sous une plongée de 60°. Publié à 84 plutôt qu'à 83,14 pour que deux cases voisines se rejoignent sans
  couture ; c'est le seul arrondi de tout le système, et il est décidé, pas calculé au vol.
- `48 = 96 × cos 60°` — un mètre debout, vu sous la même plongée. Exactement la moitié de 96.

**Les deux termes de `y_image` montent tous les deux**, et c'est la seule chose qui demande de l'attention : s'enfoncer vers le nord et s'élever font l'un comme
l'autre monter dans l'image, à deux échelles différentes.

## Les unités, et à quoi chacune sert

| Unité | Vaut | Mesure |
| --- | --- | --- |
| `TX` | 96 px | une largeur, dans l'image comme dans le monde |
| `TY` | 84 px | une profondeur au sol, **et toute distance verticale mesurée dans l'image** |

**IL N'Y A PAS D'UNITÉ POUR LA HAUTEUR DU MONDE, ET C'EST LE PIÈGE À CONNAÎTRE.** Un mètre debout ne vaut pas une case d'image : il en vaut 48/84, soit 4/7 de
`TY`. Donc :

- **une hauteur du MONDE se dit en mètres, ou en cases du monde** — « le mur monte sur trois cases » veut dire trois mètres, et occupe `3 × 48 = 144 px` ;
- **une hauteur d'IMAGE se dit en `TY`** — « l'image fait 14 TY de haut » veut dire `14 × 84 = 1176 px`.

**Les deux ne se convertissent pas l'une en l'autre sans passer par la formule ci-dessus**, et confondre les deux est ce qui a fait sortir des portes deux fois
trop hautes et des bâtiments écrasés. Un exemple, une fois, pour fixer les idées : un bâtiment de **3 mètres** de haut posé sur une emprise de **10 cases** de
profondeur occupe `10 × 84 + 3 × 48 = 984 px` de hauteur d'image, soit **11,7 TY**.

## Ce qui en découle — rien d'ajouté, tout se relit sur la formule

- **Une longueur de N cases occupe la même mesure partout dans l'image**, au premier plan comme au fond : le rapport est de un pour un, en tout point. Le
  quadrillage du monde **ne rétrécit pas** avec la profondeur.
- **S'enfoncer vers le NORD, c'est monter tout droit dans l'image** : `x_image` ne dépend que de `X`. Jamais en diagonale, jamais vers la gauche ni vers la
  droite. Le bord NORD d'une chose se dessine exactement à l'aplomb de son bord SUD.
- **Une arête debout monte tout droit** elle aussi, pour la même raison : un mur a la même largeur en haut qu'en bas, et deux murs opposés sont deux droites
  verticales parallèles.
- **Deux droites parallèles dans le monde restent parallèles dans l'image**, et deux longueurs égales sur un même axe y restent égales.
- **Une ligne est-ouest reste horizontale** dans l'image : `y_image` ne dépend pas de `X`.
- **Un même objet dessiné à deux endroits de l'image y a exactement la même forme et la même taille.** Il n'y a pas de place où les choses seraient plus petites.
- **Cela vaut à TOUTE HAUTEUR** — au sol, sur un mur, sur un toit, sur une lucarne. La formule ne connaît pas de zone où elle cesserait de s'appliquer.
- **Un pan de toit qui descend vers l'est ou vers l'ouest se projette bordé de deux VERTICALES** — sa rive et son faîtage courent nord-sud, donc verticalement.
  Jamais un parallélogramme qui fuit.

## Ce que cela interdit

- **L'isométrie**, qui satisfait « projection parallèle », « aucun point de fuite » et « pas de perspective » — mais où s'enfoncer vers le nord part **en
  diagonale**. C'est la lecture que le générateur a prise trois jours durant. Ce qui la ferme est `x_image = 96 · X` : l'abscisse ne dépend que de `X`.
- **Toute convergence**, même légère, même seulement sur les toits.
- **Toute clause d'une consigne qui redirait la projection dans ses propres mots.** Elle finirait par la contredire — c'est arrivé quatre fois. Ce qui doit
  parvenir au générateur s'assemble depuis ce fichier.

## La forme et le plan ne sont pas la projection

**L'emprise et le plan du bâtiment font foi, jamais une largeur constante.** Un toit en L reste un L, un plancher d'emprise différente reste différent. Le
rapport de un pour un dit **comment** les choses se projettent, il ne dit pas **quelle forme** elles ont. C'est pour cela que la règle s'énonce en proportion et
non en « le toit garde la même largeur » : la seconde formulation interdirait un toit en L sans le vouloir.

## Ce que la consigne en dit — et c'est ce texte-là, mot pour mot, qui part au générateur

Tout ce qui précède explique ; ce qui suit prescrit. **L'assembleur ne prend que ce bloc**, et rien de l'explication ne parvient au générateur. La règle qui
gouverne son écriture est celle de la conception descendante appliquée au texte : **il ne contient aucune justification, aucun historique, aucune mention de ce
qui a été raté** — le générateur n'a pas de mémoire, et une clause qui parle du passé lui fait dessiner le passé.

```consigne
Caméra : PROJECTION ORTHOGRAPHIQUE, donc PARALLÈLE — aucune perspective, aucun point de fuite, aucune ligne qui
converge. Azimut ZÉRO, plongée SOIXANTE DEGRÉS au-dessus du plan du sol, roulis ZÉRO : l'horizon est droit et la
caméra regarde plein NORD.
LES QUATRE POINTS CARDINAUX SONT LES SEULES DIRECTIONS DE CETTE CONSIGNE. Le SUD est le bord le plus proche de la
caméra, donc le bas de l'image ; le NORD est le plus lointain, donc le haut ; l'EST est à droite, l'OUEST à gauche.
La face SUD d'un sujet est celle que la caméra voit. Ni « gauche », ni « droite », ni « devant », ni « fond » ne
désignent jamais une direction du monde.
UN POINT DU MONDE SE DESSINE ICI, ET TOUT LE RESTE EN DÉCOULE. Une case du monde est un carré d'un mètre. Un point
situé à X mètres vers l'EST, Y mètres vers le NORD et Z mètres de HAUT se dessine à :
— x_image = 96 × X, compté vers la droite ;
— y_image = 84 × Y + 48 × Z, compté vers le HAUT.
Donc : un mètre est-ouest occupe 96 PIXELS, un mètre de profondeur au sol 84 PIXELS, un mètre debout 48 PIXELS.
S'enfoncer vers le nord et s'élever font l'un comme l'autre monter dans l'image, à ces deux échelles-là.
CE QUI EN DÉCOULE, ET QUI SE VÉRIFIE SUR L'IMAGE :
— l'abscisse ne dépend que de X, donc S'ENFONCER VERS LE NORD MONTE TOUT DROIT, jamais en diagonale, jamais vers la
  gauche ni vers la droite. Le bord NORD d'une chose se dessine exactement à l'APLOMB de son bord SUD ;
— une arête debout monte tout droit elle aussi : un mur a la même largeur en haut qu'en bas, et deux murs opposés
  sont deux droites verticales parallèles ;
— UNE LONGUEUR DE N CASES OCCUPE LA MÊME MESURE PARTOUT DANS L'IMAGE, au SUD comme au NORD. Le quadrillage
  du monde NE RÉTRÉCIT PAS avec la profondeur : c'est un rapport de UN POUR UN, en tout point ;
— deux droites parallèles dans le monde restent parallèles dans l'image, et deux longueurs égales sur un même axe y
  restent égales ;
— une ligne est-ouest reste horizontale ;
— un même objet dessiné à deux endroits de l'image y a exactement la même forme et la même taille ;
— un pan de toit qui descend vers l'EST ou vers l'OUEST se projette BORDÉ DE DEUX VERTICALES, sa rive et son
  faîtage courant nord-sud. Jamais un parallélogramme qui fuit.
TOUT CECI VAUT À TOUTE HAUTEUR — au sol, sur un mur, sur un toit, sur une lucarne. Il n'existe aucune partie de
l'image où cela cesserait de s'appliquer.
LA FORME DU SUJET N'EST PAS LA PROJECTION : l'emprise et le plan font foi. Un toit en L reste un L, un plancher
d'emprise différente reste différent. Ce qui précède dit COMMENT les choses se projettent, jamais quelle forme elles
ont.
```

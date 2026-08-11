# Rendu en calques

**Intention :** poser comment une scène s'empile à l'écran, pour que le placement d'un élément — sol, arbre, maison, créature, personnage — soit décidé une seule fois, tienne aujourd'hui pour une maquette statique et demain pour un monde animé avec déplacements, franchissements et évènements. Sans cette règle, chaque nouvel élément rouvre la question de ce qui passe devant quoi, et le rendu se rattrape par cas particuliers.

Ce nœud couvre l'organisation de l'affichage et ce que chaque asset doit porter pour y être posé. Il exclut le style graphique (voir [visuel](../visuel/index.md)) et la composition d'une scène donnée (voir [format de composition](../visuel/format-de-composition.md)).

## Décisions

- **Le monde se situe en trois coordonnées, l'écran n'en connaît aucune** — le cœur du jeu place tout sujet par deux coordonnées au sol plus une **élévation** ; la projection à l'écran appartient au moteur de rendu, qui l'applique au moment de dessiner. Le contenu et la logique ignorent l'écran, conformément à l'architecture hexagonale de la [vision](../../vision.md) : le rendu est un port, le catalogue et les plans de scène sont de la donnée, jamais du code. Écarté : stocker des positions d'écran dans le monde (interdit tout second moteur de rendu et tout changement de caméra).
- **Empilement en deux temps : familles de calques, puis profondeur** — l'ordre d'affichage se décide d'abord par la **famille de calque** de l'élément, ensuite, à l'intérieur de la famille qui contient le monde vivant, par la **profondeur** : plus l'élément est bas dans la scène, plus il est devant. C'est le modèle établi du genre — un ordre grossier par catégorie, un tri fin par profondeur à l'intérieur —, et le seul qui permette à la fois de passer derrière un arbre, sous un feuillage et devant un muret sans cas particulier. Écarté : un tri global par profondeur sans familles (ne sait traiter ni les toits, ni les surplombs, ni les passerelles) ; des familles fixes sans tri (rien ne peut jamais passer derrière quoi que ce soit) ; un tampon de profondeur matériel (mal adapté aux bords transparents des sprites).
- **Cinq familles de calques, dans cet ordre** — le **sol** (matières répétées bord à bord) ; le **décor au sol** (chemins, plaques, ombres portées, marques : tout ce qui se marche dessus) ; le **monde** (tout ce qui se dresse et tout ce qui vit : végétation, bâtiments, personnages, créatures — c'est là que joue le tri par profondeur) ; le **dessus** (ce qui passe au-dessus de la tête : feuillages hauts, toitures, surplombs) ; l'**interface** (ce qui n'appartient pas au monde). Une famille peut se subdiviser si un besoin réel l'exige ; elle ne se contourne jamais.
- **Chaque élément dessinable porte son emprise et son point de pose** — une **emprise au sol** exprimée en cases, et un **point de pose** au milieu du bord bas de cette emprise, qui est le point par lequel l'élément est posé dans le monde. Un élément est donc placé par ses pieds, jamais par son coin d'image : c'est ce qui rend le tri par profondeur juste et le placement indépendant de la taille produite de l'image. Écarté : poser par le centre ou le coin de l'image (rend le tri faux dès que deux images n'ont pas la même taille).
- **Ce qui doit laisser passer dessous se produit en deux morceaux** — un élément sous lequel on circule (grand arbre, porche, passerelle) se fabrique en une partie basse, qui vit dans le monde et se trie par profondeur, et une partie haute, qui vit dans le dessus. Ce n'est pas une exception du moteur : c'est une propriété de l'asset, déclarée au catalogue. Écarté : découper à l'affichage par calcul (fragile, et impossible à contrôler à la production).
- **L'élévation se traite en répétant les familles, pas en cas particulier** — chaque niveau habitable (le sol, une passerelle, un étage) est un jeu complet de familles empilé au-dessus du précédent ; un sujet appartient au niveau où il se tient et se trie parmi ses semblables. Le jour où le jeu veut un pont ou une maison à étage, rien du modèle ne change. Écarté : traiter les franchissements par exceptions ponctuelles (chaque nouveau cas rouvre le rendu).
- **Ce qui se dessine est un sujet, défini par un type et un profil** — le **type** dit quelle sorte de chose c'est et porte les comportements ; le **profil** est l'apparence concrète, unique, inscrite à l'[inventaire](../visuel/inventaire/README.md) sous son code stable — un chêne et un bouleau sont deux profils du type arbre. Les postures d'un profil sont ses **variants** — une orientation dans le repère du monde, une action, et la direction de chaque partie qui pointe dans le repère du sujet — et chaque variant porte une ou plusieurs **images** numérotées. Le modèle complet est au [référentiel des sujets](../visuel/assets/sujets-et-variantes.md). Écarté : parler d'entité côté rendu (le mot couvre aussi ce qui n'a aucune image) ; une image unique par sujet (interdit tout mouvement).
- **Le lot de variants est exigé par le type, et se complète à tout moment** — chaque type déclare le lot attendu de ses profils ([lots de variants](../visuel/assets/lots-de-variantes.md)) ; un profil livré avec un lot partiel reste utilisable, le variant manquant se repliant sur un variant déclaré, et compléter le lot plus tard est un pur ajout. Écarté : exiger le lot complet avant toute mise en jeu (bloquerait toute première version).
- **Un variant ne se redécrit jamais** — toutes les images d'un même profil se produisent à partir de sa fiche citée **mot pour mot**, seule la clause de l'axe changeant. C'est la seule façon constatée de tenir un style et une identité constants d'une image à l'autre ([capacités du générateur](index.md)). Écarté : réécrire la description à chaque variant (le sujet dérive d'une image à l'autre).
- **Le référentiel des sujets est la source unique** — un fichier lisible par machine décrit les **types**, les **sujets** et leurs **variants** : le code, le type, le calque, l'emprise au sol, le point de pose, l'éventuelle découpe basse/haute, les contraintes — dont le passage — et, sous chaque variant, ses **représentations**. La génération l'alimente, les plans de composition s'y réfèrent, le moteur de rendu le consomme, et le cœur du jeu n'y voit que des sujets et des actions — jamais des fichiers. Ajouter un élément au jeu reste un pur ajout de contenu, comme la [vision](../../vision.md) l'exige. Écarté : redéclarer ces informations dans les scripts de génération, dans les plans et dans le code (trois vérités qui divergent).
- **Un variant porte des représentations, pas des images** — la sprite n'est qu'une façon de représenter un variant ; un modèle en trois dimensions en serait une autre, et s'ajouterait à côté sans rien changer au reste. Le référentiel parle donc de variants et de leurs représentations, jamais de fichiers d'images au premier plan. Écarté : un référentiel construit autour de l'image — il faudrait le refaire au premier moteur qui ne consomme pas des sprites.
- **La rune d'une créature est tracée au rendu, sur une ancre portée par la représentation** — la sprite est produite **sans** rune ; le rendu trace par-dessus la forme que l'individu déclare, à
  l'endroit que l'image déclare. Trois données, chacune à un seul foyer : la **forme** — un chemin d'un seul trait dans un carré de référence — et sa **couleur exacte** vivent au référentiel avec les
  runes elles-mêmes, une fois pour toutes ; l'**ancre de rune** — un point, plus une inclinaison quand la surface est bombée — vit dans la représentation, à côté des mesures qu'elle porte déjà, et se
  pose à l'œil, une par image ; et **quel individu porte quelle rune** reste au contenu. La taille ne se déclare nulle part : elle est constante par règle ([visuel](../visuel/index.md)), calibrée sur
  une créature d'une case, donc le rendu la connaît sans que l'image la redise. **Aucun placement n'est calculé** — le moteur ne cherche jamais un front ni ne suit une posture, il applique ce qui est
  déclaré. Motivé au [visuel](../visuel/index.md) : identité exacte de la marque, taille constante tenue par construction, et un catalogue qui additionne les formes au lieu de multiplier les images.
  Écarté : la rune dessinée dans la sprite (jamais deux fois la même, et une image par espèce × rune × posture). Repli connu si un moteur ne savait pas tracer : une petite image par forme, posée sur
  la même ancre, sans rien changer au reste du modèle.
- **Le premier catalogue est gelé, un fichier neuf le remplace** — `assets/catalogue.json` était construit autour de l'image et ne sait porter ni les types, ni les contraintes, ni les connexions. Il n'est plus alimenté ni lu, et n'est pas supprimé. Écarté : l'étendre — on aurait gardé sa structure orientée image en lui ajoutant des rustines.

## La case projetée — dimensions et source de vérité

- **UNE CASE PROJETÉE N'EST PAS CARRÉE : `24 × 21 px` à l'affichage, `96 × 84 px` en source ×4.** Sous une caméra à 60° au-dessus du plan du sol et un azimut de 0°, une case carrée de 24 unités de
  largeur est-ouest mesure `24 × sin(60°) = 20,78` unités en profondeur projetée nord-sud, soit 21 px après quantification. Décision de l'opérateur, 2026-08-08.
- **Les ratios de projection : `sin(60°) = 0,8660254` pour une profondeur au sol, `cos(60°) = 0,5` pour une hauteur verticale.** Un élément haut de 24 unités dépasse donc de 12 px à l'affichage,
  48 px en source. Ces deux nombres disent l'**intention géométrique** et servent à la comprendre.
- **L'ÉCHELLE EN PIXELS FAIT FOI, PAS LE FACTEUR — ET AUCUN CODE NE MULTIPLIE PAR `0,8660254` POUR OBTENIR UNE TAILLE.** `96 × 0,8660254 = 83,14`, alors que la case publiée fait 84 : l'échelle réelle
  est `7/8`, retenue parce qu'elle se divise proprement — 96×84, 48×42, 32×28, 24×21 tombent tous justes. L'écart à la géométrie est de 1 % et il achète des entiers à tous les paliers. **Le 84 ne se
  « corrige » pas en 83** : ce serait défaire un choix, pas réparer une erreur. Un bout de code qui recalculerait la taille avec le facteur retomberait sur 83,14, et une sprite rendue à 20,78 posée
  sur un pas de 21 laisse 0,22 px par case — un liseré à chaque raccord, exactement ce que la quantification évite.
- **UNE CASE EST LA HAUTEUR MINIMUM D'UNE SPRITE, ET RIEN NE L'AUTORISE À DESCENDRE EN DESSOUS.** Décision de l'opérateur, 2026-08-10 : « RIEN ne peut autoriser un sujet d'avoir une hauteur en
  dessous de 1 case ». Une sprite occupe sa case, donc elle la remplit — un sol, un chemin, une touffe d'herbe, un ruisseau qui creuse en font une comme les autres. **Ce plancher porte sur l'image,
  pas sur une hauteur d'objet déduite** : voir la section suivante, qui dit pourquoi cette hauteur déduite n'existe plus.
- **Les cases se posent par leur coin supérieur gauche**, sur un pas entier de `24 × 21 px`, `96 × 84 px` en source. Leur centre géométrique vaut `(12 ; 10,5)` à l'affichage : c'est une frontière
  entre pixels, pas une position à écrire — **rien ne se place par son centre**, ce qui rend la demi-coordonnée sans conséquence.
- **Les ports de raccord sont centrés sur les quatre bords** — nord au milieu du bord supérieur, est au milieu du bord droit, sud en bas, ouest à gauche. Deux sprites raccordées doivent fournir sur
  leurs ports opposés **exactement la même largeur, le même alpha, la même matière et la même valeur tonale**.
- **Les calques de sol restent dans `96 × 84 px`.** Une sprite haute conserve **une empreinte de case et une ancre au sol**, mais son image reçoit le débordement vertical nécessaire **au-dessus** de
  cette ancre ; le tri et le survol se rapportent toujours à la case de l'ancre, même si l'image masque des cases arrière.
- **Le plan de composition peut afficher les deux** — la case carrée du plan et la case projetée du rendu.

## Deux unités, `TX` et `TY` — et aucune mesure ne s'écrit sans la sienne

- **« UNE CASE » NE DÉSIGNE PLUS RIEN TOUT SEUL, ET C'EST VOULU.** Décision de l'opérateur, 2026-08-10 : « selon le sens, ça va poser souci ; si tu veux inventer des unités, faut un truc comme
  `CX` et `CY` », puis « OK pour `TX` et `TY` ». **`TX` est une case en largeur, `TY` une case en hauteur.** Le mot « case » seul reste bon pour parler du monde — un carré d'un mètre —, jamais pour
  donner une mesure d'image.
- **`TY` SE CALCULE DEPUIS `TX`, ET VOICI COMMENT** : `TY = TX × 84 / 96`. Le rapport est celui de la profondeur de la case projetée sur sa largeur, les deux nombres étant publiés à la section « La
  case projetée » ci-dessus, et repris dans `scripts/tile_scale.py` (`FILE_TILE_DEPTH`, `FILE_TILE_WIDTH`, `TILE_FORESHORTENING`). **Il ne se recalcule jamais depuis `sin(60°)`** — la règle de
  l'échelle qui fait foi vaut ici comme ailleurs : le sinus donnerait 83,14 pour une case publiée à 84, et rouvrirait un liseré à chaque raccord. À l'écran, le même rapport lie `24` et `21`.
- **CE QUI S'EXPRIME EN QUOI** : une largeur en `TX` ; une hauteur d'image et une profondeur au sol en `TY`. Une pièce d'assemblage vaut donc `1 TX` sur `1 TY`, et un rectangle au sol de deux
  rangées vaut `2 TY` de profondeur.
- **AUCUN NOMBRE NE S'ÉCRIT SANS SON UNITÉ**, nulle part : consigne, référentiel, document, message. Les clés du référentiel la portent dans leur nom — `height_min_ty`, `height_max_ty` —, parce
  qu'un chiffre nu redevient ambigu dès que quelqu'un le recopie ailleurs.
- **CE QUE ÇA A COÛTÉ AVANT D'ÊTRE FIXÉ** : les hauteurs se disaient en cases-de-largeur, si bien qu'une pièce d'assemblage remplissant exactement sa case s'annonçait à `0,875 case` — un dessin
  juste avec un chiffre qui le dit faux, **et c'est l'arrondi de ce `0,875` vers `1,0` qui a fait sortir huit pièces plates carrées**. Pire, la consigne mêlait les deux unités sous le même mot : sa
  fourchette de hauteur comptait en cases-de-largeur pendant que sa clause du rectangle au sol annonçait « 1,75 case de profondeur » pour deux rangées. **Deux unités sous un seul nom, dans le même
  texte, envoyées au générateur.**
- **IL N'Y A PLUS DE RACCOURCISSEMENT À ÉNONCER.** La profondeur d'un rectangle au sol de `n` rangées fait `n TY`, point : elle se dessine plus bas que large parce que `TY` est plus court que `TX`,
  et cela se dit une seule fois, là où l'unité est convertie en pixels.

## La fourchette de hauteur se déclare, elle ne se calcule pas

- **AUCUN SCRIPT NE PEUT SAVOIR QU'UNE HERBE EST COURTE ET QU'UN CHÊNE EST GRAND.** Décision de l'opérateur, 2026-08-10 : « il n'y a pas de fourchette calculée possible, c'est une fourchette qui est
  donnée par toi ». La hauteur attendue d'une sprite est un **jugement porté sur le sujet dessiné**, et ce jugement n'existe dans aucun fichier tant que quelqu'un ne l'écrit pas. Le déduire d'un
  nombre par une formule, c'est fabriquer une autorité que personne n'a exercée.
- **ELLE APPARTIENT AU VARIANT, PAS AU SUJET** — même décision, même jour : « si le variant met le sujet dans une position allongée, il n'aura pas la même fourchette ». C'est le variant qui porte la
  posture, l'action et la forme ; un chêne couché n'a pas la hauteur du même chêne debout. Un sujet ne porte donc **aucune** fourchette, et deux variants du même sujet en portent deux différentes.
- **CE QUE CETTE DÉCISION REMPLACE, ET QUI DOIT DISPARAÎTRE** : la hauteur unique déclarée au sujet (`height`), la formule qui en tirait un plancher et un plafond (`master_band` dans
  `scripts/tile_scale.py`), et les rustines empilées dessus le 2026-08-10 — plancher d'une case sur la hauteur déclarée, tolérances élargies pour les sujets qui montaient peu. **Toutes traitaient le
  même défaut par son symptôme.** Le signe qu'il fallait chercher ailleurs : appliquer le plancher d'une case à la hauteur déclarée faisait dépasser d'une demi-case tout sujet qui ne se dresse pas,
  c'est-à-dire supprimait la possibilité même qu'un sujet soit plat.
- **CE QUE LA HAUTEUR DÉCLARÉE RESTE, SI ELLE RESTE** : une donnée de jeu — ce que le sujet mesure dans le monde —, jamais une donnée de production. Elle ne commande plus aucune toile et ne juge plus
  aucune image.

## Questions ouvertes

Aucune : le modèle est arrêté ; le contrat exact du port de rendu s'écrira au socle applicatif, sans rouvrir ces choix. Le **format du référentiel des sujets** reste à écrire, et il l'est en même temps que le fichier lui-même — il ne se décide plus, il se rédige.

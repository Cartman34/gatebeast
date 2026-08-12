# Glossaire du projet — anglais et français

**Usage :** les mots du projet GateBeast, chacun défini en une ligne, en français et en anglais. On y cherche ce qu'un terme veut dire, et rien d'autre.

**Intention :** il nomme, il ne décide pas, et il n'explique aucun fonctionnement — une définition tient sur une ligne, le reste vit dans le document qui traite du sujet. C'est de la
**documentation**, jamais de la conception. Les termes de la façon de travailler — dont *opérateur* et les rôles — vivent dans le [glossaire de la méthode](../../conceptions/methode/glossaire.md),
qui porte le même nom parce qu'il est de même nature : seul son périmètre diffère.

**Intention :** fixer chaque terme important dans les deux langues **au moment où il est créé**, jamais après coup. Une traduction décidée plus tard arrive toujours trop tard : le terme s'est déjà
répandu dans le code, les textes et les habitudes.

**Le français fait foi.** C'est la langue dans laquelle les termes sont pensés et arbitrés, et celle de l'interface de la 0.x. L'anglais servira le code, le nom du jeu et l'internationalisation
([vision](conception/vision.md)) : à terme, interface et lore existeront dans les deux langues.

**L'anglais est l'anglais américain.** Orthographe américaine sans exception — `center` et non `centre`, `color` et non `colour`, `catalog` et non `catalogue` —, dans le glossaire comme dans le code.

Règle : un terme important entre dans le glossaire **dès sa création**, avec sa forme française arrêtée et une forme anglaise **provisoire** — marquée d'un astérisque quand elle demande encore
confirmation. Une forme anglaise incertaine ne bloque jamais : elle se note, se signale, et se reprend plus tard avec quelqu'un dont c'est le métier. Ce qui est interdit, c'est de créer un terme sans
rien noter du tout et de découvrir la question de traduction une fois le mot répandu partout.

| Français | Anglais | Ce que c'est |
|---|---|---|
| créature | gatebeast | Les créatures du jeu, collectivement les *gatebeasts*. |
| `TX` | `TX` | **Une case en largeur**, l'unité de toute largeur d'image : 96 pixels dans le fichier, 24 à l'écran. Le symbole ne se traduit pas. |
| `TY` | `TY` | **Une case en hauteur**, l'unité de toute hauteur d'image et de toute profondeur au sol : `TX × 84 / 96`, soit 84 pixels dans le fichier, 21 à l'écran. C'est `TX` écrasé par la plongée à soixante degrés. Le calcul et l'origine des deux nombres sont à `doc/conception/referentiels/technique/rendu-en-calques.md`. |
| case | tile | Un carré d'un mètre **dans le monde**. Ne sert jamais à donner une mesure d'image : vue de la caméra, une case est plus large que haute, et c'est précisément ce que `TX` et `TY` distinguent. |
| biome | biome | Une portion du monde définie par son **ambiance de terrain** : son relief, la matière de son sol, son climat et ce qu'elle donne à voir. Il **ne détermine pas ce qui l'habite** — tout sujet peut se rencontrer partout ; certains y sont endémiques, d'autres l'évitent, mais ce sont des tendances, jamais des contraintes, et rien ne s'y valide. |
| dresseur | trainer | La personne qui accompagne des créatures. |
| personnage-joueur | player character | Le personnage incarné par le joueur. |
| plan parallèle | other side | Le monde d'où viennent les créatures. Terme du lore, jamais affiché tôt. |
| point de passage | gateway | Un lieu où l'autre monde touche celui-ci. |
| passage sauvage | wild gateway | Un passage qui surgit sans qu'on sache comment. |
| passage bâti | built gateway | Un passage construit, fermé par défaut, à l'emplacement secret. |
| gateball | gateball | L'objet du dresseur : il ne contient pas la créature, il la relie à l'autre monde. Identique dans les deux langues. |
| émergence | emergence | L'arrivée de créatures par un passage. |
| centre de soin | healing center | Le lieu où les créatures récupèrent. |
| terrain d'entraînement | training ground | L'enclos attenant au centre de soin. |
| boucle de jeu | game loop | Explorer, rencontrer, capturer, faire progresser, combattre, repartir. |
| case | tile | L'unité du monde : un pas, environ un mètre. |
| rune | rune | Le symbole lumineux que porte toute créature de l'autre monde. Unique à chaque créature ; deux créatures qui portent la même rune sont liées. |

## Termes de production visuelle

Le vocabulaire de la fabrication et de l'affichage des images. Les décisions qui les portent sont dans
[rendu en calques](conception/referentiels/technique/rendu-en-calques.md) et [assets](conception/referentiels/visuel/assets/index.md).

| Français | Anglais | Ce que c'est |
|---|---|---|
| sujet | subject | Tout élément du jeu qui a une représentation graphique. |
| type | type | La sorte de chose qu'est un sujet — arbre, créature, humain, bâtiment, objet, sol, chemin, point de passage. Le type porte les comportements, les évènements et le lot exigé. |
| profil | profile | L'apparence concrète d'un sujet à l'intérieur de son type : `birch-01`, `oak-01`, `asian-01`. Un profil est une apparence et une seule, et une entrée d'inventaire. |
| variant | variant | Une déclinaison précise d'un sujet, telle que son type la déclare — orientation, action, forme, composition, densité, mouvement, directions de ses parties : tous les aspects sous lesquels un sujet peut se décliner. C'est ce qu'on demande au jeu ; il n'est pas une image mais porte des **représentations**, dont la sprite n'est qu'une possibilité parmi d'autres. |
| image | frame | Un fichier d'un variant, numéroté `frame-01`, `frame-02`… Une posture fixe n'en a qu'un, une marche en a plusieurs. |
| représentation | representation | Ce par quoi un variant se réalise concrètement — une sprite aujourd'hui, un modèle en trois dimensions ou autre chose demain. Un variant porte des représentations, il n'est jamais lui-même une image. |
| lot | variant set | L'ensemble des variants exigés d'un profil, fixé par son type et complétable à tout moment. |
| vue principale | base view | Le variant de repos, de face : il existe toujours et sert de référence visuelle à tous les autres. |
| tracé | trace* | Ce qui s'assemble de case en case en reliant des bords de sa case — clôture, chemin, mur, cours d'eau ; sa forme dit lesquels. |
| forme | shape | Pour un sujet qui se pose bout à bout — clôture, chemin, mur, cours d'eau —, l'ensemble des bords de la case que le tracé rejoint, écrits dans l'ordre `n`, `e`, `s`, `w` : `shape-ns` une ligne, `shape-ne` un angle, `shape-nesw` un croisement. La forme dit où la pièce touche ses voisines, donc elle se vérifie par calcul. |
| composition d'un sujet | subject composition | De quoi une pièce est faite, **à forme égale** : la clôture `shape-ns` existe avec deux poteaux, avec un seul, ou sans aucun, ses lisses toujours identiques. On alterne les compositions le long d'une portée pour que les poteaux s'espacent au lieu de se doubler à chaque jointure. S'écrit dans la ref du variant : `posts-2`, `posts-1`, `posts-0`. |
| composition d'une scène | scene composition | Quels sujets se placent sur quelles cases d'une grille. Se déclare dans un **plan de composition** avant toute génération. Même mot que ci-dessus, autre échelle : l'un parle d'un plan, l'autre d'une pièce. |
| plan de composition | composition plan | Le plan à plat, vu de dessus, qui déclare une composition de scène case par case et se contrôle avant qu'aucune image ne soit demandée. |
| exemple d'usage | usage sample | Une image unique montrant les pièces d'un sujet **assemblées**, produite pour les comparer entre elles et servir de référence de style. Ce n'est pas une sprite et elle ne se découpe pas. |
| emprise | footprint | Le sol qu'un sujet occupe, en cases. **Toujours écrite**, sans valeur par défaut. |
| point de pose | pose point | Le milieu du bord bas de l'emprise : le point par lequel un sujet est posé dans le monde. Un sujet se pose par ses pieds, jamais par un coin d'image. |
| texture | texture | Ce qui habille une surface sans en changer la forme : le grain du bois, l'écorce, la mousse, les nuances de couleur. Elle se distingue de la **géométrie**, qui dit où sont les volumes. Un plan ou une esquisse portent la géométrie et jamais la texture ; une image générée porte les deux. |
| maître | master | L'image telle que le générateur l'a rendue, conservée pour toujours. |
| livrable | delivered asset | Le maître **exporté** à la définition de livraison. Rien d'autre ne le distingue : il n'est ni rogné ni retouché. |
| validateur | validator | Un outil qui vérifie qu'une chose respecte les règles écrites, et le dit — une consigne avant sa génération, le référentiel des sujets, une image produite. Il constate et rend un verdict ; il ne corrige rien et ne juge rien. |
| sprite | sprite | L'image d'un variant, posée telle quelle sur la carte du jeu à l'endroit qu'elle occupe. C'est une représentation parmi d'autres, la seule employée aujourd'hui. |
| dimensions d'une image | image dimensions | Ce que l'image mesure. Elles se disent **en cases** au générateur, et **en pixels** pour l'afficher ou pour valider un fichier reçu. |
| ref | ref | Ce qui désigne une chose sans ambiguïté. Un **sujet** a une ref — `OB-010` ; un **variant** a la sienne — `orientation-south_action-idle_shape-ew_gate-open_frame-01` —, **écrite dans la déclaration que son type en fait**, jamais calculée. Une image se désigne par les deux, séparées d'une barre. Une ref ne porte que ce qui distingue : orientation et action toujours, le reste seulement s'il s'écarte de son défaut, et en forme courte quand elle existe (`ns`). Une fois posée, elle ne change plus. |
| orientation | orientation | Comment le sujet est planté sur sa surface, **dans le repère du monde**, à la rose des vents : `south` (face à nous), `north` (de dos), `west` et `east` (de profil), plus les quatre intermédiaires. |
| direction | direction | Où pointe une partie du sujet, **dans le repère du sujet une fois orienté** : les mêmes valeurs, plus `up` et `down`. Convention absolue : `north` = droit devant le sujet, `east` sur sa droite, `west` sur sa gauche, `south` derrière lui. |
| instance | instance | Une **apparition** d'un sujet à un endroit précis d'une scène : le sujet, sa case, son variant et ce qu'il y fait. Le sujet se décrit une fois, ses instances sont innombrables. |
| partie qui pointe | pointing part | Ce qui porte une direction : le corps (`body`), le regard (`gaze`), et toute partie déclarée par le type — une main, une queue. Une direction non écrite vaut `north`. |
| action | action | Ce que fait le sujet : `idle`, `walk`, `run`, `sit`, `sleep`, `jump`… liste ouverte. |
| repli | fallback | Le variant de remplacement quand celui demandé n'existe pas encore. |
| emprise au sol | footprint | Les cases que le sujet occupe au sol. |
| point de pose | anchor | Le point par lequel le sujet est posé dans le monde : le milieu du bord bas de son emprise. |
| calque | layer | L'une des cinq familles d'empilement à l'écran : sol, décor au sol, monde, dessus, interface. |
| élévation | elevation | Le niveau auquel un sujet se tient : le sol, une passerelle, un étage. |
| port | harbour | Le lieu où les bateaux s'amarrent, dans le monde du jeu. **Ne s'emploie jamais pour un changement de langage d'outil** : on dit alors une *migration*. |
| grid | grid | **Le nom technique est `grid`, en français comme en anglais.** La liste de tous les sujets sur la page des sprites : une `tile` par sujet, le minimum d'information, rien d'autre. |
| tile | tile | **Le nom technique est `tile`.** Un élément de la `grid` : l'image principale d'un sujet, son nom, **son statut** et le compte de ses variants dessinés. Le statut est celui de l'ensemble de ses variants, et le plus dû l'emporte — à reprendre, écarté, à produire, à juger, validé. Ne pas confondre avec la **case** du monde, qui est une unité de la carte du jeu. |
| FSP | full screen popin | La popin plein écran : ce qui s'ouvre par-dessus la page au clic sur une vignette, occupe tout l'écran, et se ferme par une croix en haut à droite. Sur la page des sprites, la FSP d'un sujet porte ses variants, leurs versions, la comparaison et les actions. |
| drawer | drawer | **Le nom technique est `drawer`, en français comme en anglais** — on ne le traduit jamais dans le code ni dans une conversation ; « tiroir » ne sert qu'à l'expliquer. Le panneau accolé au bord droit de l'écran, qui s'ouvre **à côté** de ce qu'on regarde sans jamais le recouvrir : la page ouverte se resserre d'autant. Sur la page des sprites, le tiroir porte le texte d'une version — sa consigne ou son rapport — pendant que l'image reste visible. Il se ferme par sa croix ou par la touche d'échappement, qui le ferme lui avant la FSP. |
| inventaire des sujets | subject inventory | Le fichier `assets/subjects.json`, qui déclare types, sujets, variants et images produites ; il fait foi, tous les outils y lisent. |
| HDC | — | Abréviation d'usage, en conversation seulement, pour l'herbe de clairière (`TR-064`). |
| HH | — | Abréviation d'usage, en conversation seulement, pour les herbes hautes (`TR-062` et les sujets à venir). |
| référentiel | reference set | Un ensemble de références tenu à jour, toujours qualifié — l'inventaire des sujets, le référentiel technique —, jamais employé seul. |
| tuile de sol | ground tile | Une image de matière répétable bord à bord. |
| détourage | cutout | Le retrait du fond de fabrication, qui transforme l'image produite en image à fond transparent. |
| fond de fabrication | key color | Le magenta pur sur lequel le générateur pose le sujet, et qui n'existe dans aucune matière du monde. |
| génération d'image | image generation | L'acte de demander une image au générateur et de la recevoir, distinct de la *chaîne de production* qui l'entoure. **Toujours qualifié** : le jeu générera aussi des cartes, des noms, des plans — « génération » seul ne dit pas ce qu'on génère. |
| chaîne de production | production pipeline | L'enchaînement description → consigne → génération → livrable → contrôles → inventaire des sujets. |
| planche-contact | contact sheet | La page de revue qui rassemble un lot produit, avec sa note et le motif de chaque défaut. |
| reprise | retry | La seconde et dernière tentative accordée à une image jugée fautive. |
| mise en défaut | flagged | L'état d'une image qui a échoué deux fois : elle est écartée, signalée, et n'arrête pas le reste du lot. |

Terme en attente : **tracé** — forme anglaise provisoire (`trace`), à confirmer avec quelqu'un dont c'est le métier.

## Les acronymes du projet

**Un acronyme se donne toujours avec son terme**, écrit en toutes lettres puis le sigle entre parenthèses — « la projection parallèle à 60 degrés de plongée (PA60) ». Règle de la méthode commune,
donnée par l'opérateur le 2026-08-07 : il abrège quand il écrit vite, et les deux formes ne se rejoignent que si l'agent donne les deux.

| Sigle | Ce qu'il désigne |
|---|---|
| PA60 | La projection parallèle à 60 degrés de plongée — l'angle de prise de vue du monde, valeur unique du projet ([angle de vue](conception/referentiels/visuel/angle-de-vue.md)). |
| RS | Le serveur de revue — `review-server/`, les pages servies en local sur lesquelles l'opérateur relit le travail. |
| CDS | Le centre de soin, sujet `BT-001`. |
| HDC | L'herbe de clairière, sujet `TR-064`. |

## Les valeurs de type, en anglais depuis le 2026-08-12

**Une valeur de type est du code** — le programme la compare, la trie et l'indexe —, donc elle est en anglais ; **le libellé affiché reste français**, et il vit
ailleurs. Traduction figée, pour que personne n'en réinvente une seconde : `ground`, `path`, `stream`, `bridge`, `fence`, `tree`, `grove`, `grass`, `building`,
`human`, `creature`.

**ATTENTION À DEUX HOMONYMES QUI N'ONT PAS BOUGÉ** : le **calque** `sol` garde son nom — c'est une autre notion que le type `ground` —, et les **répertoires** du
disque (`assets/cutout/sol/`, `poc/batiment/`…) viennent du préfixe du code, pas du type : ils sont encore en français, et les renommer déplace des fichiers.

## Termes bannis

Un mot est banni quand il désigne plusieurs choses à la fois, ou quand il porte un sens venu d'ailleurs qui ne vaut pas ici. Un terme banni ne s'emploie **nulle part** — ni dans les documents, ni dans
le code, ni dans les échanges.

| Terme banni | À employer à la place | Pourquoi |
|---|---|---|
| entité | sujet | Côté fonctionnel, une entité désigne aussi des éléments sans image ; on ne sait plus si l'on parle d'une règle ou d'une image. |
| garniture | composition d'un sujet | Ne disait pas de quoi il parlait. Employé une journée, jamais compris. |
| tuile | case, ou tuile de sol | Seul, il se confond avec la *case* de la grille ; il ne s'emploie qu'accompagné, dans *tuile de sol*. |
| tir | génération d'image | Hérité du tirage photo, il suppose un original dont on tire une épreuve, alors qu'ici l'image naît de la description. |
| axe, et tout équivalent — dimension, facette | variant | Inventait une notion de plus au-dessus du variant, laissait croire à un mécanisme à part, et a conduit à en construire un second là où le premier suffisait. Un sujet a des variants, un type dit lesquels, il n'y a rien d'autre à nommer. |
| variante, au féminin | variant, au masculin | En français, c'est **un variant** : le mot couvre tous les aspects sous lesquels un sujet se décline, mouvement et densité compris, et non les seules apparences d'une même chose. |
| adresse | ref | Évoquait un chemin de fichier, alors qu'une ref désigne une chose du modèle, où qu'elle soit rangée. |
| contrôleur | validateur, ou script | N'existe pas dans ce projet, qui n'a que des scripts et des validateurs. |
| fiche | la description d'un sujet, ou son entrée à l'inventaire | Désigne indifféremment la description, l'ensemble des informations d'un sujet, celles d'un variant ou celles d'une sprite : on ne sait jamais laquelle. |
| sujet, pour ce qu'il reste à faire | **task**, ou **topic** quand c'est un sujet de discussion — **et ces deux mots ne se traduisent jamais** : on dit « une task », « un topic », en français comme ailleurs (opérateur, 2026-08-12 : « ça doit être indiqué qu'en FR, ça reste ces mots-là aussi, faut pas commencer à les traduire »). Jamais « une tâche », jamais « un point », jamais « un sujet ». | Le mot désignait à la fois les choses du monde — un chêne, un chemin — et ce qu'il reste à faire. L'opérateur a cherché des boutons de vote sur la page de la pile le 2026-08-12, et il a fallu trois allers-retours pour découvrir qu'on ne parlait pas de la même page. Les deux pages ont perdu le mot en même temps (règle du dépôt), et la donnée l'avait déjà : `review-server/tasks.json`. « Sujet » ne désigne plus qu'une chose du monde. |
| tracé | sprite, ou pièce d'un assemblage | La notion n'a jamais existé : c'était un dessin SVG, qui ne passait pas par le générateur d'images. Tout ce qui se dessine est une sprite, et une sprite qui se pose bout à bout avec ses voisines est une pièce d'un assemblage. |
| tirer une sprite | générer une sprite, ou la regénérer | **Mot interdit** (opérateur, 2026-08-11 : « tirer est un mot interdit, ce verbe ne veut rien dire en français, tu l'as inventé et tu le réinventes à chaque fois »). Une image se **génère** ; une image refaite se **regénère**. Le verbe n'a jamais désigné quoi que ce soit dans ce projet, et il revenait à chaque séance parce que rien ne l'avait écarté. |
| toile | les dimensions de l'image | Ne nomme rien du modèle : selon la phrase, il désignait la surface de l'image, ses dimensions ou le fichier lui-même. |

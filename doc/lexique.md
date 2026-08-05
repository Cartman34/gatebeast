# Lexique — anglais et français

> Ce lexique est de la **documentation**, pas de la conception : il nomme, il ne décide pas. Les termes propres à la méthode de travail — dont *opérateur* — vivent dans le [glossaire de la méthode](../../conceptions/methode/glossaire.md).

**Intention :** fixer chaque terme important dans les deux langues **au moment où il est créé**, jamais après coup. Une traduction décidée plus tard arrive toujours trop tard : le terme s'est déjà répandu dans le code, les textes et les habitudes.

**Le français fait foi.** C'est la langue dans laquelle les termes sont pensés et arbitrés, et celle de l'interface de la 0.x. L'anglais servira le code, le nom du jeu et l'internationalisation ([vision](../../vision.md)) : à terme, interface et lore existeront dans les deux langues.

**L'anglais est l'anglais américain.** Orthographe américaine sans exception — `center` et non `centre`, `color` et non `colour`, `catalog` et non `catalogue` —, dans le lexique comme dans le code.

Règle : un terme important entre dans le lexique **dès sa création**, avec sa forme française arrêtée et une forme anglaise **provisoire** — marquée d'un astérisque quand elle demande encore confirmation. Une forme anglaise incertaine ne bloque jamais : elle se note, se signale, et se reprend plus tard avec quelqu'un dont c'est le métier. Ce qui est interdit, c'est de créer un terme sans rien noter du tout et de découvrir la question de traduction une fois le mot répandu partout.

| Français | Anglais | Ce que c'est |
|---|---|---|
| créature | gatebeast | Les créatures du jeu, collectivement les *gatebeasts*. |
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

Le vocabulaire de la fabrication et de l'affichage des images. Les décisions qui les portent sont dans [rendu en calques](../technique/rendu-en-calques.md) et [assets](../visuel/assets/index.md).

| Français | Anglais | Ce que c'est |
|---|---|---|
| sujet | subject | Tout élément du jeu qui a une représentation graphique. Le mot **entité** est banni de ce vocabulaire : côté fonctionnel il désigne aussi des éléments sans image. |
| type | type | La sorte de chose qu'est un sujet — arbre, créature, humain, bâtiment, objet, sol, chemin, point de passage. Le type porte les comportements, les évènements et le lot exigé. |
| profil | profile | L'apparence concrète d'un sujet à l'intérieur de son type : `birch-01`, `oak-01`, `asian-01`. Un profil est une apparence et une seule, et une entrée d'inventaire. |
| variante | variant | Une posture précise d'un profil, définie par les axes que porte son type — orientation, action, forme, composition, directions de ses parties. C'est ce qu'on demande au jeu ; elle n'est pas une image mais porte des **représentations**, dont la sprite n'est qu'une possibilité parmi d'autres. |
| image | frame | Un fichier d'une variante, numéroté `frame-01`, `frame-02`… Une posture fixe n'en a qu'un, une marche en a plusieurs. |
| représentation | representation | Ce par quoi une variante se réalise concrètement — une sprite aujourd'hui, un modèle en trois dimensions ou autre chose demain. Une variante porte des représentations, elle n'est jamais elle-même une image. |
| lot | variant set | L'ensemble des variantes exigées d'un profil, fixé par son type et complétable à tout moment. |
| vue principale | base view | La variante de repos, de face : elle existe toujours et sert de référence visuelle à toutes les autres. |
| tracé | trace* | Ce qui s'assemble de case en case en reliant des bords de sa case — clôture, chemin, mur, cours d'eau ; sa forme dit lesquels. |
| forme | shape | Pour un sujet qui se pose bout à bout — clôture, chemin, mur, cours d'eau —, l'ensemble des bords de la case que le tracé rejoint, écrits dans l'ordre `n`, `e`, `s`, `w` : `shape-ns` une ligne, `shape-ne` un angle, `shape-nesw` un croisement. La forme dit où la pièce touche ses voisines, donc elle se vérifie par calcul. |
| composition d'un sujet | subject composition | De quoi une pièce est faite, **à forme égale** : la clôture `shape-ns` existe avec deux poteaux, avec un seul, ou sans aucun, ses lisses toujours identiques. On alterne les compositions le long d'une portée pour que les poteaux s'espacent au lieu de se doubler à chaque jointure. S'écrit dans l'adresse `posts-2`, `posts-1`, `posts-0`. |
| composition d'une scène | scene composition | Quels sujets se placent sur quelles cases d'une grille. Se déclare dans un **plan de composition** avant toute génération. Même mot que ci-dessus, autre échelle : l'un parle d'un plan, l'autre d'une pièce. |
| plan de composition | composition plan | Le plan à plat, vu de dessus, qui déclare une composition de scène case par case et se contrôle avant qu'aucune image ne soit demandée. |
| exemple d'usage | usage sample | Une image unique montrant les pièces d'un sujet **assemblées**, produite pour les comparer entre elles et servir de référence de style. Ce n'est pas une sprite et elle ne se découpe pas. |
| emprise | footprint | Le sol qu'un sujet occupe, en cases. **Toujours écrite**, sans valeur par défaut. |
| point de pose | pose point | Le milieu du bord bas de l'emprise : le point par lequel un sujet est posé dans le monde. Un sujet se pose par ses pieds, jamais par un coin d'image. |
| texture | texture | Ce qui habille une surface sans en changer la forme : le grain du bois, l'écorce, la mousse, les nuances de couleur. Elle se distingue de la **géométrie**, qui dit où sont les volumes. Un plan ou une esquisse portent la géométrie et jamais la texture ; une image générée porte les deux. |
| maître | master | L'image telle que le générateur l'a rendue, conservée pour toujours. |
| livrable | delivered asset | Le maître **exporté** à la définition de livraison. Rien d'autre ne le distingue : il n'est ni rogné ni retouché. |
| garniture | — | **Terme banni.** Employé une journée pour ce qu'on appelle désormais la *composition d'un sujet* ; il ne disait pas de quoi il parlait. |
| orientation | orientation | Comment le sujet est planté sur sa surface, **dans le repère du monde**, à la rose des vents : `south` (face à nous), `north` (de dos), `west` et `east` (de profil), plus les quatre intermédiaires. |
| direction | direction | Où pointe une partie du sujet, **dans le repère du sujet une fois orienté** : les mêmes valeurs, plus `up` et `down`. Convention absolue : `north` = droit devant le sujet, `east` sur sa droite, `west` sur sa gauche, `south` derrière lui. |
| instance | instance | Une **apparition** d'un sujet à un endroit précis d'une scène : le sujet, sa case, sa variante et ce qu'il y fait. Le sujet se décrit une fois, ses instances sont innombrables. |
| partie qui pointe | pointing part | Ce qui porte une direction : le corps (`body`), le regard (`gaze`), et toute partie déclarée par le type — une main, une queue. Une direction non écrite vaut `north`. |
| action | action | Ce que fait le sujet : `idle`, `walk`, `run`, `sit`, `sleep`, `jump`… liste ouverte. |
| repli | fallback | La variante de remplacement quand celle demandée n'existe pas encore. |
| emprise au sol | footprint | Les cases que le sujet occupe au sol. |
| point de pose | anchor | Le point par lequel le sujet est posé dans le monde : le milieu du bord bas de son emprise. |
| calque | layer | L'une des cinq familles d'empilement à l'écran : sol, décor au sol, monde, dessus, interface. |
| élévation | elevation | Le niveau auquel un sujet se tient : le sol, une passerelle, un étage. |
| catalogue d'assets | asset catalog | Le fichier qui décrit chaque profil et chaque variante ; source unique de la génération, des plans et du rendu. |
| tuile de sol | ground tile | Une image de matière répétable bord à bord. Le mot **tuile** seul est banni : il se confond avec *case / tile*. |
| détourage | cutout | Le retrait du fond de fabrication, qui transforme l'image produite en image à fond transparent. |
| fond de fabrication | key color | Le magenta pur sur lequel le générateur pose le sujet, et qui n'existe dans aucune matière du monde. |
| génération d'image | image generation | L'acte de demander une image au générateur et de la recevoir, distinct de la *chaîne de production* qui l'entoure. **Toujours qualifié** : le jeu générera aussi des cartes, des noms, des plans — « génération » seul ne dit pas ce qu'on génère. Le mot **tir**, hérité du tirage photo, est banni : il suppose un original dont on tire une épreuve, alors qu'ici l'image naît de la description. |
| chaîne de production | production pipeline | L'enchaînement fiche → consigne → génération → détourage → contrôles → catalogue. |
| planche-contact | contact sheet | La page de revue qui rassemble un lot produit, avec sa note et le motif de chaque défaut. |
| reprise | retry | La seconde et dernière tentative accordée à une image jugée fautive. |
| mise en défaut | flagged | L'état d'une image qui a échoué deux fois : elle est écartée, signalée, et n'arrête pas le reste du lot. |

Terme en attente : **tracé** — forme anglaise provisoire (`trace`), à confirmer avec quelqu'un dont c'est le métier.

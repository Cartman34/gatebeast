# Comment s'écrit une consigne

**Usage :** ce que lit qui s'apprête à modifier une consigne de génération — le socle partagé de `scripts/asset_common.py`, les clauses assemblées par
`scripts/generate-sprite.py`, ou la description d'un sujet sous `assets/descriptions/`. Il dit où chaque chose s'écrit, ce qu'une clause doit porter, et ce qui n'a
rien à y faire.

**Intention :** une consigne se modifie sous le coup d'une image ratée, donc dans l'urgence et sans que rien ne dise pourquoi la clause d'à côté existe. Deux
conséquences, payées le 2026-08-12 : la clause de caméra a grossi par empilement — trois formulations du même ordre, chacune ajoutée après un échec, si bien
que plus personne ne savait laquelle commandait ; et une clause écrite pour corriger un défaut en a créé un autre parce que son but n'était écrit nulle part.
**Sans ce document, la modification suivante annule la précédente** : c'est la demande de l'opérateur, « faut que ce soit documenté AVANT de faire des modifs,
sinon la prochaine fois tu fais la modif inverse car tu n'as pas expliqué le but, pourquoi ce paramètre, ce qui est attendu, son usage ».

**Ce qu'il ne couvre pas :** ce qu'une consigne doit DIRE d'un sujet — c'est la grille des [paramètres d'un sujet](../parametres-des-sujets.md). Ici, on ne
parle que de la façon de l'écrire.

## Où s'écrit quoi — six niveaux, et un seul par chose

**LES SIX NOMS SONT DES IDENTIFIANTS, DONC ILS SONT EN ANGLAIS**, comme `manager` ou `illustrator` : c'est la règle du dépôt sur les symboles de code, et chacun
est pris à notre propre vocabulaire plutôt qu'inventé. La prose qui les explique reste française — on dit « le `common`, ce socle partagé », jamais l'inverse.

- **`common`** (`asset_common.py`, d'où il tient son nom) porte ce qui est vrai de TOUTE image du monde : le style, la caméra, le fond, le cadrage, les unités,
  et ce qu'on dit à l'agent sur sa façon de travailler. Une clause y est écrite parce qu'elle vaudrait à l'identique pour n'importe quel sujet.
- **`type`** (`assets/subjects.json`, clé `extra_prompt`) porte ce qui est vrai de tous les sujets d'une même famille et faux pour les autres — qu'un chemin
  n'a aucun volume, qu'une créature se présente autrement selon la vue.
- **`variant`** porte ce qui change d'une pièce à l'autre du même sujet : sa forme, son orientation, sa composition.
- **`description`** (`assets/descriptions/`, d'où il tient son nom) porte ce qui n'est vrai que d'un sujet.
- **`parameters`** ([les paramètres d'un sujet](../parametres-des-sujets.md)) porte ce qu'un sujet déclare et que la commande relit au référentiel : ses
  dimensions, son emprise, son point de pose. Ce n'est écrit dans aucune description : ça se corrige au référentiel, ou dans le code qui l'énonce.
- **`call`** porte ce que la ligne de commande apporte pour CET appel-là et pour aucun autre : l'image de référence (`--ref`, `--plate`) et le motif de reprise
  (`--rework`). Ça ne se corrige ni dans un fichier ni dans le code — ça se retape à l'appel suivant.

**DEUX DE CES NOMS EN REMPLACENT UN QUE LE GLOSSAIRE PROSCRIT**, et c'est plus important que la langue. `variant` corrige « variante » au féminin — « en
français, c'est **un variant** », et le mot couvre tous les aspects sous lesquels un sujet se décline. `description` remplace « fiche », qui désigne
indifféremment la description, l'ensemble des informations d'un sujet, celles d'un variant ou celles d'une sprite : on ne sait jamais laquelle.

**UN NIVEAU DIT D'OÙ VIENT LA CONTRAINTE, JAMAIS QUEL BOUT DE CODE A PRODUIT LA CHAÎNE DE CARACTÈRES — et c'est le critère qui tranche les cas douteux.** Une
phrase que la commande écrit elle-même mais qui vaut pour tous les sujets est du `common` : ce n'est le paramètre de rien. C'est le cas des deux sections
adressées à l'agent, celle qui explique comment lire la consigne et celle qui demande la consigne transmise. Les classer d'après le code qui les assemble
enverrait les chercher dans le fichier d'un sujet. **Ce niveau s'appelait `composed` jusqu'au 2026-08-13**, et ce nom disait le mécanisme d'assemblage au lieu
de la nature de ce qui est dit ; le projet portait déjà le bon mot, et un document à son nom.

**LES DEUX DERNIERS NIVEAUX NE SONT PAS UN RAFFINEMENT, ILS DISENT OÙ PORTER LE CORRECTIF.** Corriger dans la description d'un sujet une phrase qui vient de
`parameters` ne change rien — elle revient identique à la version suivante, et sur tous les autres sujets en plus. C'est arrivé trois fois dans la semaine du
2026-08-13, et c'est ce qui a fait écrire le découpage décrit plus bas.

**UNE CHOSE S'ÉCRIT À UN SEUL NIVEAU.** La même contrainte répétée à deux niveaux se contredit dès que l'un des deux gagne une précision : c'est ce qui est
arrivé à la caméra, dite au socle et redite au rappel final dans d'autres mots. Quand un texte doit paraître deux fois — un rappel en fin de consigne, par
exemple —, il est **interpolé depuis un seul endroit**, jamais recopié.

**ET LA CONSIGNE DIT ELLE-MÊME DE QUEL NIVEAU VIENT CHAQUE PASSAGE.** Elle est découpée en sections, chacune ouverte par un titre `Titre (niveau)`, le mot
entre parenthèses étant l'un des six ci-dessus. Un titre nomme une notion en deux ou trois mots : jamais un chiffre, jamais une unité, jamais une explication —
ce qui ressemble à une cote ou à une légende finit dessiné. Les titres sont déclarés une seule fois, dans la table `SECTIONS` de `scripts/generate-sprite.py`,
d'où le gabarit les écrit et où le découpage les relit : il n'y a pas deux vocabulaires à tenir d'accord.

**LES SECTIONS VOISINES QUI PARLENT DE LA MÊME CHOSE SE RASSEMBLENT SOUS UN TITRE DE GROUPE**, écrit d'un cran moins profond et **sans parenthèses** — c'est ce
qui le distingue d'une section, qui, elle, porte toujours son niveau. Un groupe est une **suite contiguë** de la consigne : rassembler ne déplace jamais rien.
C'est d'ailleurs pourquoi on ne groupe **pas** par niveau — les sections d'un même niveau ne se suivent pas, `common` ouvrant la consigne, y revenant pour le
détourage et la fermant par le rappel de caméra —, et l'ordre, lui, porte du sens.

**UN TITRE DE GROUPE NOMME UN THÈME, JAMAIS UNE ORIGINE.** L'origine, c'est le niveau, et il vit sur les sections. Un groupe peut donc parfaitement réunir des
sections de niveaux différents, et deux le font. **Payé avant même d'être écrit** : le groupe qui réunit la description d'un sujet, son orientation et son
action avait été nommé « Ce que dit sa description » — or l'orientation et l'action sont du `variant`, et ce titre aurait envoyé les corriger dans
`assets/descriptions/`, où elles ne sont pas. C'est exactement le coût que ce découpage existe pour supprimer, réintroduit par un titre.

**Et une section seule ne se met pas dans un groupe à elle** : un groupe gagne sa ligne quand il rassemble, sinon il n'est qu'un titre de plus à lire.

**Cela ne serait pas possible sans les deux registres** décrits plus bas : la structure et le nom des niveaux s'adressent à l'agent, pas à son modèle d'images,
et la consigne le lui dit dans sa première section.

## LA CAMÉRA APPARTIENT AU SOCLE, ET AUCUNE SPRITE NE PEUT LA CHANGER

**Règle de l'opérateur, 2026-08-12 : « l'angle, c'est 60°, aucune sprite ne doit pouvoir changer ça, c'est défini dans le socle. La vue caméra ne dépend PAS du
sprite ! »** Elle est la plus dure de ce document, et elle vaut pour tout ce qui décrit une prise de vue : l'angle, la projection, ce qu'on voit d'en haut,
ce qui est écrasé.

**CE QUI EST DONC INTERDIT** dans la description d'un sujet comme dans un motif de reprise : parler de la caméra, même pour la confirmer. Une phrase qui la répète
la déplace — « le dessus de sa couronne domine l'image » a suffi à faire basculer un chêne en vue de dessus, alors que le socle demandait soixante degrés. Le
générateur lit la clause la plus proche du sujet, et une redite proche bat un socle lointain.

**CE QU'ON ÉCRIT À LA PLACE** : ce qui appartient au sujet, et rien d'autre — sa forme, ses proportions, sa matière. Un défaut d'angle sur une image ne se
corrige JAMAIS dans sa description : il se corrige au socle, où il vaut pour tous les sujets à la fois, ou il ne se corrige pas.

## LES MESURES SE DISENT EN CASES — NI PIXEL, NI RAPPORT D'IMAGE, NE SORT D'AILLEURS QUE DU SOCLE

**Règle de l'opérateur, 2026-08-12 : « les calculs de mesure en PX sont interdits dans les descriptions », puis « strictement interdit ».** Le seul endroit d'où un pixel peut partir vers le générateur
est le socle, `scripts/asset_common.py`. Une entrée à l'inventaire, une clause de variant, une description de `assets/descriptions/` parlent en **cases**, et ne convertissent jamais elles-mêmes.

**POURQUOI, ET C'EST LE FOND** : le pixel est le produit d'une projection que le socle détient déjà. Trois mesures y vivent, **interpolées depuis `scripts/tile_scale.py`**, jamais retapées — une case
de large vaut `FILE_TILE_WIDTH` pixels, un mètre de hauteur debout le même chiffre écrasé par `STANDING_HEIGHT_FACTOR`, un mètre de sol qui s'enfonce vaut `FILE_TILE_DEPTH`. Une description qui
convertit refait ce calcul à la main : elle en fige une copie qui dérivera au premier changement d'échelle, et elle peut se tromper de facteur — « 96 pixels de haut » a été écrit le 2026-08-12
pour une porte de deux cases, en appliquant l'échelle du sol à une hauteur. C'est la duplication de valeur pivot que la méthode interdit, appliquée à la consigne.

**ET UN RAPPORT VISUEL EST LE MÊME DÉFAUT, EN PIRE — UNE PROPORTION DU MONDE N'EST PAS UNE PROPORTION DE L'IMAGE.** Sous la plongée, une hauteur debout est écrasée de moitié quand une largeur ne l'est
pas : une porte de **deux cases de haut pour une case de large** apparaît donc **carrée** dans l'image, et un sapin trois fois plus haut que large y paraît une fois et demie plus haut que large. Une
description qui énonce le rapport de l'image se trompe une fois sur deux **tout en ayant l'air précise**, et le générateur suit le rapport plutôt que la mesure. Payé le 2026-08-12 : `BT-002` disait
« deux fois plus haute que large, nettement, et non une ouverture presque carrée » — la phrase **interdisait le résultat juste** et commandait une élévation ; comme la description dimensionnait tout
le bâtiment d'après cette porte, elle faisait basculer l'image entière. `BT-001` et `TR-065` portaient la même faute, et trois générations sont parties dessus.

**CE QU'ON ÉCRIT À LA PLACE** : la mesure dans l'unité du jeu, et rien qu'elle — « deux cases de haut, une case de large », « une case et demie de large ». **Jamais un rapport** : ni « deux fois plus
haute que large », ni « plus haut que large », ni « presque carré ». Le générateur reçoit la correspondance et la projection une fois, par le socle, et déduit lui-même ce que ça donne à l'écran. Une
mesure qui manque au socle s'y ajoute ; elle ne se calcule pas dans la description qui en a besoin.

**ET UN CONTRÔLE LES TIENT** : `php scripts/check-consigne-units.php` balaie les descriptions et les clauses de variant, et signale l'unité de pixel comme la formule de rapport. Ses essais :
`php scripts/dev/trial-consigne-units.php`.

## LE GÉNÉRATEUR COMPLÈTE L'IMAGE POUR ATTEINDRE NOS DIMENSIONS — CE QUI EST TOLÉRÉ, ET CE QUI NE L'EST PAS

**CONSTATÉ LE 2026-08-13** en lisant ce que l'agent a réellement exécuté : il ne dessine pas à nos dimensions, il **complète la toile** par des bandes
transparentes pour les atteindre (`alpha_composite`). Notre contrat de dimensions est donc satisfaissable par du vide, et une chaîne qui mesure la **boîte**
enregistrerait « hauteur tenue » sur une image complétée — l'erreur transparente que les règles du dépôt interdisent.

**DÉCISION DE L'OPÉRATEUR, 2026-08-13** : « c'est acceptable mais uniquement sur la dernière case », puis, précisant : « je parlais de complétion à gauche et à
droite, voire en bas. En haut, la hauteur, on s'en fout un peu, normalement tu es censé mettre une tolérance pour quelque chose d'acceptable ». Ce qui donne
trois règles, et elles ne se confondent pas :

- **AUX BORDS GAUCHE, DROIT ET BAS DE L'IMAGE, LA COMPLÉTION EST TOLÉRÉE JUSQU'À UNE CASE** — le débord de la **rangée SUD de l'emprise**, celle que la clause
  d'assise prévoit déjà pour que la matière se raccorde à ce qui l'entoure. Au-delà d'une case, le sujet n'est pas cadré comme demandé : l'image est refusée.
- **AU BORD HAUT DE L'IMAGE, LA COMPLÉTION N'EST PAS UNE FAUTE EN SOI** : la fourchette de hauteur **est** la tolérance, et elle existe pour ça. Ce qui n'est pas
  toléré, c'est qu'elle cesse de vouloir dire quelque chose.
- **DONC LA HAUTEUR SE MESURE SUR L'ENCRE, JAMAIS SUR LA BOÎTE.** Une boîte se complète à volonté ; l'encre, non. Mesurée sur la boîte, la fourchette laisse
  passer n'importe quoi et le verdict est faux sans que rien ne le dise. **Un bâtiment doit voir sa base occuper la rangée SUD de son emprise** — le pied du mur
  et le seuil y sont visibles, elle n'est laissée ni en sol nu ni en vide.

**CE QUE L'ESSAI `2026-08-13-BT-001` DONNE SOUS CETTE RÈGLE** : 1,67 case de vide au-dessus, 0,27 case en dessous, et **une encre de 11,77 TY pour un plancher à
13,12** — le bâtiment est réellement plus court que le minimum de sa fourchette, et seule la complétion le faisait passer.

## UN ORDINAL SE DONNE TOUJOURS AVEC SON AXE, ET UNE DIRECTION SE DIT EN POINTS CARDINAUX

**Règle de l'opérateur, 2026-08-13 : « quand tu dis dernière ou premier, c'est ambigu, dernier par rapport à quel critère ? ».** Un rang n'existe que le long
d'un ordre, et une consigne en manipule au moins quatre à la fois : la profondeur du monde, la hauteur dans l'image, le fil du texte, et le temps. « La dernière
rangée » se lit aussi bien comme celle du fond que comme celle du premier plan — deux rangées opposées, à deux bouts de l'emprise.

**CE QU'ON ÉCRIT À LA PLACE : le critère, pas le rang.** « La passe envoyée en dernier dans le temps » ; « la clause qui se lit le plus près du sujet ». C'est
plus long de quatre mots et cela ne se lit que d'une façon.

**ET UNE DIRECTION DANS LE MONDE SE NOMME PAR SON POINT CARDINAL, JAMAIS PAR UN CÔTÉ D'IMAGE** (même jour : « tu peux aussi nommer les directions avec les points
cardinaux, comme ça il sait quand tu parles du sud ; c'est plus clair qu'en bas, il ne sait pas si c'est le bas de l'image ou du bâtiment »). « En bas » désigne
trois choses à la fois — le bord de l'image, le pied du sujet, et la rangée d'emprise la plus proche de la caméra —, et le générateur en choisit une. **La
rangée SUD**, **la façade SUD**, **le bord EST de l'emprise** ne désignent qu'une chose, et les points cardinaux sont déjà ceux du socle : X va vers l'est, Y
s'enfonce vers le nord, la caméra regarde depuis le sud. Les orientations du référentiel les emploient déjà (`orientation-south`).

**ET UN NOM QUI SE COMPTE PORTE SON UNITÉ, COMME UN NOMBRE** (même jour, sur « aucune ligne transparente en dessous » : « ligne de case ? peu clair »). Une
ligne, une rangée, un bord se comptent en **cases** ou en **pixels**, et les deux mesures diffèrent d'un facteur quatre-vingt-quatre : une rangée de cases vide
sous un sujet est un défaut grossier, une rangée de pixels vide est un défaut d'un pixel. **On écrit « rangée de cases » ou « rangée de pixels », jamais
« ligne » seule.** C'est le prolongement exact de la règle du référentiel technique — aucun nombre ne s'écrit sans son unité —, appliquée aux noms que l'on
compte.

**CE QUI RESTE DIT EN CÔTÉS D'IMAGE, ET C'EST LA SEULE EXCEPTION** : ce qui parle de **l'image en tant que fichier** — la marge transparente au bord haut, la
matière qui touche le bord bas. Là, il n'y a pas de direction du monde à nommer, et un point cardinal serait faux.

**ET LE GÉNÉRATEUR NE DEMANDE PAS DE PRÉCISION, IL TRANCHE SEUL.** Face à un ordinal sans axe, il en choisit un et dessine — l'erreur ne se voit qu'à l'image,
une génération plus tard. C'est la même famille que la caméra dite « en plongée » sans dire écrasée, et que « projection orthographique » qui laissait passer
une isométrie : une formulation qui a l'air précise et qui autorise deux résultats.

## Ce qu'une clause doit porter — quatre choses, et elles sont toutes obligatoires

Ce sont les quatre que l'opérateur nomme, et l'ordre importe peu :

1. **Le but** — ce que la clause obtient. « L'image se pose sur une case sans se rattraper. »
2. **Pourquoi ce paramètre existe** — ce qui casse sans lui. C'est ce qui empêche la modification inverse six semaines plus tard.
3. **Ce qui est attendu**, en termes vérifiables sur l'image finie : un nombre, une proportion, une chose qu'on voit ou qu'on ne voit pas.
4. **Son usage** — à quels sujets elle s'applique, et à quels sujets elle ne s'applique pas.

**LES QUATRE NE VONT PAS AU MÊME ENDROIT, ET C'EST LE POINT LE PLUS SOUVENT MANQUÉ.** Ce que le générateur lit, c'est **ce qui est attendu**, et rien d'autre.
Le but, la raison et l'usage s'écrivent en **commentaire du code** qui assemble la clause, ou dans ce référentiel. Une consigne qui raconte pourquoi elle
existe est une consigne plus longue, moins claire, et qui décrit un échec passé au lieu de prescrire une image.

## Ce qui ne s'écrit JAMAIS dans une consigne

- **L'historique d'un échec.** « Trois versions ont répondu en dessinant une élévation, refusé par l'opérateur le 11 » n'apprend rien à qui dessine : il lui
  faut la prescription, pas le procès-verbal. L'historique va au commentaire du code, ou au journal des séances.
- **Une justification.** « Parce que sinon le bâtiment paraît flotter » double la longueur sans changer ce qu'il faut dessiner.
- **Un renforcement.** Répéter une clause en majuscules, la redire plus bas « pour être sûr », ajouter « et c'est impératif » : cela n'ajoute pas de contrainte,
  cela ajoute du texte à contredire. **Un ordre est dit une fois, à sa place, positivement.**
- **UNE INTERDICTION, ET C'EST LA RÈGLE LA PLUS RENTABLE DU DOCUMENT** (opérateur, 2026-08-13 : « on doit éviter de lui dire ce qu'il ne faut pas faire, il faut
  être plus précis dans ce qu'on lui dit qu'il faut faire »). Ce n'est pas une préférence de style : une interdiction laisse ouvert **tout le reste**, donc elle
  ne contraint rien. « Ne dessine pas de perspective » autorise encore mille images ; « une face verticale tournée vers la caméra se projette en un rectangle à
  arêtes horizontales et verticales, largeur conservée, hauteur multipliée par 0,5 » n'en autorise qu'une. **Quand on se surprend à écrire « jamais », « aucun »
  ou « est refusé », c'est qu'on n'a pas encore trouvé la prescription** — et c'est elle qu'il faut chercher, pas un interdit de plus.

  **Payé le 2026-08-13** : la clause de caméra interdisait le point de fuite quatre fois, en majuscules, en nommant trois façons de se tromper — et les bâtiments
  revenaient avec des toitures qui convergeaient. Réécrite en disant ce que chaque famille de faces **devient** à l'image, elle n'a plus rien à interdire : un
  rectangle ne converge pas.

## À QUI LA CONSIGNE S'ADRESSE — ET CE N'EST PAS AU MODÈLE D'IMAGES

**LA CONSIGNE EST LUE PAR UN AGENT, QUI LA REFORMULE ENSUITE POUR SON PROPRE MODÈLE D'IMAGES** (opérateur, 2026-08-13 : « le générateur est un agent IA, ce
n'est pas directement le générateur de l'image, lui il reformule la demande à son propre générateur d'image »). Il y a donc **deux lecteurs**, et une réécriture
entre eux que personne ici ne voit.

**Ce que ça change, et c'est considérable :**

- **Le premier lecteur comprend le vocabulaire technique, la structure et le raisonnement.** On peut lui parler de projection orthographique, d'azimut, de
  facteur d'échelle, et lui donner des titres de section : il en tire ce qu'il faut. C'est ce qui justifie la section suivante.
- **Mais rien de ce qu'on écrit n'atteint le modèle d'images tel quel.** Une contrainte survit à la reformulation ou n'y survit pas, et on n'a aucun moyen de le
  savoir autrement qu'en regardant l'image. **C'est l'explication la plus probable d'un défaut qui résiste à une clause pourtant claire** : la clause a été lue
  et comprise, puis perdue en chemin. Constaté sur la projection parallèle, prescrite quatre fois et absente de l'image.
- **Il en découle une conduite** : devant un défaut qui résiste, on ne durcit pas la clause et on n'en ajoute pas une cinquième — on cherche ce qui, dans la
  consigne, **entre en concurrence** avec elle au moment de la reformulation, ou on lui donne à VOIR ce qu'on n'arrive pas à lui faire écrire.

**ET ON PEUT LUI PARLER À LUI, SANS QUE ÇA PARTE AU MODÈLE D'IMAGES** (opérateur, 2026-08-13 : « tu peux donner des consignes à l'agent IA générateur qui ne
seront pas envoyées à son générateur d'image »). Une consigne a donc **deux registres**, et les confondre est ce qui a rendu son écriture si difficile jusqu'ici :

- **Ce qui doit atteindre l'image** — le sujet, sa matière, ses mesures, sa lumière. Tout y est un risque d'être dessiné, donc rien d'inutile n'y entre : ni
  titre de service, ni mot de vocabulaire interne, ni cote destinée à un humain.
- **Ce qui s'adresse à l'agent lui-même** — comment il travaille. Cela ne parvient jamais au modèle d'images, donc cela ne peut pas être dessiné, et les
  précautions du premier registre n'ont pas lieu d'être. Y vont : la structure du document et le nom des niveaux, ce qu'il doit vérifier avant de rendre, ce
  qu'il ne doit surtout pas transmettre à son propre générateur, et la façon de traiter une contradiction s'il en trouve une.

**CE SECOND REGISTRE SERT À CADRER SON INTERPRÉTATION, PAS À LUI SOUS-TRAITER DES CONTRÔLES** (opérateur, 2026-08-13 : « il s'agit plus de contrôler comment il
interprète notre consigne. Si tu lui donnes des consignes de faire un truc qui est mécanisable, on va perdre un contrôle et on va surconsommer des jetons »).
Un contrôle mécanisable reste chez nous : le lui confier nous en priverait — c'est lui qui rendrait le verdict sur son propre travail — et ferait payer en jetons
ce qu'un script fait mieux, gratuitement, et à chaque fois de la même façon. **Ce qui s'y écrit, c'est ce que seul lui peut faire : traduire.**

**LA TRANSPARENCE EST L'EXEMPLE QUI LE MONTRE.** Son modèle d'images ne sait pas produire de fond transparent : il rend un fond plein, souvent magenta, et c'est
**l'agent** qui le détoure ensuite. Cette étape n'est donc ni dans notre chaîne ni dans le modèle — elle est dans son interprétation, et nous n'en voyons ni les
choix ni les ratés. **À terme, cette étape doit revenir chez nous** : ce que nous faisons nous-mêmes se contrôle et se rejoue, ce qu'il fait pour nous se
redemande à chaque génération.

**L'adressage doit être EXPLICITE.** Une instruction de travail glissée sans le dire au milieu de la description sera reformulée avec elle, et pourra donc être
dessinée : c'est ainsi qu'une consigne finit par produire une image portant une légende ou une grille. Chaque registre s'annonce.

**ET ON LUI DEMANDE DE RENDRE VISIBLE SA RÉÉCRITURE** (opérateur, 2026-08-13 : « tu peux lui demander de rapporter la consigne précise qu'il a envoyée à son
générateur, comme ça on peut la stocker et tu peux l'analyser et voir ce qui va ou pas à plus bas niveau »). C'est la première clause du registre « agent », et
elle est exactement de sa nature : elle ne lui sous-traite aucun contrôle, elle rend lisible ce que lui seul fait.

**Ce que ça tranche, et rien d'autre ne le tranche** : devant une image fausse, trois causes très différentes sont aujourd'hui indiscernables — notre consigne
prescrivait mal, la réécriture a perdu la clause, ou le modèle d'images ne l'a pas tenue. Chacune appelle un correctif opposé. Trois jours ont été passés sur la
projection parallèle, prescrite quatre fois et absente de l'image, sans pouvoir choisir.

**Comment ça marche, et pourquoi ainsi** : la consigne lui demande de terminer son dernier message par le texte transmis, entre deux marqueurs ; la chaîne le
relève dans le journal d'événements du générateur et l'écrit en `<nom>.transmitted.txt` à côté de l'image, de la consigne figée et de son découpage. **Par un
message et non par un fichier** : `scripts/generate-image.php` lui interdit d'écrire quoi que ce soit d'autre que son PNG, et c'est cet interdit qui empêche une
génération d'éparpiller des fichiers dans le dépôt.

**TROIS PIÈGES, ET ILS SONT TOUS SILENCIEUX :**

- **Il peut rendre une paraphrase** — « voici en substance ce que j'ai demandé » — au lieu de la chose. La demande dit donc en toutes lettres qu'on attend le
  texte lui-même, intégral, et non un compte rendu. **Rien ne le garantit pour autant** : cela se constate en lisant le fichier, jamais en le supposant. Une
  trace approximative est pire que pas de trace, parce qu'elle a l'air d'une preuve.
- **Le journal contient AUSSI notre propre consigne**, marqueurs compris, puisque la clause qui les demande les écrit. Chercher les marqueurs dans le journal
  entier rendrait nos propres mots comme s'ils étaient sa réponse — une trace qui est un miroir. Seuls ses messages sont lus.
- **La demander peut changer le résultat** : un agent à qui l'on demande de montrer son travail peut le soigner davantage. Ce risque ne s'élimine pas ; il se
  constate en comparant des générations faites avec et sans.

**Une absence n'écrit aucun fichier**, jamais un fichier vide : un fichier vide se lirait comme une réécriture vide, c'est-à-dire comme un fait, alors que la
vérité est qu'on ne sait pas ce qui a été transmis.

**CE QUE ÇA OUVRE** : comparer notre consigne à la sienne **bloc par bloc**, en s'appuyant sur le découpage — et savoir, pour chaque niveau, ce qui survit à la
traduction et ce qui s'y perd. On cesserait alors de réécrire des clauses qui n'arrivent jamais.

## LA TRACE D'UNE CONSIGNE SE RELIT AVEC SON VOCABULAIRE D'ÉPOQUE

**Ce qui accompagne une consigne s'écrit AU MOMENT OÙ ELLE EST FIGÉE, à côté d'elle, jamais dans un registre central** (opérateur, 2026-08-13 : « l'historique
des titres doit être conservé quelque part pour pouvoir relire une consigne générée avec un ancien titre. Ça ne doit pas alourdir l'app »).

**Le geste qui résout les deux exigences d'un coup** : la consigne figée porte déjà ses propres titres, puisqu'elle est la trace exacte de ce qui a été envoyé.
Son découpage écrit à côté d'elle, au même instant, est donc valable pour elle seule et pour toujours. **Chaque version devient auto-descriptive** : elle se
relit avec le vocabulaire de son époque sans que rien n'ait à s'en souvenir.

**Ce qu'il ne faut donc surtout pas construire** : un registre des titres, un historique versionné, une table de correspondance entre l'ancien et le nouveau. Ce
sont des choses à tenir, à migrer et à contredire — et l'application les porterait pour toujours alors que l'information vit déjà à côté de chaque consigne.

**CE QUE PORTE LE DÉCOUPAGE, ET CE QU'IL NE PORTE PAS.** Le fichier voisin est `<nom>.parts.json`, écrit au même instant que la consigne, à côté d'elle — sous
`assets/poc/` pour une consigne figée, sous `var/tmp/consignes/` pour un brouillon. Il donne, pour chaque bloc, **son niveau, son groupe, son titre, son décalage
et sa longueur en octets** ; plus, en tête, la longueur totale et l'empreinte SHA-256 du texte. **Il ne recopie pas la consigne** : une seconde copie du même texte
diverge au premier changement, alors qu'une empreinte de soixante-quatre caractères dit la même chose et ne peut pas se contredire.

**LE PAVAGE EST PLAT, SUR LES SECTIONS, ET LA HIÉRARCHIE EST UN CHAMP** : la ligne de titre d'un groupe appartient à la section qui la suit, si bien qu'il n'y a
toujours qu'une seule suite de blocs et **une seule somme à contrôler**. Paver à deux profondeurs demanderait deux sommes et une règle disant à qui appartient
cette ligne — deux choses de plus à rater, pour rien de gagné : la garantie ci-dessous est aussi forte ainsi.

**LES DEUX GARANTIES QUI L'EMPÊCHENT DE MENTIR**, et il faut les deux : les blocs **pavent** la consigne bord à bord, sans trou ni recouvrement, la somme de
leurs longueurs valant exactement sa longueur — un découpage faux ne pave pas ; et l'**empreinte** le lie à ce texte-là — consigne réassemblée depuis, le
lecteur **refuse** au lieu d'attribuer des phrases au mauvais niveau. C'est le seul défaut sérieux des décalages, la péremption silencieuse, et il est supprimé
plutôt que contourné.

**Les octets, jamais les caractères** : la consigne est de l'UTF-8 et son lecteur est en PHP, où un index de chaîne est un octet. Un décalage compté en
caractères tomberait au milieu du premier « é » et désignerait le mauvais endroit sans rien lever.

**COMMENT ON DEMANDE D'OÙ VIENT UNE PHRASE** — c'est la seule question utile devant une image fausse, et elle a sa commande :

- `php scripts/show-prompt-parts.php <consigne.txt>` — le sommaire : un bloc par ligne, son niveau, son titre, sa première ligne.
- `php scripts/show-prompt-parts.php <consigne.txt> --grep "<phrase>"` — le ou les blocs qui portent cette phrase, sous la forme `groupe › section`, donc de
  quoi elle parle **et où se corrige ce qu'elle dit**.
- `--level common` n'en montre qu'un niveau, `-v` donne le texte entier de chaque bloc, `-h` l'aide.

**Le niveau est écrit deux fois — dans le titre que le générateur lit, et dans le découpage — et c'est délibéré.** Deux énoncés du même fait qu'une commande
peut comparer attrapent une divergence qu'aucun des deux ne montrerait seul ; le contrôle est fait à chaque lecture et ne coûte rien.

## Le vocabulaire d'une consigne — technique, et dans un seul repère

**ON EMPLOIE LES VRAIS TERMES TECHNIQUES : LE GÉNÉRATEUR LES COMPREND** (opérateur, 2026-08-13 : « sors de vrais termes techniques, il comprend »). Écrire
« projection orthographique, azimut zéro, site soixante degrés » vaut mieux que « vu de haut, un peu de face » — le second se lit de dix façons, le premier
d'une seule. Une formulation vague n'est pas plus douce, elle est plus chère : elle se paie en générations qu'on refuse sans savoir pourquoi.

**Ce que ça a coûté** : l'emprise au sol était décrite comme « CE RECTANGLE EST VU DE HAUT », pendant que la façade était demandée « DE FRONT, entière ». Un sol
vu de haut sous une façade vue de face ne se concilie que par un point de fuite : le générateur recevait deux ordres inconciliables et tranchait en dessinant
une perspective. Les deux clauses disent maintenant en quoi chaque face **se projette**, et la contradiction n'existe plus.

**ET UNE GRANDEUR SE DIT DANS UN SEUL REPÈRE.** Le même angle énoncé « soixante degrés sous l'horizontale » à un endroit et « site soixante degrés au-dessus du
plan du sol » à un autre donne deux repères contraires sur un même nombre : rien ne dit au lecteur que c'est le même angle, et il n'a aucun moyen de trancher.
Cela vaut pour tout ce qui se mesure — un angle, une hauteur, une profondeur, une part : **un repère, une fois, et tout le reste s'y rapporte.**

## Comment on modifie une consigne

1. **On lit la consigne ASSEMBLÉE avant de la changer** — `python3 scripts/generate-sprite.py <SUJET> <VARIANTE>` sans `--generate` l'écrit sous `var/tmp/`. Une
   clause se juge dans le texte que le générateur reçoit, jamais dans le fichier où elle est écrite : c'est là, et seulement là, que les contradictions se
   voient.
2. **On demande d'où vient la phrase fautive AVANT de chercher où la corriger** — `php scripts/show-prompt-parts.php <consigne.txt> --grep "<phrase>"` rend son
   bloc et son niveau. C'est ce qui évite de corriger au mauvais endroit une clause qui reviendra identique : le geste ne coûte rien et il tranche.
3. **On cherche ensuite si la contrainte existe déjà**, à un autre niveau et dans d'autres mots. Si elle existe, on la reformule au bon endroit ; on n'en ajoute
   pas une seconde.
4. **On reformule, on n'empile pas.** Si la clause a grossi, on la réécrit entière et plus courte, en gardant chaque contrainte distincte qu'elle portait.
5. **On mesure ce qui a bougé partout** — `bash scripts/diff-prompts.sh` compare toutes les consignes déclarées à leur référence figée et dit lesquelles ont
   changé. Une modification au socle touche tout le monde : c'est ce qu'on veut savoir avant de dépenser une génération.
6. **On refige la référence** — `bash scripts/diff-prompts.sh --freeze` — une fois le changement voulu et vérifié, pour que la prochaine dérive involontaire se
   voie.

**ET TROUVER UNE CAUSE N'EST PAS AVOIR TROUVÉ LA CAUSE** (opérateur, 2026-08-12 : « ce n'est pas parce que tu as trouvé une cause qu'il n'y en a pas
d'autres »). Une image fausse peut l'être pour trois raisons à la fois, et corriger la première laisse les deux autres produire le même symptôme au tour
suivant. On lit la consigne assemblée EN ENTIER, une fois la cause trouvée, avant de relancer.

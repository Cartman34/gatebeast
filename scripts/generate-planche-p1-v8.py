#!/usr/bin/env python3
"""Plate P1 countryside, eighth pass — v7's wins are carried unchanged (large doubled crops, multi-tile
oak, majestic clear of the fields). Fixed here, from the v7 report: SP-010 came out a real stag and the
SP-007 pair rabbit-like; the brook was drawn one or two columns off and the bottom road missing — both
are now anchored to each other rather than merely listed; the cottage access ran past its door to the
edge; one surplus conifer. Plus the current standard: light band in the shared base, a size reminder
next to EVERY human (the audit found two of four), and the ground prescribed SURFACE BY SURFACE — "these
ways and nothing else" was not enough on its own."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import RAPPEL_FINAL_FR, preambule_fr, shoot

COMPOSITION = """
CONTRÔLE DE GRILLE — chaque élément est donné par ses coordonnées de case. Place-le EXACTEMENT à ces
cases, avec l'emprise annoncée, remplie jusqu'à ses bords. Un adulte debout fait deux cases : huit cases
valent QUATRE adultes bout à bout.

PLANCHE P1 — CAMPAGNE BOISÉE. Biome : campagne cultivée et vallonnée en plein soleil de fin de matinée,
champs bordés de haies, un verger, de larges prairies d'un vert vif et frais, arbres feuillus aux
couronnes éclairées sur le dessus. Chaleureux, lumineux, saturé.

LE SOL, PRESCRIT SURFACE PAR SURFACE — cinq natures, rien d'autre :
1. TERRE BATTUE CLAIRE : uniquement les six voies listées ci-dessous, une case de large chacune, aux
   bords nets sur l'herbe.
2. EAU VIVE : uniquement le ru, une case de large, sur la seule colonne 14.
3. CULTURES : les quatre parcelles listées plus bas, chacune remplissant son rectangle.
4. TOITS ET BÂTI : les quatre emprises bâties listées plus bas.
5. PRAIRIE VERTE : TOUT LE RESTE DE LA PLANCHE, d'un seul tenant — une herbe unie et lumineuse qui
   court sous les arbres, entre les champs, autour de chaque bâtiment et jusqu'aux quatre bords.
   Aucune autre bande de terre nue, aucune ornière, aucun sentier de traverse, aucune trace de passage :
   là où il n'y a pas une des quatre premières natures, il y a de l'herbe.

LES DEUX AXES DU BAS SE PLACENT L'UN PAR RAPPORT À L'AUTRE — c'est ce qui a échoué au passage précédent,
alors lis-les ensemble avant de tracer :
- LA ROUTE DU SUD descend la COLONNE 12, de (12,16) jusqu'au BORD BAS en (12,24). Terre battue claire.
- LE RU descend la COLONNE 14, du BORD HAUT (14,1) au BORD BAS (14,24). Eau vive et claire.
- ILS SONT PARALLÈLES ET SÉPARÉS D'EXACTEMENT UNE CASE DE PRAIRIE : entre la route en colonne 12 et le
  ru en colonne 14, il y a la seule colonne 13, en herbe. Route à gauche, ru à droite. Les deux
  atteignent le bord bas et y sont visiblement coupés. Le PONT DE PIERRE en (13,16)-(15,16) porte la
  route principale par-dessus le ru : c'est le seul endroit où quelque chose franchit le ru.

VOIES — EXACTEMENT ces six et rien d'autre, terre battue claire, une case de large :
1. ROUTE PRINCIPALE, rangée 16, du BORD GAUCHE (1,16) au BORD DROIT (32,16), coupée par les deux bords.
2. ROUTE DU SUD, colonne 12, de (12,16) au BORD BAS (12,24).
3. DESSERTE DE LA FERME, colonne 8, de (8,16) à (8,12), s'arrêtant À la porte en (8,11).
4. DESSERTE DE LA GRANGE, colonne 19, de (19,15) à (19,10), s'arrêtant À la double porte en (19,9).
5. DESSERTE DU MOULIN, colonne 28, de (28,16) à (28,11), s'arrêtant À la porte en (28,10).
6. DESSERTE DE LA CHAUMIÈRE, colonne 17, de (17,16) à (17,18), s'arrêtant NET À la porte en (17,19).
   ELLE NE VA PAS PLUS LOIN : sous la chaumière et de part et d'autre, c'est de la prairie jusqu'au
   bord bas. Aucune voie ne longe ni ne contourne la chaumière.
Chaque bâtiment est ainsi relié au réseau : sa desserte part de la route principale et va à sa porte.

BÂTIMENTS — chaque porte NETTEMENT PLUS HAUTE qu'un adulte debout, murs et toits ÉCLAIRÉS :
- FERME, (2,2)-(13,11) : douze cases sur dix — six adultes de large. Pierre claire et colombage, toit de
  tuiles chaudes, cheminée, porte sur sa face basse en (8,11). Usée, entretenue.
- GRANGE, (15,3)-(24,9) : dix sur sept — cinq adultes de large. Bardage rouge, double porte en (19,9)
  de trois cases de haut, fenil.
- MOULIN, (26,4)-(31,10) : moulin rond en pierre claire à quatre ailes, porte sur sa face basse en
  (28,10).
- CHAUMIÈRE, (15,19)-(23,24) : neuf sur six visibles, coupée par le bord bas. Toit de chaume doré,
  porte sur sa face haute en (17,19).

CULTURES — larges et nombreuses, rangs bien alignés sur les axes de la grille :
- GRAND POTAGER clos de haies basses, (1,12)-(7,15) : sept cases sur quatre, soigné, TOUS les rangs
  plantés — choux pommés, salades, fanes de carottes, rames de haricots, en bandes nettes alternées.
- CHAMP DE LÉGUMES, (2,19)-(7,22) : six sur quatre, en pleine terre sans clôture, rangs droits de
  courges à gros feuillage et de poireaux, soigné, plein.
- CHAMP DE BLÉ MÛR, (24,11)-(27,15) : quatre sur cinq, épis dorés en plein soleil, plein. Il ne touche
  aucune voie.
- VERGER MÊLÉ, (24,17)-(31,23) : arbres tous adultes, chacun d'une hauteur et d'une couronne
  différentes — deux pommiers à 80 % de fruits, un poirier à 50 %, un prunier à 30 %, un cerisier en
  fleurs sans fruits, un cognassier à 20 %.
- HAIES taillées le long de (2,17)-(7,17) et de (15,12)-(18,12).

RAPPEL D'ÉCHELLE, AU MILIEU DE LA CONSIGNE : un adulte DEBOUT fait ENTRE 1,75 ET 2 CASES, moins d'un
douzième de la hauteur de l'image. Les humains SEMBLENT PETITS dans la campagne, comme des figurines.
La façade de la ferme fait SIX FOIS la hauteur d'un adulte debout.

VÉGÉTATION — LE GRAND CHÊNE est un ARBRE MULTI-CASES : son EMPRISE AU SOL couvre TROIS CASES SUR TROIS,
de (9,17) à (11,19), tronc massif au centre et houppier dense débordant encore au-dessus de cette
emprise ; adulte, vieux, feuillage dense et éclairé sur le dessus. Trois bouleaux fins, chacun d'une
hauteur différente, en (3,18), (16,14), (30,2). EXACTEMENT DEUX conifères sombres, pas un de plus, en
(1,8) et (32,12) — aucun ailleurs, et aucun dans le verger. Partout ailleurs : prairie, semée de touffes
d'herbe, de fleurs des champs et de cailloux clairs dans la limite d'habillage d'une case sur trois.

OBJETS — trois meules de foin de tailles différentes en (22,10), (22,15) et (23,13), aucune sur une voie
ni dans une culture ; un PUITS de pierre à petit toit couvrant (16,10)-(17,10), deux cases ; une
CHARRETTE à demi chargée de sacs couvrant (10,15)-(11,15), deux cases ; un abreuvoir plein en (12,13),
au bord du ru, hors de l'emprise de la ferme.

HABITANTS — chacun cité de sa fiche, dessiné EXACTEMENT ainsi, et chacun PETIT dans la scène :
- (9,13), DEBOUT — ENTRE 1,75 ET 2 CASES, pas plus — fourchant du foin, REGARDANT DROIT VERS LE BAS
  face caméra, visage bien visible : homme d'une quarantaine d'années, peau brun foncé, cheveux noirs
  très courts, carrure large, tunique de travail brun terre aux manches retroussées, bottes solides,
  visage ouvert et buriné.
- (18,16), DEBOUT — ENTRE 1,75 ET 2 CASES — portant un panier de pommes, marchant vers la GAUCHE sur la
  route : femme de la trentaine, traits d'Asie de l'Est, cheveux noirs en chignon bas, silhouette mince,
  tablier rouille sur un chemisier crème, portant ses charges avec l'aisance de l'habitude.
- (28,12), DEBOUT — ENTRE 1,75 ET 2 CASES — sur la desserte devant la porte du moulin, un sac de farine
  à ses pieds, REGARDANT VERS LE BAS : vieil homme à la peau claire poudrée de farine, cheveux gris et
  sourcils gris épais, maigre et légèrement voûté, chemise de lin pâle, tablier de toile noué haut.
- (20,16) et (21,16), deux enfants NETTEMENT PLUS PETITS que les adultes — environ 1,25 case — courant
  vers la DROITE : un enfant d'environ neuf ans, peau brune, courtes boucles sombres, pieds nus,
  vêtements de jeu simples — et un enfant d'environ sept ans, peau claire, cheveux blonds ébouriffés,
  blouse verte, vif et rieur.
- (24,16), une case, REGARDANT DROIT VERS LE BAS face caméra, pas en diagonale : SP-001, petit
  quadrupède rond de la taille d'un renardeau, fourrure ambre chaud sur le dos et la tête, ventre et
  museau crème, quatre pattes courtes aux pieds crème, deux grandes oreilles RONDES, ambre dehors et
  crème dedans, grands yeux sombres amicaux, queue courte et épaisse à bout crème — une CRÉATURE
  INVENTÉE aux formes de figurine : corps plus rond, museau plus court et oreilles plus rondes que celles
  d'un renard réel. Sa rune, un seul trait au milieu du front : une ARCHE, turquoise.
- (26,20), une case, endormi en boule sous un arbre du verger : SP-004, créature basse et dodue couverte
  d'une fourrure de mousse, en forme de pierre arrondie, large visage calme, oreilles minuscules, pattes
  invisibles au repos. Sa rune, un seul trait sur le flanc gauche : une VAGUE, vert d'eau.
- (13,14), SUR LA BERGE du ru, les pattes avant DANS L'EAU touchant le fond, tête baissée pour boire,
  REGARDANT VERS LA DROITE : SP-008, créature échassière aux longues pattes fines, haute comme la
  poitrine d'un humain, peau lisse et mate couleur sable à pommelures discrètes, corps ovale compact,
  petite tête sur un cou courbé, courte queue en fouet. NI plumes NI fourrure. Sa rune, un seul trait sur
  le poitrail : un S ALLONGÉ, bleu-vert.
- (8,18), assis, et (8,19), trottant vers la DROITE : deux individus de l'espèce SP-007 — créature fine
  gris argenté au corps souple et agile, grands yeux ronds, fourrure courte et dense, museau court
  arrondi, PETITES OREILLES RONDES posées bas sur le crâne, pattes fines à larges doigts, et surtout une
  LONGUE QUEUE ANNELÉE portée en panache derrière elle, aussi longue que son corps — c'est sa queue qui
  la définit. Elle n'a NI longues oreilles dressées, NI oreilles tombantes, NI arrière-train de lapin :
  rien d'un lapin, rien d'un chat. Le premier, plus grand et plus foncé, porte sa rune au bout de la
  queue : une GOUTTE, rose. Le second, plus petit et plus pâle, au même endroit : une BOUCLE CROISÉE,
  rose pâle.
- LA CRÉATURE MAJESTUEUSE, (9,21)-(10,22), DEUX CASES au sol, debout calmement dans la prairie ouverte
  entre le chêne et la route du sud, loin des voies et des cultures, tête haute, REGARDANT VERS LA
  GAUCHE : SP-010, grand être au pelage ambre profond, crinière de longs poils pâles le long du cou,
  pattes fines et fortes, queue en long pinceau, et de larges bois dorés pâles ramifiés s'élevant bien
  au-dessus de lui. SA SILHOUETTE EST INVENTÉE, ce n'est PAS un cerf réel : les bois se COURBENT VERS
  L'INTÉRIEUR et se referment en COURONNE au-dessus de sa tête au lieu de s'ouvrir en ramure, le museau
  est COURT ET ARRONDI comme celui d'une figurine, le corps est compact et sculpté. Aucun cerf réel
  copié, aucun bois de cerf réaliste. Sa rune, un seul trait sur l'épaule gauche : une COURONNE OUVERTE
  à trois pointes d'un seul geste, or pâle.
"""

FIN = "\nRien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.\n"

if __name__ == "__main__":
    sys.exit(shoot("p1-campagne-v8", preambule_fr("UNE CASE SUR TROIS") + COMPOSITION
                   + RAPPEL_FINAL_FR + FIN))

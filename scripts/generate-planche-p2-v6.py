#!/usr/bin/env python3
"""Plate P2 town, sixth pass — v5 was a regression: the tile composition stopped being followed and the
humans grew back. The hypothesis kept here is dilution: on a building-dense biome, a long prose prompt
drowns the scale and grid rules. So this pass hammers scale and grid THREE times (head, middle, tail),
gives every building its size in adults, and drops prose for dry lists. The validated v5 content stays.
New layout decided by the owner: the potter's HOUSE goes north and the LOW workshop south, so neither
masks the other under the steep camera."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import RAPPEL_FINAL_FR, preambule_fr, shoot

KEY = "p2-bourg-v6"

PROMPT = preambule_fr() + """
CONTRÔLE DE GRILLE — À TENIR SUR TOUTE LA PLANCHE. Chaque élément ci-dessous est donné par ses
coordonnées de case. Place-le EXACTEMENT à ces cases, avec l'emprise annoncée, remplie jusqu'à ses
bords. Rien n'est implanté librement, rien n'est déplacé « pour mieux composer ». Une taille se donne
aussi en ADULTES DEBOUT : un adulte debout fait deux cases, donc huit cases valent quatre adultes mis
bout à bout. Compare chaque bâtiment aux humains que tu dessines : si un adulte fait plus du quart de
la largeur d'une façade de huit cases, c'est faux.

PLANCHE P2 — BOURG. Biome : petit bourg marchand dense mais VERT. Pavés RÉSERVÉS à la place et aux
rues ; tout le reste du sol est de l'HERBE VERTE vive, avec des plates-bandes fleuries et des potagers
de pied de mur. Pierre chaude, colombage, tuiles ; chaque bâtiment distinct par sa forme, sa hauteur,
son toit, sa couleur. Image LUMINEUSE : soleil franc, OMBRES COURTES ET CLAIRES, aucun recoin sombre,
aucune ruelle noire. Couleurs riches : façades colorées, toits chauds, herbe franche.

RACCORDS DE BORD — trois rues pavées d'une case de large, chacune VISIBLEMENT coupée par son bord :
1. rangée 16, atteignant le BORD GAUCHE en (1,16) ;
2. rangée 8, atteignant le BORD DROIT en (32,8) ;
3. colonne 18, atteignant le BORD BAS en (18,24).

VOIES — EXACTEMENT celles-ci et RIEN D'AUTRE, une case de large, pavées :
- rue 1 : (1,16) à (18,16) ;
- rue 3 : (18,24) à (18,8) ;
- rue 2 : (18,8) à (32,8) ;
- bande devant les échoppes : le long de la rangée 7, de (20,7) à (31,7), jointe à la rue 2 ;
- accès maison du potier : (19,12) à (23,12), s'arrêtant À la porte en (24,12) ;
- accès atelier : (19,20) à (25,20), s'arrêtant À la porte en (26,20) ;
- accès des trois maisons mitoyennes : (4,17), (8,17), (12,17), un pas depuis la rue 1 ;
- accès lavoir : (4,13) à (4,15).
Seules ces voies et la place sont pavées. Aucune autre ruelle, aucun sentier, aucune ornière.

PLACE — dallée, (10,9)-(17,15). FONTAINE RONDE de pierre en (13,11)-(14,12), eau claire.
ÉTALS — deux, auvent rayé sur poteaux, DEUX CASES chacun : (11,10)-(12,10), à moitié plein de légumes ;
(16,10)-(17,10), à moitié plein de rouleaux d'étoffe.

BÂTIMENTS — tous droits sur la grille, tous différents, chaque porte NETTEMENT PLUS HAUTE qu'un adulte :
- HALLE COUVERTE, (2,1)-(9,8) : huit cases sur huit — quatre adultes de large sur quatre de profond.
  Charpente ouverte sur poteaux trapus, toit de tuiles pentu, caisses à moitié pleines dessous. Usée,
  entretenue.
- LAVOIR PUBLIC, (3,10)-(6,12) : quatre cases sur trois — deux adultes de large. Bassin de pierre sous
  un toit ouvert, eau claire, linge sur la margelle. Ouvert, pas une habitation : la règle des huit
  cases ne s'y applique pas.
- TROIS ÉCHOPPES MITOYENNES, (20,1)-(31,6), COUPÉES PAR LE BORD HAUT : douze cases de large en tout —
  six adultes bout à bout. À gauche une BOULANGERIE, enduit crème, vitrine garnie de pains, porte en
  (22,6) ; au centre une FORGE, bois sombre, devanture ouverte sur le foyer rougeoyant, enclume dehors,
  porte en (26,6) ; à droite une AUBERGE, rez-de-chaussée de pierre, potence d'enseigne sans texte,
  porte en (30,6). Leurs portes donnent sur la bande de la rangée 7.
- MAISON DU POTIER, (24,10)-(31,17) : huit cases sur huit — quatre adultes de large. Enduit ocre clair,
  toit de tuiles, deux étages, porte sur sa FACE GAUCHE en (24,12), desservie par son accès.
- ATELIER DU POTIER, (26,18)-(31,23), ACCOLÉ à la maison par un mur mitoyen : six cases sur six — trois
  adultes de large. C'est un ATELIER, pas une habitation : la règle des huit cases ne s'y applique pas.
  Il est BAS, UN SEUL NIVEAU, toit presque plat : L'ATELIER NE MASQUE PAS LA MAISON,
  ET LA MAISON NE MASQUE PAS L'ATELIER — on voit les deux entièrement. Brique, large porte d'atelier sur
  sa FACE GAUCHE en (26,20), étagères de poteries visibles, cheminée de four qui fume doucement sur son
  FLANC DROIT pour ne rien cacher.
- DEUX MAISONS MITOYENNES, (2,18)-(13,24), COUPÉES PAR LE BORD BAS : douze cases de large ensemble —
  six adultes. Maison de pierre aux volets verts, porte en (4,18) ; maison ocre plus haute à balcon,
  porte en (8,18) ; portillon de cour commun en (12,18).

RAPPEL D'ÉCHELLE, AU MILIEU DE LA CONSIGNE — relis-le avant de dessiner le moindre habitant : un adulte
DEBOUT fait ENTRE 1,75 ET 2 CASES, moins d'un douzième de la hauteur de l'image. Les humains SEMBLENT
PETITS dans le bourg, comme des figurines. Une façade de huit cases fait QUATRE FOIS la hauteur d'un
adulte debout. Vérifie chaque coordonnée déjà posée avant de continuer.

VÉGÉTATION — généreuse : herbe verte vive sur tout le sol non pavé ; trois arbres adultes et denses,
d'espèces différentes, en (10,17) et (21,10) en bac de pierre, et en (21,22) en pleine herbe ;
plates-bandes fleuries au pied des façades ; potager de pied de mur contre la maison du potier en
(24,18)-(25,19) ; jardinières aux fenêtres. Le tout dans la limite d'habillage.

OBJETS — CHARRETTE À BRAS à moitié chargée de sacs, deux cases, (15,16)-(16,16) ; caisses empilées en
(9,9) ; PUITS PUBLIC à petit toit et seau, deux cases, (19,15)-(20,15) ; deux tonneaux en (29,7).

HABITANTS — chacun cité de sa fiche, dessiné EXACTEMENT ainsi, et chacun PETIT dans la scène :
- (13,13), DEBOUT — ENTRE 1,75 ET 2 CASES, pas plus — remplissant une cruche à la fontaine, REGARDANT
  DROIT VERS LE BAS face caméra, visage bien visible : femme corpulente d'une cinquantaine d'années,
  peau brune chaude, cheveux noirs sous un fichu blanc, tablier fariné sur une robe prune, avant-bras
  solides, visage rieur.
- (26,7), DEBOUT — ENTRE 1,75 ET 2 CASES — martelant à l'enclume devant la forge, REGARDANT VERS LE
  BAS : homme large d'une quarantaine d'années, peau foncée, crâne rasé, barbe épaisse, lourd tablier
  de cuir sur un torse musclé nu, manchettes de cuir aux poignets.
- (17,12), DEBOUT — ENTRE 1,75 ET 2 CASES — au bord de la place, la surveillant, REGARDANT VERS LA
  GAUCHE : grande femme de la trentaine, peau olive, cheveux sombres en tresse serrée, uniforme simple
  de cuir et d'étoffe bleu ardoise à petite épaulière, bâton simple, expression posée et attentive.
- (11,11), DEBOUT — ENTRE 1,75 ET 2 CASES — arrangeant ses légumes à l'étal, REGARDANT VERS LA GAUCHE :
  homme aux traits d'Asie de l'Est, cheveux striés de gris, tablier de toile.
- (24,20), DEBOUT — ENTRE 1,75 ET 2 CASES — sortant de l'atelier une pile de bols, marchant vers la
  GAUCHE sur son accès : jeune homme d'une vingtaine d'années, peau claire tachée de son, cheveux roux
  bouclés, blouse tachée d'argile, mains fines et vives.
- (16,16) et (17,16), deux enfants NETTEMENT PLUS PETITS que les adultes — environ 1,25 case — se
  poursuivant vers la DROITE sur la rue 1 : un enfant d'environ neuf ans, peau brune, courtes boucles
  sombres, pieds nus, vêtements de jeu simples — et un enfant d'environ sept ans, peau claire, cheveux
  blonds ébouriffés, blouse verte, rieur.
- (12,15), une case, somnolant contre le socle de la fontaine : SP-001, petit quadrupède rond de la
  taille d'un renardeau, fourrure ambre chaud sur le dos et la tête, ventre et museau crème, quatre
  pattes courtes aux pieds crème, deux grandes oreilles rondes ambre dehors et crème dedans, grands yeux
  sombres amicaux, queue courte et épaisse à bout crème. Sa rune, un seul trait au milieu du front : une
  ARCHE, turquoise.
- (20,16), une case, trottant vers le BAS le long de la rue 3, REGARDANT DROIT VERS LE BAS face caméra,
  pas en diagonale : SP-005, petite créature bleu pâle dressée sur ses pattes arrière, longues oreilles
  souples TOMBANT le long du dos, corps mince, queue à pinceau, museau pointu, pattes avant longues et
  fines — oreilles tombantes et non dressées. Sa rune, un seul trait à la base de l'oreille droite : un
  CHEVRON, orange.
- (6,9), une case, flairant les caisses de la halle, REGARDANT VERS LE HAUT : SP-004, créature basse et
  dodue couverte d'une fourrure de mousse, en forme de pierre arrondie, large visage calme, oreilles
  minuscules, pattes invisibles au repos. Sa rune, un seul trait sur le flanc gauche : une VAGUE, vert
  d'eau.
- LA CRÉATURE MAJESTUEUSE, (14,9)-(15,10), DEUX CASES au sol, debout calmement en haut de la place, tête
  haute, REGARDANT VERS LE BAS : SP-011, grand être élégant au pelage sarcelle profond, collerette de
  fourrure pâle plumeuse autour du cou, une seule corne élancée courbée VERS L'ARRIÈRE depuis le front,
  pattes fines à pieds fourchus, queue en panache portée haut. Calme parmi les gens, tête haute.
  Sa rune, un seul trait le long du cou côté droit : une FLAMME ondulante dressée, argent.
""" + RAPPEL_FINAL_FR + """
Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    sys.exit(shoot(KEY, PROMPT))

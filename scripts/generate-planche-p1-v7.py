#!/usr/bin/env python3
"""Plate P1 countryside, seventh pass — composition carried from v6, with the owner's four corrections:
paths hammered as the ONLY ones, free dressing raised to one tile in three for this biome (Q1A: the
ceiling is per biome), crops larger and more numerous (the kitchen garden widened plus a second
vegetable field), and the oak turned into a multi-tile tree — the new format rule that a tree may
declare a footprint of several tiles like a building. The majestic creature moves clear of the new
field."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PROJECT, TARGET, TOOL, preambule_fr

PROMPT = preambule_fr("UNE CASE SUR TROIS") + """
PLANCHE P1 — CAMPAGNE BOISÉE. Biome : campagne cultivée et vallonnée, champs bordés de haies, un
verger, de larges prairies d'un vert vif et frais, arbres feuillus. Chaleureux, lumineux, saturé.

LES VOIES SONT LA PREMIÈRE CHOSE À TRACER, ET IL Y EN A EXACTEMENT SEPT — CES VOIES-LÀ ET RIEN
D'AUTRE. Aucun autre chemin, sentier, ornière, allée ou passage n'existe dans cette image : toute
autre bande de terre au sol est une faute. Chaque voie fait UNE CASE de large, en terre battue claire,
aux bords nets sur l'herbe.
1. ROUTE PRINCIPALE, le long de la RANGÉE 16, du BORD GAUCHE en (1,16) au BORD DROIT en (32,16),
   visiblement coupée par chacun des deux bords.
2. ROUTE DU SUD, descendant la COLONNE 12 de (12,16) au BORD BAS en (12,24), visiblement coupée par
   le bord bas.
3. DESSERTE DE LA FERME, colonne 8, de (8,16) à (8,11), s'arrêtant À la porte de la ferme.
4. DESSERTE DE LA GRANGE, colonne 19, de (19,15) à (19,10), s'arrêtant À la double porte.
5. DESSERTE DU MOULIN, colonne 28, de (28,16) à (28,11), s'arrêtant À la porte du moulin, qui est sur
   la face basse du moulin en (28,10).
6. DESSERTE DE LA CHAUMIÈRE, colonne 17, de (17,16) à (17,19), s'arrêtant À la porte de la chaumière.
7. LE RU — un ru clair d'une case de large, eau vive, coulant TOUT DROIT le long de la COLONNE 14 du
   bord haut (14,1) au bord bas (14,24). Il ne croise RIEN d'autre : aucun bâtiment, aucun champ,
   aucune desserte. Un PONT DE PIERRE couvre (13,16)-(15,16) et porte la route principale par-dessus,
   ses deux bouts posés sur la route.

Bâtiments — chaque porte fait 2,5 cases de haut, une case de large :
- FERME en (2,2)-(13,11) : douze cases sur dix, pierre et colombage, toit de tuiles, cheminée, porte
  sur sa face basse en (8,11). État : usée, entretenue.
- GRANGE en (15,3)-(24,9) : dix sur sept, bardage rouge, double porte en (19,9) de trois cases de haut,
  fenil.
- MOULIN en (26,4)-(31,10) : moulin rond en pierre à quatre ailes, porte sur sa face basse en (28,10).
- CHAUMIÈRE en (15,19)-(23,24) : neuf sur six visibles, toit de chaume, porte sur sa face haute en
  (17,19).

CULTURES — elles sont LARGES ET NOMBREUSES, elles occupent une vraie part de la planche, rangs bien
alignés sur les axes de la grille :
- GRAND POTAGER clos de haies basses en (1,12)-(7,15) : sept cases sur quatre, soigné, TOUS les rangs
  plantés — choux pommés, salades, fanes de carottes, rames de haricots, alternés en bandes nettes.
- SECOND CHAMP DE LÉGUMES en (2,19)-(7,22) : six cases sur quatre, en pleine terre sans clôture, rangs
  droits de courges à gros feuillage et de poireaux, soigné, plein.
- CHAMP DE BLÉ MÛR en (24,11)-(27,15) : quatre sur cinq, épis dorés, plein — il ne touche aucune voie.
- VERGER MÊLÉ en (24,17)-(31,23), arbres tous adultes, chacun d'une hauteur et d'une couronne
  différentes : deux pommiers à 80 % de fruits, un poirier à 50 %, un prunier à 30 %, un cerisier en
  fleurs sans fruits, un cognassier à 20 %.
- HAIES taillées le long de (2,17)-(7,17) et de (15,12)-(18,12).

Végétation — LE GRAND CHÊNE est un ARBRE MULTI-CASES : son EMPRISE AU SOL couvre TROIS CASES SUR TROIS,
de (9,17) à (11,19), tronc massif au centre et houppier dense débordant encore au-dessus de cette
emprise ; adulte, vieux, feuillage dense. Trois bouleaux fins, chacun d'une hauteur différente, en
(3,18), (16,14), (30,2) ; deux sapins sombres en (1,8) et (32,12), hors du verger. Partout ailleurs : prairie, semée de
touffes d'herbe, de fleurs des champs et de cailloux dans la limite d'habillage d'une case sur trois.

Objets — trois meules de foin de tailles différentes en (22,10), (22,15) et (23,13), aucune sur une
voie ni dans une culture ; un PUITS de pierre à petit toit couvrant (16,10)-(17,10), deux cases ; une CHARRETTE à demi
chargée de sacs couvrant (10,15)-(11,15), deux cases ; un abreuvoir plein en (12,13), au bord du ru, hors de l'emprise de la ferme.

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (9,13), DEBOUT (entre 1,75 et 2 cases), fourchant du foin, REGARDANT DROIT VERS LE BAS face
  caméra, visage bien visible : fermier d'une quarantaine d'années, peau brun foncé, cheveux noirs très
  courts, carrure large, tunique de travail brun terre aux manches retroussées, bottes solides, visage
  ouvert et buriné.
- En (18,16), DEBOUT, portant un panier de pommes, marchant vers la GAUCHE sur la route : femme de la
  trentaine, traits d'Asie de l'Est, chignon bas, silhouette mince, tablier rouille sur un chemisier
  crème, portant ses charges avec l'aisance de l'habitude.
- En (28,12), DEBOUT sur la desserte devant la porte du moulin, un sac de farine à ses pieds, REGARDANT
  VERS LE BAS :
  vieux meunier, peau claire poudrée de farine, cheveux gris et sourcils épais, maigre et légèrement
  voûté, chemise de lin pâle, tablier de toile noué haut.
- En (20,16) et (21,16), deux enfants nettement PLUS PETITS que les adultes, courant vers la DROITE :
  un enfant d'environ neuf ans, peau brune, courtes boucles sombres, pieds nus, vêtements de jeu
  simples, toujours en mouvement — et un enfant d'environ sept ans, peau claire, cheveux blonds
  ébouriffés, blouse verte, vif et rieur.
- En (24,16), une case, REGARDANT DROIT VERS LE BAS face caméra, pas en diagonale : SP-001, petit
  quadrupède rond de la taille d'un renardeau, fourrure ambre chaud sur le dos et la tête, ventre et
  museau crème, quatre pattes courtes aux pieds crème, deux grandes oreilles rondes ambre dehors et
  crème dedans, grands yeux sombres amicaux, queue courte et épaisse à bout crème. Sa rune, un seul
  trait scintillant au milieu du front : une ARCHE, turquoise.
- En (26,20), une case, endormi en boule sous un arbre du verger : SP-004, créature basse et dodue
  couverte d'une fourrure de mousse, en forme de pierre arrondie, large visage calme, oreilles
  minuscules, pattes invisibles au repos. Sa rune, un seul trait sur le flanc gauche : une VAGUE, vert
  d'eau.
- En (13,14), SUR LA BERGE du ru, les pattes avant DANS L'EAU touchant le fond, tête baissée pour
  boire, REGARDANT VERS LA DROITE : SP-008, créature échassière aux longues pattes fines, haute comme
  la poitrine d'un humain, peau lisse et mate couleur sable à pommelures discrètes, corps ovale
  compact, petite tête sur un cou courbé, courte queue en fouet. NI plumes NI fourrure : peau lisse et
  mate. Sa rune, un seul trait sur le poitrail : un S ALLONGÉ, bleu-vert.
- En (8,18), assis, et en (8,19), trottant vers la DROITE : deux individus de l'espèce SP-007 —
  créature fine gris argenté à la LONGUE QUEUE ANNELÉE portée en panache, grands yeux ronds, fourrure
  courte et dense, corps souple et agile SANS AUCUN trait de chat ni de lapin : museau court arrondi,
  petites oreilles rondes, pattes fines à larges doigts. Le premier, plus grand et plus foncé, porte sa
  rune au bout de la queue : une GOUTTE, rose. Le second, plus petit et plus pâle, porte la sienne au
  même endroit : une BOUCLE CROISÉE, rose pâle.
- LA CRÉATURE MAJESTUEUSE en (9,21)-(10,22), DEUX CASES au sol, debout calmement dans la prairie
  ouverte entre le chêne et la route du sud, loin des voies et des cultures, tête haute, REGARDANT VERS
  LA GAUCHE : SP-010, grand être cervidé au pelage ambre profond, crinière de longs poils pâles le long
  du cou, pattes fines et fortes, larges bois dorés pâles ramifiés s'élevant bien au-dessus de lui et se
  courbant vers l'intérieur comme une couronne, queue en long pinceau — silhouette inventée, aucun cerf
  réel copié. Sa rune, un seul trait sur l'épaule gauche : une COURONNE OUVERTE à trois pointes d'un
  seul geste, or pâle.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p1-campagne-v7.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p1-campagne-v7.png", PROMPT], cwd=PROJECT
    ).returncode)

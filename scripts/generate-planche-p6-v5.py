#!/usr/bin/env python3
"""Plate P6 beach, fifth pass — v4's faults, in the operator's order: humans STILL not on the calibrated
scale (so the scale is hammered at the head, next to every human, and again at the very tail), too
empty (38.9% of load — free dressing raised to one tile in three and the coastal planting widened),
luminance far too high (147.7 — bright but never overexposed, deep golden sand, no burnt white), and
ghost paths (the segment list is hammered as exhaustive and repeated at the end). Composition otherwise
carried from v4.

USAGE
  A FROZEN PLATE PROMPT — a historical document, not a command to run again. It produced
  assets/revue-da/planche-p6-plage-v5.png, and its prompt is frozen beside it in
  assets/revue-da/prompt-p6-plage-v5.txt. It is kept so the exact text sent to the generator can be
  read back next to the image it made. It takes no argument and answers no help: there is nothing to
  call it with. Running it would spend a generation on a plate that already exists.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import RAPPEL_FINAL_FR, preambule_fr, shoot

KEY = "p6-plage-v5"

PROMPT = preambule_fr("UNE CASE SUR TROIS") + """
CONTRÔLE DE GRILLE — chaque élément ci-dessous est donné par ses coordonnées de case. Place-le
EXACTEMENT à ces cases, avec l'emprise annoncée. Rien n'est implanté librement. Un adulte debout fait
deux cases : une façade de huit cases vaut QUATRE adultes bout à bout.

PLANCHE P6 — PLAGE. Biome : plage de SABLE DORÉ SOUTENU, dunes, palmiers et plantes littorales, un
appontement de bois, deux cabanes de pêcheurs, mer turquoise lumineuse à écume blanche.
LUMIÈRE — claire et ensoleillée mais JAMAIS SUREXPOSÉE : le sable garde une couleur dorée franche et
chaude, JAMAIS de blanc brûlé, jamais de zone délavée sans matière. L'écume est blanche, le sable ne
l'est pas. Les ombres restent courtes et lisibles.
DENSITÉ — la plage n'est PAS vide : côté terre, le sable est ponctué de bois flotté, de galets, de
coquillages, de touffes d'herbe des dunes et d'algues séchées, dans la limite d'habillage d'UNE CASE
SUR TROIS. Les massifs de plantes littorales couvrent de VRAIES SURFACES, pas des touffes isolées.

RACCORDS DE BORD — deux, chacun un chemin de sable damé d'une case de large, VISIBLEMENT coupé par son
bord :
1. le long de la RANGÉE 20, atteignant le BORD GAUCHE exactement en (1,20) — le chemin arrive
   horizontal, sur l'axe de la rangée 20 ;
2. le long de la COLONNE 26, atteignant le BORD HAUT exactement en (26,1) — vertical, sur l'axe de la
   colonne 26.

CHEMINS — EXACTEMENT CES SEGMENTS ET RIEN D'AUTRE. Aucune boucle, aucun rectangle de chemin, aucune
allée fantôme, aucune trace de pas formant une voie. Toute autre bande de sable damé est une faute :
- (1,20) à (4,20) ;
- colonne 4, de (4,20) à (4,16) ;
- rangée 16, de (4,16) à (15,16) ;
- colonne 26, de (26,1) à (26,12) ;
- rangée 12, de (26,12) à (15,12) ;
- colonne 5, de (5,10) à (5,15) ;
- colonne 15, de (15,11) à (15,16) ;
- rangée 13, de (15,13) à (18,13), vers l'appontement.
LE RIVAGE N'A PAS DE CHEMIN : entre les chemins et la mer, c'est du sable ouvert.

LA MER — turquoise lumineuse à douces lignes d'écume blanche, couvrant (20,14)-(32,21) et toute la
bande basse (1,22)-(32,24). La ligne d'eau traverse le sable en une courbe douce et irrégulière. Des
créatures sont visibles SOUS l'eau par transparence.

L'APPONTEMENT — en bois, (18,13)-(19,22), tablier PLAT AU NIVEAU DE LA PLAGE, planches usées, partant
du sable droit au-dessus de l'eau sur de gros pieux, desservi par le chemin de la rangée 13. Pas de
marches, pas d'entrée surélevée.

BÂTIMENTS — chaque porte NETTEMENT PLUS HAUTE qu'un adulte debout :
- CABANE DE PÊCHEUR 1, (2,2)-(9,9) : huit cases sur huit — quatre adultes de large. Planches blanchies
  par le soleil, toit plat de bois flotté, porte sur sa face basse en (5,9), filets pendus au mur.
  Patinée.
- CABANE DE PÊCHEUR 2, (12,3)-(19,10) : huit sur huit, visiblement différente — murs chaulés, volets
  bleus, toit de tuiles à une pente, porte sur sa face basse en (15,10).

DUNES ET VÉGÉTATION — DUNES douces en (6,12)-(11,15), sable doré aux crêtes couvertes de touffes
d'herbe s'étendant sur plusieurs cases voisines. QUATRE PALMIERS, chacun d'une hauteur et d'une
inclinaison différentes, en (2,11), (10,13), (21,2), (29,4). MASSIFS DE MALCOLMIE DES CÔTES — plantes
littorales basses à petites fleurs lilas, en tapis continus — en (6,12)-(8,13) et (11,18)-(14,20).
MASSIFS D'ARBUSTES LITTORAUX bas et denses en (22,5)-(25,8), (28,8)-(31,11) et (8,2)-(10,4). LAISSE DE
MER — algues brunes séchées et bois flotté blanchi le long de la ligne d'eau — en (20,21)-(23,21).

COQUILLAGES — vides, éparpillés LE LONG DE LA LIGNE D'EAU : amas visibles en (4,21), (9,21), (15,21) et
(24,20), rose pâle et crème, chacun large comme une main.

OBJETS — BARQUE échouée de deux cases en (5,18)-(6,18), coque rayée ; seconde BARQUE échouée plus
vieille, deux cases, en (13,19)-(14,19) ; casiers d'osier empilés en (16,13) et (21,13) ; rochers striés
de blanc en (28,12)-(29,13) et (2,16)-(3,17).

HABITANTS — chacun cité de sa fiche, dessiné EXACTEMENT ainsi, et chacun PETIT dans la scène :
- (10,20), DEBOUT — ENTRE 1,75 ET 2 CASES de haut, pas plus, une figurine dans un grand paysage —
  marchant vers la DROITE sur le chemin : femme de la trentaine, peau brune, boucles noires sous un
  foulard noué, robe bleue sans manches délavée par le soleil, épaules solides, panier de filets tressé
  sur la hanche.
- (19,16), À GENOUX sur l'appontement, lovant un cordage — à genoux, donc NETTEMENT PLUS BAS qu'un
  adulte debout, bien moins d'1,75 case — REGARDANT DROIT VERS LE BAS face caméra, visage bien visible :
  homme d'une quarantaine d'années, peau claire rougie par le soleil, barbe blonde, bonnet de laine
  roulé, chemise bleue rapiécée aux manches retroussées, mains épaisses et burinées.
- (27,8), NETTEMENT PLUS PETIT qu'un adulte — environ 1,25 case — courant vers le BAS sur le chemin de
  la colonne 26, REGARDANT VERS LE BAS : enfant d'environ neuf ans, peau brune, courtes boucles sombres,
  pieds nus, vêtements de jeu simples, toujours en mouvement.
- (7,19), une case, somnolant sur le sable près de la barque, REGARDANT DROIT VERS LE BAS face caméra,
  pas en diagonale : SP-006, quadrupède trapu rouge rouille au dos arrondi en carapace, deux courtes
  cornes émoussées, pattes épaisses, allure lente et lourde. Sa rune, un seul trait au centre de la
  carapace : un ANNEAU FERMÉ, bleu profond.
- (24,18), entièrement SOUS L'EAU, sa silhouette de ruban bien visible par la transparence turquoise,
  ondulant vers la GAUCHE : SP-017, créature-ruban sous-marine longue comme un humain est haut, corps
  plat ondulant comme une bannière, peau jade pâle à bandes plus sombres, quatre petites nageoires de
  gouverne, tête ronde et amicale aux grands yeux sombres, queue en voile translucide. Elle ne perce
  jamais la surface. Sa rune, un seul trait derrière la tête : un MÉANDRE, vert jade lumineux.
- (30,22), NAGEANT EN SURFACE près des rochers, corps à moitié hors de l'eau, se déplaçant vers la
  GAUCHE : SP-009, créature nageuse longue comme un bras, peau lisse olive à ventre plus pâle, queue
  plate en godille dont elle scull, quatre courtes pattes palmées, tête ronde aux petits yeux hauts,
  deux moustaches charnues et souples. Aucune écaille, aucune ouïe, aucune nageoire dorsale. Sa rune, un
  seul trait sur le sommet du crâne : une BOUCLE OUVERTE, cuivre.
- LA CRÉATURE MAJESTUEUSE, (12,13)-(13,14), DEUX CASES au sol, debout sur la crête de la dune, dominant
  la plage, REGARDANT VERS LE BAS : SP-015, grand arpenteur des rivages, blanc nacré moucheté de vert
  d'eau, quatre longues pattes d'échassier, poitrail profond EN CARÈNE, collerette de nageoires
  translucides autour du cou remuant comme des anémones, tête étroite aux yeux sombres et calmes. Jarrets
  articulés VERS L'ARRIÈRE : sa silhouette n'appartient à aucun animal réel. Sa rune, un seul trait sur
  le flanc gauche : une VAGUE DOUBLE, turquoise.

RAPPEL DES CHEMINS, EN FIN DE CONSIGNE : les huit segments listés plus haut sont les SEULS chemins de
l'image. Repasse-les un par un et efface toute autre bande de sable damé.
""" + RAPPEL_FINAL_FR + """
Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    sys.exit(shoot(KEY, PROMPT))

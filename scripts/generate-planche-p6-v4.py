#!/usr/bin/env python3
"""Plate P6 beach, fourth pass — calibrated French standard. Composition carried from v3 (shells,
palms, dunes, flat jetty, exact path network); fixed here: humans on the calibrated scale (v3's fault),
SP-009 hardened against the fish collapse, brightness kept without overexposure (v3 measured 152 of
luminance)."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PREAMBULE_FR, PROJECT, TARGET, TOOL

PROMPT = PREAMBULE_FR + """
PLANCHE P6 — PLAGE. Biome : une plage de sable doré lumineuse, dunes, palmiers et plantes littorales,
un appontement de bois, deux cabanes de pêcheurs, une mer turquoise lumineuse à écume blanche. Claire
et ensoleillée SANS être surexposée : le sable reste doré, jamais blanc brûlé.

Dessine d'abord ces deux raccords de bord — mesure et axe exacts, chacun VISIBLEMENT coupé par son
bord :
1. Un CHEMIN DE SABLE damé, une case de large, LE LONG DE LA RANGÉE 20, atteignant le BORD GAUCHE
   exactement en (1,20) — c'est le raccord avec la planche de la falaise : le chemin arrive horizontal,
   sur l'axe de la rangée 20.
2. Un CHEMIN DE SABLE damé, une case de large, LE LONG DE LA COLONNE 26, atteignant le BORD HAUT
   exactement en (26,1) — le chemin venant des contreforts, vertical sur l'axe de la colonne 26.

Réseau des chemins — EXACTEMENT ces segments et RIEN D'AUTRE — pas de boucles, pas de rectangles de
chemin vides, aucune autre voie : de (1,20) à (4,20) ; remontant la colonne 4 de (4,20) à (4,16) ; le
long de la rangée 16 de (4,16) à (15,16) ; descendant la colonne 26 de (26,1) à (26,12) ; le long de
la rangée 12 de (26,12) à (15,12) ; descendant la colonne 5 de (5,10) à (5,15) ; descendant la colonne
15 de (15,11) à (15,16) ; le long de la rangée 13 de (15,13) à (18,13) vers l'appontement. LE RIVAGE
N'A PAS DE CHEMIN : la plage entre les chemins et la mer est du sable doré ouvert.

La mer — eau turquoise lumineuse à douces lignes d'écume blanche, couvrant (20,14)-(32,21) et toute la
bande basse (1,22)-(32,24). La ligne d'eau traverse le sable en une courbe douce et irrégulière. Des
créatures sont visibles SOUS l'eau par transparence.

L'appontement — en bois, en (18,13)-(19,22) : son tablier PLAT AU NIVEAU DE LA PLAGE, planches usées,
partant du sable droit au-dessus de l'eau sur de gros pieux, desservi par le chemin de la rangée 13.
Pas de marches, pas d'entrée surélevée.

Bâtiments — portes de 2,5 cases de haut, une case de large :
- CABANE DE PÊCHEUR 1 en (2,2)-(9,9) : huit sur huit, planches blanchies par le soleil, toit plat de
  bois flotté, porte sur sa face basse en (5,9), filets pendus au mur. État : patinée.
- CABANE DE PÊCHEUR 2 en (12,3)-(19,10) : huit sur huit, visiblement différente — murs chaulés, volets
  bleus, toit de tuiles à une pente, porte sur sa face basse en (15,10).

Dunes et végétation — douces DUNES en (6,12)-(11,15), sable doré aux crêtes couvertes de TOUFFES
D'HERBE s'étendant sur plusieurs cases voisines ; QUATRE PALMIERS, chacun d'une hauteur et d'une
inclinaison différentes, en (2,11), (10,13), (21,2), (29,4) ; un massif de MALCOLMIE DES CÔTES —
plantes littorales basses à petites fleurs lilas — en (12,18)-(14,19) ; arbustes littoraux en
(23,6)-(25,7) et (30,9)-(31,10).

Coquillages — des coquillages vides éparpillés LE LONG DE LA LIGNE D'EAU : amas visibles en (4,21),
(9,21), (15,21) et (24,20), rose pâle et crème, chacun large comme une main.

Objets — une BARQUE échouée de deux cases en (5,18)-(6,18), coque rayée ; une seconde BARQUE échouée
plus vieille de deux cases en (13,19)-(14,19) ; des casiers d'osier empilés en (16,13) et (21,13) ;
des rochers striés de blanc en (28,12)-(29,13) et (2,16)-(3,17).

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (10,20), DEBOUT (entre 1,75 et 2 cases), marchant vers la DROITE sur le chemin : pêcheuse de la
  côte, la trentaine, peau brune, boucles noires sous un foulard noué, robe bleue délavée sans manches,
  épaules solides, panier de filets sur la hanche.
- En (19,16), À GENOUX sur l'appontement, lovant un cordage — agenouillé, donc nettement PLUS BAS que
  debout — REGARDANT DROIT VERS LE BAS face caméra, visage bien visible : pêcheur d'une quarantaine
  d'années, peau claire rougie par le soleil, barbe blonde, bonnet de laine roulé, chemise bleue
  rapiécée.
- En (27,8), nettement PLUS PETIT qu'un adulte, courant vers le BAS sur le chemin des contreforts,
  REGARDANT VERS LE BAS : enfant d'environ neuf ans, peau brune, courtes boucles sombres, pieds nus.
- En (7,19), une case, somnolant sur le sable près de la barque, REGARDANT DROIT VERS LE BAS face
  caméra, pas en diagonale : SP-006, quadrupède trapu rouge rouille au dos arrondi en carapace, deux
  courtes cornes émoussées, pattes épaisses, allure lente et lourde. Sa rune, un seul trait au centre
  de la carapace : un ANNEAU FERMÉ, bleu profond.
- En (24,18), entièrement SOUS L'EAU, sa silhouette de ruban bien visible par la transparence
  turquoise, ondulant vers la GAUCHE : SP-017, créature-ruban sous-marine longue comme un humain, corps
  plat ondulant comme une bannière, peau jade pâle à bandes plus sombres, quatre petites nageoires de
  gouverne, tête ronde et amicale aux grands yeux sombres, queue en voile translucide. Sa rune, un seul
  trait derrière la tête : un MÉANDRE, vert jade lumineux.
- En (30,22), NAGEANT EN SURFACE près des rochers, se déplaçant vers la GAUCHE : SP-009, créature
  nageuse longue comme un bras, peau lisse olive à ventre plus pâle, queue plate en godille, quatre
  courtes pattes palmées, tête ronde aux petits yeux hauts, deux moustaches charnues. AUCUN trait de
  poisson : PAS de nageoires, PAS d'écailles, PAS d'ouïes. Sa rune, un seul trait sur le sommet du
  crâne : une BOUCLE OUVERTE, cuivre.
- LA CRÉATURE MAJESTUEUSE en (12,13)-(13,14), DEUX CASES au sol, debout sur la crête de la dune,
  dominant la plage, REGARDANT VERS LE BAS : SP-015, grand arpenteur des rivages, blanc nacré moucheté
  de vert d'eau, quatre longues pattes d'échassier, poitrail profond en carène, collerette de nageoires
  translucides autour du cou remuant comme des anémones, tête étroite aux yeux sombres et calmes. PAS
  un cheval : poitrail en carène et jarrets inversés, sa silhouette n'appartient à aucun animal réel.
  Sa rune, un seul trait sur le flanc gauche : une VAGUE DOUBLE, turquoise.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p6-plage-v4.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p6-plage-v4.png", PROMPT], cwd=PROJECT
    ).returncode)

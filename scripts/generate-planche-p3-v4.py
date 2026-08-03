#!/usr/bin/env python3
"""Plate P3 foothills, fourth pass — calibrated French standard. Corrections from v3's review: density
floor (v3 measured 41% against ~74), the fold hammered at eight tiles (it rendered small), intense
colours kept. Composition otherwise from v3, translated."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PREAMBULE_FR, PROJECT, TARGET, TOOL

PROMPT = PREAMBULE_FR + """
PLANCHE P3 — CONTREFORTS. Biome : pentes rocheuses de montagne vues d'en haut — parois gris pâle
striées d'ocre, éboulis, herbe rase d'un VERT VIF ET SATURÉ, pins sombres, torrent dans un ravin. La
planche est PLEINE : entre les parois, l'herbe est parsemée de rochers, de pierriers, de fleurs de
montagne et de pins — pas de grands vides.

La roche d'abord — des bandes de paroi abrupte vues d'en haut : en haut à gauche en (1,1)-(13,4) ;
autour de la mine en (16,1)-(19,9) ; en haut à droite en (28,1)-(32,8) avec un ÉBOULIS en dessous en
(29,9)-(32,13). Des rochers de tailles variées en (17,11)-(18,12), (7,9)-(8,10), (23,17)-(24,18),
(29,21)-(30,22), (12,16)-(13,17), (20,22)-(21,23). Aucun ne touche un chemin.

Dessine d'abord ces deux raccords de bord — chacun un sentier pierreux d'une case de large, VISIBLEMENT
coupé par son bord, courant sur l'herbe dégagée, jamais perdu dans les rochers :
1. Le long de la RANGÉE 8, atteignant le BORD GAUCHE en (1,8) — bien visible sur l'herbe unie au bord.
2. Le long de la COLONNE 26, atteignant le BORD BAS en (26,24).

Réseau des sentiers — en lacets : de (1,8) à (10,8), descendant la colonne 10 de (10,8) à (10,14), le
long de la rangée 14 de (10,14) à (26,14), descendant la colonne 26 de (26,14) à (26,24). Branches :
colonne 5 de (5,9) à (5,11), s'arrêtant À la porte de la bergerie ; colonne 23 de (23,8) à (23,13),
reliant la gueule de la mine au sentier ; de (26,17) un pas vers (27,17) vers la tour en ruine. Aucun
autre chemin n'existe.

Le ravin — le torrent court dans un ravin étroit le long des colonnes 14-15 SEULEMENT de (14,5) à
(15,13) : herbe unie au-dessus et en dessous, le ravin n'atteint AUCUN bord. Un PONT SUSPENDU en
(14,14)-(15,14) porte le sentier de la rangée 14 par-dessus : planches et cordes, légèrement affaissé,
ses deux bouts posés sur le sentier.

Bâtiments — chaque porte de 2,5 cases de haut :
- BERGERIE en (2,12)-(9,19) : HUIT CASES SUR HUIT — sa façade fait QUATRE FOIS la hauteur d'un adulte
  debout, c'est un vrai bâtiment, pas un abri — grange basse en pierre sèche au toit de bois, large
  porte sur sa face haute en (5,12), le sentier d'accès s'arrête à cette porte, foin à l'intérieur. Son
  ENCLOS muré en pierre sèche en (2,20)-(9,23), relié à la grange par un portillon dans le mur commun.
  État : usée, entretenue.
- ENTRÉE DE MINE en (20,1)-(27,7) : gueule de galerie boisée taillée dans la paroi, poutres trapues,
  petite lanterne éteinte suspendue, rails sortant vers un CHARIOT DE MINE de deux cases en
  (21,9)-(22,9), à moitié plein de minerai.
- TOUR EN RUINE en (28,16)-(31,19) : tour de guet ronde brisée, effondrée d'un côté, mousse sur les
  pierres. Une ruine — pas de porte requise.

Végétation — des pins sombres, chacun d'une hauteur et d'une inclinaison différentes, en (4,6), (8,6),
(18,18), (22,20), (30,14), (12,20) ; herbe rase de montagne partout ailleurs, semée de petites fleurs
et de pierres dans la limite d'habillage — la pente vit, elle n'est pas nue.

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (5,15), DEBOUT (entre 1,75 et 2 cases), près de la bergerie, REGARDANT DROIT VERS LE BAS face
  caméra, visage bien visible : bergère d'une cinquantaine d'années, burinée, peau olive, cheveux gris
  tressés, épais châle tissé sur une robe de laine, bâton de bergère.
- En (23,8), DEBOUT, s'épongeant le front à la gueule de la mine, REGARDANT VERS LE BAS : mineur trapu
  de la trentaine, peau brun moyen, casque de cuir à petite lampe éteinte, veste de toile poussiéreuse,
  gros gants à la ceinture.
- En (12,14), DEBOUT, s'engageant vers le pont suspendu vers la DROITE, tenant la corde : jeune
  voyageuse, peau claire tachée de son, cheveux roux, petit sac usé à couverture roulée, bonnes
  chaussures de marche, visage curieux.
- Dans l'enclos, broutant : en (4,21), le plus grand, REGARDANT DROIT VERS LE BAS face caméra, pas en
  diagonale, et en (7,21), plus petit et plus brun : deux individus de l'espèce SP-016 — créature
  ronde de pâture de la taille d'un grand chien, couverte d'une laine dense VERT MOUSSE sur une peau
  gris ardoise, SIX courtes pattes robustes, deux cornes enroulées vers l'arrière comme des coquilles
  d'escargot, museau plat et amical, pas de queue visible. Le grand porte sa rune, un seul trait au
  front entre les cornes : une VOLUTE, jaune paille. Le petit, au même endroit : un DOUBLE ANNEAU LIÉ,
  jaune paille.
- En (17,11), perché sur le rocher au-dessus du ravin, REGARDANT VERS LA GAUCHE : SP-007, créature
  fine gris argenté à la LONGUE QUEUE ANNELÉE portée en panache, grands yeux ronds, fourrure courte et
  dense, corps souple SANS AUCUN trait de chat : museau court arrondi, petites oreilles rondes, pattes
  fines à larges doigts. Sa rune, un seul trait au bout de la queue : une GOUTTE, rose.
- En (29,12), sautillant dans l'éboulis : SP-005, petite créature bleu pâle dressée sur ses pattes
  arrière, longues oreilles souples TOMBANT le long du dos, corps mince, queue à pinceau, museau pointu
  — sans aucun trait de lapin : oreilles tombantes et non dressées. Sa rune, un seul trait à la base de
  l'oreille droite : un CHEVRON, orange.
- LA CRÉATURE MAJESTUEUSE en (21,10)-(22,11), DEUX CASES au sol, debout près du sentier de la mine,
  contemplant la vallée, REGARDANT VERS LE BAS : SP-014, puissante créature des montagnes aux plaques
  de pierre bleu ardoise le long du dos et des épaules, lourde tête calme à deux cornes couchées vers
  l'arrière, pattes épaisses à larges pieds, de la mousse dans les joints de ses plaques — comme un
  versant de colline qui aurait décidé de marcher. Sa rune, un seul trait sur l'avant-bras gauche : un
  ZIGZAG HORIZONTAL, vert mousse.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p3-contreforts-v4.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p3-contreforts-v4.png", PROMPT], cwd=PROJECT
    ).returncode)

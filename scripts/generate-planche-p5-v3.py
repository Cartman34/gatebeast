#!/usr/bin/env python3
"""Plate P5 cliff, third pass — calibrated French standard. Composition carried from the retained v2,
translated; inhabitants aligned on the witness sheets (SP-013 majestic, SP-004, SP-005 hardened,
SP-007 hardened); humans on the calibrated scale. The cliff stays the subject: rock face band, rocks
at its foot, the sea below in the lower right."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PREAMBULE_FR, PROJECT, TARGET, TOOL

PROMPT = PREAMBULE_FR + """
PLANCHE P5 — HAUT DE FALAISE. Biome : un plateau herbeux battu par le vent finissant en FALAISE
ABRUPTE ; la mer loin en contrebas dans le coin bas droit, turquoise soutenu à écume blanche, DES
ROCHERS AU PIED DE LA FALAISE brisant les vagues. Herbe rase sculptée par le vent d'un vert vif, pierre
rongée de sel, bois patiné.

LA FALAISE EST LE SUJET, ET ELLE RESTE DANS LE COIN BAS DROIT : une bande de paroi rocheuse striée vue
d'en haut, de (18,21) à (32,22), remontant le long de (30,17)-(32,19) — le bord du plateau, la paroi,
puis la mer en contrebas en (20,23)-(32,24). Tout le reste de la planche est le plateau herbeux, qui
ne tombe nulle part ailleurs. Des rochers au pied de la paroi en (22,23)-(24,24) et (28,23)-(30,24),
l'écume blanche s'y brisant.

Dessine d'abord ces trois raccords de bord — chacun un chemin d'une case de large, VISIBLEMENT coupé
par son bord :
1. Le long de la RANGÉE 12, atteignant le BORD GAUCHE en (1,12) — la passerelle du marais devient
   chemin de terre ici.
2. Le long de la COLONNE 18, atteignant le BORD HAUT en (18,1) — la route venant du bourg.
3. Le long de la RANGÉE 20, atteignant le BORD DROIT en (32,20) — franchissant la roche haute sur une
   PASSERELLE DE BOIS en (30,20)-(32,20), ses deux bouts posés au sol, descendant vers la plage.

Réseau des chemins — chemin 1 de (1,12) à (18,12) ; chemin 2 descendant la colonne 18 de (18,1) à
(18,20) ; chemin 3 de (18,20) à (32,20). Branches : depuis la porte du phare, descendant la colonne 25
de (25,10) à (25,19), rejoignant le chemin 3 ; de (6,13) à (6,15) vers la porte du cabanon. Aucun autre
chemin n'existe.

L'escalier — un ESCALIER TAILLÉ DANS LA FALAISE en (29,18)-(30,20) : marches de pierre descendant du
plateau dans la roche, relié au chemin 3.

Bâtiments — portes de 2,5 cases de haut :
- PHARE en (22,2)-(29,9) : une grosse tour ronde de pierre, huit cases de large, bandes blanches et
  rouges rongées de sel, lanterne à gros verre au sommet vue d'en haut, porte sur sa face basse en
  (25,9), desservie par sa branche. État : usé, entretenu.
- CABANON DE PÊCHE en (3,16)-(10,23) : huit sur huit, murs bas de pierre, toit de bois goudronné tenu
  par des cordes et des pierres contre le vent, porte sur sa face haute en (6,16), petite cheminée.
  État : patiné.
- SÉCHOIR À FILETS en (12,16)-(15,17) : un cadre de bois où sèchent des filets au vent, à moitié garni.

Végétation — UN ARBRE COUCHÉ PAR LE VENT en (5,4), penché vers la droite, sculpté par le vent,
couronne basse et dense ; un petit arbuste tordu en (13,6). Partout ailleurs : herbe rase d'un vert
vif, semée de touffes, de petites pierres et de bois flotté blanchi dans la limite d'habillage — le
plateau vit, il n'est pas nu.

Objets — des affleurements rocheux en (2,8)-(3,9) et (20,15)-(21,16), pierre grise striée de blanc ;
une pile de casiers d'osier en (8,13), une case d'empilement ; cordages lovés et un tonneau près de la
porte du cabanon.

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (26,11), DEBOUT (entre 1,75 et 2 cases), descendant la branche du phare, REGARDANT DROIT VERS LE
  BAS face caméra, visage bien visible : gardienne du phare, solide femme d'une soixantaine d'années,
  peau foncée, cheveux blancs attachés, ciré jaune, bottes, regard habitué au large.
- En (13,15), DEBOUT, réparant un filet au séchoir, REGARDANT VERS LE HAUT : pêcheur sec aux traits
  d'Asie de l'Est.
- En (19,13), DEBOUT, descendant la colonne 18, REGARDANT VERS LE BAS : jeune voyageuse, peau claire
  tachée de son, cheveux roux, petit sac usé à couverture roulée, bonnes chaussures de marche.
- En (7,6), une case, assise près de l'arbre couché, la fourrure ébouriffée par le vent, REGARDANT
  DROIT VERS LE BAS face caméra, pas en diagonale : SP-004, créature basse et dodue couverte d'une
  fourrure de mousse, en forme de pierre arrondie, large visage calme, oreilles minuscules. Sa rune, un
  seul trait sur le flanc gauche : une VAGUE, vert d'eau.
- En (21,21), perchée au bord de la falaise, regardant la mer, REGARDANT VERS LA DROITE : SP-007,
  créature fine gris argenté à la LONGUE QUEUE ANNELÉE en panache, grands yeux ronds, fourrure courte
  et dense, corps souple SANS AUCUN trait de chat : museau court arrondi, petites oreilles rondes,
  pattes fines à larges doigts. Sa rune, un seul trait au bout de la queue : une GOUTTE, rose.
- En (30,18), sautillant de marche en marche dans l'escalier : SP-005, petite créature bleu pâle
  dressée sur ses pattes arrière, longues oreilles souples TOMBANT le long du dos, corps mince, queue à
  pinceau, museau pointu — sans aucun trait de lapin : oreilles tombantes et non dressées. Sa rune, un
  seul trait à la base de l'oreille droite : un CHEVRON, orange.
- LA CRÉATURE MAJESTUEUSE en (4,10)-(5,11), DEUX CASES au sol, debout au point haut du plateau,
  regardant la mer, REGARDANT VERS LA DROITE : SP-013, grand être au long cou, gris orage aux flancs
  argentés, crête de plumes raides rejetées en arrière par le vent, fortes pattes nues, et repliées le
  long du dos deux VOILES CÔTELÉES — pas des ailes : des girouettes de peau qu'il déploie pour
  s'appuyer sur les rafales. Sa rune, un seul trait sur le poitrail : une RAFALE de trois traits liés
  d'un seul geste, blanc.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p5-falaise-v3.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p5-falaise-v3.png", PROMPT], cwd=PROJECT
    ).returncode)

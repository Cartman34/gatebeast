#!/usr/bin/env python3
"""Plate P2 town, fourth pass — calibrated French standard. Owner's remarks on v3 carried in: the
walled garden must sit next to a house or disappear (a dense town was wanted) — it is REMOVED and
replaced by a public washhouse on a paved yard; the image gets more light. Composition otherwise from
v3, translated."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PREAMBULE_FR, PROJECT, TARGET, TOOL

PROMPT = PREAMBULE_FR + """
PLANCHE P2 — BOURG. Biome : un petit bourg marchand vivant et DENSE — rues pavées, place dallée à
fontaine, halle couverte, forge, maisons mitoyennes toutes différentes. Pierre chaude, colombage et
tuiles, chaque bâtiment distinct par sa forme, sa hauteur, son toit et sa couleur. Image LUMINEUSE : le
bourg est baigné de soleil, pas de recoin sombre.

Dessine d'abord ces trois raccords de bord — chacun une rue pavée d'une case de large, VISIBLEMENT
coupée par son bord :
1. Le long de la RANGÉE 16, atteignant le BORD GAUCHE en (1,16).
2. Le long de la RANGÉE 8, atteignant le BORD DROIT en (32,8).
3. Le long de la COLONNE 18, atteignant le BORD BAS en (18,24).

Réseau des rues — rue 1 de (1,16) à (18,16) ; rue 3 remontant la colonne 18 de (18,24) à (18,8) ;
rue 2 de (18,8) à (32,8), toutes jointes à leurs angles. Courtes branches pavées : de (22,7) vers les
portes des échoppes ; de (19,14) vers la porte du potier ; de (4,17), (8,17) et (12,17) depuis la rue 1
vers les portes des maisons ; de (4,13) à (4,15) vers le lavoir. Aucune autre voie n'existe.

Place du bourg — une place dallée couvrant (10,9)-(17,15), jointe aux rues 1 et 3. En son centre une
FONTAINE RONDE DE PIERRE en (13,11)-(14,12), eau claire et vive. Deux ÉTALS DE MARCHÉ de DEUX CASES
chacun, auvent rayé sur poteaux : l'un en (11,10)-(12,10) à moitié plein de légumes, l'autre en
(16,10)-(17,10) à moitié plein de rouleaux d'étoffe.

Bâtiments — tous droits sur la grille, tous différents, CHAQUE PORTE de 2,5 cases de haut :
- HALLE COUVERTE en (2,1)-(9,8) : huit sur huit, halle de charpente ouverte sur poteaux trapus, toit de
  tuiles pentu, caisses de marché à moitié pleines dessous. État : usée, entretenue.
- LAVOIR PUBLIC en (3,10)-(6,12) : un bassin de pierre sous un toit ouvert sur poteaux, eau claire,
  linge sur la margelle — ouvert, pas une habitation. Desservi par sa branche pavée.
- RANGÉE DE TROIS ÉCHOPPES MITOYENNES en (20,1)-(31,6), COUPÉE PAR LE BORD HAUT — seuls leurs
  rez-de-chaussée et leurs portes sont visibles ; la rangée fait 12 cases de large. À gauche : une
  BOULANGERIE, enduit crème, vitrine garnie de pains, porte en (22,6). Au centre : une FORGE, bois
  sombre, devanture ouverte sur le foyer rougeoyant, enclume dehors, porte en (26,6). À droite : une
  AUBERGE, rez-de-chaussée de pierre, potence d'enseigne (sans texte), porte en (30,6). Leurs portes
  donnent sur une bande pavée le long de la rangée 7, jointe à la rue 2.
- ATELIER DU POTIER en (22,10)-(31,19) : dix sur dix, brique, cheminée de four arrondie fumant
  doucement, large porte d'atelier sur sa face gauche en (22,14), étagères de poteries, desservi par la
  branche de la rue 3.
- PAIRE DE MAISONS MITOYENNES en (2,18)-(13,24), COUPÉE PAR LE BORD BAS — deux maisons accolées de 12
  cases de large ensemble : maison de pierre aux volets verts, porte en (4,18) ; maison ocre plus haute
  à balcon, porte en (8,18) ; en (12,18) un portillon de cour commun.

Végétation — deux arbres de rue en bac de pierre en (10,17) et (19,10), adultes, denses, d'espèces et
de hauteurs différentes ; jardinières fleuries aux fenêtres, dans la limite d'habillage.

Objets — une CHARRETTE À BRAS à moitié chargée de sacs couvrant (15,16)-(16,16), deux cases ; des
caisses empilées en (9,9) ; un PUITS PUBLIC à petit toit et seau couvrant (19,15)-(20,15), deux cases ;
deux tonneaux près de la porte de l'auberge en (29,7).

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (13,13), DEBOUT (entre 1,75 et 2 cases), remplissant une cruche à la fontaine, REGARDANT DROIT
  VERS LE BAS face caméra, visage bien visible : boulangère d'une cinquantaine d'années, peau brun
  chaud, fichu blanc, tablier fariné sur une robe prune, avant-bras solides, visage rieur.
- En (26,7), DEBOUT, martelant à l'enclume devant la forge, REGARDANT VERS LE BAS : forgeron d'une
  quarantaine d'années, peau foncée, crâne rasé, barbe épaisse, lourd tablier de cuir sur un torse
  musclé, manchettes de cuir.
- En (17,12), DEBOUT au bord de la place, la surveillant, REGARDANT VERS LA GAUCHE : garde de la
  trentaine, grande, peau olive, cheveux sombres en tresse serrée, uniforme simple de cuir et d'étoffe
  bleu ardoise à petite épaulière, bâton simple en main.
- En (11,11), DEBOUT, arrangeant ses légumes à l'étal, REGARDANT VERS LA GAUCHE : marchand aux traits
  d'Asie de l'Est, cheveux striés de gris.
- En (23,14), DEBOUT, sortant de l'atelier une pile de bols, marchant vers la GAUCHE : jeune potier
  d'une vingtaine d'années, peau claire tachée de son, cheveux roux bouclés, blouse tachée d'argile.
- En (16,16) et (17,16), deux enfants nettement PLUS PETITS que les adultes, se poursuivant vers la
  DROITE sur la rue 1 : un enfant d'environ neuf ans, peau brune, courtes boucles sombres, pieds nus —
  et un enfant d'environ sept ans, peau claire, cheveux blonds ébouriffés, blouse verte.
- En (12,15), une case, somnolant contre le socle de la fontaine : SP-001, petit quadrupède rond de la
  taille d'un renardeau, fourrure ambre chaud sur le dos et la tête, ventre et museau crème, grandes
  oreilles rondes, queue courte à bout crème. Sa rune, un seul trait au milieu du front : une ARCHE,
  turquoise.
- En (20,16), une case, trottant vers le BAS le long de la rue 3, REGARDANT DROIT VERS LE BAS face
  caméra, pas en diagonale : SP-005, petite créature bleu pâle dressée sur ses pattes arrière, longues
  oreilles souples TOMBANT le long du dos, corps mince, queue à pinceau, museau pointu et éveillé —
  sans aucun trait de lapin : oreilles tombantes et non dressées, pattes fines à larges doigts. Sa
  rune, un seul trait à la base de l'oreille droite : un CHEVRON, orange.
- En (6,9), une case, flairant les caisses de la halle, REGARDANT VERS LE HAUT : SP-004, créature basse
  et dodue couverte d'une fourrure de mousse, en forme de pierre arrondie, large visage calme. Sa rune,
  un seul trait sur le flanc gauche : une VAGUE, vert d'eau.
- LA CRÉATURE MAJESTUEUSE en (14,9)-(15,10), DEUX CASES au sol, debout calmement en haut de la place,
  tête haute, REGARDANT VERS LE BAS : SP-011, grand être élégant au pelage sarcelle profond, collerette
  de fourrure pâle plumeuse autour du cou, une seule corne élancée courbée VERS L'ARRIÈRE depuis le
  front, pattes fines à pieds fourchus, queue en panache portée haut — ni licorne ni cheval : corne
  vers l'arrière, collerette, pieds fourchus. Sa rune, un seul trait le long du cou côté droit : une
  FLAMME ondulante dressée, argent.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p2-bourg-v4.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p2-bourg-v4.png", PROMPT], cwd=PROJECT
    ).returncode)

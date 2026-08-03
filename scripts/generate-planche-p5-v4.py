#!/usr/bin/env python3
"""Plate P5 cliff, fourth pass — the geometry decided by the owner (Q3): the cliff runs along the WHOLE
bottom edge and climbs the right edge only BELOW the half of the image, the sea beyond it; the right
joint (row 20) is a WOODEN WALKWAY OVER THE SEA reaching (32,20); the carved stair links the plateau
path to that walkway. Brittany as the reference: granite, yellow gorse, heather, driftwood, and a
SLENDER lighthouse. More inhabitants than v3 (one more human, two more creatures) and free dressing
raised to one tile in three for this biome."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PROJECT, TARGET, TOOL, preambule_fr

PROMPT = preambule_fr("UNE CASE SUR TROIS") + """
PLANCHE P5 — HAUT DE FALAISE. Biome : un plateau herbeux battu par le vent, D'INSPIRATION BRETONNE —
granite gris clair veiné de rose affleurant partout, ajoncs à fleurs JAUNE VIF, bruyère mauve en
coussins, herbe rase sculptée par le vent d'un vert franc, bois flotté blanchi par le sel. Le plateau
finit en FALAISE ABRUPTE, la mer loin en contrebas, turquoise soutenu à écume blanche.

LA GÉOMÉTRIE DE LA FALAISE D'ABORD — c'est le sujet, et elle se lit sans ambiguïté :
- La falaise court sur TOUT LE BORD BAS DE L'IMAGE : une bande continue de paroi de granite vue d'en
  haut, de (1,21) à (30,22), d'un bord latéral à l'autre. Le plateau s'arrête net sur sa lèvre en
  rangée 20 ; en dessous, la paroi plonge.
- Elle REMONTE LE BORD DROIT, mais SEULEMENT SOUS LA MOITIÉ DE L'IMAGE : une bande de paroi en
  (29,13)-(30,19). AU-DESSUS DE LA RANGÉE 12, IL N'Y A AUCUNE FALAISE À DROITE — le plateau herbeux
  atteint le bord droit intact sur toute la moitié haute de l'image.
- LA MER EN CONTREBAS, nettement plus bas que le plateau : (1,23)-(32,24) tout le long du bas, et
  (31,13)-(32,22) le long du bord droit sous la rangée 12. Les deux se rejoignent dans le coin bas
  droit : c'est une seule mer.
- Des rochers de granite au pied de la paroi, dans l'eau, l'écume blanche s'y brisant : (5,23)-(7,24)
  et (18,23)-(20,24).

Dessine ensuite ces trois raccords de bord — chacun VISIBLEMENT coupé par son bord :
1. Le long de la RANGÉE 12, atteignant le BORD GAUCHE en (1,12) : un chemin de terre d'une case de
   large.
2. Le long de la COLONNE 18, atteignant le BORD HAUT en (18,1) : la route venant du bourg, une case.
3. Le long de la RANGÉE 20, atteignant le BORD DROIT en (32,20) : une PASSERELLE DE BOIS AU-DESSUS DE
   LA MER en (31,20)-(32,20) — un tablier de planches sur des pieux plantés dans l'eau bien plus bas,
   garde-corps de cordes, qui sort de l'image par le bord droit. ON VOIT LA MER SOUS ELLE.

Réseau des chemins — ce sont les SEULS de l'image, une case de large : chemin 1 de (1,12) à (18,12) ;
chemin 2 descendant la colonne 18 de (18,1) à (18,20) ; chemin du bord de falaise de (18,20) à (28,20),
courant le long de la lèvre. Branches : desserte du phare, colonne 25, de (25,7) à (25,20) ; desserte du
cabanon, colonne 6, de (6,12) à (6,13), s'arrêtant À sa porte. Aucun autre chemin n'existe.

L'ESCALIER — un ESCALIER TAILLÉ DANS LA FALAISE en (29,20)-(30,20), deux cases : des marches de granite
creusées dans la paroi, avec une main courante de cordes. IL DESCEND DU CHEMIN À LA PASSERELLE : sa
marche haute touche le chemin du bord de falaise en (28,20), sa marche basse arrive exactement sur le
tablier de la passerelle en (31,20). Le trajet se lit d'un seul coup d'œil, sans interruption : chemin
du plateau → escalier → passerelle → bord droit de l'image.

Bâtiments — portes de 2,5 cases de haut :
- PHARE en (24,4)-(27,7) : une TOUR ÉLANCÉE, QUATRE CASES de côté au sol seulement, qui MONTE TRÈS
  HAUT — sa hauteur vaut SIX FOIS sa largeur. Fût droit et fin, à peine évasé au pied, JAMAIS BULBEUX,
  jamais renflé, jamais trapu : une longue aiguille blanche coiffée d'une lanterne à gros verre et
  d'une coupole SOMBRE, avec une étroite galerie sous la lanterne. Maçonnerie de granite blanchie à la
  chaux, rongée de sel. Porte sur sa face basse en (25,7), desservie par sa branche. État : usé,
  entretenu. (Ce n'est pas une habitation : sa base est une tour.)
- CABANON DE PÊCHE en (3,13)-(10,20) : huit cases sur huit, murs bas de granite, toit de bois goudronné
  tenu par des cordes et des pierres contre le vent, porte sur sa face haute en (6,13), petite cheminée.
  État : patiné.
- SÉCHOIR À FILETS en (12,16)-(15,17) : un cadre de bois où sèchent des filets au vent, à moitié garni.

Végétation — DES AJONCS EN MASSIFS DENSES, épineux, couverts de fleurs JAUNE VIF, en (10,3)-(12,5) et
(20,16)-(22,18) ; de la BRUYÈRE mauve en coussins bas en (8,8)-(10,10) ; UN ARBRE COUCHÉ PAR LE VENT en
(5,4), penché vers la droite, couronne basse et dense, tronc tordu ; un petit arbuste rabougri en
(13,6). Partout ailleurs : herbe rase d'un vert franc, semée de touffes, de cailloux de granite et de
BOIS FLOTTÉ blanchi dans la limite d'habillage — le plateau vit, il n'est pas nu.

Objets — des affleurements de granite gris veiné de rose en (2,8)-(3,9) et (14,9)-(15,10) ; une pile de
casiers d'osier en (8,11), une case d'empilement ; cordages lovés et un tonneau près de la porte du
cabanon.

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (26,11), DEBOUT (entre 1,75 et 2 cases), descendant la branche du phare, REGARDANT DROIT VERS LE
  BAS face caméra, visage bien visible : gardienne du phare, solide femme d'une soixantaine d'années,
  peau foncée, cheveux blancs attachés, ciré jaune, bottes, regard habitué au large.
- En (13,15), DEBOUT, réparant un filet au séchoir, REGARDANT VERS LE HAUT : pêcheuse de la trentaine,
  peau brune, boucles noires sous un foulard noué, robe bleue sans manches délavée par le soleil,
  épaules solides, un panier de filets tressé sur la hanche.
- En (19,13), DEBOUT, descendant la colonne 18, REGARDANT VERS LE BAS : jeune voyageuse, peau claire
  tachée de son, cheveux roux, petit sac usé à couverture roulée, bonnes chaussures de marche, visage
  curieux.
- En (27,20), DEBOUT sur le chemin du bord de falaise, au sommet de l'escalier, lovant un cordage,
  REGARDANT VERS LA DROITE vers la passerelle : pêcheur d'une quarantaine d'années, peau claire rougie
  par le soleil, barbe blonde, bonnet de laine roulé, chemise bleue rapiécée aux manches retroussées,
  mains épaisses et burinées.
- En (15,12), nettement PLUS PETIT que les adultes, courant vers la DROITE sur le chemin, REGARDANT
  DROIT VERS LE BAS face caméra : enfant d'environ neuf ans, peau brune, courtes boucles sombres, pieds
  nus, vêtements de jeu simples, toujours en mouvement.
- En (7,6), une case, assise près de l'arbre couché, la fourrure ébouriffée par le vent, REGARDANT
  DROIT VERS LE BAS face caméra, pas en diagonale : SP-004, créature basse et dodue couverte d'une
  fourrure de mousse, en forme de pierre arrondie, large visage calme, oreilles minuscules, pattes
  invisibles au repos. Sa rune, un seul trait sur le flanc gauche : une VAGUE, vert d'eau.
- En (21,21), perchée sur la lèvre de la falaise, regardant la mer, REGARDANT VERS LA DROITE : SP-007,
  créature fine gris argenté à la LONGUE QUEUE ANNELÉE en panache, grands yeux ronds, fourrure courte
  et dense, corps souple SANS AUCUN trait de chat : museau court arrondi, petites oreilles rondes,
  pattes fines à larges doigts. Sa rune, un seul trait au bout de la queue : une GOUTTE, rose.
- En (30,20), sautillant de marche en marche dans l'escalier : SP-005, petite créature bleu pâle
  dressée sur ses pattes arrière, longues oreilles souples TOMBANT le long du dos, corps mince, queue à
  pinceau, museau pointu — sans aucun trait de lapin : oreilles tombantes et non dressées, pattes avant
  longues et fines. Sa rune, un seul trait à la base de l'oreille droite : un CHEVRON, orange.
- En (16,18), une case, trottant dans l'herbe vers la GAUCHE : SP-001, petit quadrupède rond de la
  taille d'un renardeau, fourrure ambre chaud sur le dos et la tête, ventre et museau crème, quatre
  pattes courtes aux pieds crème, deux grandes oreilles rondes ambre dehors et crème dedans, grands
  yeux sombres amicaux, queue courte et épaisse à bout crème. Sa rune, un seul trait scintillant au
  milieu du front : une ARCHE, turquoise.
- En (9,4), une case, immobile au pied des ajoncs, REGARDANT VERS LE HAUT : SP-002, petit quadrupède
  rond vert mousse, à peine plus haut que large, dos rond et lisse, pattes courtes et trapues, large
  bouche amicale et petits yeux sombres. Pas de queue. Sa rune, un seul trait au centre du dos : un
  CROISSANT, jaune pâle.
- LA CRÉATURE MAJESTUEUSE en (4,10)-(5,11), DEUX CASES au sol, debout au point haut du plateau, face au
  large, REGARDANT VERS LA DROITE : SP-013, grand être au long cou, gris orage aux flancs argentés,
  crête de plumes raides rejetées en arrière par le vent, fortes pattes nues, et repliées le long du dos
  deux VOILES CÔTELÉES — pas des ailes : des girouettes de peau qu'il déploie pour s'appuyer sur les
  rafales. Sa rune, un seul trait sur le poitrail : une RAFALE de trois traits liés d'un seul geste,
  blanc.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p5-falaise-v4.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p5-falaise-v4.png", PROMPT], cwd=PROJECT
    ).returncode)

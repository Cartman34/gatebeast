#!/usr/bin/env python3
"""Plate P5 cliff, fifth pass — v4 landed the operator's Q3 geometry, the slender lighthouse, Brittany and
the richer population, and all of that is carried unchanged. Fixed here, from the v4 report: the CARVED
STAIR was simply not drawn — a small work with no declared footprint gets lost, so it now has its own
emprise, its own step count and its own paragraph; the plateau was far too empty (43.8% of load), so the
filling is prescribed as LISTED MASSES with footprints instead of a dressing proportion; SP-001 came out
oversized. Plus the current standard: the light band from the shared base, and a size reminder next to
EVERY human (the audit found three of five)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import RAPPEL_FINAL_FR, preambule_fr, shoot

COMPOSITION = """
CONTRÔLE DE GRILLE — chaque élément est donné par ses coordonnées de case. Place-le EXACTEMENT à ces
cases, avec l'emprise annoncée. Un adulte debout fait deux cases : huit cases valent QUATRE adultes.

PLANCHE P5 — HAUT DE FALAISE. Biome : plateau herbeux battu par le vent, D'INSPIRATION BRETONNE, en
plein soleil — granite gris clair veiné de rose affleurant partout, ajoncs à fleurs JAUNE VIF, bruyère
mauve en coussins, herbe rase d'un vert franc, bois flotté blanchi par le sel. Le plateau finit en
FALAISE ABRUPTE, la mer loin en contrebas, turquoise soutenu à écume blanche. La roche de la falaise est
CLAIRE et pleinement éclairée sur sa face, veinée de blanc et de rose, jamais une masse grise.

GÉOMÉTRIE DE LA FALAISE — c'est le sujet, et elle se lit sans ambiguïté :
- La falaise court sur TOUT LE BORD BAS : une bande continue de paroi de granite vue d'en haut, de
  (1,21) à (30,22), d'un bord latéral à l'autre. Le plateau s'arrête net sur sa lèvre en rangée 20.
- Elle REMONTE LE BORD DROIT, mais SEULEMENT SOUS LA MOITIÉ DE L'IMAGE : une bande de paroi en
  (29,13)-(30,19). AU-DESSUS DE LA RANGÉE 12, AUCUNE FALAISE À DROITE — le plateau herbeux atteint le
  bord droit intact sur toute la moitié haute.
- LA MER EN CONTREBAS, nettement plus bas que le plateau : (1,23)-(32,24) le long du bas et
  (31,13)-(32,22) le long du bord droit sous la rangée 12. Les deux se rejoignent dans le coin bas
  droit : c'est une seule mer.
- Rochers de granite au pied de la paroi, dans l'eau, écume blanche s'y brisant : (5,23)-(7,24) et
  (18,23)-(20,24).

RACCORDS DE BORD — trois, chacun VISIBLEMENT coupé par son bord :
1. RANGÉE 12, atteignant le BORD GAUCHE en (1,12) : chemin de terre d'une case de large.
2. COLONNE 18, atteignant le BORD HAUT en (18,1) : la route venant du bourg, une case.
3. RANGÉE 20, atteignant le BORD DROIT en (32,20) : la passerelle de bois décrite ci-dessous.

CHEMINS — les SEULS de l'image, une case de large : chemin 1 de (1,12) à (18,12) ; chemin 2 descendant
la colonne 18 de (18,1) à (18,20) ; chemin du bord de falaise de (18,20) à (28,20), courant le long de
la lèvre. Branches : desserte du phare, colonne 25, de (25,7) à (25,20) ; desserte du cabanon, colonne
6, de (6,12) à (6,13), s'arrêtant À sa porte. Tout le reste du plateau est de l'herbe : aucune autre
bande de terre battue.

LA DESCENTE VERS LA MER — TROIS OUVRAGES QUI SE TOUCHENT, à dessiner comme une seule suite continue.
C'est le point qui a manqué au passage précédent : l'escalier n'avait pas été dessiné du tout. Il a donc
ici sa propre emprise, comme un bâtiment, et il doit être VISIBLE ET COMPTABLE :
1. Le CHEMIN DU BORD DE FALAISE arrive par la rangée 20 et se termine en (28,20), sur la lèvre.
2. L'ESCALIER TAILLÉ DANS LA FALAISE occupe (29,20)-(30,20), DEUX CASES PLEINES. C'est un vrai escalier
   de granite creusé dans la paroi : on compte HUIT À DIX MARCHES distinctes, larges d'une case, qui
   descendent en biais de la lèvre du plateau jusqu'au niveau de la passerelle, chacune avec son nez de
   marche éclairé et son ombre portée. Une MAIN COURANTE DE CORDE tendue entre des piquets de bois
   longe l'escalier sur toute sa descente. Sa marche HAUTE touche le chemin en (28,20) ; sa marche
   BASSE arrive exactement sur le tablier de la passerelle en (31,20).
3. La PASSERELLE DE BOIS AU-DESSUS DE LA MER occupe (31,20)-(32,20) : un tablier de planches sur des
   pieux plantés dans l'eau bien plus bas, garde-corps de cordes, qui sort de l'image par le bord droit.
   ON VOIT LA MER SOUS ELLE, entre les planches et autour des pieux.
On doit pouvoir suivre le trajet d'un seul coup d'œil, sans interruption : chemin du plateau → marches →
passerelle → bord droit de l'image.

BÂTIMENTS — chaque porte NETTEMENT PLUS HAUTE qu'un adulte debout :
- PHARE, (24,4)-(27,7) : une TOUR ÉLANCÉE, QUATRE CASES de côté au sol seulement, qui MONTE TRÈS HAUT —
  sa hauteur vaut SIX FOIS sa largeur. Fût droit et fin, à peine évasé au pied, JAMAIS bulbeux, jamais
  renflé, jamais trapu : une longue aiguille blanche coiffée d'une lanterne à gros verre et d'une
  coupole SOMBRE, avec une étroite galerie sous la lanterne. Maçonnerie de granite blanchie à la chaux.
  Porte sur sa face basse en (25,7), desservie par sa branche. Usé, entretenu. Ce n'est pas une
  habitation : sa base est une tour, la règle des huit cases ne s'y applique pas.
- CABANON DE PÊCHE, (3,13)-(10,20) : huit cases sur huit — quatre adultes de large. Murs bas de granite
  clair, toit de bois goudronné tenu par des cordes et des pierres contre le vent, porte sur sa face
  haute en (6,13), petite cheminée. Patiné.
- SÉCHOIR À FILETS, (12,16)-(15,17) : un cadre de bois où sèchent des filets au vent, à moitié garni.

LE PLATEAU EST OCCUPÉ — MASSES LISTÉES AVEC LEUR EMPRISE, pas une proportion : le passage précédent
était trop vide, et un plafond d'habillage n'a pas suffi. Dessine donc CHACUNE de ces surfaces, pleine
jusqu'à ses bords, et l'herbe rase entre elles :
- AJONCS en massifs denses et épineux, couverts de fleurs JAUNE VIF : (10,3)-(12,5), (20,16)-(22,18),
  (2,17)-(4,19), (14,7)-(16,9), (27,10)-(28,12).
- BRUYÈRE mauve en coussins bas et serrés : (8,8)-(10,10), (13,2)-(15,4), (22,13)-(24,15).
- AFFLEUREMENTS DE GRANITE gris clair veiné de rose, arrondis et polis par le vent : (2,8)-(3,9),
  (14,9)-(15,10), (26,17)-(27,19), (8,3)-(9,5), (19,4)-(20,6).
- UN ARBRE COUCHÉ PAR LE VENT en (5,4), penché vers la droite, couronne basse et dense, tronc tordu ;
  un petit arbuste rabougri en (13,6) ; un second arbuste en (23,8).
- MURETS DE PIERRE SÈCHE bretons, bas, délimitant deux parcelles d'herbe rase : le long de (11,13) à
  (17,13), et le long de (2,15) à (2,20).
- BOIS FLOTTÉ blanchi et casiers d'osier : une pile de casiers en (8,11), du bois flotté empilé en
  (16,19)-(17,19), cordages lovés et un tonneau près de la porte du cabanon.
Entre ces masses, herbe rase d'un vert franc, semée de touffes et de cailloux clairs dans la limite
d'habillage d'une case sur trois.

RAPPEL D'ÉCHELLE, AU MILIEU DE LA CONSIGNE : un adulte DEBOUT fait ENTRE 1,75 ET 2 CASES, moins d'un
douzième de la hauteur de l'image. Les humains SEMBLENT PETITS sur le plateau, comme des figurines. Le
phare fait plus de DOUZE FOIS la hauteur d'un adulte debout.

HABITANTS — chacun cité de sa fiche, dessiné EXACTEMENT ainsi, et chacun PETIT dans la scène :
- (26,11), DEBOUT — ENTRE 1,75 ET 2 CASES, pas plus — descendant la branche du phare, REGARDANT DROIT
  VERS LE BAS face caméra, visage bien visible : solide femme d'une soixantaine d'années, peau foncée,
  cheveux blancs attachés, ciré jaune, bottes, regard habitué au large.
- (13,15), DEBOUT — ENTRE 1,75 ET 2 CASES — réparant un filet au séchoir, REGARDANT VERS LE HAUT :
  femme de la trentaine, peau brune, boucles noires sous un foulard noué, robe bleue sans manches
  délavée par le soleil, épaules solides, panier de filets tressé sur la hanche.
- (19,13), DEBOUT — ENTRE 1,75 ET 2 CASES — descendant la colonne 18, REGARDANT VERS LE BAS : jeune
  femme à la peau claire tachée de son, cheveux roux, petit sac usé à couverture roulée, bonnes
  chaussures de marche, visage curieux.
- (27,20), DEBOUT — ENTRE 1,75 ET 2 CASES — sur le chemin du bord de falaise, au sommet de l'escalier,
  lovant un cordage, REGARDANT VERS LA DROITE vers la passerelle : homme d'une quarantaine d'années,
  peau claire rougie par le soleil, barbe blonde, bonnet de laine roulé, chemise bleue rapiécée aux
  manches retroussées, mains épaisses et burinées.
- (15,12), NETTEMENT PLUS PETIT qu'un adulte — environ 1,25 case — courant vers la DROITE sur le chemin,
  REGARDANT DROIT VERS LE BAS face caméra : enfant d'environ neuf ans, peau brune, courtes boucles
  sombres, pieds nus, vêtements de jeu simples, toujours en mouvement.
- (7,6), UNE SEULE CASE au sol, assise près de l'arbre couché, la fourrure ébouriffée par le vent,
  REGARDANT DROIT VERS LE BAS face caméra, pas en diagonale : SP-004, créature basse et dodue couverte
  d'une fourrure de mousse, en forme de pierre arrondie, large visage calme, oreilles minuscules, pattes
  invisibles au repos. Sa rune, un seul trait sur le flanc gauche : une VAGUE, vert d'eau.
- (21,21), perchée sur la lèvre de la falaise, regardant la mer, REGARDANT VERS LA DROITE : SP-007,
  créature fine gris argenté au corps souple, grands yeux ronds, fourrure courte et dense, museau court
  arrondi, petites oreilles rondes, pattes fines à larges doigts, et une LONGUE QUEUE ANNELÉE portée en
  panache, aussi longue que son corps. Sa rune, un seul trait au bout de la queue : une GOUTTE, rose.
- (30,20), sautillant de marche en marche DANS L'ESCALIER : SP-005, petite créature bleu pâle À
  FOURRURE, dressée sur ses pattes arrière, corps mince, queue à pinceau, museau pointu, et de LONGUES
  OREILLES SOUPLES QUI RETOMBENT ET PENDENT LE LONG DU DOS comme deux rubans — tombantes, jamais
  dressées. Sa rune, un seul trait à la base de l'oreille droite : un CHEVRON, orange.
- (16,18), UNE SEULE CASE au sol — pas plus grand qu'un chat de salon, bien plus petit qu'un humain —
  trottant dans l'herbe vers la GAUCHE : SP-001, petit quadrupède rond de la taille d'un renardeau,
  fourrure ambre chaud sur le dos et la tête, ventre et museau crème, quatre pattes courtes aux pieds
  crème, deux grandes oreilles rondes ambre dehors et crème dedans, grands yeux sombres amicaux, queue
  courte et épaisse à bout crème. Sa rune, un seul trait au milieu du front : une ARCHE, turquoise.
- (9,4), une case, immobile au pied des ajoncs, REGARDANT VERS LE HAUT : SP-002, petit quadrupède rond
  vert mousse, à peine plus haut que large, dos rond et lisse, pattes courtes et trapues, large bouche
  amicale, petits yeux sombres, sans queue. Sa rune, un seul trait au centre du dos : un CROISSANT,
  jaune pâle.
- LA CRÉATURE MAJESTUEUSE, (4,10)-(5,11), DEUX CASES au sol, debout au point haut du plateau, face au
  large, REGARDANT VERS LA DROITE : SP-013, grand être au long cou, gris orage aux flancs argentés,
  crête de plumes raides rejetées en arrière par le vent, fortes pattes nues, et repliées le long du dos
  deux VOILES CÔTELÉES — pas des ailes : des girouettes de peau qu'il déploie pour s'appuyer sur les
  rafales. Sa rune, un seul trait sur le poitrail : une RAFALE de trois traits liés d'un seul geste,
  blanc.
"""

FIN = "\nRien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.\n"

if __name__ == "__main__":
    sys.exit(shoot("p5-falaise-v5", preambule_fr("UNE CASE SUR TROIS") + COMPOSITION
                   + RAPPEL_FINAL_FR + FIN))

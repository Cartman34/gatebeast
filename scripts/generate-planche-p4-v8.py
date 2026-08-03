#!/usr/bin/env python3
"""Plate P4 marsh, eighth pass — v7 was retained by the owner, so its composition is carried unchanged.
Three fixes only: the light standard now in the shared base plus the water and foliage prescribed in
their bright values (v7 measured 99.9 of luminance, under the 115-130 band); the second hut's outside
stair lands ON THE WALKWAY, never in the water (the owner's remark); and a size reminder next to EVERY
human (the audit found one of three)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import RAPPEL_FINAL_FR, preambule_fr, shoot

COMPOSITION = """
CONTRÔLE DE GRILLE — chaque élément est donné par ses coordonnées de case. Place-le EXACTEMENT à ces
cases, avec l'emprise annoncée. Un adulte debout fait deux cases : huit cases valent QUATRE adultes.

PLANCHE P4 — MARAIS. Biome : une zone humide LUXURIANTE, VERTE ET ÉCLATANTE DE LUMIÈRE où L'EAU DOMINE.
La lumière d'abord, c'est le point à corriger : le soleil de fin de matinée tombe en plein sur le
marais, l'EAU EST CLAIRE ET BRILLANTE — turquoise et vert d'eau LUMINEUX, fond de sable pâle visible par
transparence, éclats de soleil à la surface — et le FEUILLAGE EST D'UN VERT FRAIS ET CLAIR, éclairé sur
le dessus des couronnes, jamais en masse sombre. Les troncs eux-mêmes sont éclairés. Aucune eau brune,
aucune brume, aucun sous-bois obscur.

L'eau — PLUS D'EAU QUE DE TERRE. Mares irrégulières s'écoulant de (30,3) vers (4,22) : une mare en
(27,2)-(31,7), un chenal en (21,6)-(27,10), une mare en (14,9)-(21,12), un chenal en (8,11)-(14,16),
une mare en (3,14)-(9,18), un chenal en (2,18)-(7,22), une mare en (23,12)-(28,14). Bancs de vase clairs
et buttes herbeuses entre elles. Nénuphars fleuris sur trois mares, autour de (10,15), (25,18) et (6,6).

RACCORDS DE BORD — deux passerelles de planches d'une case de large, VISIBLEMENT coupées par leur bord :
1. Le long de la COLONNE 12, atteignant le BORD HAUT en (12,1) ; ses quatre dernières cases courent sur
   la terre ferme.
2. Le long de la RANGÉE 12, atteignant le BORD DROIT en (32,12).

PASSERELLES — de (12,12) descendant à (12,20) ; une branche de (5,8) à (12,8) ; une courte branche
(13,8)-(14,8) vers le séchoir ; une branche descendant la colonne 20 de (20,12) à (20,20). Planches
usées, quelques-unes remplacées, main courante de corde côté eau. Aucune branche ne finit dans l'eau.
Aucun autre chemin n'existe.

BÂTIMENTS — droits sur la grille, chaque porte NETTEMENT PLUS HAUTE qu'un adulte debout :
- HUTTE SUR PILOTIS, (2,2)-(13,11) : douze sur dix — six adultes de large. Toit de roseaux, véranda de
  planches sur sa face basse, porte en (7,11) desservie par la branche. ELLE A LES PIEDS DANS L'EAU :
  ses pilotis trapus sortent tout droit de la mare, des algues vertes sur chaque poteau.
- SECONDE HUTTE SUR PILOTIS, (21,15)-(31,23) : onze sur neuf, visiblement différente — murs de planches,
  toit à une pente. Ses pilotis baignent EN PARTIE DANS L'EAU de la mare voisine. SON ESCALIER
  EXTÉRIEUR, sur sa face gauche, DESCEND ET ABOUTIT SUR LE TABLIER DE LA PASSERELLE en (20,20) : sa
  marche basse se pose à plat sur les planches de la passerelle, on passe de l'escalier à la passerelle
  sans un pas dans le vide. AUCUNE MARCHE NE PLONGE DANS L'EAU, aucun escalier ne descend vers la mare :
  l'escalier ne touche que la passerelle.

- SÉCHOIR À RÉCOLTES DU MARAIS, (15,6)-(18,8) : un cadre de bois ouvert où sèchent des bottes d'ALGUES
  et de JONCS suspendues, à moitié garni, desservi par sa courte passerelle.

RAPPEL D'ÉCHELLE, AU MILIEU DE LA CONSIGNE : un adulte DEBOUT fait ENTRE 1,75 ET 2 CASES, moins d'un
douzième de la hauteur de l'image. Les humains SEMBLENT PETITS sur les passerelles, comme des figurines.

VÉGÉTATION — abondante ET HAUTE, d'un vert frais et clair, éclairée, jamais en masse sombre :
- CINQ GRANDS saules tordus, vieux, aux couronnes LARGES (trois à quatre cases) et HAUTES, trempant dans
  l'eau, en (4,17), (8,4), (17,19), (24,4), (29,20), chacun d'un tronc et d'une inclinaison différents ;
- SEPT arbres de mangrove aux racines arquées dressés dans l'eau peu profonde en (2,13), (9,21),
  (16,16), (26,10), (30,6), (15,3), (28,14) — DEUX AUSSI HAUTS QUE LES SAULES ;
- roselières en touffes denses et claires le long des mares ; herbes de marais sur les buttes,
  généreuses mais dans la limite d'habillage ; plantes immergées visibles par transparence.

OBJETS — une barque à fond plat amarrée en (14,13)-(14,14), une perche en travers ; une barque plus
vieille échouée dans la vase en (7,22)-(8,22) ; des nasses d'osier à demi immergées en (17,17) et (27,7).

HABITANTS — chacun cité de sa fiche, dessiné EXACTEMENT ainsi, et chacun PETIT dans la scène :
- (10,8), DEBOUT — ENTRE 1,75 ET 2 CASES, pas plus — marchant vers la GAUCHE sur la branche de
  passerelle : jeune homme élancé, peau foncée, cheveux ras, pantalon retroussé, pieds nus ou chaussures
  basses, bêche de coupe habituellement sur l'épaule.
- (16,12), DEBOUT — ENTRE 1,75 ET 2 CASES — hissant une nasse ruisselante sur la passerelle, REGARDANT
  VERS LA DROITE : femme nerveuse d'une quarantaine d'années, peau tannée, large chapeau de paille,
  manteau huilé couleur de roseaux sombres, gestes vifs et précis.
- (20,18), ACCROUPI au bord de la passerelle — accroupi, donc NETTEMENT PLUS BAS qu'un adulte debout,
  bien moins d'1,25 case — scrutant l'eau, REGARDANT DROIT VERS LE BAS face caméra : enfant d'environ
  neuf ans, peau brune, courtes boucles sombres, pieds nus, vêtements de jeu simples.
- (6,15), PATAUGEANT, les pattes DANS L'EAU touchant le fond, l'eau aux genoux, visibles par
  transparence, tête baissée, REGARDANT VERS LA DROITE : SP-008, créature échassière aux longues pattes
  fines, haute comme la poitrine d'un humain, peau lisse et mate couleur sable à pommelures discrètes,
  corps ovale compact, petite tête sur un cou courbé, courte queue en fouet. NI plumes NI fourrure. Sa
  rune, un seul trait sur le poitrail : un S ALLONGÉ, bleu-vert.
- (28,17), NAGEANT EN SURFACE, corps à moitié hors de l'eau, se déplaçant vers la GAUCHE, des rides
  s'écartant derrière elle : SP-009, créature nageuse longue comme un bras, peau lisse olive à ventre
  plus pâle, queue plate en godille, quatre courtes pattes palmées, tête ronde aux petits yeux hauts,
  deux moustaches charnues et souples. AUCUN trait de poisson : PAS de nageoires, PAS d'écailles, PAS
  d'ouïes — une peau lisse et quatre vraies pattes. Sa rune, un seul trait sur le sommet du crâne : une
  BOUCLE OUVERTE, cuivre.
- (25,13), entièrement SOUS L'EAU de la mare, bien visible par transparence, ondulant, REGARDANT DROIT
  VERS LE BAS face caméra : SP-017, créature-ruban sous-marine longue comme un humain est haut, corps
  plat ondulant comme une bannière, peau jade pâle à bandes plus sombres, quatre petites nageoires de
  gouverne, tête ronde et amicale aux grands yeux sombres, queue finissant en voile translucide. Elle ne
  perce jamais la surface. Sa rune, un seul trait derrière la tête : un MÉANDRE, vert jade lumineux.
- (18,21), tapi SUR une souche moussue au-dessus de l'eau : SP-002, petit quadrupède rond vert mousse, à
  peine plus haut que large, dos lisse arrondi, courtes pattes trapues, large bouche amicale, petits
  yeux sombres, sans queue. Sa rune, un seul trait au centre du dos : un CROISSANT, jaune pâle.
- (19,22), assis SUR LE BANC DE VASE à côté : un second individu de la même espèce SP-002, plus petit et
  plus pâle. Sa rune, au même endroit : une SPIRALE, jaune pâle.
- LA CRÉATURE MAJESTUEUSE, (7,3)-(8,4), DEUX CASES au sol, immobile dans la mare peu profonde, ses
  longues pattes d'échassier DANS L'EAU touchant le fond, REGARDANT VERS LA DROITE : SP-012, grand être
  échassier à la peau gris-bleu pâle, large éventail de membranes translucides le long du dos accrochant
  la lumière, crête courbée couronnant la tête, long cou tenu en S — immobile des heures, comme une
  pierre levée. Sa rune, un seul trait à la base du cou : un ROSEAU PLIÉ, bleu glacier.
"""

FIN = "\nRien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.\n"

if __name__ == "__main__":
    sys.exit(shoot("p4-marais-v8", preambule_fr() + COMPOSITION + RAPPEL_FINAL_FR + FIN))

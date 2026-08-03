#!/usr/bin/env python3
"""Plate P4 marsh, seventh pass — calibrated French standard. Carried from v6 (which was good on
water, stilts, trees and light): same composition, translated. Fixed here: the rack dries MARSH
HARVEST (algae, rushes) — the word fish never appears; SP-009 hardened against the fish collapse;
humans on the calibrated scale."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PREAMBULE_FR, PROJECT, TARGET, TOOL

PROMPT = PREAMBULE_FR + """
PLANCHE P4 — MARAIS. Biome : une zone humide LUXURIANTE, VERTE ET LUMINEUSE où L'EAU DOMINE : larges
mares d'eau claire et vive reliées par des chenaux lents, traversées de passerelles, roselières denses
et GRANDS arbres. La planche doit paraître claire et ensoleillée.

L'eau d'abord — PLUS D'EAU QUE DE TERRE. Claire et vive, vert d'eau et turquoise, le fond sableux
visible par transparence, JAMAIS brune ni sombre, AUCUNE brume. Mares irrégulières s'écoulant de (30,3)
vers (4,22) : une mare en (27,2)-(31,7), un chenal en (21,6)-(27,10), une mare en (14,9)-(21,12), un
chenal en (8,11)-(14,16), une mare en (3,14)-(9,18), un chenal en (2,18)-(7,22), une mare en
(23,12)-(28,14). Bancs de vase et buttes herbeuses entre elles. Nénuphars fleuris sur trois mares,
autour de (10,15), (25,18) et (6,6).

Dessine d'abord ces deux raccords de bord — passerelles de planches d'une case de large, VISIBLEMENT
coupées par leur bord :
1. Le long de la COLONNE 12, atteignant le BORD HAUT en (12,1) ; ses quatre dernières cases courent sur
   la terre ferme.
2. Le long de la RANGÉE 12, atteignant le BORD DROIT en (32,12).

Passerelles — de (12,12) descendant jusqu'à (12,20) ; une branche de (5,8) à (12,8) ; une courte
branche (13,8)-(14,8) vers le séchoir ; une branche descendant la colonne 20 de (20,12) à (20,20).
Planches usées, quelques-unes remplacées, main courante de corde côté eau. Aucune branche ne finit dans
l'eau. Aucun autre chemin n'existe.

Bâtiments — droits sur la grille, portes de 2,5 cases de haut :
- HUTTE SUR PILOTIS en (2,2)-(13,11) : douze sur dix, toit de roseaux, véranda de planches sur sa face
  basse, porte en (7,11) desservie par la branche. ELLE A LES PIEDS DANS L'EAU : ses pilotis trapus
  sortent tout droit de la mare, des algues vertes sur chaque poteau.
- SECONDE HUTTE SUR PILOTIS en (21,15)-(31,23) : onze sur neuf, visiblement différente — murs de
  planches, toit à une pente, escalier extérieur sur sa face gauche posé sur la passerelle en (20,20).
  Ses pilotis baignent EN PARTIE DANS L'EAU de la mare voisine.
- SÉCHOIR À RÉCOLTES DU MARAIS en (15,6)-(18,8) : un cadre de bois ouvert où sèchent des bottes
  d'ALGUES et de JONCS suspendues, à moitié garni, desservi par sa courte passerelle.

Végétation — abondante ET HAUTE, d'un vert frais et clair, jamais en masse sombre :
- CINQ GRANDS saules tordus, vieux, aux couronnes LARGES (trois à quatre cases) et HAUTES, trempant
  dans l'eau, en (4,17), (8,4), (17,19), (24,4), (29,20), chacun d'un tronc et d'une inclinaison
  différents ;
- SEPT arbres de mangrove aux racines arquées dressés dans l'eau peu profonde en (2,13), (9,21),
  (16,16), (26,10), (30,6), (15,3), (28,14) — DEUX AUSSI HAUTS QUE LES SAULES ;
- roselières en touffes denses le long des mares ; herbes de marais sur les buttes, généreuses mais
  dans la limite d'habillage ; plantes immergées visibles par transparence.

Objets — une barque à fond plat amarrée en (14,13)-(14,14), une perche en travers ; une barque plus
vieille échouée dans la vase en (7,22)-(8,22) ; des nasses d'osier à demi immergées en (17,17) et
(27,7).

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (10,8), DEBOUT (entre 1,75 et 2 cases), marchant vers la GAUCHE sur la branche de passerelle :
  jeune tourbier élancé, peau foncée, cheveux ras, pantalon retroussé, bêche de coupe sur l'épaule.
- En (16,12), DEBOUT, hissant une nasse ruisselante sur la passerelle, REGARDANT VERS LA DROITE :
  pêcheuse nerveuse d'une quarantaine d'années, peau tannée, large chapeau de paille, manteau huilé
  couleur de roseaux sombres, gestes vifs et précis.
- En (20,18), ACCROUPI au bord de la passerelle — accroupi, donc nettement PLUS BAS que debout —
  scrutant l'eau, REGARDANT DROIT VERS LE BAS : enfant d'environ neuf ans, peau brune, courtes boucles
  sombres, pieds nus.
- En (6,15), PATAUGEANT, les pattes DANS L'EAU touchant le fond, l'eau aux genoux, visibles par
  transparence, tête baissée, REGARDANT VERS LA DROITE : SP-008, créature échassière aux longues pattes
  fines, haute comme la poitrine d'un humain, peau lisse et mate couleur sable à pommelures discrètes,
  corps ovale compact, petite tête sur un cou courbé, courte queue en fouet. NI oiseau NI mammifère.
  Sa rune, un seul trait sur le poitrail : un S ALLONGÉ, bleu-vert.
- En (28,17), NAGEANT EN SURFACE, se déplaçant vers la GAUCHE, des rides s'écartant derrière elle :
  SP-009, créature nageuse longue comme un bras, peau lisse olive à ventre plus pâle, queue plate en
  godille, quatre courtes pattes palmées, tête ronde aux petits yeux hauts, deux moustaches charnues et
  souples. AUCUN trait de poisson : PAS de nageoires, PAS d'écailles, PAS d'ouïes — une peau lisse et
  quatre vraies pattes. Sa rune, un seul trait sur le sommet du crâne : une BOUCLE OUVERTE, cuivre.
- En (25,13), entièrement SOUS L'EAU de la mare, bien visible par transparence, ondulant, REGARDANT
  DROIT VERS LE BAS face caméra : SP-017, créature-ruban sous-marine longue comme un humain, corps plat
  ondulant comme une bannière, peau jade pâle à bandes plus sombres, quatre petites nageoires de
  gouverne, tête ronde et amicale aux grands yeux sombres, queue finissant en voile translucide. Sa
  rune, un seul trait derrière la tête : un MÉANDRE, vert jade lumineux.
- En (18,21), tapi SUR une souche moussue au-dessus de l'eau : SP-002, petit quadrupède rond vert
  mousse, à peine plus haut que large, dos lisse arrondi, courtes pattes trapues, large bouche
  amicale, petits yeux sombres, sans queue. Sa rune, un seul trait au centre du dos : un CROISSANT,
  jaune pâle.
- En (19,22), assis SUR LE BANC DE VASE à côté : un second individu de la même espèce SP-002, plus
  petit et plus pâle. Sa rune, au même endroit : une SPIRALE, jaune pâle.
- LA CRÉATURE MAJESTUEUSE en (7,3)-(8,4), DEUX CASES au sol, immobile dans la mare peu profonde, ses
  longues pattes d'échassier DANS L'EAU touchant le fond, REGARDANT VERS LA DROITE : SP-012, grand être
  échassier à la peau gris-bleu pâle, large éventail de membranes translucides le long du dos accrochant
  la lumière, crête courbée couronnant la tête, long cou tenu en S — immobile des heures, comme une
  pierre levée. Sa rune, un seul trait à la base du cou : un ROSEAU PLIÉ, bleu glacier.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p4-marais-v7.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p4-marais-v7.png", PROMPT], cwd=PROJECT
    ).returncode)

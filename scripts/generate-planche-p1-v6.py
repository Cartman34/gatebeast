#!/usr/bin/env python3
"""Plate P1 countryside, sixth pass — first plate on the calibrated standard:
French prompt, style fully defined in text (reference image as an aid only), every size in tiles and
image ratios, NEVER pixels, adult standing between 1.75 and 2 tiles, childlike toon proportions.
Composition carried over from v5 (measures and plan were good); the only v5 fault — the SP-007 pair
rendered as cat and rabbit — is countered by tighter wording on those two individuals."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PROJECT, TARGET, TOOL

PROMPT = """\
Style graphique — définition complète : rendu 3D « toon volume », doux et chaleureux. Volumes sculptés
et arrondis, comme de petites figurines modelées. Ombrage cel-shading en DEUX BANDES NETTES (une teinte
claire, une teinte ombrée, transition franche), AUCUN contour dessiné. Hautes lumières spéculaires
discrètes, liseré de lumière sur les bords. Couleurs FRANCHES, RICHES ET SATURÉES, jamais ternes,
grisées, pastel ou délavées. Détail de surface modéré : les grandes surfaces restent lisibles et unies.
(À titre d'aide seulement, ./da-gb-b4v6-scene.png montre ce rendu ; le texte ci-dessus fait foi. On en
prend le style, PAS l'échelle des personnages.)

Cadre : une image de 1536 x 1152 pixels représentant une grille de 32 colonnes sur 24 rangées de cases
carrées. UNE CASE = UN MÈTRE, un trente-deuxième de la largeur de l'image. Toutes les tailles sont
données en cases : calcule chacune à partir de la case. Ne dessine pas la grille. Les positions
s'écrivent (colonne,rangée), origine (1,1) en haut à gauche.

Caméra : forte plongée, environ soixante-dix degrés, comme une carte de jeu de rôle classique. Le sol
remplit toute l'image. Pas d'horizon, pas de ciel, pas de point de fuite. Soleil en haut à gauche, une
seule ombre douce par élément, portée vers le bas à droite. Image lumineuse, nette de bord en bord.

L'ÉCHELLE EST LA PREMIÈRE CHOSE VÉRIFIÉE SUR LE RÉSULTAT — LES HUMAINS DOIVENT SEMBLER PETITS, comme
des figurines dans un grand paysage :
- Un adulte DEBOUT fait ENTRE 1,75 ET 2 CASES de haut — moins d'un douzième de la hauteur de l'image.
  Jamais plus. S'il paraît grand ou proche, c'est faux.
- Assis, accroupi ou penché, un personnage est nettement plus bas. Un enfant est nettement plus petit
  qu'un adulte : environ 1,25 case debout.
- Aucun humain ne dépasse UNE CASE de large, même corpulent.
- Proportions : dans ce monde, même les adultes semblent un peu enfantins — silhouettes rondes et
  compactes, tête un peu grande, à la manière toon. On les dessine AVEC ces proportions et PETITS.
- Toute PORTE fait 2,5 cases de haut et une case de large — nettement plus haute qu'un adulte debout.
- Aucune habitation ne fait moins de 8 CASES dans sa plus petite dimension.
- RIEN DE CONSTRUIT ne tient dans une seule case : toute construction couvre au moins 2 cases. Une case
  porte des sacs, une chaise, un tonneau — rien de bâti.
- Les emprises remplissent leur rectangle sans déborder sur les cases voisines ; seule la hauteur
  s'élève au-dessus. TOUT EST DROIT sur les axes de la grille, rien en diagonale.

Deux limites mesurées : au plus UNE CASE SUR SEPT sombre ; au plus UNE CASE SUR CINQ d'habillage libre
(touffes, fleurs, cailloux), le reste en prairie unie.

Varier les orientations : certains humains regardent DROIT VERS LE BAS, face caméra, visage bien
visible ; au moins une créature aussi, de face et pas en diagonale.

Cohérence : rien ne se termine dans le vide. Chaque bâtiment est desservi jusqu'à sa porte ; le pont
repose sur la route à ses deux bouts.

Exhaustif : dessine ce qui est listé et RIEN D'AUTRE — aucun humain, créature, bâtiment ou objet
supplémentaire.

AUCUN ANIMAL RÉEL N'EXISTE — ni oiseau, ni chat, ni lapin, ni chien, ni bétail, ni insecte, ni aucun
animal réel recoloré ou à peine déguisé. Chaque être vivant ci-dessous est décrit par sa fiche : on le
dessine EXACTEMENT comme décrit, et rien de vivant au-delà. Aucun n'a de visage humain. Les humains ne
portent pas de rune.

Runes : une par créature, comme précisé — UN SEUL trait continu, UNE seule couleur, épousant la courbe
du corps, scintillant faiblement, environ un quart de case. Deux runes de l'image ne partagent jamais
la même forme.

PLANCHE P1 — CAMPAGNE BOISÉE. Biome : campagne cultivée et vallonnée, champs bordés de haies, un
verger, de LARGES PRAIRIES UNIES d'un vert vif et frais, arbres feuillus. Chaleureux, lumineux, saturé.

Dessine d'abord ces deux sorties de bord — chacune visiblement coupée par son bord :
1. Une ROUTE DE TERRE, une case de large, le long de la RANGÉE 16, du BORD GAUCHE en (1,16) au BORD
   DROIT en (32,16).
2. Une ROUTE DE TERRE, une case de large, descendant la COLONNE 12 depuis (12,16) et ATTEIGNANT LE BORD
   BAS en (12,24).

Le ru : un ru clair, une case de large, coule TOUT DROIT le long de la COLONNE 14, du bord haut (14,1)
au bord bas (14,24), eau vive. Un PONT DE PIERRE en (13,16)-(15,16) porte la route par-dessus, ses deux
bouts sur la route. Le ru ne croise RIEN d'autre : aucun bâtiment, aucun champ, aucun autre chemin.

Chemins d'accès — en terre, une case de large : colonne 8 de (8,16) à la porte de la ferme ; colonne 19
de (19,15) à (19,10) vers les portes de la grange ; colonne 25 de (25,16) à (25,10) puis un pas à
droite vers la porte du moulin ; colonne 17 de (17,16) à (17,18), s'arrêtant À la porte de la
chaumière. Aucun autre chemin n'existe.

Bâtiments — chaque porte fait 2,5 cases de haut, une case de large :
- FERME en (2,2)-(13,11) : douze cases sur dix, pierre et colombage, toit de tuiles, cheminée, porte
  sur sa face basse en (8,11). État : usée, entretenue.
- GRANGE en (15,3)-(24,9) : dix sur sept, bardage rouge, double porte en (19,9) de trois cases de haut,
  fenil.
- MOULIN en (26,4)-(31,10) : moulin rond en pierre à quatre ailes, porte sur sa face basse en (26,10).
- CHAUMIÈRE en (15,19)-(23,24) : neuf sur six visibles, toit de chaume, porte sur sa face haute en
  (17,19).

Champs et verger — un VERGER MÊLÉ en (24,17)-(31,23), arbres tous adultes, chacun d'une hauteur et
d'une couronne différentes : deux pommiers à 80 % de fruits, un poirier à 50 %, un prunier à 30 %, un
cerisier en fleurs sans fruits, un cognassier à 20 %. Un potager clos de haies en (2,12)-(7,15), soigné,
la moitié des rangs plantés. Un champ de blé mûr en (26,11)-(31,15). Des haies le long de (2,17)-(7,17)
et (15,12)-(18,12).

Végétation — un large vieux chêne, dense, en (10,18) ; trois bouleaux fins en (3,18), (16,14), (30,2) ;
deux sapins sombres en (1,8) et (31,20). Partout ailleurs : LARGE PRAIRIE UNIE, habillage dans la
limite d'une case sur cinq.

Objets — trois meules de foin de tailles différentes en (24,10), (27,16), (29,16) ; un PUITS de pierre
à petit toit couvrant (16,10)-(17,10), deux cases ; une CHARRETTE à demi chargée de sacs couvrant
(10,15)-(11,15), deux cases ; un abreuvoir plein en (12,10).

Habitants — chacun décrit par sa fiche, dessiné EXACTEMENT ainsi :
- En (9,13), DEBOUT (entre 1,75 et 2 cases), fourchant du foin, REGARDANT DROIT VERS LE BAS face
  caméra, visage bien visible : fermier d'une quarantaine d'années, peau brun foncé, cheveux noirs très
  courts, carrure large, tunique de travail brun terre aux manches retroussées, bottes solides, visage
  ouvert et buriné.
- En (18,16), DEBOUT, portant un panier de pommes, marchant vers la GAUCHE sur la route : femme de la
  trentaine, traits d'Asie de l'Est, chignon bas, silhouette mince, tablier rouille sur un chemisier
  crème.
- En (27,11), DEBOUT devant la porte du moulin, un sac de farine à ses pieds, REGARDANT VERS LE BAS :
  vieux meunier, peau claire poudrée de farine, cheveux gris et sourcils épais, maigre et légèrement
  voûté, chemise de lin pâle, tablier de toile noué haut.
- En (20,16) et (21,16), deux enfants nettement PLUS PETITS que les adultes, courant vers la DROITE :
  un enfant d'environ neuf ans, peau brune, courtes boucles sombres, pieds nus, vêtements de jeu
  simples — et un enfant d'environ sept ans, peau claire, cheveux blonds ébouriffés, blouse verte.
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
  compact, petite tête sur un cou courbé, courte queue en fouet. NI oiseau NI mammifère : peau lisse,
  sans plumes ni fourrure. Sa rune, un seul trait sur le poitrail : un S ALLONGÉ, bleu-vert.
- En (5,19), assis, et en (6,19), trottant vers la DROITE : deux individus de l'espèce SP-007 —
  créature fine gris argenté à la LONGUE QUEUE ANNELÉE portée en panache, grands yeux ronds, fourrure
  courte et dense, corps souple et agile SANS AUCUN trait de chat ni de lapin : museau court arrondi,
  petites oreilles rondes, pattes fines à larges doigts. Le premier, plus grand et plus foncé, porte sa
  rune au bout de la queue : une GOUTTE, rose. Le second, plus petit et plus pâle, porte la sienne au
  même endroit : une BOUCLE CROISÉE, rose pâle.
- LA CRÉATURE MAJESTUEUSE en (4,21)-(5,22), DEUX CASES au sol, debout calmement dans la prairie
  ouverte, loin des chemins, tête haute, REGARDANT VERS LA GAUCHE : SP-010, grand être cervidé au
  pelage ambre profond, crinière de longs poils pâles le long du cou, pattes fines et fortes, larges
  bois dorés pâles ramifiés s'élevant bien au-dessus de lui et se courbant vers l'intérieur comme une
  couronne, queue en long pinceau — silhouette inventée, aucun cerf réel copié. Sa rune, un seul trait
  sur l'épaule gauche : une COURONNE OUVERTE à trois pointes d'un seul geste, or pâle.

Rien d'autre dans l'image : pas de texte, pas d'interface, pas de logo, pas de grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-p1-campagne-v6.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-p1-campagne-v6.png", PROMPT], cwd=PROJECT
    ).returncode)

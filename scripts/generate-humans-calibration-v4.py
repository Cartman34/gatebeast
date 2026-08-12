#!/usr/bin/env python3
"""Human scale calibration, fourth attempt — operator's request: 3 men, 3 women, 2 children, each shown
STANDING on the top row and, directly below, the SAME person SITTING. French prompt, sizes in tiles and
image ratios only — never pixels for elements (frame size stays, the backend needs it).

USAGE
  A FROZEN CALIBRATION PROMPT — a historical document, not a command to run again. It produced
  assets/revue-da/calibration-humains-v4.png, the sheet the human scale of every later plate is held
  to. It is kept so the exact text sent to the generator can be read back next to the image it made.
  It takes no argument and answers no help: there is nothing to call it with. Running it would spend
  a generation on a sheet that already exists.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PROJECT, TARGET, TOOL

PROMPT = """\
Style graphique — définition complète : rendu 3D « toon volume », doux et chaleureux. Volumes sculptés
et arrondis, comme de petites figurines modelées. Ombrage cel-shading en DEUX BANDES NETTES, AUCUN
contour dessiné. Hautes lumières spéculaires discrètes, liseré de lumière sur les bords. Couleurs
FRANCHES, RICHES ET SATURÉES, jamais ternes ni délavées. Grandes surfaces lisibles et unies.
(À titre d'aide seulement, ./da-gb-b4v6-scene.png montre ce rendu ; le texte ci-dessus fait foi.)

Cadre : une image de 1152 x 576 pixels — une prairie vue en forte plongée, environ soixante-dix degrés.
L'image représente une grille de 24 colonnes sur 12 rangées de cases carrées : UNE CASE = UN MÈTRE, un
vingt-quatrième de la largeur de l'image. Toutes les tailles ci-dessous sont données en cases : calcule
chaque taille à partir de la case. Ne dessine pas la grille. Le sol — herbe rase d'un vert vif et uni —
remplit toute l'image. Pas d'horizon, pas de ciel. Soleil en haut à gauche, une seule ombre douce par
personnage. Image lumineuse, nette partout.

CETTE IMAGE N'A QU'UN SUJET : L'ÉCHELLE HUMAINE. LES HUMAINS DOIVENT SEMBLER PETITS — des figurines sur
une grande table :
- Un adulte DEBOUT fait ENTRE 1,75 ET 2 CASES de haut — un sixième de la hauteur de l'image, jamais
  plus. S'il paraît grand ou proche, c'est faux.
- Un enfant DEBOUT est nettement plus petit : environ 1,25 case.
- Un personnage ASSIS par terre est bien plus bas que debout : environ 1,25 case, à peine plus qu'un
  enfant debout.
- Aucun personnage ne dépasse UNE CASE de large, même corpulent.
- Proportions : dans ce monde, même les adultes semblent un peu enfantins — silhouettes rondes et
  compactes, tête un peu grande, à la manière toon. On les dessine AVEC ces proportions et PETITS ; on
  ne les agrandit jamais pour des proportions réalistes.

SEIZE FIGURES EN DEUX RANGÉES. Rangée haute : huit personnages DEBOUT, côte à côte, espacés d'UNE CASE
vide entre chacun, tous FACE À LA CAMÉRA, visage bien visible, bras détendus. Rangée basse : LES HUIT
MÊMES PERSONNAGES, chacun ASSIS PAR TERRE jambes croisées, exactement SOUS sa version debout — même
visage, même peau, mêmes cheveux, mêmes vêtements, seule la posture change.

Les huit personnages, de gauche à droite :
1. HOMME — fermier d'une quarantaine d'années, peau brun foncé, cheveux noirs très courts, carrure
   large, tunique de travail brun terre, bottes solides.
2. HOMME — vieux meunier, peau claire poudrée de farine, cheveux gris et sourcils épais, maigre et
   légèrement voûté, chemise de lin pâle, tablier de toile noué haut.
3. HOMME — pêcheur d'une quarantaine d'années, peau claire rougie par le soleil, barbe blonde, bonnet
   de laine roulé, chemise bleue rapiécée.
4. FEMME — la trentaine, traits d'Asie de l'Est, chignon bas, silhouette mince, tablier rouille sur un
   chemisier crème.
5. FEMME — boulangère d'une cinquantaine d'années, peau brun chaud, fichu blanc, tablier fariné sur une
   robe prune, avant-bras solides, visage rieur.
6. FEMME — pêcheuse de la trentaine, peau brune, boucles noires sous un foulard noué, robe bleue
   délavée sans manches, épaules solides.
7. ENFANT — environ neuf ans, peau brune, courtes boucles sombres, pieds nus, vêtements de jeu simples.
8. ENFANT — environ sept ans, peau claire, cheveux blonds ébouriffés, blouse verte.

Rien d'autre dans l'image : aucun bâtiment, aucune créature, aucun objet, aucun texte, aucune grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-calibration-humains-v4.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/calibration-humains-v4.png", PROMPT], cwd=PROJECT
    ).returncode)

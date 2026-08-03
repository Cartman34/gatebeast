#!/usr/bin/env python3
"""Human scale calibration, second attempt — owner's directives:
- the style is defined COMPLETELY IN TEXT, self-sufficient; the reference image only aids comprehension;
- the prompt is in FRENCH (owner's decision: generators understand French well and it can be more
  precise; the English-sheets convention will migrate accordingly);
- the key instruction: humans must LOOK SMALL; sizes are given as ratios inside the image, not absolute
  pixels, which the first attempt proved unheard (x1.55 to x2 on every figure)."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import ASSETS, PROJECT, TARGET, TOOL

PROMPT = """\
Style graphique — définition complète : rendu 3D « toon volume », doux et chaleureux. Volumes sculptés
et arrondis, comme de petites figurines modelées. Ombrage cel-shading en DEUX BANDES NETTES (une teinte
claire, une teinte ombrée, à transition franche), AUCUN contour dessiné. Hautes lumières spéculaires
discrètes et liseré de lumière sur les bords. Couleurs FRANCHES, RICHES ET SATURÉES, jamais ternes,
grisées, pastel ou délavées. Détail de surface modéré : les grandes surfaces restent lisibles et unies.
(À titre d'aide seulement, l'image ./da-gb-b4v6-scene.png montre ce rendu ; le texte ci-dessus fait foi.)

Cadre : une image de 768 x 384 pixels représentant une prairie vue en forte plongée, environ soixante-dix
degrés, comme une carte de jeu de rôle classique. Le sol — une herbe rase d'un vert vif et uni — remplit
toute l'image. Pas d'horizon, pas de ciel. Soleil en haut à gauche, une seule ombre douce par personnage,
portée vers le bas à droite. Image lumineuse, nette partout.

CETTE IMAGE N'A QU'UN SUJET : L'ÉCHELLE HUMAINE. LES HUMAINS DOIVENT SEMBLER PETITS. Ils sont posés sur
une grande prairie presque vide et paraissent minuscules dedans, comme des figurines sur une grande
table :

- Les quatre personnages ensemble, ombres comprises, tiennent dans le QUART CENTRAL de l'image ; tout le
  reste n'est que de l'herbe vide.
- Un adulte debout est PETIT : sa hauteur fait UN QUART de la hauteur de l'image, pas davantage. S'il
  paraît grand ou proche, c'est faux.
- L'enfant debout est nettement plus petit que les adultes : les deux tiers de leur hauteur.
- L'homme assis par terre est bien plus bas qu'un adulte debout : à peine plus haut que l'enfant.
- Aucun personnage n'est plus large que LA MOITIÉ de sa propre hauteur debout, même corpulent.

Proportions des personnages : dans ce monde, même les adultes semblent un peu enfantins — silhouettes
rondes et compactes, tête un peu grande, à la manière toon. On dessine l'adulte AVEC ces proportions et
PETIT dans l'image ; on ne l'agrandit jamais pour lui donner des proportions réalistes.

Quatre humains, côte à côte sur une même ligne horizontale au centre, régulièrement espacés d'environ
une largeur de personnage, tous FACE À LA CAMÉRA, visage bien visible, bras détendus :
1. Un homme DEBOUT : fermier d'une quarantaine d'années, peau brun foncé, cheveux noirs coupés très
   court, carrure large, tunique de travail brun terre aux manches retroussées, bottes solides, visage
   ouvert et buriné.
2. Une femme DEBOUT : la trentaine, traits d'Asie de l'Est, cheveux noirs en chignon bas, silhouette
   mince, tablier rouille sur un chemisier crème.
3. Un enfant DEBOUT : environ neuf ans, peau brune, courtes boucles sombres, pieds nus, vêtements de jeu
   simples.
4. Un homme ASSIS par terre : pêcheur d'une quarantaine d'années, peau claire rougie par le soleil,
   barbe blonde, bonnet de laine roulé, chemise bleue rapiécée aux manches retroussées, mains épaisses.

Rien d'autre dans l'image : aucun bâtiment, aucune créature, aucun objet, aucun texte, aucune grille.
"""

if __name__ == "__main__":
    (ASSETS / "prompt-calibration-humains-v2.txt").write_text(PROMPT, encoding="utf-8")
    sys.exit(subprocess.run(
        ["php", TOOL, f"{TARGET}/calibration-humains-v2.png", PROMPT], cwd=PROJECT
    ).returncode)

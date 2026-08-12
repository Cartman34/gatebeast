"""Shared base for plate generation prompts.

Single source for the style anchor, the scale/rules block, and the WITNESS SHEETS: every creature and
every human that appears in a prompt is quoted from its sheet WORD FOR WORD — the generator never
invents an inhabitant. Sheets live in the design (referentiels/contenu/creatures-temoins.md and
referentiels/visuel/inventaire/personnages.md); the texts below are their verbatim copies. When a sheet changes there, it
changes here in the same gesture.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

STYLE = (
    "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and rim "
    "light, cel shading in two crisp bands, no outline."
)

ANCHOR = (
    "STYLE REFERENCE — ./da-gb-b4v6-scene.png is the exact target. Reproduce ITS rendering with no "
    "deviation: same modelling of volumes, same crisp two-band cel shading, same FRANK SATURATED COLOURS "
    "— rich and intense, never muted, greyed, pastel or washed out — same amount of surface detail, same "
    "degree of stylisation. PEOPLE AND CREATURES ARE RENDERED IN EXACTLY THAT SAME STYLE — never more "
    "realistic, never flatter. Take ONLY the style from it; the composition below applies."
)

# The old English SCALE block is gone (operator, 2026-08-03): the French base below is the single
# standard for every plate. It carried a pixel size for the runes, which the standard forbids.

# Witness sheets — creatures. Verbatim from referentiels/contenu/creatures-temoins.md.
SPECIES = {
    "SP-001": ("A small round quadruped the size of a fox cub. Warm amber fur (#D98A33) over back and "
               "head, cream belly and muzzle (#F5E6CC), four short legs with cream paws, two large "
               "rounded ears amber outside and cream inside, big dark friendly eyes, short thick tail "
               "with a cream tip.", "in the middle of the forehead"),
    "SP-002": ("A small round mossy-green quadruped, barely taller than it is wide, with a smooth "
               "rounded back, short stubby legs, a wide friendly mouth and small dark eyes. No tail.",
               "at the centre of the back"),
    "SP-004": ("A plump low creature covered in soft moss-like fur, shaped like a rounded stone, with a "
               "broad calm face, tiny ears and no visible legs when resting.", "on the left flank"),
    "SP-005": ("A small pale-blue creature sitting up on its hind legs, with long floppy ears, a slim "
               "body, a tufted tail and an alert pointed muzzle.", "at the base of the right ear"),
    "SP-006": ("A stocky rust-red quadruped with a rounded shell-like back, two short blunt horns, "
               "thick legs and a slow heavy stance.", "at the centre of the shell"),
    "SP-007": ("A slim silver-grey creature with a long ringed tail, large round eyes, short dense fur "
               "and a light agile build, often perched.", "at the tip of the tail"),
    "SP-008": ("A long-limbed wading creature, chest-high to a human, with smooth pale sand-coloured "
               "skin, four slender stilt legs ending in wide splayed toes, a compact oval body, a small "
               "head on a curved neck and a short whisk tail. No feathers, no fur — smooth matte skin "
               "with faint darker dapples.", "on the chest"),
    "SP-009": ("A sleek swimming creature the length of an arm, smooth olive skin with a paler belly, a "
               "flattened paddle tail it sculls with, four short webbed limbs, a rounded head with small "
               "eyes set high and two soft fleshy whiskers. It swims at the surface, body half out of "
               "the water.", "on the top of the skull"),
    "SP-010": ("A tall stag-like being, two tiles of ground at rest, with a deep amber coat, a mane of "
               "long pale fur down the neck, slender strong legs and broad branching antlers of pale "
               "gold rising well above it. Its bearing is calm and regal; its silhouette is invented — "
               "the antlers curve inward like a crown and the tail is a long tuft, no real deer copied.",
               "on the left shoulder"),
    "SP-012": ("A tall wading being, two tiles of ground, standing on long stilt legs in shallow water — "
               "pale grey-blue skin, a wide fan of translucent membranes along its back catching the "
               "light, a curved crest crowning its head, a long neck held in an S. Motionless for hours, "
               "like a standing stone.", "at the base of the neck"),
    "SP-014": ("A powerful mountain creature, two tiles of ground, with slate-blue stone-like plates "
               "along its back and shoulders, a heavy calm head with two backswept horns, thick legs "
               "with broad feet, and moss growing in the seams of its plates. It moves rarely and "
               "slowly, like a hillside deciding to walk.", "on the left foreleg"),
    "SP-015": ("A tall shore-strider, two tiles of ground, pearl-white with sea-green mottling, four "
               "long wading legs, a deep keel-shaped chest, a collar of translucent fins around the "
               "neck that stir like anemones, and a narrow head with dark calm eyes. NOT a horse: the "
               "body is keel-chested and legs jointed backwards at the hock, its silhouette belongs to "
               "no real animal.", "on the left flank"),
    "SP-016": ("A round grazing creature the size of a large dog, covered in dense moss-green wool over "
               "a slate-grey skin, SIX short sturdy legs, two horns curling backwards like snail "
               "shells, a flat friendly muzzle and no visible tail.", "on the forehead, between the "
               "horns"),
    "SP-017": ("A ribbon-like underwater creature, as long as a human is tall, its flat body undulating "
               "like a banner — pale jade skin with darker bands, four small steering fins, a blunt "
               "friendly head with large dark eyes, and a tail ending in a translucent veil. Clearly "
               "visible through clear water; never breaks the surface.", "behind the head"),
}

# INDIVIDUALS IS GONE, AND WITH IT THE LAST COPY OF THE RUNES (2026-08-12). It mapped each individual to its species and to the wording of its rune — the second
# half being a copy of assets/runes.json, and the first half the only machine-side trace of a link the content referential already declared. The rune wording is
# no longer wanted anywhere: a creature sprite is now produced WITHOUT its rune, which is traced at render on the anchor the image declares. The species link
# moved into assets/runes.json, beside the individual it belongs to, and asset_common.py reads it there.

# Witness sheets — humans. Verbatim from referentiels/visuel/inventaire/personnages.md.
HUMANS = {
    "HU-001": "A farmer in his forties, deep brown skin, short tight-cropped black hair, broad build, a "
              "plain earth-brown work tunic with rolled sleeves, sturdy boots. Open, weathered face.",
    "HU-002": "A woman in her thirties, East Asian features, black hair in a low bun, slim build, a "
              "rust-red apron over a cream blouse, carrying things with easy habit.",
    "HU-003": "An old miller, pale skin dusted with flour, grey hair and thick grey brows, lean and "
              "slightly stooped, a pale linen shirt and a canvas apron tied high.",
    "HU-008": "A lean young man, dark skin, close-cropped hair, rolled trousers, bare feet or low "
              "boots, a cutting spade habitually over his shoulder.",
    "HU-009": "A wiry woman in her forties, tanned skin, a wide straw hat, an oiled coat the colour of "
              "dark reeds, quick precise gestures.",
    "HU-011": "A weathered woman in her fifties, olive skin, braided grey hair, a thick woven shawl "
              "over a wool dress, a herder's staff.",
    "HU-012": "A stocky man in his thirties, medium-brown skin, a leather helmet with a small unlit "
              "lamp, a dusty canvas jacket, heavy gloves at his belt.",
    "HU-013": "A child of about nine, brown skin, short dark curls, bare feet, simple play clothes, "
              "always in motion.",
    "HU-014": "A young traveller, pale freckled skin, red hair, a small worn pack with a bedroll, "
              "sturdy walking boots, a curious face.",
    "HU-015": "A child of about seven, pale skin, blond tousled hair, a green smock, quick and "
              "laughing, often chasing or being chased.",
    "HU-016": "A fisherwoman in her thirties, brown skin, black curls under a knotted headscarf, a "
              "sleeveless sun-faded blue dress, strong shoulders, a woven basket of nets on her hip.",
    "HU-017": "A fisherman in his forties, pale sun-reddened skin, blond beard, a rolled woollen cap, a "
              "patched blue shirt with rolled sleeves, thick weathered hands.",
}


# French preamble — the calibrated standard adopted by the operator (2026-08-03): prompt in French, style
# fully defined in text, every size in tiles and image ratios, NEVER pixels for elements, humans small.
# The art direction itself, in one paragraph — the single source shared by the plates and by the POC
# assets. The direction is validated and frozen: this text is what makes an asset match a plate.
STYLE_FR = """\
Style graphique — définition complète : rendu 3D « toon volume », doux et chaleureux. Volumes sculptés
et arrondis, comme de petites figurines modelées. Ombrage cel-shading en DEUX BANDES NETTES, toutes
deux CLAIRES : une teinte pleinement éclairée et une teinte d'ombre à peine plus soutenue, transition
franche. AUCUN contour dessiné. Hautes lumières spéculaires discrètes, liseré de lumière sur les bords.
Couleurs FRANCHES, RICHES ET SATURÉES — claires ET intenses à la fois, jamais ternes, grisées, pastel
ou délavées. Détail de surface modéré : les grandes surfaces restent lisibles et unies."""

PREAMBULE_FR = STYLE_FR + """
(À titre d'aide seulement, ./da-gb-b4v6-scene.png montre ce rendu ; le texte ci-dessus fait foi. On en
prend le style, PAS l'échelle des personnages, ET PAS LE NIVEAU DE LUMIÈRE : la planche demandée est
NETTEMENT PLUS LUMINEUSE que cette image d'aide.)

Cadre : une image de 1536 x 1152 pixels représentant une grille de 32 colonnes sur 24 rangées de cases
carrées. UNE CASE = UN MÈTRE, un trente-deuxième de la largeur de l'image. Toutes les tailles sont
données en cases : calcule chacune à partir de la case. Ne dessine pas la grille. Les positions
s'écrivent (colonne,rangée), origine (1,1) en haut à gauche.

Caméra : forte plongée, environ soixante-dix degrés, comme une carte de jeu de rôle classique. Le sol
remplit toute l'image. Pas d'horizon, pas de ciel, pas de point de fuite. Image nette de bord en bord.

LUMIÈRE — la planche est FRANCHEMENT ET ÉGALEMENT LUMINEUSE, du premier au dernier centimètre. C'est un
SOLEIL DE FIN DE MATINÉE, haut et vif, venant d'en haut à gauche :
- CHAQUE SURFACE REÇOIT LA LUMIÈRE. Les toits sont ÉCLAIRÉS, teintes chaudes et claires. Les façades
  sont ÉCLAIRÉES, y compris celles tournées vers le bas. Le sol est éclairé partout, sous les arbres
  comme entre les bâtiments. Le fond d'une ruelle, d'un porche ou d'un sous-bois reste LISIBLE : on y
  distingue la matière et la couleur.
- Les OMBRES SONT COURTES ET PÂLES : une seule par élément, portée vers le bas à droite, longue d'un
  tiers de la hauteur de l'élément au plus, d'un ton simplement plus doux que la surface qu'elle couvre
  — une ombre reste de la couleur locale, en plus tendre.
- L'eau, la roche et les toits d'ardoise sont eux aussi rendus dans leurs valeurs CLAIRES : eau
  turquoise lumineuse, roche gris pâle, ardoise bleu clair.
- Repère chiffré vérifié à la mesure : la luminance moyenne de l'image se tient ENTRE 115 ET 130 sur
  256, et AU PLUS UNE CASE SUR DIX lit comme sombre. Une planche plus terne que cela est fautive
  quelle que soit sa composition.

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
- Aucune habitation ne fait moins de 8 CASES dans sa plus petite dimension — sa façade fait au moins
  quatre fois la hauteur d'un adulte debout.
- RIEN DE CONSTRUIT ne tient dans une seule case : toute construction couvre au moins 2 cases. Une case
  porte des sacs, une chaise, un tonneau — rien de bâti.
- Les emprises remplissent leur rectangle sans déborder sur les cases voisines ; seule la hauteur
  s'élève au-dessus. TOUT EST DROIT sur les axes de la grille, rien en diagonale.

Trois limites mesurées : NEUF CASES SUR DIX sont dans les valeurs claires — au plus une case sur dix lit
comme sombre ; au plus UNE CASE SUR CINQ d'habillage libre (touffes, fleurs, cailloux) ; et LA PLANCHE
EST PLEINE — environ TROIS CASES SUR QUATRE portent quelque chose à voir, une planche trop vide est
aussi fautive qu'une planche fouillie.

Varier les orientations : certains humains regardent DROIT VERS LE BAS, face caméra, visage bien
visible ; au moins une créature aussi, de face et pas en diagonale.

Cohérence : rien ne se termine dans le vide. Chaque bâtiment est desservi jusqu'à sa porte ; un pont
repose sur sa voie à ses deux bouts ; une barque est amarrée ou tirée au sec.

Exhaustif : dessine ce qui est listé et RIEN D'AUTRE — aucun humain, créature, bâtiment, chemin ou
objet supplémentaire.

AUCUN ANIMAL RÉEL N'EXISTE — ni oiseau, ni chat, ni lapin, ni chien, ni bétail, ni poisson, ni insecte,
ni aucun animal réel recoloré ou à peine déguisé. Chaque être vivant est décrit par sa fiche : on le
dessine EXACTEMENT comme décrit, et rien de vivant au-delà. Aucun n'a de visage humain. Les humains ne
portent pas de rune.

Runes : une par créature, comme précisé — UN SEUL trait continu, UNE seule couleur, épousant la courbe
du corps, scintillant faiblement, environ un quart de case. Deux runes de l'image ne partagent jamais
la même forme.
"""


# Closing block, appended AFTER every composition (operator, 2026-08-03): on a dense plate the long text
# dilutes the scale rule stated at the top, so it is repeated last, just before "nothing else".
RAPPEL_FINAL_FR = """
RAPPEL FINAL, À VÉRIFIER AVANT DE RENDRE L'IMAGE — C'EST LE PREMIER CRITÈRE DE RECETTE :
- LES HUMAINS DOIVENT SEMBLER PETITS, comme des figurines dans un grand paysage. Un adulte DEBOUT fait
  ENTRE 1,75 ET 2 CASES de haut — moins d'un douzième de la hauteur de l'image — JAMAIS plus. S'il
  paraît grand ou proche, c'est faux : redessine-le plus petit.
- Assis, à genoux ou penché : nettement plus bas. Un enfant : nettement plus petit, environ 1,25 case.
- Aucun humain ne dépasse UNE CASE de large. Proportions rondes, compactes, un peu enfantines, tête un
  peu grande — on ne l'agrandit JAMAIS pour faire tenir des proportions réalistes.
- Toute porte reste NETTEMENT PLUS HAUTE qu'un adulte debout.
- Reprends chaque coordonnée donnée plus haut et vérifie que l'élément est bien à cette case, avec
  l'emprise annoncée : la composition se lit case par case, rien n'est placé librement.
- LUMIÈRE : soleil de fin de matinée, franc et haut. Toits éclairés, façades éclairées, sol éclairé
  partout, ombres courtes et pâles de la couleur locale. Neuf cases sur dix dans les valeurs claires.
"""


def preambule_fr(habillage: str = "UNE CASE SUR CINQ") -> str:
    """The French base, with the free-dressing ceiling set for this biome.

    The operator's Q1A decision: the ceiling is per biome, not global — an open plateau or a countryside
    reads empty at one tile in five. The default reproduces PREAMBULE_FR unchanged.
    """
    original = "au plus UNE CASE SUR CINQ d'habillage libre"
    replacement = f"au plus {habillage} d'habillage libre"
    if original not in PREAMBULE_FR:
        raise ValueError("dressing sentence not found in PREAMBULE_FR")
    return PREAMBULE_FR.replace(original, replacement)


def human(code: str) -> str:
    return f"{code}: {HUMANS[code]}"


def shoot(key: str, prompt: str) -> int:
    """Save the prompt next to the image and launch the generation — never twice for one key.

    The operator's absolute rule: one shot per plate version. An existing target image means the shot was
    already made; this refuses rather than overwriting it.
    """
    # The prompt is saved first, so the pre-flight check can read the exact text before any shot.
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    if "--dump" in sys.argv:
        print(f"DUMPED prompt-{key}.txt — no generation")
        return 0
    target = ASSETS / f"planche-{key}.png"
    if target.is_file():
        print(f"REFUSED {target.name} already exists — one shot per version, never a second")
        return 1
    return subprocess.run(
        ["php", TOOL, f"{TARGET}/planche-{key}.png", prompt], cwd=PROJECT
    ).returncode

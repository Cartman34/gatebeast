"""Shared base for POC asset generation — one subject per image, in the validated art direction.

An asset is not a plate: a plate is a composed scene, an asset is ONE subject alone, framed to fill the
image, meant to be cut out and placed as a sprite. Everything the two have in common — the art
direction, the camera, the ban on free-described inhabitants, the ban on pixel sizes — is shared with
plate_common so the two can never drift apart.

Two families, because they need opposite backgrounds:
- CUTOUT assets (building, vegetation, human, creature): the subject sits alone on a plain background
  that exists only to be removed. Codex is not asked for transparency (it writes PNG through a text
  agent and transparency has never been verified) — it is asked for a flat, pure magenta field, a
  colour no asset of this world contains, which any tool can key out.
- TILE assets (ground): there is no background at all. The material fills the frame edge to edge.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import HUMANS, INDIVIDUALS, SPECIES, STYLE_FR

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/poc"
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "poc"

# The key colour. Pure magenta appears in no material of this world — grass, stone, wood, water, fur —
# so keying it out cannot eat into a subject.
FOND = "MAGENTA PUR, c'est-à-dire un rose-violet électrique parfaitement saturé (rouge au maximum, vert " \
       "absent, bleu au maximum)"

CAMERA_FR = """\
Caméra : forte plongée, environ SOIXANTE-DIX DEGRÉS sous l'horizontale — exactement l'angle des cartes
de jeu de rôle vues de dessus, le même que celui des planches du monde. On regarde le sujet d'en haut et
un peu de face. Pas d'horizon, pas de ciel, pas de point de fuite. Lumière : soleil de fin de matinée
venant du HAUT À GAUCHE, franc et clair ; le sujet est pleinement éclairé, ses faces tournées vers le
bas restent lisibles, l'ombrage se fait en deux bandes claires."""

CADRAGE_CUTOUT = f"""\
UN SEUL SUJET, ET RIEN D'AUTRE. L'image contient le sujet décrit ci-dessous et absolument rien de plus :
aucun décor, aucun sol, aucune herbe, aucun accessoire, aucun autre être vivant, aucun cadre, aucune
bordure, aucun texte.

LE FOND EST UNI ET UNIQUE : toute la surface qui n'est pas le sujet est remplie d'un {FOND}, parfaitement
plat et identique partout — une seule et même couleur, sans dégradé, sans texture, sans vignettage, sans
motif, sans damier. AUCUNE OMBRE PORTÉE sur ce fond : le sujet ne projette pas d'ombre, il n'y a pas de
sol sous lui. L'ombrage reste sur le corps du sujet lui-même.

CADRAGE : le sujet est CENTRÉ et il REMPLIT LE CADRE — sa plus grande dimension occupe environ QUATRE
CINQUIÈMES de la hauteur de l'image, et il reste une marge de fond tout autour. Rien du sujet n'est
coupé par un bord."""

CADRAGE_TUILE = """\
UNE SEULE MATIÈRE, EN PLEIN CADRE. L'image montre uniquement la surface décrite ci-dessous, vue d'en
haut, remplissant TOUTE l'image d'un bord à l'autre. Il n'y a pas de fond : la matière EST l'image.
Aucun objet posé dessus, aucun être vivant, aucune bordure, aucun cadre, aucun texte, aucune ombre
portée d'un élément extérieur.

La matière est RÉGULIÈRE SUR TOUTE LA SURFACE : sa densité, sa teinte et son grain sont les mêmes au
centre et sur les bords, sans zone plus claire ni plus sombre, sans motif dominant qui attirerait l'œil
à un endroit. Elle doit pouvoir se répéter côte à côte sans qu'on repère la jointure."""

REGLES_FR = """\
Aucun être vivant ne se décrit librement : le sujet ci-dessous est cité de sa fiche, mot pour mot, et se
dessine EXACTEMENT comme décrit. Aucun animal réel n'existe dans ce monde.

Toutes les tailles sont données en CASES — une case vaut un mètre. Ne dessine pas de grille, n'écris
aucune mesure dans l'image.

Rien d'autre dans l'image : pas de texte, pas de chiffre, pas d'interface, pas de logo, pas de
signature, pas de grille, pas de bordure."""

# Element sheets for things that are not creatures or humans. A series never starts without the sheet:
# the same rule as for inhabitants, for the same reason — without it every generation reinvents.
ELEMENTS = {
    "SOL-001": ("tuile", "1 case",
                "Une PRAIRIE RASE d'herbe verte vive et fraîche, tondue court, telle qu'on la voit du "
                "dessus : un tapis dense de brins courts, d'un vert franc et lumineux légèrement plus "
                "clair par endroits, sans fleur, sans caillou, sans touffe haute, sans terre nue. La "
                "texture est fine et régulière, le relief presque nul."),
}

# The player character. DRAFT, written here to unblock the capability probe the lead asked for; it is
# NOT yet a design sheet. It must be transcribed into personnages-temoins.md before any production
# series, exactly as every other inhabitant.
JOUEUR = ("HU-000", "2 cases debout",
          "Le personnage-joueur : un humain d'aventure classique, jeune adulte, silhouette "
          "d'explorateur immédiatement lisible et sans excentricité. Peau brune moyenne, cheveux noirs "
          "courts et bouclés, carrure ordinaire. Veste de toile vert olive aux manches retroussées "
          "sur un tee-shirt crème, pantalon de marche brun, bottines solides, un petit sac à dos de "
          "cuir fauve à l'épaule. Debout, en appui sur une jambe, le regard tourné DROIT VERS LE BAS "
          "face caméra, visage bien visible et ouvert. Proportions toon : silhouette ronde et "
          "compacte, tête un peu grande.")

TYPES = {
    "sol": ("tuile", "une tuile de sol"),
    "batiment": ("cutout", "un bâtiment"),
    "vegetation": ("cutout", "un élément de végétation"),
    "personnage": ("cutout", "un personnage humain"),
    "creature": ("cutout", "une créature"),
}


def fiche(code: str) -> tuple:
    """Resolve a code to (taille, description) — creature individual, human, element, or the player."""
    if code == JOUEUR[0]:
        return JOUEUR[1], JOUEUR[2]
    if code in INDIVIDUALS:
        species, rune = INDIVIDUALS[code]
        description, position = SPECIES[species]
        taille = "2 cases au sol" if "two tiles of ground" in description else "1 case au sol"
        return taille, (f"{description} Sa rune, un seul trait continu et scintillant, {position} : "
                        f"{rune}. La rune LUIT DOUCEMENT sans éclairer : elle ne projette aucune "
                        f"lumière, ne rayonne pas, ne fait pas de halo, et elle ÉPOUSE la courbure du "
                        f"corps au lieu d'être plaquée à plat.")
    if code in HUMANS:
        return "entre 1,75 et 2 cases debout", HUMANS[code]
    if code in ELEMENTS:
        _, taille, description = ELEMENTS[code]
        return taille, description
    raise KeyError(f"unknown sheet code: {code}")


def prompt(type_asset: str, code: str) -> str:
    famille, libelle = TYPES[type_asset]
    taille, description = fiche(code)
    cadrage = CADRAGE_TUILE if famille == "tuile" else CADRAGE_CUTOUT
    destination = ("destinée à être répétée en damier pour couvrir le sol d'une carte vue de dessus"
                   if famille == "tuile" else
                   "SEUL SUJET DE L'IMAGE, destiné à être détouré et posé comme sprite sur une carte "
                   "vue de dessus")
    entete = (f"ASSET DE JEU — {libelle}, {destination}.\nÉCHELLE ANNONCÉE : {taille}.")

    return (f"{STYLE_FR}\n\n{CAMERA_FR}\n\n{entete}\n\n{cadrage}\n\n{REGLES_FR}\n\n"
            f"LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :\n{code} : {description}\n")


def shoot(type_asset: str, code: str) -> int:
    """Save the prompt beside the asset and generate it — never twice for one code."""
    if type_asset not in TYPES:
        raise KeyError(f"unknown asset type: {type_asset} (known: {', '.join(TYPES)})")
    dossier = ASSETS / type_asset
    dossier.mkdir(parents=True, exist_ok=True)
    texte = prompt(type_asset, code)
    (dossier / f"prompt-{code}.txt").write_text(texte, encoding="utf-8")
    if "--dump" in sys.argv:
        print(f"DUMPED {type_asset}/prompt-{code}.txt — no generation")
        return 0
    cible = dossier / f"{code}.png"
    if cible.is_file():
        print(f"REFUSED {type_asset}/{cible.name} already exists — one shot per asset, never a second")
        return 1

    return subprocess.run(
        ["php", TOOL, f"{TARGET}/{type_asset}/{code}.png", texte], cwd=PROJECT
    ).returncode

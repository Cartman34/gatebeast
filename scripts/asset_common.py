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
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tile_scale
from plate_common import HUMANS, INDIVIDUALS, SPECIES, STYLE_FR

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/poc"
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "poc"

# Transparency is asked for directly. Constated on our own generator: it returns a real alpha channel,
# including inside the enclosed holes of an openwork subject. The former magenta key left the background
# in those holes, needed a pink fringe cleanup, and forbade that colour to subjects that may wear it.
FOND = """\
LE FOND EST ENTIÈREMENT TRANSPARENT. L'image est un PNG à canal alpha : tout ce qui n'est pas le sujet a
une opacité NULLE. Cela vaut aussi pour les VIDES ENCERCLÉS — entre des rondins, sous une lisse, entre
des feuilles, dans une fenêtre : on doit voir au travers. Aucun fond de couleur, aucun damier, aucune
ombre portée, aucun sol sous le sujet ; l'ombrage reste sur le corps du sujet lui-même.

AUCUN HALO : pas de liseré clair, pas de contour lumineux, pas de lueur, pas de fondu diffus autour du
sujet. Le bord du sujet est net et la transparence commence immédiatement — sauf si le sujet lui-même
demande une lueur, auquel cas sa fiche le dit."""

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

{FOND}

CADRAGE : le sujet est CENTRÉ et il REMPLIT LE CADRE — sa plus grande dimension occupe environ QUATRE
CINQUIÈMES de la hauteur de l'image, et il reste une marge transparente tout autour. Rien du sujet n'est
coupé par un bord."""

CADRAGE_TRACE = f"""\
UN SEUL SUJET, ET RIEN D'AUTRE : la pièce d'assemblage décrite ci-dessous, et absolument rien de plus —
aucun décor, aucun sol, aucun accessoire, aucun être vivant, aucun cadre, aucune bordure, aucun texte.

{FOND}

CADRAGE : le sujet TOUCHE les bords que le tracé rejoint — il y est coupé net, c'est voulu, c'est ce qui
permet le raccordement. Sur les bords qu'il ne rejoint pas, il reste une marge transparente et rien ne
dépasse."""

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
    # Quoted WORD FOR WORD from referentiels/visuel/inventaire/sols-et-chemins.md, "Campagne et parc".
    # The sheet carries the edge-to-edge requirement itself, which is what makes it reproducible.
    "CH-001": ("tuile", "1 case",
               "Close-cropped lawn seen from straight above, a dense mat of short blades in a bright "
               "fresh green, unevenly lighter in a few soft patches, with a scattering of small "
               "clover leaves and a handful of paler dried blades; no flower, no stone, no bare "
               "earth, no tall tuft. Fine even texture, almost flat relief. The grass is cropped "
               "short and stops cleanly at the edge of the image, no blade crossing it; the texture "
               "at each edge matches the opposite edge, so that copies laid side by side show no "
               "seam."),
    # Quoted WORD FOR WORD from referentiels/visuel/inventaire/vegetation.md, "Campagne et parc".
    "TR-060": ("cutout", "2 cases sur 2",
               "A broad solitary oak with a thick furrowed trunk and a wide rounded crown of deep "
               "green lobed leaves, its lowest branches reaching out almost level, a ring of exposed "
               "roots at its foot and moss creeping up one side of the trunk."),
    "TR-062": ("cutout", "1 case au sol",
               "A knee-high tuft of long meadow grass, its blades arching outward in every "
               "direction, pale seed heads nodding at their tips, a few blades bent and bleached "
               "where they have dried."),
    # Quoted WORD FOR WORD from referentiels/visuel/inventaire/objets.md.
    "OB-010": ("cutout", "1 case au sol",
               "A waist-high fence of split logs, two horizontal rails pegged between stout round "
               "posts, the bark still on the wood and silvered by weather, moss at the foot of every "
               "post and the grass grown long against it."),
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
    "cloture": ("trace", "une pièce de clôture"),
    "chemin": ("trace", "une pièce de chemin"),
}

# A track is not a lone object: it is one piece of an assembly, and the consigne must say so, or the
# generator returns a handsome isolated object that connects to nothing (constated on the fence).
TRACE_FR = """\
CE SUJET EST UNE PIÈCE D'ASSEMBLAGE, PAS UN OBJET ISOLÉ. Des cases voisines porteront la même pièce, et
l'ensemble doit former une ligne continue, sans décrochement ni interruption.

Le tracé PASSE PAR LE CENTRE de la case et REJOINT LES BORDS indiqués par la variante demandée. Ses
éléments porteurs — lisses, rondins, rails, revêtement — ATTEIGNENT EXACTEMENT ces bords : ils y sont
coupés net, à la MÊME HAUTEUR et à la MÊME ÉPAISSEUR de chaque côté, de sorte qu'en posant deux images
identiques côte à côte, les éléments se prolongent l'un dans l'autre sans marche ni trou.

Les bords que le tracé ne rejoint PAS restent libres : rien ne les touche."""

# The ground footprint of each known code, in tiles. It is what the delivery definition is computed
# from, so it belongs beside the sheets rather than being guessed at the call site.
FOOTPRINTS = {
    "CH-001": (1, 1),
    "TR-060": (2, 2),
    "TR-062": (1, 1),
    "OB-010": (1, 1),
    "SOL-001": (1, 1),
    "HU-000": (1, 1),
    "SP-001-1": (1, 1),
}
DEFAULT_FOOTPRINT = (1, 1)


def definition(footprint: tuple, famille: str) -> str:
    """The output definition asked of the generator, computed by the scale service — never by hand.

    The generator takes no size parameter: it passes the description through and decides the
    dimensions itself. Left unasked, it returned 1254 square, which is far too little for a wide
    subject. The plates only came out at 1536 x 1152 because their own prompt demanded it, so an asset
    prompt has to demand its size the same way.

    WHAT IS ASKED IS THE MASTER'S DEFINITION, NEVER THE DELIVERY'S — the service holds the rule.

    It is asked as a TARGET, not as a minimum. A minimum would invite the generator to render far more
    than anything consumes, which is precisely the cost the cap exists to avoid.

    A GROUND MATERIAL is asked for its exact box: it has to tile on the grid. A CUTOUT SUBJECT is
    asked for an exact WIDTH — the design scales a sprite on its footprint width, so that width is
    contractual — while the height follows the subject's own proportions, since a tall subject
    overflows upwards and fixing its height would squash its base off its tiles.
    """
    columns, rows = footprint
    box = tile_scale.master_definition(columns, rows)
    if famille == "tuile":
        return (f"DÉFINITION ATTENDUE : exactement {box['width']} × {box['height']} pixels. "
                f"La matière doit couvrir toute cette surface, bord à bord.")

    return (f"DÉFINITION ATTENDUE : {box['width']} pixels de large — c'est la largeur de l'emprise, "
            f"elle est contractuelle. La hauteur suit les proportions du sujet : compte environ "
            f"{box['height']} pixels pour un sujet aussi large que haut, davantage pour un sujet "
            f"élancé, sans jamais dépasser {tile_scale.MASTER_CAP} pixels. Inutile de rendre plus "
            f"grand : rien ne consomme au-delà. N'écris aucune dimension dans l'image.")


def emprise_clause(footprint: tuple, trace: bool = False) -> str:
    """The footprint contract, quoted from the art direction: filled in width, never exceeded.

    "Une emprise se remplit et ne se déborde jamais" (referentiels/visuel/index.md). Both halves
    matter: nothing sticks out sideways, or the map stops being measurable and positions stop being
    reliable; and the silhouette must reach the last fifth of the border tiles, or a building
    announced on ten tiles occupies six and the scale is silently wrong. Height is the exception —
    overflowing upwards is normal and wanted, since the footprint describes the GROUND.
    """
    columns, rows = footprint

    marge = ("" if trace else
             "NE CONFONDS PAS LA MARGE ET L'EMPRISE : la marge transparente demandée plus haut est "
             "une marge SUR LA TOILE, dont l'unique raison d'être est qu'aucune partie du sujet ne "
             "soit coupée par un bord de l'image ; elle NE DIT RIEN DE LA PLACE DU SUJET AU SOL. ")

    return (f"EMPRISE AU SOL — {columns} case(s) de large sur {rows} de profondeur. Cette emprise est "
            f"un contrat dans les deux sens.\n"
            f"{marge} L'emprise, elle, décrit le sol que le sujet couvre : sur cette "
            f"largeur-là, le sujet va d'un bord à l'autre sans rien laisser de vide et sans rien "
            f"faire dépasser.\n"
            f"CONTENU EN LARGEUR : RIEN du sujet ne dépasse latéralement de cette largeur, ni "
            f"branche, ni auvent, ni marche, ni ombre. La largeur du sujet est sa largeur au sol.\n"
            f"REMPLI : le sujet occupe VRAIMENT toute cette largeur — sa silhouette atteint les "
            f"bords de son emprise, il ne flotte pas au milieu en n'en occupant que la moitié.\n"
            f"EN HAUTEUR, LE DÉBORDEMENT EST NORMAL : l'emprise décrit le SOL. Un sujet haut monte "
            f"librement dans l'image ; seule sa largeur est contrainte.")


def reference_clause(reference_name: str) -> str:
    """Point the generator at the main view, which sits in its working directory.

    The chain's cascade rule: every variant of a profile is produced from its main view, given as a
    visual reference on top of the sheet, so the subject cannot drift from one image to the next. The
    wrapper runs the generator with the output directory as its working directory, so a file dropped
    there is reachable by name — exactly how the reference plates were already produced.
    """
    return (f"RÉFÉRENCE VISUELLE — le fichier ./{reference_name}, présent dans ton répertoire de "
            f"travail, est la VUE PRINCIPALE de ce même sujet, déjà validée. C'EST LE MÊME SUJET, "
            f"le même individu, le même costume, les mêmes couleurs, les mêmes proportions : "
            f"reproduis-le à l'identique et ne change QUE ce que la clause de variante demande "
            f"ci-dessous. En cas de désaccord entre l'image de référence et le texte, l'image fait "
            f"foi pour l'apparence, le texte pour la posture demandée.")


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


def prompt(type_asset: str, code: str, footprint: tuple = None, reference_name: str = None,
           variant_clause: str = None) -> str:
    """Assemble one asset prompt.

    THE STYLE BASE IS ALWAYS FIRST AND ALWAYS VERBATIM. STYLE_FR is imported from plate_common, the
    very object the plates use — not a copy — so an asset and a plate can never drift apart on style.
    """
    famille, libelle = TYPES[type_asset]
    taille, description = fiche(code)
    footprint = footprint or FOOTPRINTS.get(code, DEFAULT_FOOTPRINT)
    cadrage = {"tuile": CADRAGE_TUILE, "trace": CADRAGE_TRACE}.get(famille, CADRAGE_CUTOUT)
    destination = ("destinée à être répétée en damier pour couvrir le sol d'une carte vue de dessus"
                   if famille == "tuile" else
                   "SEUL SUJET DE L'IMAGE, destiné à être détouré et posé comme sprite sur une carte "
                   "vue de dessus")
    entete = (f"ASSET DE JEU — {libelle}, {destination}.\nÉCHELLE ANNONCÉE : {taille}.\n"
              f"{definition(footprint, famille)}")

    blocs = [STYLE_FR, CAMERA_FR, entete, cadrage]
    if famille != "tuile":
        blocs.append(emprise_clause(footprint, trace=famille == "trace"))
    if famille == "trace":
        blocs.append(TRACE_FR)
    blocs.append(REGLES_FR)
    if reference_name:
        blocs.append(reference_clause(reference_name))
    blocs.append(f"LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :\n{code} : {description}")
    if variant_clause:
        blocs.append(f"LA VARIANTE DEMANDÉE :\n{variant_clause}")

    return "\n\n".join(blocs) + "\n"


def reference_file_name(code: str) -> str:
    """The name the main view takes inside the generator's working directory."""
    return f"reference-{code}.png"


def place_reference(dossier: Path, code: str, main_view: Path) -> str:
    """Put the main view where the generator will run, and return the name to quote in the prompt.

    The wrapper starts the generator with the OUTPUT DIRECTORY as its working directory, writable.
    A file copied there is therefore reachable by a plain relative name — the same mechanism the
    reference plates already use for their style anchor.
    """
    if not main_view.is_file():
        raise FileNotFoundError(f"main view missing, cannot cascade from it: {main_view}")
    name = reference_file_name(code)
    shutil.copyfile(main_view, dossier / name)

    return name


def shoot(type_asset: str, code: str, footprint: tuple = None, main_view: Path = None,
          variant_clause: str = None, output_name: str = None) -> int:
    """Save the prompt beside the asset and generate it — never twice for the same output.

    A variant other than the main view is produced FROM the main view: pass main_view and its image is
    copied into the generator's working directory and quoted in the prompt, so the subject cannot
    drift. That is the cascade the production chain requires.
    """
    if type_asset not in TYPES:
        raise KeyError(f"unknown asset type: {type_asset} (known: {', '.join(TYPES)})")
    dossier = ASSETS / type_asset
    dossier.mkdir(parents=True, exist_ok=True)
    stem = output_name or code
    reference_name = place_reference(dossier, code, main_view) if main_view else None
    texte = prompt(type_asset, code, footprint, reference_name, variant_clause)
    cible = dossier / f"{stem}.png"
    # A prompt beside an image is the only trace of how that image was obtained: once the image exists,
    # its prompt is frozen. A dump goes to the scratch directory instead, so inspecting a consigne can
    # never overwrite the record of a produced one.
    if "--dump" in sys.argv:
        brouillon = PROJECT / "gatebeast" / "local" / f"dump-{type_asset}-{stem}.txt"
        brouillon.parent.mkdir(parents=True, exist_ok=True)
        brouillon.write_text(texte, encoding="utf-8")
        print(f"DUMPED local/{brouillon.name} — no generation"
              + (f", reference {reference_name} in place" if reference_name else ""))
        return 0
    if cible.is_file():
        print(f"REFUSED {type_asset}/{cible.name} already exists — one shot per asset, never a second")
        return 1
    (dossier / f"prompt-{stem}.txt").write_text(texte, encoding="utf-8")

    return subprocess.run(
        ["php", TOOL, f"{TARGET}/{type_asset}/{stem}.png", texte], cwd=PROJECT
    ).returncode

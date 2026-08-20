"""Shared base for POC asset generation — one subject per image, in the validated art direction.

An asset is not a plate: a plate is a composed scene, an asset is ONE subject alone, framed to fill the
image, meant to be cut out and placed as a sprite. Everything the two have in common — the art
direction, the camera, the ban on free-described inhabitants, the ban on pixel sizes — is shared with
plate_common so the two can never drift apart.

Two families, because one has a subject to lift out of the image and the other does not:
- CUTOUT (and TRACE) assets (building, vegetation, human, creature, fence, path): a subject that must
  come out of the image whole, to be placed as a sprite. The generator is asked directly for a
  transparent PNG — a real alpha channel, constated on our own generator, that reaches even the
  enclosed voids of an openwork subject (between rondins, under a rail, between leaves). See FOND
  below. A magenta key was tried first and abandoned: it left the background inside those voids and
  forbade the colour to any subject that might wear it.
- TILE assets (ground): there is no subject and nothing to lift out. The material fills the frame edge
  to edge and is asked to repeat seamlessly with itself.
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tile_scale
from plate_common import HUMANS, SPECIES, STYLE_FR

# The rune data, read from its own file rather than from a copy kept here. Imported by path because the file name carries a dash, and it is safe to import: the
# check it performs runs on the command, never on the import.
_runes_spec = importlib.util.spec_from_file_location("check_runes", Path(__file__).resolve().parent / "check-runes.py")
check_runes = importlib.util.module_from_spec(_runes_spec)
_runes_spec.loader.exec_module(check_runes)

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/poc"
ASSETS = Path(__file__).resolve().parents[1] / "assets" / "poc"

# Where a produced image lands under assets/poc/, by the family its own code belongs to — read from
# the CODE, never from a reference image. A reference is an input the generator reads, not a
# destination: deriving where to WRITE from where a reference happens to sit is what once sent two
# produced tracés into assets/revue-da/, among the reference plates, because the reference given for
# them lived there. The destination depends on the sujet, full stop.
CODE_FOLDER = {"TR": "vegetation", "BT": "building", "CH": "ground", "OB": "fence",
               "HU": "character", "SP": "creature"}

# A single, lone asterisk on each side — never a pair. Markdown bold ("**word**") is built from pairs
# of this same character, so a naive split on "*" tears bold spans into empty fragments and can no
# longer tell a sujet's description from its own emphasis. The lookarounds below refuse to open or
# close on a star that has another star touching it, which is exactly what keeps bold and italics
# apart.
DESCRIPTION_PATTERN = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")

# The fixed phrase that introduces a description proper to one particular value or form — a marker of
# the FICHE FORMAT, written once for all, never a word the description itself chooses. Finding it is
# exactly the same kind of structural read as finding the italics: form and place, never content.
QUALIFIED_DESCRIPTION_PATTERN = "Description propre à la {kind} `{qualifier}`"

QUALIFIED_DESCRIPTION_KINDS = ("valeur", "forme")


def declares_qualified_description(text: str, qualifier: str) -> bool:
    """Whether the fiche in `text` writes a description proper to `qualifier` — asked BEFORE quoting it.

    A qualified description is OPTIONAL (inventaire/README.md): a value may rewrite the sujet's
    description, or be a mere finish the consigne renders with a clause of its own. A caller holding
    several asked values therefore has to know which of them the fiche actually describes, and it must
    find that out without provoking the fault sheet_description() raises for a qualifier it cannot
    honour. Asked here rather than by re-matching the phrase elsewhere: the fiche format has one owner.
    """
    return any(QUALIFIED_DESCRIPTION_PATTERN.format(kind=kind, qualifier=qualifier) in text for kind in QUALIFIED_DESCRIPTION_KINDS)


def sheet_description(text: str, code: str, qualifier: str = None) -> tuple:
    """The sheet's own description in `text`, found by its FORM and its PLACE — never by the words it
    happens to start with.

    A heuristic on first words ("A ", "An ", "The ") is exactly what broke the day descriptions moved
    from English to French: every fiche still carries its description in italics, in the same place,
    right after the label/profile/type/emprise/hauteur preamble and before any "Description propre à
    ..." that may follow for one particular form or value — only the language of the words changed,
    and a heuristic on words is blind to a fiche it has never seen written that way. Nothing here reads
    a single word of the description: it reads structure only, so the next language change costs it
    nothing.

    Without `qualifier`, the description is the first italic span on the line — the base description,
    used by default.

    With `qualifier` (a value like "gate-closed", or a form), the description PROPER TO that qualifier is returned instead: introduced by the fixed phrase
    "Description propre à la valeur `X`" or "...à la forme `X`", followed by its own italic span — never guessed from the qualifier's own words. A qualifier
    that is asked for and finds no such phrase is a FAULT, not a silent fall back to the base description: producing the wrong thing quietly (the plain
    fence's description for a gate, say) is worse than refusing outright.

    Whether that text REPLACES the base description or is ADDED to it is not decided here: this returns
    one span, its caller assembles the consigne (see generate-sprite.sheet_of, where a value completes
    by default and replaces only when its field declares defines_kind).

    Returns (description, start) so a caller can also cut everything before the description off for
    its own use — the sujet's precisions never include a description, qualified or not.

    Raises loudly when the description sought is not found: a consigne without a description, or with
    the wrong one, must never reach the generator silently.
    """
    if qualifier:
        for kind in QUALIFIED_DESCRIPTION_KINDS:
            phrase = QUALIFIED_DESCRIPTION_PATTERN.format(kind=kind, qualifier=qualifier)
            introduced = text.find(phrase)
            if introduced == -1:
                continue
            match = DESCRIPTION_PATTERN.search(text, introduced + len(phrase))
            if match:
                return match.group(1).strip(), match.start()
        raise SystemExit(f"FAULT {code} n'a pas de description propre à {qualifier!r} — elle est "
                         f"obligatoire pour ce qualificatif, la description de base ne s'y substitue "
                         f"jamais.")

    match = DESCRIPTION_PATTERN.search(text)
    if not match:
        raise SystemExit(f"FAULT {code} n'a pas de description écrite — elle est obligatoire.")

    return match.group(1).strip(), match.start()

# Transparency is asked for directly. Constated on our own generator: it returns a real alpha channel,
# including inside the enclosed holes of an openwork subject. The former magenta key left the background
# in those holes, needed a pink fringe cleanup, and forbade that colour to subjects that may wear it.
FOND = """\
LE FOND EST ENTIÈREMENT TRANSPARENT. L'image est un PNG à canal alpha : tout ce qui n'est pas le sujet a
une opacité NULLE. Cela vaut aussi pour les VIDES ENCERCLÉS que le sujet peut avoir — tout trou entouré
de matière : on doit voir au travers. Aucun fond de couleur, aucun damier, aucune ombre portée, aucun
sol sous le sujet ; l'ombrage reste sur le corps du sujet lui-même.

AUCUN HALO : pas de liseré clair, pas de contour lumineux, pas de lueur, pas de fondu diffus autour du
sujet. Le bord du sujet est net et la transparence commence immédiatement — sauf si le sujet lui-même
demande une lueur, auquel cas sa fiche le dit."""

# WHAT THE IMAGE IS FOR, said before anything else. Without it the generator draws an illustration and reasons like an illustrator: it composes a little scene, sets its
# subject on a patch of ground, adds what would look good around it. It is not making a picture — it is making ONE PIECE of a map that a renderer will assemble. Told this,
# every clause that follows stops being arbitrary: the transparent background, the exact width, the ground that is not its business, the light that never varies. Constated
# on the clearing grass, which came back sitting on a round patch of brown earth because its description mentioned bare soil (operator, 2026-08-06).
CONTEXTE_FR = """\
CE QUE TU PRODUIS, ET POURQUOI CHAQUE CONTRAINTE CI-DESSOUS EXISTE : une SPRITE, c'est-à-dire une pièce détourée que le moteur d'un jeu posera sur UNE CASE d'une carte
quadrillée, vue en plongée. Ce n'est pas une illustration : personne ne la regardera seule. Elle sera posée à côté de centaines d'autres, et PLUSIEURS SPRITES PEUVENT
occuper la même case — une herbe devant un arbre, un chemin sous un bâtiment : c'est le moteur qui les empile dans le bon ordre, ce n'est pas ton affaire et tu n'as rien à
anticiper de cela."""

# THE PLUNGE, WRITTEN ONCE AND ONLY ONCE. It is the value the whole world is drawn under, and it appeared
# in two texts in two wordings — the camera clause and the closing reminder. A technical parameter said
# twice is a parameter that contradicts itself the first time one of the two is made more precise
# (opérateur, 2026-08-12). Both now interpolate this string, so there is one text and two placements.
#
# AND ITS TWO FIGURES ARE READ FROM tile_scale, NEVER TYPED HERE. They were typed once, on 2026-08-12, and
# the ground figure came out as 83 — recomputed from sin(60°), which is the one operation tile_scale forbids
# by name: the published depth is 84 and "is therefore not to be 'corrected' to 83: that would undo a
# decision, not repair a mistake" (tile_scale, from the operator's decision of 2026-08-08). The generator was
# then told, for every image, a ground scale one pixel short of the one the pixel ladder publishes. A prompt
# that retypes a pivot value is a copy like any other, and it drifts the same way — so it interpolates.
# THE UNSQUASHED UNIT COMES FIRST, AND WITHOUT IT THE OTHER TWO ARE ONLY A RATIO (opérateur, 2026-08-12 :
# « TY et TX restent la référence pour parler d'une case avec 96 px »). The clause used to give the two
# FORESHORTENED figures alone — 48 across the height, 84 into the ground — and never TX, the one length the
# camera leaves alone. Two squashed numbers with nothing to anchor them fix a proportion, not a scale, so
# nothing in the prompt said how big a tile actually is: the oak came back drawn at its canvas height
# instead of its eight metres. TX is the reference the other two are measured against, so it is said first.
PLUNGE_WIDTH_PX = tile_scale.FILE_TILE_WIDTH
PLUNGE_HEIGHT_PX = round(tile_scale.FILE_TILE_WIDTH * tile_scale.STANDING_HEIGHT_FACTOR)
PLUNGE_DEPTH_PX = tile_scale.FILE_TILE_DEPTH
PLUNGE_FR = f"""\
CETTE PROJECTION SE VÉRIFIE PAR TROIS MESURES, PAS À L'IMPRESSION. Une case du monde est un carré d'un mètre, et
voici ce que son côté devient dans l'image selon l'axe qu'il suit — ce sont aussi les trois unités dans lesquelles
toute mesure de cette consigne est donnée :
— le long de X, gauche-droite, un mètre occupe {PLUNGE_WIDTH_PX} PIXELS ; cette unité se note TX ;
— le long de Y, en s'enfonçant vers le fond au sol, un mètre occupe {PLUNGE_DEPTH_PX} PIXELS ; cette unité se note TY, et
  c'est aussi en TY que se mesure une hauteur DANS L'IMAGE ;
— le long de Z, debout, un mètre occupe {PLUNGE_HEIGHT_PX} PIXELS.
On voit donc largement le DESSUS de ce qui est posé au sol, et les faces verticales tiennent dans la moitié de
leur mesure : c'est le rapport que cette caméra donne."""

# THE GEOMETRY IS SAID AS TWO EQUALITIES, AND THAT IS WHAT ENDED THREE DAYS ON THE PARALLEL VIEW. A description is interpreted; an equality is checked. The
# clause used to describe the projection face by face, in prose — and everything it said is ALSO true of an isometric view, which is a parallel projection with
# no vanishing point whose depth simply runs diagonally. Nothing in our text closed that reading, and it is very probably the one the generator took: it
# satisfied every word we wrote. The one thing that separates our projection from an isometry — Δx = 0 on both the standing edge and the ground depth — was
# written nowhere (opérateur, 2026-08-13, after obtaining the right rendering by talking to the generator directly, session 019ff7b5-874b-7f13-b999-eb15476ab0da).
#
# AND TWO OF THE FOUR PROSE BULLETS WERE FALSE, WHICH IS WORSE THAN REDUNDANT. At azimuth zero, Y and Z both project onto the image's vertical axis, so a face
# whose edges follow Y and Z — a gable, a flank — is seen edge-on and projects to a SEGMENT, not to a « parallélogramme » as the clause claimed; the same goes
# for a roof pitch. Those two bullets described an isometric view, in the middle of the clause meant to forbid one, and were the likeliest invitation to draw it.
#
# NO INTERDICTION REPLACED THEM, ON PURPOSE. The generator's own answer offered ten of them — no vanishing point, no convergence, no leaning wall — and this
# document proscribes exactly that: an interdiction leaves everything else open, so it constrains nothing, and four such wordings had already failed. « Δx = 0 »
# authorises one drawing where « pas de diagonale » still authorises a thousand. It is also why the missing sentence is written positively, « monte tout droit
# vers le haut de l'image », rather than as the « jamais en diagonale » it was first phrased in.
#
# THE FIGURES ARE NOT RESTATED HERE EITHER: PLUNGE_FR gives the three measures just above, so the tests name the axes and the units it defines. What is new is
# the equality, not the number — and a pivot value said twice in one consigne is the repetition the operator named on 2026-08-12.
#
# FOUR CONSTRAINTS, EACH SAID ONCE — projection, orientation, plunge, light. This clause had grown by
# accumulation: every failed image added its paragraph on top of the previous ones, so the same thing was
# prescribed three times in three wordings and the fourth reader could no longer tell which one ruled
# (opérateur, 2026-08-12 : « au lieu de reformuler proprement au bon endroit, tu empiles les consignes »).
# Nothing was dropped in the rewrite: what each paragraph forbade is still forbidden, said in the one place
# where it belongs. What DID go is the history — why a rule exists belongs in a comment, never in a prompt.
CAMERA_FR = f"""\
Caméra : PROJECTION ORTHOGRAPHIQUE, direction de vue unique pour toute l'image, azimut ZÉRO et site SOIXANTE DEGRÉS
au-dessus du plan du sol. Les axes du monde sont ceux de la grille : X vers la droite, Y vers le fond, Z vers le
haut.
{PLUNGE_FR}
CES MESURES SE VÉRIFIENT PAR DEUX ÉGALITÉS, ET CES DEUX ÉGALITÉS DÉCRIVENT LA GÉOMÉTRIE TOUT ENTIÈRE :
— UNE ARÊTE DEBOUT, qui suit Z, MONTE TOUT DROIT DANS L'IMAGE : son sommet se dessine à la MÊME ABSCISSE que son
  pied, soit Δx = 0, et seule sa mesure le long de Z les sépare, verticalement. Un mur a donc exactement la même
  largeur en haut qu'en bas, et les deux murs opposés d'un bâtiment sont deux droites verticales parallèles ;
— UNE PROFONDEUR AU SOL, qui suit Y, MONTE TOUT DROIT ELLE AUSSI, VERS LE HAUT DE L'IMAGE : en s'enfonçant vers le
  fond, un point se dessine à la MÊME ABSCISSE que le point correspondant du bord avant, soit Δx = 0, et seule sa
  mesure en TY les sépare, verticalement. Le bord arrière d'une emprise a donc exactement la longueur du bord
  avant, et se dessine à son aplomb.
La largeur est la seule mesure qui reste horizontale dans l'image : elle suit X, en TX, et vaut autant au premier
plan qu'au fond.
Il suit de ces deux égalités que deux arêtes parallèles dans le monde le restent dans l'image, et que deux segments
de même longueur sur un même axe y ont la même longueur, au premier plan comme au fond.
Lumière : soleil de fin de matinée venant du HAUT À GAUCHE, franc et clair, et de là SEULEMENT — jamais de la
caméra. Ce qui est exposé au ciel reçoit la lumière ; ce qu'une masse surplombe est dans son ombre, et le reste
franchement plus sombre : le dessous d'une couronne, les branches sous le feuillage, l'intérieur d'un porche, le
pied d'un mur. Un sujet éclairé uniformément sur toute sa surface est un sujet sans volume. L'ombrage se fait en
deux bandes claires, et les faces tournées vers le bas restent lisibles. Pas d'horizon, pas de ciel."""

# The camera, said again as the LAST word of every asset prompt. Stating it once at the top is not
# enough: everything after it — the framing, the piece asked for, the sheet — talks about a map seen
# from above, and on a flat subject (a path, a gate leaf) that wins over a clause read twenty lines
# earlier. Constated on the paths and on the gates, whose prompts carried the camera clause word for
# word and came out drawn flat anyway. Positive prescription: it says what to draw, never what to avoid.
#
# AND IT QUOTES THE SAME SENTENCE, IT NO LONGER PARAPHRASES IT (opérateur, 2026-08-12 : « les paramètres
# techniques ne doivent être précisés qu'une fois, c'est le meilleur moyen d'éviter les contradictions
# […] tu dupliques et tu te contredis, et c'est du débug »). The two texts said the same thing in
# different words, so the day one of them gained a precision — the wall being FORESHORTENED, added the
# same day — the other went on saying the older, vaguer version twenty lines later. One text, placed
# twice, cannot drift.
# THE CLOSING REMINDER POINTS AT THE PLUNGE, IT DOES NOT REPRINT IT. Placing it last is deliberate — what
# reads last weighs most on the generator — but the position is what does the work, not a second copy of the
# text. It used to interpolate PLUNGE_FR whole, so the three measures were stated twice in every consigne;
# sharing one string stopped the two from DIVERGING but not from REPEATING, which is the fault the operator
# named on 2026-08-12: « les paramètres techniques ne doivent être précisés qu'une fois […] tu dois éviter le
# renforcement comme une brute ». What is kept here is only what this position adds and the clause above does
# not say: that the plunge applies to the SUBJECT, not just to the map it stands on.
RAPPEL_CAMERA_FR = """\
RAPPEL, ET C'EST LA DERNIÈRE CONSIGNE — LA DIRECTION DE VUE EST CELLE DÉCRITE PLUS HAUT, la même pour le sujet
et pour le sol sur lequel il pose : azimut zéro, site soixante degrés, projection orthographique, avec ses trois
mesures. Le sujet est vu sous cette direction-là, entier, du premier plan au fond."""

CADRAGE_CUTOUT = f"""\
UN SEUL SUJET, ET RIEN D'AUTRE. L'image contient le sujet décrit ci-dessous et absolument rien de plus : rien ne s'ajoute AUTOUR de lui, ni décor, ni autre sujet, ni cadre, ni bordure, ni texte. Tout
ce que la description demande appartient au sujet et se dessine, quelle que soit la matière dont il est fait.

{FOND}

CADRAGE : le sujet est CENTRÉ et occupe toute la largeur du cadre, à une fine marge transparente près.
Sa place en hauteur est celle que lui donne l'angle de vue décrit plus haut, appliqué à sa taille réelle :
c'est la caméra qui en décide, et elle seule. Rien du sujet n'est coupé par un bord, et une marge
transparente subsiste tout autour."""
# An imposed height proportion contradicted the camera: to fill four fifths of the height a subject has to stand upright and face us, whereas the seventy-degree
# dive flattens it. The generator followed the more concrete of the two clauses and returned front views — the apple tree and the thicket came back that way.
# What is asked now is what is actually wanted: the full width, and the height left to the camera, instead of two rules that contradict each other.

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

REGLES_FR = f"""\
Aucun être vivant ne se décrit librement : le sujet ci-dessous est cité de sa fiche, mot pour mot, et se
dessine EXACTEMENT comme décrit. Aucun animal réel n'existe dans ce monde.

L'image ne porte aucune inscription : pas de texte, pas de chiffre, pas de cote, pas de grille."""

# LES DESCRIPTIONS D'ÉLÉMENTS NE VIVENT PLUS DANS LE CODE. Cinq d'entre elles étaient recopiées ici à la main, en anglais, chacune annoncée « citée mot
# pour mot » de l'inventaire — une promesse qu'aucun contrôle ne tenait. Elles vivent dans assets/descriptions/, un fichier par description, lu en entier.
# Le doublon n'avait jamais été demandé et plus personne ne le lisait (opérateur, 2026-08-07).

# The player character. DRAFT, written here to unblock the capability probe the lead asked for; it is
# NOT a design sheet, and it will not become one: there is no "player character" subject. There are
# only humans, at referentiels/visuel/inventaire/personnages.md, and the player character could be
# any of them (operator, 2026-08-04). This draft stays here as the probe text it was.
JOUEUR = ("HU-000", "2 cases debout",
          "Le personnage-joueur : un humain d'aventure classique, jeune adulte, silhouette "
          "d'explorateur immédiatement lisible et sans excentricité. Peau brune moyenne, cheveux noirs "
          "courts et bouclés, carrure ordinaire. Veste de toile vert olive aux manches retroussées "
          "sur un tee-shirt crème, pantalon de marche brun, bottines solides, un petit sac à dos de "
          "cuir fauve à l'épaule. Debout, en appui sur une jambe, le regard tourné DROIT VERS LE BAS "
          "face caméra, visage bien visible et ouvert. Proportions toon : silhouette ronde et "
          "compacte, tête un peu grande.")

TYPES = {
    "ground": ("tile", "une tuile de sol"),
    "building": ("cutout", "un bâtiment"),
    "vegetation": ("cutout", "un élément de végétation"),
    "character": ("cutout", "un personnage humain"),
    "creature": ("cutout", "une créature"),
    "fence": ("trace", "une pièce de clôture"),
    "chemin": ("trace", "une pièce de chemin"),
}

# A track is not a lone object: it is one piece of an assembly, and the consigne must say so, or the
# generator returns a handsome isolated object that connects to nothing (constated on the fence).
TRACE_FR = """\
CE SUJET EST UNE PIÈCE D'ASSEMBLAGE, PAS UN OBJET ISOLÉ. Des cases voisines porteront la même pièce, et
l'ensemble doit former une ligne continue, sans décrochement ni interruption.

Le tracé PASSE PAR LE CENTRE de la case et REJOINT LES BORDS indiqués par la variante demandée. Ce qui
le constitue — la matière décrite par sa fiche, et elle seule — ATTEINT EXACTEMENT ces bords : il y est
coupé net, à la MÊME HAUTEUR et à la MÊME ÉPAISSEUR de chaque côté, de sorte qu'en posant deux images
identiques côte à côte, la matière se prolonge d'une case à l'autre sans marche ni trou.

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

    The generator takes no size parameter: it passes the description through and decides the dimensions itself, and left unasked it returned far too little
    for a wide subject. So the dimensions are asked — IN TILES, NEVER IN PIXELS. The correspondence between the two is stated once, in the shared base of
    every consigne (REGLES_FR), and the generator works out the rest; a pixel figure was never anything it needed, and asking one taught it nothing about
    the subject. The pixel computation still exists, but only to validate the file that comes back and to display it (operator, 2026-08-05).

    A GROUND MATERIAL is asked for its exact box: it has to tile on the grid. Any other subject is asked for an exact WIDTH — the design scales a sprite on
    its footprint width, so that width is contractual — while the height follows the subject's own proportions, since a tall subject overflows upwards and
    fixing its height would squash its base off its tiles.
    """
    columns, rows = footprint
    if famille == "tile":
        return (f"DIMENSIONS ATTENDUES : exactement {columns} case(s) sur {rows}. La matière doit "
                f"couvrir toute cette surface, bord à bord.")

    return (f"DIMENSIONS ATTENDUES : l'image fait {columns} case(s) de large — c'est la largeur de "
            f"l'emprise, elle est contractuelle. Sa hauteur suit les proportions du sujet : un sujet "
            f"élancé monte plus haut, et l'image le suit. N'écris aucune dimension dans l'image.")


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
             "NE CONFONDS PAS LA MARGE ET L'EMPRISE : la marge transparente demandée plus haut est une marge DANS L'IMAGE, dont l'unique raison d'être est "
             "qu'aucune partie du sujet ne soit coupée par un bord de l'image ; elle NE DIT RIEN DE LA PLACE DU SUJET AU SOL.")

    return (f"EMPRISE AU SOL — {columns} case(s) de large sur {rows} de profondeur. C'est la place que le sujet a le droit d'occuper au sol : un plafond, "
            f"jamais une obligation de le remplir.\n"
            f"{marge}\n"
            f"CONTENU EN LARGEUR : RIEN du sujet ne dépasse latéralement de cette largeur, ni branche, ni auvent, ni marche, ni ombre. La largeur du sujet "
            f"est sa largeur au sol.\n"
            f"COMBIEN IL EN OCCUPE VRAIMENT, C'EST SA FICHE QUI LE DIT, et elle seule : un bâtiment couvre son emprise d'un bord à l'autre, une bande de "
            f"chemin n'en couvre qu'une partie et laisse des marges libres de chaque côté. Suis ce que la fiche décrit, sans jamais élargir le sujet pour "
            f"combler sa case.\n"
            f"EN HAUTEUR, LE DÉBORDEMENT EST NORMAL : l'emprise décrit le SOL. Un sujet haut monte librement dans l'image ; seule sa largeur est "
            f"contrainte.")


def taille_clause(footprint: tuple, height: float) -> str:
    """The subject's real height, quoted from its own inventory sheet, in tiles and as a ratio.

    Framing height used to be forced to four fifths of the image (see the note above CADRAGE_CUTOUT):
    that fought the camera's steep top-down angle and made the generator draw the subject standing
    upright and face-on instead of seen from above. What replaces it is the subject's OWN height
    against its OWN footprint — a fir six tiles tall on two tiles wide, a fence not even one tile
    tall — so the camera derives the right proportion itself instead of being told one that fights it.

    ALWAYS IN TILES AND IN A RATIO, NEVER IN PIXELS: a pixel count says nothing once the master
    definition changes size, while a tile count and a ratio hold regardless of scale.
    """
    columns, rows = footprint
    hauteur_txt = f"{height:g}".replace(".", ",")
    rapport = height / columns if columns else height
    rapport_txt = f"{rapport:g}".replace(".", ",")
    return (f"TAILLE RÉELLE DU SUJET — il mesure {hauteur_txt} case(s) de haut, pour une emprise de "
            f"{columns} sur {rows} : un rapport hauteur/largeur de {rapport_txt}. C'est cette "
            f"proportion réelle, jamais une fraction du cadre ni une mesure en pixels, qui doit se "
            f"lire dans l'image une fois la caméra appliquée.")


# The marker a fiche uses to carry an extra generation instruction, read by FORM and PLACE like the
# description itself (see sheet_description) — never by the words that follow it.
EXTRA_MARKER = "Consigne supplémentaire de génération :"

# THE THREE SOURCES OF AN EXTRA INSTRUCTION, NAMED ONCE. They used to be spelled out where the dict is filled, so a caller wanting to tell them apart had to
# recopy the three strings — and a caller that recopies a key finds nothing the day one of them is reworded, in silence. They are levels of the model, not
# labels: the type's own clause, the inventory entry's, and the subject's. The consigne's split names each block by the level that wrote it, and that is
# exactly what these three distinguish.
EXTRA_FROM_TYPE = "Consigne supplémentaire — le type"
EXTRA_FROM_INVENTORY = "Consigne supplémentaire — fiche d'inventaire"
EXTRA_FROM_SUBJECT = "Consigne supplémentaire — le sujet"

# The one sentence that opens the extra instructions, whatever their number and wherever they come from. It belongs to the socle: it is true of every image
# that carries any extra instruction at all, and it is quoted, never rebuilt, by whoever needs to split that block source by source.
EXTRA_HEADER = "CONSIGNE SUPPLÉMENTAIRE POUR CE SUJET — elle s'ajoute à tout ce qui précède et ne l'annule pas :"


def extra_instructions(code: str, subject: dict = None, type_: dict = None) -> dict:
    """The extra generation instructions that apply here, from the three places they may live.

    All three are optional and none is required (operator, 2026-08-05): a subject may carry one, two,
    all or none. Whatever is found is quoted to the generator and shown in the report — the report
    holds every one of them, so nothing is silently preferred.

    - the TYPE, under its own "extra_prompt" key: what every subject of that family needs said, and what the common base must NOT say. The base is used by every generation there is, so a
      need proper to one family put there contaminates all the others — a clause forbidding grass in the image, written for a tree that kept sprouting some at its foot, made every grass subject
      contradict its own description (operator, 2026-08-06). A type is exactly the level where such a clause belongs, and it is also where two families can
      want opposite things: a tree wants nothing at its foot, a fence wants grass at the foot of its posts.
    - the INVENTORY ENTRY, after the marker above, in italics like every other quoted text there;
    - the subject's own "extra_prompt" key in the inventory of subjects.

    Returns a dict keyed by the human name of each source, empty values dropped: it is passed straight
    to the report and iterated to build the prompt block.
    """
    found = {}
    if type_ and type_.get("extra_prompt"):
        found[EXTRA_FROM_TYPE] = type_["extra_prompt"]
    for folder in (Path(__file__).resolve().parents[1] / "doc" / "conception" / "referentiels"
                   / "visuel" / "inventaire",):
        for path in sorted(folder.glob("*.md")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.startswith(f"- **{code} ") or EXTRA_MARKER not in line:
                    continue
                after = line.split(EXTRA_MARKER, 1)[1]
                match = DESCRIPTION_PATTERN.search(after)
                if match:
                    found[EXTRA_FROM_INVENTORY] = match.group(1).strip()
    if subject and subject.get("extra_prompt"):
        found[EXTRA_FROM_SUBJECT] = subject["extra_prompt"]

    return found


def extra_clause(extras: dict) -> str:
    """The extra instructions as one block of the consigne — empty when there is none to give."""
    if not extras:
        return ""

    return EXTRA_HEADER + "\n" + "\n".join(text for text in extras.values())


def reference_clause(reference_name: str) -> str:
    """Point the generator at the main view, by its own path.

    The chain's cascade rule: every variant of a profile is produced from its main view, given as a
    visual reference on top of the sheet, so the subject cannot drift from one image to the next.
    """
    return (f"RÉFÉRENCE VISUELLE — le fichier {reference_name}, que tu peux ouvrir et regarder, "
            f"est la VUE PRINCIPALE de ce même sujet, déjà validée. C'EST LE MÊME SUJET, "
            f"le même individu, le même costume, les mêmes couleurs, les mêmes proportions : "
            f"reproduis-le à l'identique et ne change QUE ce que la clause de variante demande "
            f"ci-dessous. En cas de désaccord entre l'image de référence et le texte, l'image fait "
            f"foi pour l'apparence, le texte pour la posture demandée.")


def reference_address(reference: Path) -> str:
    """The address a consigne gives for a reference image: its REAL path, absolute.

    Nothing is ever copied or moved to make a reference reachable (operator, 2026-08-05). The wrapper
    starts the generator in the output directory, and the generator reads the path it is given — so
    the path it is given is the file's own, wherever it lives. Copying one into the working directory
    is what once left multi-megabyte reference plates sitting in assets/poc/, where anything scanning
    that tree took them for sprites.
    """
    return str(reference.resolve())


def fiche(code: str) -> tuple:
    """Resolve a code to (taille, description) — creature individual, human, element, or the player."""
    if code == JOUEUR[0]:
        return JOUEUR[1], JOUEUR[2]
    individuals = check_runes.load()["individuals"]
    if code in individuals:
        # LA SPRITE SE PRODUIT SANS SA RUNE, ET LA CONSIGNE N'EN PARLE PLUS (rendu-en-calques.md, décision du 2026-08-11) : la rune se trace au rendu, sur
        # l'ancre que l'image déclare. La clause qui la décrivait ici demandait au générateur de dessiner ce qu'on lui reprochait ensuite d'avoir dessiné —
        # jamais deux fois la même, jamais à la bonne taille. Un individu n'est donc plus qu'un porteur : sa consigne est celle de son espèce, mot pour mot.
        description, _position = SPECIES[individuals[code]["species"]]
        taille = "2 cases au sol" if "two tiles of ground" in description else "1 case au sol"
        return taille, description
    if code in HUMANS:
        return "entre 1,75 et 2 cases debout", HUMANS[code]
    # LES ÉLÉMENTS NE SONT PLUS SERVIS D'ICI : leurs descriptions vivent dans assets/descriptions/, un fichier par description, lu en entier. La copie qui
    # se trouvait ici — cinq sujets recopiés à la main en anglais, chacun annoncé « cité mot pour mot » de l'inventaire — n'avait jamais été demandée et
    # n'était plus lue par personne (opérateur, 2026-08-07 : « le doublon n'a jamais été demandé, c'est une erreur d'un agent »).
    raise KeyError(f"unknown sheet code: {code}")


def prompt(type_asset: str, code: str, footprint: tuple = None, reference_name: str = None,
           variant_clause: str = None) -> str:
    """Assemble one asset prompt.

    THE STYLE BASE IS ALWAYS FIRST AND ALWAYS VERBATIM. STYLE_FR is imported from plate_common, the
    very object the plates use — not a copy — so an asset and a plate can never drift apart on style.
    """
    famille, label = TYPES[type_asset]
    taille, description = fiche(code)
    footprint = footprint or FOOTPRINTS.get(code, DEFAULT_FOOTPRINT)
    cadrage = {"tile": CADRAGE_TUILE, "trace": CADRAGE_TRACE}.get(famille, CADRAGE_CUTOUT)
    destination = ("destinée à être répétée en damier pour couvrir le sol d'une carte vue de dessus"
                   if famille == "tile" else
                   "SEUL SUJET DE L'IMAGE, destiné à être détouré et posé comme sprite sur une carte "
                   "vue de dessus")
    entete = (f"ASSET DE JEU — {label}, {destination}.\nÉCHELLE ANNONCÉE : {taille}.\n"
              f"{definition(footprint, famille)}")

    blocs = [STYLE_FR, CAMERA_FR, entete, cadrage]
    if famille != "tile":
        blocs.append(emprise_clause(footprint, trace=famille == "trace"))
    if famille == "trace":
        blocs.append(TRACE_FR)
    blocs.append(REGLES_FR)
    if reference_name:
        blocs.append(reference_clause(reference_name))
    blocs.append(f"LE SUJET, cité de sa fiche — dessine-le EXACTEMENT ainsi :\n{code} : {description}")
    if variant_clause:
        blocs.append(f"LA VARIANTE DEMANDÉE :\n{variant_clause}")
    blocs.append(RAPPEL_CAMERA_FR)  # always last: see the note above RAPPEL_CAMERA_FR

    return "\n\n".join(blocs) + "\n"


def name_reference(main_view: Path) -> str:
    """The address to quote in a consigne for a main view — its own, nothing copied anywhere."""
    if not main_view.is_file():
        raise FileNotFoundError(f"main view missing, cannot cascade from it: {main_view}")

    return reference_address(main_view)


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
    reference_name = name_reference(main_view) if main_view else None
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

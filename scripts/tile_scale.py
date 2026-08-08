"""The tile scale — the single service that owns how a tile becomes pixels, and every use of it.

The design states it plainly (referentiels/visuel/assets/index.md): "La conversion est un service
unique, pas une constante recopiée — un seul composant détient cette valeur et toutes les opérations
qui la mettent en jeu [...]. Voir un 48 ailleurs qu'à cet endroit est un défaut." Tools, renderers and
review pages ask this service and never convert on their own.

WHAT THIS SERVICE OWNS
  the value        one tile is one metre in the world, and PIXELS_PER_TILE pixels on screen
  both directions  tiles_to_pixels / pixels_to_tiles
  sizing           sprite_box for a subject, tile_box for a ground material
  placement        place, which turns a pose point in tiles into a pixel position
  delivery         delivery_size, at FILE_PIXELS_PER_TILE
  master           master_definition, the size asked of the generator — never the delivery size

CALLERS MUST NOT MULTIPLY OR DIVIDE BY THE SCALE THEMSELVES. If an operation is missing, it is added
here rather than improvised at the call site.

A SPRITE IS SCALED ON ITS WIDTH, NEVER ON ITS HEIGHT. The design fixes this: the image occupies
exactly the width of its footprint, and the height follows the image's own proportions. A tall subject
therefore overflows upwards, which is wanted — the footprint describes the ground, not the silhouette.
Scaling on a declared height would shrink a tall building's base until it stopped covering its tiles.

A MASTER'S CANVAS FOLLOWS THE SUBJECT'S REAL SHAPE, NOT ITS FOOTPRINT ALONE, once its height is known
(master_definition's height parameter). A footprint only describes the ground; asking a square canvas
for a subject three tiles tall and one tile wide leaves it nothing to stand in but a square, which is
exactly the defect constated on the apple tree and the fir grove. See CAMERA_ELEVATION_DEGREES,
GROUND_DEPTH_FACTOR and STANDING_HEIGHT_FACTOR below for the rule and why it holds under this world's
camera.
"""

import math

# THE CAMERA'S ANGLE, THE ONE FACT EVERY PROJECTION BELOW IS BUILT ON. Convention, fixed here so it is
# never re-guessed at a call site: 0° is a flat, eye-level view (the horizon — you stand level with the
# ground and look straight across it), 90° is a pure top-down view (straight overhead, no perspective
# at all). The world's camera sits at 60°, "un peu de face" (see CAMERA_FR in asset_common.py) — the
# thirty degrees short of 90 are exactly that bit of front-on view. Getting this convention backwards is
# the one mistake this constant exists to rule out: it was made once, while drafting this very feature,
# before scripts/check-asset.py ("the world is seen under this camera, which foreshortens the vertical")
# and the note above asset_common.CADRAGE_CUTOUT ("la plongée l'écrase") settled it the other way.
#
# 60 AND NOT 70, DECIDED BY THE OPERATOR ON 2026-08-07 AND NOT TO BE ASKED AGAIN. The project says
# "projection parallèle à 60 degrés de plongée", PA60 for short, and it holds for every subject — it is
# not an exception granted to one of them. Raising the camera from 70 to 60 shows half of a subject's
# true height on screen instead of a third, so every height band this module computes widens with it.
CAMERA_ELEVATION_DEGREES = 60

# GROUND DEPTH — a span lying flat on the ground, receding away from the camera (a footprint's ROWS) —
# projects onto the screen scaled by sin(θ). At θ=90° (straight overhead) the ground is seen in true
# plan, factor 1: nothing is lost. At θ=0° (eye level) the ground recedes to the horizon and shows no
# depth at all, factor 0. At 70°, close to overhead, depth is shown at ~94% of its true scale — barely
# foreshortened, because the camera is looking almost straight down at it.
GROUND_DEPTH_FACTOR = math.sin(math.radians(CAMERA_ELEVATION_DEGREES))

# STANDING HEIGHT — a span rising straight up off the ground (a subject's own height) — projects onto
# the screen scaled by cos(θ), the complementary case: at θ=90° a column directly under the camera
# shows no length at all (you are looking straight down its axis), factor 0; at θ=0° a side-on column
# stands at its full true height, factor 1. At 70°, height is shown at only ~34% of its true scale —
# THIS is the foreshortening scripts/check-asset.py names and scripts/asset_common.py warns fighting:
# a subject drawn to stand tall and face-on defeats the very camera that is meant to flatten it.
STANDING_HEIGHT_FACTOR = math.cos(math.radians(CAMERA_ELEVATION_DEGREES))

# TWO VALUES, NEVER CONFUSED. One tile is one metre in the world; how many pixels that is on screen
# is a SETTING, while how fine the image file is, is FIXED. Mixing them is what made the tile size
# look irreversible when it is not.

# TWO VALUES, AND TWO ONLY. Each is written here once and nowhere else in the code; everything that
# needs one asks this module for it. Intermediate figures and multiplying factors are not written at
# all: they explained where a value came from, which nobody needs and which made the same number exist
# in several places at once (operator, 2026-08-05).

# A PROJECTED TILE IS NOT SQUARE, AND THESE FOUR NUMBERS ARE THE SOURCE OF TRUTH (operator, 2026-08-08).
# Under a camera 60° above the ground plane at azimuth 0, a tile 24 units wide east-west measures
# 24 × sin(60°) = 20.78 units deep north-south, quantised to 21.
#
# THE PIXEL LADDER IS AUTHORITATIVE, NOT THE FACTOR, and nothing here multiplies by GROUND_DEPTH_FACTOR
# to obtain a size. 96 × 0.8660254 = 83.14 while the published tile is 84: the real ratio is 7/8, kept
# because it divides cleanly — 96×84, 48×42, 32×28, 24×21 all land on integers. The 1 % departure from
# the geometry buys whole pixels at every step, and a sprite rendered at 20.78 laid on a step of 21
# leaves 0.22 px per tile, which reads as a seam at every join. The 84 is therefore not to be
# "corrected" to 83: that would undo a decision, not repair a mistake.
DISPLAY_TILE_WIDTH = 24
DISPLAY_TILE_DEPTH = 21
FILE_TILE_WIDTH = 96
FILE_TILE_DEPTH = 84

# What a tile measures on screen by default. The game varies it — zooming changes THIS value and
# nothing else, never the files. Adjusting it costs nothing and reworks no image.
DISPLAY_PIXELS_PER_TILE = DISPLAY_TILE_WIDTH

# What a tile measures in the file itself, delivered and produced alike. Raising it later regenerates
# nothing: the masters are kept and a re-export suffices — which is exactly why the masters are kept.
FILE_PIXELS_PER_TILE = FILE_TILE_WIDTH


def projected_depth_tiles(rows):
    """A ground depth of ROWS tiles, as it is DRAWN — in tiles of width. Read off the pixel ladder, so
    it can never drift from the sizes: 84/96 tile of image per tile of depth."""
    return rows * FILE_TILE_DEPTH / FILE_TILE_WIDTH

# Kept as the display value under its old name so callers that mean "on screen" keep working. Anything
# that means "how fine the file is" must go through delivery_size or master_definition instead.
PIXELS_PER_TILE = DISPLAY_PIXELS_PER_TILE

# A master is never larger than this on its longest side. 1536 is the long side of the six reference
# plates, so it is a definition the generator has already been proved to reach — and a ceiling worth
# stopping at, since going further costs a great deal for a gain nothing consumes.
MASTER_CAP = 1536


def tiles_to_pixels(tiles):
    """Tiles to display pixels."""
    return tiles * PIXELS_PER_TILE


def pixels_to_tiles(pixels):
    """Display pixels back to tiles. Fractional: a subject rarely lands on a whole tile."""
    return pixels / PIXELS_PER_TILE


def sprite_width(columns):
    """The display width of a sprite: exactly the width of its footprint."""
    return tiles_to_pixels(columns)


def sprite_box(columns, image_width, image_height):
    """The display box of a sprite: footprint width, height following the image's own proportions."""
    width = sprite_width(columns)

    return {"width": width, "height": width * image_height / image_width}


def tile_box(columns=1, rows=1):
    """The display box of a footprint on the ground — what a ground material occupies exactly."""
    return {"width": tiles_to_pixels(columns), "height": tiles_to_pixels(rows)}


def delivery_fineness():
    """Pixels per tile in the file — the one figure, held above and never retyped by a caller."""
    return FILE_PIXELS_PER_TILE


def delivery_size(columns, rows):
    """The pixel box a GROUND MATERIAL is delivered at: an exact box on both axes, because a tile has
    to fill its footprint edge to edge — there is no proportion of its own to follow.

    THE BOX IS NOT SQUARE, and that is the whole point of the projected tile: 96 wide by 84 deep per
    tile. It used to be square on both axes, which was a tile seen from straight above rather than
    from the world's camera — and it is what put every flat piece at 96 × 96 on disk.

    Sized on the STRONGEST ZOOM, never on the default display size: the file must still be sharp when
    the player zooms all the way in. Changing the default display size therefore changes nothing here,
    and no asset is ever re-exported because someone adjusted the on-screen tile.
    """
    return {"width": columns * FILE_TILE_WIDTH, "height": rows * FILE_TILE_DEPTH}


def delivery_width(columns):
    """The delivered width of a SPRITE: exactly the width of its footprint, at delivery fineness."""
    return columns * delivery_fineness()


def delivery_box(columns, image_width, image_height):
    """The delivery box of a sprite: footprint width at delivery fineness, height following the
    image's own proportions — sprite_box's rule, asked at the strongest zoom instead of the default
    display. A sprite is never delivered at a fixed height: fixing it would squash a tall subject's
    base off its own tiles, the same reason sprite_box never fixes it for display.
    """
    width = delivery_width(columns)

    return {"width": width, "height": round(width * image_height / image_width)}


def master_definition(columns, rows, height=None):
    """The definition of the master — used to VALIDATE the file received, never to ask the generator for anything (the generator is spoken to in tiles).

    The delivered definition itself, capped at MASTER_CAP on the longest side: 96 pixels per tile, the
    validated standard, which is already twice the strongest zoom. It was doubled a second time here,
    which asked for 192 per tile — a figure nothing consumes.

    HEIGHT IS OPTIONAL AND CHANGES ONLY THE CANVAS SHAPE, NOT THE RULE ABOVE. Left at its default
    (None), the canvas follows the footprint alone, rows included at their flat, unforeshortened
    extent — correct for a GROUND MATERIAL, which is a flat plan texture the camera never looks at
    obliquely. Pass the subject's own height, in tiles, and the canvas becomes what the world's camera
    actually SEES of that subject standing on its footprint: its ground depth (rows) foreshortened by
    GROUND_DEPTH_FACTOR, plus its own standing height foreshortened by STANDING_HEIGHT_FACTOR — the two
    project at very different scales under this camera, so simply adding a bare height in tiles to the
    footprint's rows would overstate it by roughly three to one. The width is untouched either way: it
    is dictated by the footprint's columns alone (see sprite_width), which the camera does not
    foreshorten sideways.

    A NEGATIVE HEIGHT IS A LEGITIMATE SUBJECT, NOT A FAULT — a streambed that is dug into the ground
    rather than standing on it, its lowest point below the surrounding terrain. It is real information
    (a streambed sunk by 0.3 tile is a different subject from one flush with the ground) and keeping the
    signed value, rather than clamping it to zero at the inventory, is exactly what preserves that.  But
    it must not shrink the CANVAS below the footprint's own depth: what is dug below the surface takes
    no room ABOVE it, and an assembling piece — this is where a recessed subject actually occurs — has
    to fill its case regardless of what it does below the surface line, or it stops meeting its
    neighbours edge to edge. So only a RISING height (max(height, 0)) ever adds to the canvas; a
    recessed one leaves it exactly at the footprint's own projected depth, same as height=0 would.
    """
    # UNE PIÈCE PLATE GARDE LA TOILE DE SON EMPRISE, CARRÉE — même raisonnement que pour une hauteur négative, juste en dessous, et il vaut aussi pour la hauteur zéro.
    # Un sol, un chemin, un cours d'eau sont des pièces d'assemblage : elles doivent remplir leur case bord à bord pour rejoindre leurs voisines, donc leur toile ne
    # se raccourcit pas en profondeur. Écraser leur toile déclarait toute pièce plate « trop haute » dès que la caméra est passée à 60 degrés — un verdict faux porté
    # sur des images justes, et sur exactement les pièces de réseau qu'on est en train de produire.
    if height is None or height <= 0:
        box = delivery_size(columns, rows)
    else:
        # THE GROUND DEPTH COMES FROM THE PIXEL LADDER, THE STANDING HEIGHT FROM THE FACTOR. They are
        # not symmetrical and must not be written as if they were: a tile of depth is a published size
        # (84 px), quantised so that tiles meet without a seam, while a tile of standing height is a
        # free projection with nothing to line up against — cos(60°) applies to it untouched.
        projected_depth = rows * FILE_TILE_DEPTH
        projected_height = max(height, 0) * FILE_TILE_WIDTH * STANDING_HEIGHT_FACTOR
        box = {"width": columns * FILE_TILE_WIDTH, "height": projected_depth + projected_height}
    # The file's own fineness, and nothing beyond it — reduced only when the cap would otherwise be exceeded.
    factor = min(1.0, MASTER_CAP / max(box["width"], box["height"]))

    return {"width": round(box["width"] * factor), "height": round(box["height"] * factor)}


# How far a drawing may stray from the height the model computes, ON THE STANDING PART ONLY. There is no single right height and there never will be: a roof
# ridge, a chimney, a crown leaning one way rather than another all move it, and asking a draughtsman for one exact figure asks him to stop drawing. But there
# IS a floor and there IS a ceiling, and both come from the model rather than from taste. The GROUND part is not negotiable — it is geometry, the projection of
# a footprint whose depth the plan relies on to place the subject — so the tolerance never applies to it. What varies is what rises: a quarter either way.
STANDING_TOLERANCE_LOW = 0.75
STANDING_TOLERANCE_HIGH = 1.25


def master_band(columns, rows, height=None):
    """The band of acceptable image heights for a subject, in PIXELS, around what master_definition computes.

    Why a band and not a figure (operator, 2026-08-06): a height depends on too many things to be demanded to the pixel, but a drawing that falls below the
    floor is a subject crushed into its own footprint — nothing rises, and the mock-up has nothing to overlap its neighbours with — while one above the ceiling
    towers over everything around it. Both are what made the park look wrongly calibrated: a care centre at twelve tiles for eight declared, a thicket at 1.6
    for six.

    Returns (floor, ceiling). A subject with no declared height, or one that is dug in rather than standing, has no room to vary: its canvas is its footprint,
    and floor and ceiling meet on it.
    """
    box = master_definition(columns, rows, height)
    flat = master_definition(columns, rows, 0)["height"]
    # A FLAT SUBJECT HAS A BAND TOO, and refusing to give it one is what broke the path: declared height zero produced floor and ceiling on the same pixel, so a drawing four
    # pixels short was rejected although it was right. Nothing is drawn to the exact pixel — only a ground TILE is, and that one is checked elsewhere, as a tile.
    standing = max(box["height"] - flat, 0)
    play = standing * (STANDING_TOLERANCE_HIGH - 1)
    # A FLOOR UNDER THE PLAY, or the band closes on the subjects that barely rise. A quarter of a very small standing part is a very small number: a tuft of grass three
    # tenths of a tile high got a band three pixels wide, which no drawing can hit and which would have refused a perfectly good image. The play is therefore never less
    # than a tenth of the whole expected height — tight on what stands tall, breathable on what barely stands.
    play = max(play, box["height"] * 0.1)

    return round(box["height"] - play), round(box["height"] + play)


def place(column, row):
    """A pose point expressed in tiles, turned into its pixel position on screen."""
    return {"x": tiles_to_pixels(column), "y": tiles_to_pixels(row)}


def describe():
    """The one sentence any page or report shows, so the figure is never retyped by a caller."""
    return f"une case = {PIXELS_PER_TILE} pixels"


def describe_delivery():
    """What a tile measures in the file, stated the same way and from the same place."""
    return f"fichier : une case = {FILE_PIXELS_PER_TILE} pixels"

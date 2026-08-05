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
  delivery         delivery_size, at DELIVERY_SUPERSAMPLE times the display fineness
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
# at all). The world's camera sits at 70°, i.e. close to straight overhead but "un peu de face" (see
# CAMERA_FR in asset_common.py) — the ten degrees short of 90 are exactly that little bit of front-on
# view. Getting this convention backwards is the one mistake this constant exists to rule out: it was
# made once, while drafting this very feature, before scripts/check-asset.py ("the world is seen under
# a 70° camera, which foreshortens the vertical") and the note above asset_common.CADRAGE_CUTOUT ("la
# plongée l'écrase") settled it the other way.
CAMERA_ELEVATION_DEGREES = 70

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

# What a tile measures on screen by default. The game varies it — zooming changes THIS value and
# nothing else, never the files. Adjusting it costs nothing and reworks no image.
DISPLAY_PIXELS_PER_TILE = 24

# The largest a tile will ever be shown, zoom included. Delivery fineness is sized on this and not on
# the default: an asset delivered for the default would go soft the first time anyone zoomed in, and
# it would be too late. Below it the engine scales down, which is always clean.
MAX_ZOOM_PIXELS_PER_TILE = 48

# Delivery is twice the strongest zoom, so assets stay sharp on high-density screens too. Raising this
# later regenerates nothing: the masters are kept and a re-export suffices — which is exactly why the
# masters are kept.
DELIVERY_SUPERSAMPLE = 2

# Kept as the display value under its old name so callers that mean "on screen" keep working. Anything
# that means "how fine the file is" must go through delivery_size or master_definition instead.
PIXELS_PER_TILE = DISPLAY_PIXELS_PER_TILE

# A master is rendered at twice the delivered definition, but never beyond this on its longest side.
# 1536 is the long side of the six reference plates, so it is a definition the generator has already
# been proved to reach — and a ceiling worth stopping at, since going further costs a great deal for a
# gain nothing consumes.
MASTER_CAP = 1536

# Why twice the delivery, and not simply the delivery: it buys the resampling margin down to the
# delivered size, the precision the cutout needs at the silhouette's edges, and the room to raise the
# delivery fineness by one step without reshooting the subject.
MASTER_SUPERSAMPLE = 2


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
    """Pixels per tile at delivery — the strongest zoom, doubled for high-density screens."""
    return MAX_ZOOM_PIXELS_PER_TILE * DELIVERY_SUPERSAMPLE


def delivery_size(columns, rows):
    """The pixel box a GROUND MATERIAL is delivered at: an exact box on both axes, because a tile has
    to fill its footprint edge to edge — there is no proportion of its own to follow.

    Sized on the STRONGEST ZOOM, never on the default display size: the file must still be sharp when
    the player zooms all the way in. Changing the default display size therefore changes nothing here,
    and no asset is ever re-exported because someone adjusted the on-screen tile.
    """
    fineness = delivery_fineness()

    return {"width": columns * fineness, "height": rows * fineness}


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
    """The definition asked of the generator — the MASTER's, never the delivery's.

    Twice the delivered definition, capped at MASTER_CAP on the longest side, and never below the
    delivered definition itself (assets/index.md).

    The doubling pays for three concrete things: the resampling margin down to the delivered size, the
    precision the cutout needs at the silhouette's edges, and one spare step of delivery fineness
    without reshooting. The cap stops that doubling from becoming absurd — a one-tile patch of grass
    delivered at 96 has no use for 1536, which would be sixteen times what is ever consumed. Past the
    cap a large subject simply gets no margin: the healing centre's master IS its delivery, and that
    is accepted rather than paid for.

    HEIGHT IS OPTIONAL AND CHANGES ONLY THE CANVAS SHAPE, NOT THE RULE ABOVE. Left at its default
    (None), the canvas follows the footprint alone, rows included at their flat, unforeshortened
    extent — correct for a GROUND MATERIAL, which is a flat plan texture the camera never looks at
    obliquely. Pass the subject's own height, in tiles, and the canvas becomes what the 70° camera
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
    if height is None:
        box = delivery_size(columns, rows)
    else:
        fineness = delivery_fineness()
        projected_depth = rows * fineness * GROUND_DEPTH_FACTOR
        projected_height = max(height, 0) * fineness * STANDING_HEIGHT_FACTOR
        box = {"width": columns * fineness, "height": projected_depth + projected_height}
    factor = min(MASTER_SUPERSAMPLE, MASTER_CAP / max(box["width"], box["height"]))
    factor = max(factor, 1.0)  # a master is never coarser than what it has to deliver

    return {"width": round(box["width"] * factor), "height": round(box["height"] * factor)}


def place(column, row):
    """A pose point expressed in tiles, turned into its pixel position on screen."""
    return {"x": tiles_to_pixels(column), "y": tiles_to_pixels(row)}


def describe():
    """The one sentence any page or report shows, so the figure is never retyped by a caller."""
    return f"une case = {PIXELS_PER_TILE} pixels"


def describe_delivery():
    """The delivery fineness, stated the same way and from the same place."""
    return f"livraison au double de cette finesse (×{DELIVERY_SUPERSAMPLE})"

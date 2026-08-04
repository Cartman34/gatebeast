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
"""

# One tile is one metre in the world. On screen it is this many pixels — inherited from the six
# reference plates (1536 x 1152 pixels for 32 x 24 tiles), so it agrees with the validated art
# direction. This is the only value in pixels the project owns.
PIXELS_PER_TILE = 48

# Assets are delivered at twice the display fineness, so they stay sharp on high-density screens. This
# does not enlarge the tile: the world's scale is unchanged, only the image quality rises. The factor
# can rise to three later without regenerating anything, since the masters are kept — which is exactly
# why it starts at the lighter value.
DELIVERY_SUPERSAMPLE = 2

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


def delivery_size(columns, rows):
    """The pixel box an asset of that footprint is delivered at — finer than the display."""
    box = tile_box(columns, rows)

    return {"width": box["width"] * DELIVERY_SUPERSAMPLE,
            "height": box["height"] * DELIVERY_SUPERSAMPLE}


def master_definition(columns, rows):
    """The definition asked of the generator — the MASTER's, never the delivery's.

    Twice the delivered definition, capped at MASTER_CAP on the longest side, and never below the
    delivered definition itself (assets/index.md).

    The doubling pays for three concrete things: the resampling margin down to the delivered size, the
    precision the cutout needs at the silhouette's edges, and one spare step of delivery fineness
    without reshooting. The cap stops that doubling from becoming absurd — a one-tile patch of grass
    delivered at 96 has no use for 1536, which would be sixteen times what is ever consumed. Past the
    cap a large subject simply gets no margin: the healing centre's master IS its delivery, and that
    is accepted rather than paid for.
    """
    box = delivery_size(columns, rows)
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

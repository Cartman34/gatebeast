#!/usr/bin/env python3
"""The asset catalogue — the single source that says what exists, where it lives, and what is missing.

The design makes this file the one place that describes every drawable profile (rendu-en-calques.md:
"Le catalogue d'assets est la source unique"). The generation chain writes it, scene plans refer to it,
the renderer consumes it, and the game core never sees a file name.

WHAT A PROFILE CARRIES
  code        the inventory code XX-nnn, stable for life
  name        the profile name, us-english lowercase, shape "kind-nn"
  type        ground | path | fence | vegetation | building | object | human | creature | waypoint
  layer       the layer family it is drawn in: ground | ground-decor | world | above
  footprint   ground footprint in tiles {columns, rows}
  height      the declared height in tiles, quoted from the inventory sheet ("2 cases debout"). It is
              what gives a pixel measurement a scale; null when the sheet declares none.
  anchor      the pose point, in tile coordinates inside the footprint. The design fixes it at the
              middle of the bottom edge, so it is derived, not chosen; it is written out anyway so a
              machine reader never has to know the rule.
  split       null, or {"low": <code>, "high": <code>} when one walks underneath and the profile is
              delivered in two pieces (a low piece in "monde", a high piece in "dessus")
  images      every produced file, with the variant address it answers to

ADDRESSING (sujets-et-variantes.md, applied to the letter)
  <orientation>_<action>[_<shape>][_<part>-<direction>]*_<frame>
  orientation and action are ALWAYS written. The SHAPE follows the action and is written ONLY when it
  leaves its default "plain"; a direction is written ONLY when it differs from its default "north";
  parts are sorted by name so one variant has exactly one address.
    orientation-south_action-idle_frame-01
    orientation-north_action-idle_shape-corner_frame-01
    orientation-south_action-point_gaze-east_left-hand-up_frame-01

  A SHAPE IS NEITHER AN ACTION NOR AN ORIENTATION, AND IT IS NOT THE NAME OF A DRAWING. For a subject
  that assembles end to end — a fence, a path, a watercourse, a wall — the shape is THE SET OF EDGES
  THE TRACK REACHES, written n, e, s, w: "ns" a line, "ne" an angle, "nes" a three-way, "nesw" a full
  crossing, "n" a dead end. Because it says exactly where the track meets its neighbours, a layout can
  be CHECKED BY CALCULATION — see joins() and check_layout(). Every other subject stays at "plain".

FALLBACK (a variant never fails)
  image -> frame-01, then each direction -> north, then action -> idle, then orientation -> the nearest
  available one on the compass rose.

THREE QUESTIONS THE CATALOGUE ANSWERS
  variants(code)  the postures a subject has
  files(code)     the files a subject has
  missing(code)   the images its type's lot requires and that are absent

Usage:
  python3 asset_catalog.py [--lot v0|target] [<code> ...]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import shape_vocab

REPOSITORY = Path(__file__).resolve().parents[1]
CATALOG = REPOSITORY / "assets" / "catalogue.json"

FORMAT = "gatebeast-asset-catalog"
FORMAT_VERSION = 1

# The compass rose. Orientations use the first eight; a direction may also point up or down.
ORIENTATIONS = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
DIRECTIONS = ORIENTATIONS + ["up", "down"]
DEFAULT_DIRECTION = "north"
DEFAULT_ACTION = "idle"

# The shape axis. "plain" is the value of every subject that does not assemble end to end — very
# nearly all of them — and is never written into an address.
#
# A TRACK'S SHAPE IS THE SET OF EDGES IT REACHES, and what makes a shape NAME well-formed — the four
# edges, the fifteen combinations — is shape_vocab's alone to say (see that module for why). This
# catalogue asks it rather than keeping its own copy, exactly as it asks tile_scale for pixel sizes
# rather than keeping its own.
EDGES = shape_vocab.EDGES
DEFAULT_SHAPE = shape_vocab.DEFAULT_SHAPE
EDGE_SHAPES = shape_vocab.edge_combinations()
SHAPES = [DEFAULT_SHAPE] + EDGE_SHAPES

# The opposite edge, which is the one a neighbour shares.
OPPOSITE = {"n": "s", "s": "n", "e": "w", "w": "e"}
# Which neighbour lies past each edge, in tile coordinates.
NEIGHBOUR = {"n": (0, -1), "e": (1, 0), "s": (0, 1), "w": (-1, 0)}


def edges_of(shape):
    """The edges a shape reaches. Delegates to shape_vocab: a LAYOUT's neighbour geometry (OPPOSITE,
    NEIGHBOUR, joins, check_layout below) is this catalogue's own concern, but what a shape NAME means
    is not — shape_vocab knows nothing of a grid and this catalogue keeps it that way.
    """
    return shape_vocab.edges_of(shape)


def joins(shape, other_shape, edge):
    """Do two neighbouring tiles agree across the edge they share?

    The shape says exactly where a track touches its neighbours, so a track's consistency is a matter
    of calculation rather than of looking: two neighbouring tiles agree when each reaches the edge
    they share, or when neither does.
    """
    return (edge in edges_of(shape)) == (OPPOSITE[edge] in edges_of(other_shape))


def check_layout(placed):
    """Check a whole layout of tracks. `placed` maps (column, row) to a shape.

    Returns the list of faults, each naming the two tiles and the edge they disagree on. An empty list
    means every track in the layout runs into its neighbours without a break or a dangling end.
    """
    faults = []
    for (column, row), shape in sorted(placed.items()):
        for edge in edges_of(shape):
            step = NEIGHBOUR[edge]
            neighbour = (column + step[0], row + step[1])
            other = placed.get(neighbour, DEFAULT_SHAPE)
            if not joins(shape, other, edge):
                faults.append({
                    "tile": (column, row), "shape": shape, "edge": edge,
                    "neighbour": neighbour, "neighbour_shape": other,
                })

    return faults

# The five layer families, in drawing order (rendu-en-calques.md). "interface" carries no asset profile.
LAYERS = ["ground", "ground-decor", "world", "above", "interface"]

# The layer each type is drawn in.
# ATTENTION AUX HOMONYMES : la VALEUR DE TYPE « sol » est devenue `ground` le 2026-08-12, mais le NOM DE CALQUE « sol » n'a pas bougé — ce sont deux notions qui
# portaient le même mot. Traduire les deux d'un même geste aurait renommé un calque que personne n'a demandé de renommer.
TYPE_LAYER = {
    "ground": "ground",
    "path": "ground-decor",
    "fence": "world",
    "vegetation": "world",
    "building": "world",
    "object": "world",
    "human": "world",
    "creature": "world",
    "waypoint": "world",
}

# A flat track is drawn once per DRAWING, not once per edge set: the fifteen combinations come down to
# five pictures, and the renderer turns a path to obtain the rest. One representative edge set per
# drawing is what gets produced.
PATH_DRAWINGS = {"n": "extrémité", "ns": "ligne", "ne": "angle", "nes": "trois branches",
                 "nesw": "croisement"}
PATH_SHAPES = list(PATH_DRAWINGS)

# A fence or a wall stands up. Turning it would put the sun on the wrong side, so every useful edge
# combination is drawn separately. This is the park lot of lots-de-variantes.md.
FENCE_SHAPES = ["ns", "ew", "ne", "es", "sw", "nw"]
FENCE_LOT = [("south", shape) for shape in FENCE_SHAPES]

# The lot required of every profile of a type (lots-de-variantes.md), in target and in v0. Each entry
# is a list of (orientation, shape) pairs at the idle action; all directions stay at their default.
MAIN_VIEW = ("south", DEFAULT_SHAPE)
MOVING_ORIENTATIONS = ["south", "north", "west", "east"]


def _lot_moving(actions):
    """A subject that turns: every orientation, for each action, at the default shape."""
    return [(orientation, DEFAULT_SHAPE, action)
            for action in actions for orientation in MOVING_ORIENTATIONS]


def _lot_still(pairs):
    """A subject that does not act: every (orientation, shape) pair, at idle."""
    return [(orientation, shape, DEFAULT_ACTION) for orientation, shape in pairs]


REQUIRED_LOTS = {
    "ground": {"target": _lot_still([MAIN_VIEW]), "v0": _lot_still([MAIN_VIEW])},
    "path": {
        "target": _lot_still([("south", shape) for shape in PATH_SHAPES]),
        "v0": _lot_still([("south", "ns"), ("south", "ne")]),
    },
    # The target lot is "the useful edge combinations, each drawn separately" — which combinations a
    # profile actually uses is a property of its layout, so only the park lot the design spells out is
    # expressible here.
    "fence": {"target": _lot_still(FENCE_LOT), "v0": _lot_still(FENCE_LOT)},
    "vegetation": {"target": _lot_still([MAIN_VIEW]), "v0": _lot_still([MAIN_VIEW])},
    "building": {"target": _lot_still([MAIN_VIEW]), "v0": _lot_still([MAIN_VIEW])},
    "object": {"target": _lot_still([MAIN_VIEW]), "v0": _lot_still([MAIN_VIEW])},
    "human": {"target": _lot_moving(["idle", "walk"]), "v0": _lot_moving(["idle"])},
    "creature": {"target": _lot_moving(["idle", "walk"]), "v0": _lot_moving(["idle"])},
    # The target lot of a crossing point is "a series of images", whose count the design leaves open.
    # Only its v0 lot is expressible today.
    "waypoint": {"target": _lot_still([MAIN_VIEW]), "v0": _lot_still([MAIN_VIEW])},
}


class Variant:
    """A posture: an orientation, an action, a shape, and the direction of each pointing part."""

    def __init__(self, orientation, action=DEFAULT_ACTION, directions=None, shape=DEFAULT_SHAPE):
        if orientation not in ORIENTATIONS:
            raise ValueError(f"unknown orientation: {orientation}")
        if not shape_vocab.valid_shape(shape):
            raise ValueError(f"unknown shape: {shape}")
        self.orientation = orientation
        self.action = action
        self.shape = shape
        self.directions = {}
        for part, direction in (directions or {}).items():
            if direction not in DIRECTIONS:
                raise ValueError(f"unknown direction for {part}: {direction}")
            if direction != DEFAULT_DIRECTION:
                self.directions[part] = direction

    def address(self, frame=1):
        """The full address of one image of this variant."""
        pieces = [f"orientation-{self.orientation}", f"action-{self.action}"]
        if self.shape != DEFAULT_SHAPE:
            pieces.append(f"shape-{self.shape}")
        for part in sorted(self.directions):
            pieces.append(f"{part}-{self.directions[part]}")
        pieces.append(f"frame-{frame:02d}")

        return "_".join(pieces)

    def key(self):
        """The address without the frame — what identifies the posture itself."""
        return self.address(1).rsplit("_frame-", 1)[0]

    def __eq__(self, other):
        return isinstance(other, Variant) and self.key() == other.key()

    def __hash__(self):
        return hash(self.key())

    def __repr__(self):
        return f"Variant({self.key()})"


def parse_address(address):
    """Read an address back into (Variant, frame). The inverse of Variant.address()."""
    pieces = address.split("_")
    if len(pieces) < 3:
        raise ValueError(f"malformed address: {address}")
    if not pieces[0].startswith("orientation-") or not pieces[1].startswith("action-"):
        raise ValueError(f"address must start with orientation then action: {address}")
    if not pieces[-1].startswith("frame-"):
        raise ValueError(f"address must end with a frame: {address}")
    orientation = pieces[0][len("orientation-"):]
    action = pieces[1][len("action-"):]
    frame = int(pieces[-1][len("frame-"):])
    middle = pieces[2:-1]
    # The shape, if written at all, sits immediately after the action.
    shape = DEFAULT_SHAPE
    if middle and middle[0].startswith("shape-"):
        shape = middle[0][len("shape-"):]
        if not shape_vocab.valid_shape(shape):
            raise ValueError(f"unknown shape in address: {shape}")
        middle = middle[1:]
    directions = {}
    for piece in middle:
        # A part name may itself contain hyphens (left-hand); the direction is the known suffix, and
        # the longest match wins so "north-east" is never read as "east".
        match = None
        for candidate in sorted(DIRECTIONS, key=len, reverse=True):
            if piece.endswith(f"-{candidate}"):
                match = candidate
                break
        if match is None:
            raise ValueError(f"no known direction in address piece: {piece}")
        directions[piece[: -len(match) - 1]] = match

    return Variant(orientation, action, directions, shape), frame


def compass_distance(one, other):
    """How far apart two orientations are on the eight-point rose, in steps."""
    gap = abs(ORIENTATIONS.index(one) - ORIENTATIONS.index(other))

    return min(gap, len(ORIENTATIONS) - gap)


class Image:
    """One produced file, answering one address."""

    def __init__(self, address, path, measures=None, source=None):
        self.variant, self.frame = parse_address(address)
        self.address = address
        self.path = path
        # The image the cutout was made from. Nothing is thrown away, so the origin stays reachable.
        self.source = source
        # What the cutout measured on this very file: apparent footprint and pose point, in pixels.
        self.measures = measures or {}

    def to_json(self):
        payload = {"address": self.address, "path": self.path}
        if self.source:
            payload["source"] = self.source
        if self.measures:
            payload["measures"] = self.measures

        return payload


class Profile:
    """One appearance, one inventory entry."""

    def __init__(self, code, type_, name=None, footprint=None, split=None, images=None, layer=None,
                 height=None):
        if type_ not in TYPE_LAYER:
            raise ValueError(f"unknown type: {type_}")
        self.code = code
        self.name = name
        self.type = type_
        self.layer = layer or TYPE_LAYER[type_]
        self.footprint = footprint or {"columns": 1, "rows": 1}
        self.height = height
        self.split = split
        self.images = list(images or [])

    @property
    def anchor(self):
        """The pose point in tile coordinates: middle of the bottom edge of the footprint."""
        return {"x": self.footprint["columns"] / 2, "y": float(self.footprint["rows"])}

    def variants(self):
        """The postures this subject owns, as addresses without a frame."""
        seen = []
        for image in self.images:
            key = image.variant.key()
            if key not in seen:
                seen.append(key)

        return seen

    def files(self):
        """Every file this subject owns."""
        return [image.path for image in self.images]

    def frames(self, variant):
        """The frame numbers available for one posture, in order."""
        key = variant.key() if isinstance(variant, Variant) else variant

        return sorted(image.frame for image in self.images if image.variant.key() == key)

    def required(self, lot="v0"):
        """The addresses the type's lot demands of this profile."""
        entries = REQUIRED_LOTS[self.type][lot]

        return [Variant(orientation, action, shape=shape).address(1)
                for orientation, shape, action in entries]

    def missing(self, lot="v0"):
        """What the lot demands and the profile does not have."""
        owned = {image.address for image in self.images}

        return [address for address in self.required(lot) if address not in owned]

    def resolve(self, address):
        """Find the best file for an address, applying the fallback rule. Never fails if any image exists.

        Order, as the design fixes it: image -> frame-01, each direction -> north, action -> idle,
        orientation -> the nearest available.

        THE SHAPE NEVER FALLS BACK. It is absent from the design's fallback list because it is part of
        what is being asked for, not a nicety: serving a straight run where a corner was asked for
        would put a visible break in a fence. The shape is therefore held constant at every step, and
        the orientation only falls back among images of that same shape when there are any.
        """
        if not self.images:
            return None
        wanted, frame = parse_address(address)
        by_address = {image.address: image for image in self.images}

        # 1. Exact hit.
        if address in by_address:
            return by_address[address]
        # 2. The image falls back to frame-01 of the same posture.
        if wanted.address(1) in by_address:
            return by_address[wanted.address(1)]
        # 3. Directions drop to their default, one at a time, the last-named part first.
        directions = dict(wanted.directions)
        for part in sorted(directions, reverse=True):
            directions.pop(part)
            candidate = Variant(wanted.orientation, wanted.action, directions,
                                wanted.shape).address(1)
            if candidate in by_address:
                return by_address[candidate]
        # 4. The action falls back to idle.
        candidate = Variant(wanted.orientation, DEFAULT_ACTION, shape=wanted.shape).address(1)
        if candidate in by_address:
            return by_address[candidate]
        # 5. The orientation falls back to the nearest available — among the same shape if it exists.
        pool_images = [image for image in self.images if image.variant.shape == wanted.shape]
        if not pool_images:
            pool_images = self.images
        available = {}
        for image in pool_images:
            available.setdefault(image.variant.orientation, []).append(image)
        nearest = min(available, key=lambda o: (compass_distance(o, wanted.orientation),
                                                ORIENTATIONS.index(o)))
        pool = available[nearest]
        idle = [image for image in pool if image.variant.action == DEFAULT_ACTION]

        return sorted(idle or pool, key=lambda image: (image.variant.key(), image.frame))[0]

    def to_json(self):
        payload = {
            "code": self.code,
            "name": self.name,
            "type": self.type,
            "layer": self.layer,
            "footprint": self.footprint,
            "height": self.height,
            "anchor": self.anchor,
            "split": self.split,
            "images": [image.to_json() for image in self.images],
        }

        return payload

    @staticmethod
    def from_json(payload):
        images = [Image(entry["address"], entry["path"], entry.get("measures"), entry.get("source"))
                  for entry in payload.get("images", [])]

        return Profile(payload["code"], payload["type"], payload.get("name"),
                       payload.get("footprint"), payload.get("split"), images, payload.get("layer"),
                       payload.get("height"))


class Catalog:
    """The whole catalogue: every profile, read from and written to one JSON file."""

    def __init__(self, profiles=None, path=None):
        self.profiles = {profile.code: profile for profile in (profiles or [])}
        self.path = path

    def __contains__(self, code):
        return code in self.profiles

    def __iter__(self):
        return iter(self.profiles.values())

    def profile(self, code):
        if code not in self.profiles:
            raise KeyError(f"unknown profile: {code}")

        return self.profiles[code]

    def add(self, profile):
        self.profiles[profile.code] = profile

        return profile

    def record(self, code, address, path, measures=None, source=None):
        """Inscribe one validated image. The chain calls this, never a human."""
        profile = self.profile(code)
        profile.images = [image for image in profile.images if image.address != address]
        profile.images.append(Image(address, path, measures, source))
        profile.images.sort(key=lambda image: image.address)

        return profile

    def variants(self, code):
        return self.profile(code).variants()

    def files(self, code):
        return self.profile(code).files()

    def missing(self, code=None, lot="v0"):
        """What is missing for one profile, or for every profile when no code is given."""
        if code is not None:
            return self.profile(code).missing(lot)

        return {profile.code: profile.missing(lot) for profile in self
                if profile.missing(lot)}

    def to_json(self):
        return {
            "format": FORMAT,
            "version": FORMAT_VERSION,
            "profiles": [self.profiles[code].to_json() for code in sorted(self.profiles)],
        }

    def save(self, path=None):
        target = Path(path or self.path or CATALOG)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_json(), indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        self.path = target

        return target


def load(path=None):
    """Read the catalogue. An absent file is an empty catalogue, not an error."""
    target = Path(path or CATALOG)
    if not target.is_file():
        return Catalog(path=target)
    payload = json.loads(target.read_text(encoding="utf-8"))
    if payload.get("format") != FORMAT:
        raise ValueError(f"not an asset catalogue: {target}")

    return Catalog([Profile.from_json(entry) for entry in payload.get("profiles", [])], path=target)


def main(arguments):
    lot = "v0"
    codes = []
    index = 0
    while index < len(arguments):
        if arguments[index] == "--lot":
            lot = arguments[index + 1]
            index += 2
            continue
        codes.append(arguments[index])
        index += 1
    if lot not in ("v0", "target"):
        print(f"unknown lot: {lot} (v0 | target)")
        return 2

    catalog = load()
    if not catalog.profiles:
        print(f"empty catalogue: {CATALOG}")
        return 1
    for code in codes or sorted(catalog.profiles):
        profile = catalog.profile(code)
        print(f"{profile.code}  {profile.name or '-'}  type {profile.type}  layer {profile.layer}  "
              f"footprint {profile.footprint['columns']}x{profile.footprint['rows']} tiles  "
              f"height {profile.height if profile.height is not None else '-'}  "
              f"anchor {profile.anchor['x']},{profile.anchor['y']}"
              + (f"  split {profile.split}" if profile.split else ""))
        for variant in profile.variants():
            print(f"    variant {variant}  frames {profile.frames(variant)}")
        for path in profile.files():
            print(f"    file    {path}")
        absent = profile.missing(lot)
        print(f"    missing ({lot}): {len(absent)}")
        for address in absent:
            print(f"      - {address}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

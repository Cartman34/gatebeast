#!/usr/bin/env python3
"""Plate P6 beach, second pass — first composition written to the format, from the plan the owner
retained. Lessons from the first version's review are carried in: BRIGHT image, SHELLS on the
waterline, palms and coastal plants (grass tufts may cover several tiles, as in reality), CREATURES
VISIBLE UNDER THE WATER, a jetty at beach level with no raised entrance, and the P5 joint given with
exact measure and axis (edge, row 20). Edge connections: P5 (left edge, row 20), P3 (top edge,
column 26). The path climbs inland: the shore stays an open sand beach."""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

STYLE = (
    "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and rim "
    "light, cel shading in two crisp bands, no outline."
)

ANCHOR = (
    "STYLE REFERENCE — ./da-gb-b4v6-scene.png is the exact target. Reproduce ITS rendering with no "
    "deviation: same modelling of volumes, same crisp two-band cel shading, same FRANK SATURATED COLOURS, "
    "same amount of surface detail, same degree of stylisation. PEOPLE AND CREATURES ARE RENDERED IN "
    "EXACTLY THAT SAME STYLE — never more realistic, never flatter. Take ONLY the style from it; the "
    "composition below applies."
)

SCALE = """
FRAME AND SCALE — the image is 1536 x 1152 pixels for a grid of 32 columns by 24 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row), origin
(1,1) top left.

SCALE IS THE FIRST THING CHECKED ON THE RESULT — respect it over everything else:
- An adult human is 2 metres tall: EXACTLY 2 TILES, 96 PIXELS, never more, standing on ONE tile of ground.
- EVERY DOOR IS 2.5 TILES HIGH — 120 PIXELS — and one tile wide, noticeably taller than the people.
- A dwelling is NEVER narrower than 8 tiles (384 PIXELS) in its smallest dimension.
- NOTHING BUILT FITS IN ONE TILE: any structure covers AT LEAST 2 tiles. One tile holds a crate, an oar,
  a coil of rope — nothing built.
- Footprints are filled to their edges, never spilling onto neighbouring tiles. Only height rises above.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. The
image is BRIGHT — this biome was too dark last time: golden sand, luminous turquoise water, FRANK
SATURATED COLOURS, never muted. No deep shadow. Sharp edge to edge.

TWO MEASURED LIMITS:
1. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark, the sea included — the sea is LUMINOUS
   turquoise, never deep blue-black.
2. DRESSING: shells, pebbles, ripples in the sand, dry seaweed. AT MOST ONE TILE IN FIVE carries
   dressing — but grass tufts on the dunes MAY cover several adjoining tiles, as in reality.

VARY THE FACING DIRECTIONS — recurring fault to avoid: humans never face down, creatures only in
diagonal. Here, SOME HUMANS FACE STRAIGHT DOWN towards the camera, face fully visible, and at least one
creature faces STRAIGHT DOWN too, not diagonally.

COHERENCE — nothing ends in the void, and LOGIC over realism: the jetty starts AT BEACH LEVEL, its deck
flat and walkable straight from the sand — no raised entrance, no steps to nowhere. Boats are beached or
moored. Every building is reached by a path.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, boats or props.

NO REAL ANIMALS EXIST — no gulls, no crabs, no fish, no starfish, no insects. Everything alive that is
not human is an invented CREATURE wearing a rune, never a real animal recoloured, none with a human face.
Empty SHELLS on the sand are fine — they are objects, not animals.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body,
glimmering faintly, about a QUARTER OF A TILE (12 pixels). No two share a shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair.

No text, no interface, no logos, no grid lines.
"""

P6 = """
PLATE P6 — BEACH. Biome: a bright golden sand beach with dunes, palms and coastal plants, a timber
jetty, two fishermen's cabins, and a luminous turquoise sea with white foam.

DRAW THESE TWO EDGE CONNECTIONS FIRST — exact measure and axis, each VISIBLY TOUCHING its border:
1. A SANDY PATH, one tile wide, ALONG ROW 20, reaching the LEFT EDGE at EXACTLY (1,20) — 912 to 960
   pixels from the top. This is the joint with the cliff plate: the path arrives horizontally, on the
   row 20 axis, cut off by the left border.
2. A SANDY PATH, one tile wide, ALONG COLUMN 26, reaching the TOP EDGE at EXACTLY (26,1) — the path
   from the foothills, vertical on the column 26 axis, cut off by the top border.

PATH NETWORK — the path from the left edge runs (1,20) to (4,20), then climbs INLAND up column 4 from
(4,20) to (4,16), then east along row 16 from (4,16) to (15,16). The path from the top edge runs down
column 26 from (26,1) to (26,12), then west along row 12 from (26,12) to (15,12). Branches: down column 5
from (5,10) to (5,15) to cabin 1's door; down column 15 from (15,11) to (15,16) linking cabin 2, both
paths and, via row 13 from (15,13) to (18,13), the jetty. THE SHORE HAS NO PATH: the beach between the
paths and the sea is open sand.

THE SEA — luminous turquoise water with gentle white foam lines, covering (20,14)-(32,21) and the whole
bottom band (1,22)-(32,24). The waterline crosses the sand in a soft irregular curve. CREATURES ARE
VISIBLE UNDER THE WATER through the transparency (see inhabitants).

THE JETTY — a timber JETTY at (18,13)-(19,22): its deck FLAT AT BEACH LEVEL, boards worn, running from
the sand straight out over the water on stout posts, reached by the row-13 branch. No steps, no raised
entrance.

BUILDINGS — doors 2.5 tiles (120 pixels) high:
- FISHERMAN'S CABIN 1 at (2,2)-(9,9): eight by eight, sun-bleached planks, flat driftwood roof, door on
  its lower side at (5,9), nets hung on the wall. State: weathered.
- FISHERMAN'S CABIN 2 at (12,3)-(19,10): eight by eight, visibly different — whitewashed walls, blue
  shutters, single-slope tiled roof, door on its lower side at (15,10).

DUNES AND VEGETATION — soft DUNES at (6,12)-(11,15), golden sand with GRASS TUFTS covering several
adjoining tiles on their crests; FOUR PALMS, each a different height and lean, at (2,11), (10,13),
(21,2), (29,4), their fronds catching the light; a patch of MALCOLMIA — low coastal plants with small
lilac flowers — at (12,18)-(14,19); coastal shrubs at (23,6)-(25,7) and (30,9)-(31,10).

SHELLS — empty shells scattered ALONG THE WATERLINE: visible clusters at (4,21), (9,21), (15,21) and
(24,20), pale pink and cream, each shell a hand's width.

OBJECTS — a beached BOAT, two tiles, at (5,18)-(6,18), hull striped; a second beached BOAT, two tiles,
older, at (13,19)-(14,19); stacked wicker CRATES at (16,13) and (21,13); rocks streaked with white at
(28,12)-(29,13) and (2,16)-(3,17).

INHABITANTS
- (10,20) a FISHERWOMAN, brown skin, headscarf, carrying a basket of nets along the path, walking RIGHT.
- (19,16) a FISHER, pale skin, blond beard, kneeling on the jetty coiling a rope, FACING STRAIGHT DOWN
  towards the camera, face fully visible.
- (27,8) a child of about ten, East Asian features, running DOWN the foothill path, FACING DOWN.
- CREATURES, each one tile, each with its rune: at (7,19) a sand-coloured creature with a spiral shell
  on its back dozing near the boat, FACING STRAIGHT DOWN towards the camera, not diagonally; at (24,18)
  a sleek finned creature VISIBLE UNDER THE WATER, its silhouette clear through the turquoise
  transparency, swimming LEFT; at (30,22) a second aquatic creature UNDER THE WATER near the rocks, only
  its shadowed shape and glowing rune showing through.
- THE MAJESTIC CREATURE at (12,13)-(13,14): TWO TILES of ground at rest — a tall shore-strider with
  long wading legs, pearl-white with sea-green mottling, a collar of translucent fins around its neck,
  standing on the dune crest FACING DOWN, overlooking the beach. Its rune, a single glimmering stroke,
  along its flank.
"""

KEY = "p6-plage-v2"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P6}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

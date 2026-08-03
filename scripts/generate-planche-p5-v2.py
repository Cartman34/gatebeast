#!/usr/bin/env python3
"""Plate P5 cliff, second pass — first composition written to the format, from the validated SVG plan.

Everything established applies: scale hammered in pixels, nothing built in one tile, buildings served by
paths, no real animals, varied facing angles, measured limits (darkness, dressing), frank colours
anchored on da-gb-b4v6-scene. Edge connections per the plate plan: P4 (left edge, row 12), P2 (top edge,
column 18), P6 (right edge, row 20 — over the cliff on a footbridge). The cliff reads as a rock face
band between the plateau and the sea below, rocks at its foot.
"""
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
- NOTHING BUILT FITS IN ONE TILE: any structure covers AT LEAST 2 tiles. One tile holds a barrel, a
  coiled rope, a lobster pot — nothing built.
- Footprints are filled to their edges, never spilling onto neighbouring tiles. Only height rises above.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point. The sea at the foot
of the cliff is seen from above, far below.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. Bright
image, FRANK SATURATED COLOURS — rich, vivid, never muted or washed out. No deep shadow. Sharp edge to
edge.

TWO MEASURED LIMITS:
1. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark, the cliff face and sea included.
2. DRESSING: grass tufts, small stones, salt-bleached driftwood. AT MOST ONE TILE IN FIVE carries any
   dressing; the rest is plain wind-cropped grass.

VARY THE FACING DIRECTIONS — recurring fault to avoid: humans never face down, creatures only in
diagonal. Here, SOME HUMANS FACE STRAIGHT DOWN towards the camera, face fully visible, and at least one
creature faces STRAIGHT DOWN too, not diagonally.

COHERENCE — nothing ends in the void. Every building is reached by a path; the stair lands somewhere;
the footbridge touches ground at both ends.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, boats or props.

NO REAL ANIMALS EXIST — no gulls, no seabirds, no fish, no crabs, no insects. Everything alive that is
not human is an invented CREATURE wearing a rune, never a real animal recoloured, none with a human face.
Two creatures of one species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body,
glimmering faintly, about a QUARTER OF A TILE (12 pixels). No two share a shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair.

No text, no interface, no logos, no grid lines.
"""

P5 = """
PLATE P5 — CLIFF TOP. Biome: a windswept grassy plateau ending in a SHEER CLIFF; the sea far below in
the lower right corner, dark turquoise with white foam, ROCKS AT THE FOOT OF THE CLIFF breaking the
waves. Wind-cropped grass, salt-worn stone, weathered timber.

THE CLIFF IS THE SUBJECT: a rock face band crossing the lower right of the plate — from (18,21) to
(32,22) and rising along (30,17)-(32,19) — drawn as a steep drop seen from above: the plateau edge, the
striated rock face, then the sea below at (20,23)-(32,24). Rocks at the cliff foot at (22,23)-(24,24)
and (28,23)-(30,24), waves foaming white against them.

DRAW THESE THREE EDGE CONNECTIONS FIRST — each a path one tile wide that VISIBLY TOUCHES its border,
cut off by it:
1. Along ROW 12, reaching the LEFT EDGE at (1,12) — the walkway from the marsh becomes a dirt path here.
2. Along COLUMN 18, reaching the TOP EDGE at (18,1) — the road from the town.
3. Along ROW 20, reaching the RIGHT EDGE at (32,20) — crossing the high rock on a WOODEN FOOTBRIDGE at
   (30,20)-(32,20), both ends on ground, leading down towards the beach.

PATH NETWORK — path 1 runs from (1,12) to (18,12); path 2 runs down column 18 from (18,1) to (18,20);
path 3 runs from (18,20) to (32,20). Branches: from the lighthouse door, down column 25 from (25,10) to
(25,19), joining path 3; from (6,13) down to (6,15) to the cabin door.

THE STAIR — a STAIR CUT INTO THE CLIFF at (29,18)-(30,20): stone steps descending from the plateau into
the rock, connected to path 3.

BUILDINGS — doors 2.5 tiles (120 pixels) high:
- LIGHTHOUSE at (22,2)-(29,9): a stout round stone tower, eight tiles across, white and red bands worn
  by salt, lantern room with thick glass at the top seen from above, door on its lower side at (25,9),
  reached by its branch. State: worn, cared for.
- FISHING CABIN at (3,16)-(10,23): eight by eight, low stone walls, tarred timber roof held by ropes and
  stones against the wind, door on its upper side at (6,16), a small chimney. State: weathered.
- DRYING RACKS at (12,16)-(15,17): a timber frame hung with nets drying in the wind, half full.

VEGETATION — ONE WIND-BENT TREE at (5,4), leaning right, sculpted by the wind, dense low crown; a small
twisted shrub at (13,6). Everywhere else: plain wind-cropped grass in vivid green, dressing within the
one-in-five limit.

OBJECTS — rock outcrops at (2,8)-(3,9) and (20,15)-(21,16), grey stone streaked with white; a stack of
lobster pots covering (8,13), one tile of stacked wicker; coiled ropes and a barrel by the cabin door.

INHABITANTS
- (26,11) the LIGHTHOUSE KEEPER, a sturdy woman in her sixties, dark skin, white hair tied back, oilskin
  coat, walking DOWN the lighthouse branch, FACING STRAIGHT DOWN towards the camera, face fully visible.
- (13,15) a FISHER, a lean man with East Asian features, mending a net at the drying racks, FACING UP.
- (19,13) a young traveller, pale freckled skin, red hair, pack on their back, walking DOWN along
  column 18, FACING DOWN.
- CREATURES, each one tile, each with its rune, each different: at (7,6) a plump grey-blue creature with
  wind-ruffled fur sitting near the bent tree, FACING STRAIGHT DOWN towards the camera, not diagonally;
  at (21,21) a sleek dark creature perched on the cliff edge looking out to sea, FACING RIGHT; at
  (30,18) a small pale creature with membrane flaps hopping between the stair steps.
- THE MAJESTIC CREATURE at (4,10)-(5,11): TWO TILES of ground at rest — a tall long-necked creature,
  storm-grey with silver flanks, a crest of stiff feather-like plumes swept back by the wind, standing
  at the plateau's high point FACING RIGHT, watching the sea. Its rune, a single glimmering stroke, on
  its chest.
"""

KEY = "p5-falaise-v2"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P5}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

#!/usr/bin/env python3
"""Plate P1 countryside, fourth pass.

Carried corrections, each traced to a recorded fault:
- OVERLOAD: v3 measured 94.5% busy tiles against 74 expected. The dressing cap (one tile in five) and
  wide plain meadow surfaces are now explicit.
- SCALE: hammered per building with door heights in pixels — the rule was prescribed and ignored before.
- BUILT THINGS NEVER FIT ONE TILE: the cart and the well now cover two tiles.
- FACING ANGLES VARY: recorded recurring fault — humans never face down, creatures only diagonally.
  This composition includes humans FACING DOWN towards the camera and a creature facing straight down.
Everything else carries over from v3 unchanged: it was not faulted.
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
    "deviation: same modelling of volumes, same crisp two-band cel shading, same FRANK SATURATED COLOURS, "
    "same amount of surface detail, same degree of stylisation. PEOPLE AND CREATURES ARE RENDERED IN "
    "EXACTLY THAT SAME STYLE. Take ONLY the style from it; the composition below applies."
)

SCALE = """
FRAME AND SCALE — the image is 1536 x 1152 pixels for a grid of 32 columns by 24 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row), origin
(1,1) top left.

SCALE IS THE FIRST THING CHECKED ON THE RESULT — respect it over everything else:
- An adult human is 2 metres tall: EXACTLY 2 TILES, 96 PIXELS, never more, standing on ONE tile of ground.
- EVERY DOOR IS 2.5 TILES HIGH — 120 PIXELS — and one tile wide. A human fits through with room above.
- A dwelling is NEVER narrower than 8 tiles (384 PIXELS) in its smallest dimension.
- NOTHING BUILT FITS IN ONE TILE: a stall, a cart, a well, any structure covers AT LEAST 2 tiles. One
  tile holds sacks, a chair, a barrel — nothing built.
- Footprints are filled to their edges, never spilling onto neighbouring tiles. Only height rises above.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. Bright
image, FRANK SATURATED COLOURS — never muted, greyed or washed out. No deep shadow. Sharp edge to edge.

TWO MEASURED LIMITS:
1. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark.
2. DRESSING: grass tufts, flowers, pebbles, fallen leaves. AT MOST ONE TILE IN FIVE carries any dressing;
   the other four are PLAIN UNBROKEN MEADOW — flat colour, no scatter. Wide plain surfaces are the style.

VARY THE FACING DIRECTIONS — recurring fault to avoid: humans never face down, creatures only in
diagonal. Here, SOME HUMANS FACE STRAIGHT DOWN towards the camera, face fully visible, and at least one
creature faces STRAIGHT DOWN too, not diagonally.

COHERENCE — nothing ends in the void. A bridge lands on the road at both ends, a door opens onto a path.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings or props.

NO REAL ANIMALS EXIST — no birds, ducks, dogs, cattle, sheep or insects. Everything alive that is not
human is an invented CREATURE wearing a rune, never a real animal recoloured, none with a human face. Two
creatures of one species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body,
glimmering faintly, about a QUARTER OF A TILE (12 pixels). No two share a shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair.

No text, no interface, no logos, no grid lines.
"""

P1 = """
PLATE P1 — WOODED COUNTRYSIDE. Biome: rolling cultivated land, hedged fields, orchards, WIDE PLAIN
MEADOWS, copses of broadleaf trees, soft fresh green tones.

DRAW THESE TWO EDGE EXITS FIRST:
1. A DIRT ROAD, one tile wide, running along ROW 16 and REACHING THE RIGHT EDGE OF THE IMAGE at (32,16),
   visibly cut off by the border.
2. A DIRT ROAD, one tile wide, running down COLUMN 12 and REACHING THE BOTTOM EDGE OF THE IMAGE at
   (12,24), visibly cut off by the border.

OTHER PATHS — a branch climbs from (8,16) to (8,12) to the farmhouse door; one from (22,16) to (22,11) to
the mill door; one from (17,16) to (17,20) to the cottage door.

WATER — a brook enters at (28,1), runs down to (28,13), left along row 13 to (20,13), then down to (20,24),
flowing that way. A STONE BRIDGE at (20,16)-(21,16) carries the main road over it, both ends on the road.

BUILDINGS — doors 2.5 tiles (120 pixels) high, one tile wide, every one of them:
- FARMHOUSE at (2,2)-(13,11): twelve by ten (576 by 480 pixels), stone and timber, tiled roof, chimney,
  door on its lower side at (8,11). State: worn, cared for.
- BARN at (15,3)-(24,9): ten by seven, red-boarded, double doors at (19,9) three tiles high, hayloft.
- WINDMILL at (26,4)-(31,10): a round stone mill with four sails, door at (28,10).
- COTTAGE at (14,19)-(23,24): ten by six visible, thatched, door on its upper side at (17,19).

FIELDS AND ORCHARD — a MIXED ORCHARD at (24,17)-(31,23), all adult, each tree a different height and
crown: two apple trees at 80% fruit, one pear at 50%, one plum at 30%, one cherry in blossom without
fruit, one quince at 20%. A hedged vegetable plot at (2,12)-(7,15), well kept, half its rows planted. A
ripe wheat field at (26,11)-(31,15). Hedgerows along (2,16)-(7,16) and (14,12)-(19,12).

VEGETATION — one broad old oak, dense, at (10,18); three slim birches at (3,18), (15,14), (30,2); two dark
firs at (1,8) and (31,20). Everywhere else: WIDE PLAIN MEADOW, flat fresh green, dressing within the
one-in-five limit.

OBJECTS — three haystacks of differing sizes at (25,10), (27,16), (29,16); a STONE WELL covering
(14,10)-(15,10), two tiles, with a small roof; a CART half loaded with sacks covering (10,15)-(11,15),
two tiles; a full water trough at (16,10).

INHABITANTS
- (9,13) a farmer in his forties, deep brown skin, forking hay, FACING STRAIGHT DOWN towards the camera,
  face fully visible.
- (14,16) a woman in her thirties, East Asian features, carrying a basket of apples, walking LEFT.
- (28,11) a miller, pale skin, grey hair, in the mill doorway FACING DOWN, a flour sack at his feet.
- (18,16) and (19,16) two children of different origins running RIGHT along the road.
- CREATURES, each one tile, each with its rune: at (24,16) a russet fox-like creature FACING STRAIGHT
  DOWN towards the camera, not diagonally; at (26,20) a stocky mossy-backed creature asleep under an
  orchard tree; at (21,14) a long-legged creature ON THE BANK of the brook, FACING LEFT, front feet IN
  THE SHALLOW WATER touching the bottom; at (5,17) and (6,18) two OF THE SAME SPECIES, pale cream with
  ringed tails — one larger and darker sitting, one smaller and paler trotting RIGHT.
- THE MAJESTIC CREATURE at (10,20)-(11,21): TWO TILES of ground at rest, tall and striking — a
  slender-legged stag-like creature with a deep amber coat, a mane of long pale fur and broad branching
  antlers. Standing calmly in the meadow FACING LEFT, head raised. Its rune on its shoulder.
"""

KEY = "p1-campagne-v4"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P1}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

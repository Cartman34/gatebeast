#!/usr/bin/env python3
"""Plates P1 and P4, third pass.

Corrections carried in, each one traced to what went wrong:
- edge connections restated as the FIRST thing to draw, with the exact tile and an explicit "must touch
  the edge" instruction — the previous prompt buried them among the paths and neither was drawn;
- the marsh regains its greenery: the previous prompt said "plain water elsewhere", which impoverished the
  plate; reed beds, floating weed and bank vegetation are now specified generously;
- no building narrower than eight tiles;
- every creature near water states its relation to it: under the surface, swimming at the surface, legs in
  the water touching the bottom, on the bank;
- the majestic creature covers two tiles of ground at rest — remarkable by bearing, not by size.
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
    "STYLE REFERENCE — ./da-b4-r15-scene.png is the exact target. Reproduce ITS rendering with no "
    "deviation: same modelling of volumes, same crisp two-band cel shading, same frank saturated colours, "
    "same amount of surface detail, same degree of stylisation. PEOPLE AND CREATURES ARE RENDERED IN "
    "EXACTLY THAT SAME STYLE. Take ONLY the style from it; the composition below applies."
)

SCALE = """
FRAME AND SCALE — the image is 1536 x 1152 pixels for a grid of 32 columns by 24 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row), origin
(1,1) top left.

CHECK THESE FIRST — they have been wrong before:
- An adult human is 2 metres tall: 2 TILES, about 96 PIXELS on this image, standing on ONE tile of ground.
- A door is at least 2.5 tiles high, about 120 PIXELS, and one tile wide.
- A dwelling covers at least 12 by 10 tiles — about 576 by 480 PIXELS, more than a third of the image
  width — and is NEVER narrower than 8 tiles in its smallest dimension. No two-metre-wide houses.
- Footprints are filled to their edges, never spilling sideways or downwards onto neighbouring tiles. Only
  height rises above the footprint, hiding what is behind.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. Bright
image, frank saturated colours — never muted, greyed or washed out. No deep shadow. Perfectly sharp edge to
edge.

COHERENCE — nothing ends in the void. A walkway lands on ground or on a building; a door opens onto an
access at the same ground level; a boat is moored or beached.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, boats or props. Ground
dressing is free but stays sparse.

NO REAL ANIMALS EXIST — no birds, ducks, herons, frogs, fish, dogs, cattle or insects. Everything alive
that is not human is an invented CREATURE wearing a rune. A creature may take inspiration from anything,
real or fantastical, but is never a real animal recoloured, and none has a human face. Two creatures of
one species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body. It
GLIMMERS FAINTLY, casts no light, has no halo; in daylight it reads as a marking slightly brighter than
the skin. About a QUARTER OF A TILE, roughly 12 pixels. No two share a rune shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair. Ages,
builds and genders vary.

No text, no interface, no logos, no grid lines.
"""

P1 = """
PLATE P1 — WOODED COUNTRYSIDE. Biome: rolling cultivated land, hedged fields, orchards, meadows, copses of
broadleaf trees, soft green tones.

DRAW THESE TWO EDGE EXITS FIRST — they matter more than anything else on this plate, and both were missing
last time:
1. A DIRT ROAD, one tile wide, running along ROW 16 and REACHING THE RIGHT EDGE OF THE IMAGE at (32,16).
   The road must be visible touching the right border, cut off by it, not stopping short.
2. A DIRT ROAD, one tile wide, running down COLUMN 12 and REACHING THE BOTTOM EDGE OF THE IMAGE at
   (12,24). It must be visible touching the bottom border, cut off by it, not stopping short.

OTHER PATHS — a branch climbs from (8,16) to (8,12) to the farmhouse door; one from (22,16) to (22,11) to
the mill door; one from (17,16) to (17,20) to the cottage door.

WATER — a brook enters at (28,1), runs down to (28,13), left along row 13 to (20,13), then down to (20,24),
flowing that way. A STONE BRIDGE at (20,16)-(21,16) carries the main road over it, both ends on the road.

BUILDINGS
- FARMHOUSE at (2,2)-(13,11): twelve by ten, stone and timber, tiled roof, chimney, door on its lower side
  at (8,11), 2.5 tiles high. State: worn, cared for.
- BARN at (15,3)-(24,9): ten by seven, red-boarded, double doors at (19,9) three tiles high, hayloft above.
- WINDMILL at (26,4)-(31,10): a round stone mill with four sails, door at (28,10).
- COTTAGE at (14,19)-(23,24): ten by six visible, thatched, door on its upper side at (17,19), 2.5 tiles
  high.

FIELDS AND ORCHARD — a MIXED ORCHARD at (24,17)-(31,23), all adult, each tree a different height and
crown: two apple trees at 80% fruit, one pear at 50%, one plum at 30%, one cherry in blossom without
fruit, one quince at 20%. A hedged vegetable plot at (2,12)-(7,15), well kept, half its rows planted. A
ripe wheat field at (26,11)-(31,15). Hedgerows along (2,16)-(7,16) and (14,12)-(19,12).

VEGETATION — one broad old oak, dense, at (10,18); three slim birches at (3,18), (15,14), (30,2); two dark
firs at (1,8) and (31,20). Meadow grass elsewhere, plain, dressing sparse.

OBJECTS — three haystacks of differing sizes at (25,10), (27,16), (29,16); a stone well at (14,10); a cart
half loaded with sacks at (10,15); a full water trough at (16,10).

INHABITANTS
- (9,13) a farmer in his forties, deep brown skin, forking hay, FACING RIGHT.
- (14,16) a woman in her thirties, East Asian features, carrying a basket of apples, walking LEFT.
- (28,11) a miller, pale skin, grey hair, in the mill doorway FACING DOWN, a flour sack at his feet.
- (18,16) and (19,16) two children of different origins running RIGHT along the road.
- CREATURES, each one tile, each with its rune: at (24,16) a russet fox-like creature walking RIGHT; at
  (26,20) a stocky mossy-backed creature asleep under an orchard tree; at (21,14) a long-legged creature
  ON THE BANK of the brook, FACING LEFT, head lowered to drink, its front feet IN THE SHALLOW WATER
  touching the bottom; at (5,17) and (6,18) two OF THE SAME SPECIES, pale cream with ringed tails — one
  larger and darker sitting, one smaller and paler trotting RIGHT.
- THE MAJESTIC CREATURE at (10,20)-(11,21): TWO TILES of ground at rest, but tall and striking — a
  slender-legged stag-like creature with a deep amber coat, a mane of long pale fur and broad branching
  antlers rising well above it. Standing calmly in the meadow FACING LEFT, head raised. Its rune, a single
  glimmering stroke, sits on its shoulder.
"""

P4 = """
PLATE P4 — MARSH. Biome: a LUSH flat wetland — shallow water and mud threaded by DENSE reed beds, many
twisted willows and alders, floating weed over most still water, marsh grasses on every bank, thin ground
mist. This plate must feel GREEN and OVERGROWN, never bare: open water is the exception, vegetation the
rule.

DRAW THESE TWO EDGE CONNECTIONS FIRST — both were missing last time:
1. A PLANK WALKWAY, one tile wide, running along COLUMN 12 and REACHING THE TOP EDGE OF THE IMAGE at
   (12,1). It must be visible touching the top border, cut off by it, not stopping short. Its last four
   tiles run over firm ground: this is where the countryside road becomes a walkway.
2. A PLANK WALKWAY, one tile wide, running along ROW 12 and REACHING THE RIGHT EDGE OF THE IMAGE at
   (32,12). It must be visible touching the right border, cut off by it.

OTHER WALKWAYS — from (12,12) the walkway continues down to (12,20); a branch runs from (12,8) left to
(5,8); another from (20,12) down to (20,20). State: worn, a few boards replaced, rope handrail on the
water side. No branch ends in water.

WATER — shallow water and mud flats between the vegetation, in irregular pools linked by slow channels
draining from (30,3) towards (4,22), the current shown by bent reeds and drifting weed. Duckweed covers
most of the quiet pools.

BUILDINGS — square to the grid, never at an angle:
- STILT HOUSE at (2,2)-(13,11): twelve by ten, raised on stout stilts above the water, reed thatch, a
  plank veranda on its lower side, door at (7,11) 2.5 tiles high reached by the walkway branch, green
  algae on every post. State: worn.
- SECOND STILT HOUSE at (21,15)-(31,23): eleven by nine, visibly different — plank walls, single-slope
  roof, an outside stair on its left side landing on the walkway at (20,20).
- FISH DRYING RACK at (15,6)-(18,8): an open timber frame, half full.

VEGETATION — ABUNDANT, this is the point of the plate: twisted willows, old, dense, trailing into the
water at (4,17), (8,4), (17,19), (24,4), (29,20), each a different girth and lean; black alders standing
in shallow water at (2,13), (9,21), (16,16), (26,10), (30,6); DENSE REED BEDS filling the water edges
across at least a third of the plate; marsh grass tufts along every bank; water lilies on two pools; moss
on the walkway posts.

OBJECTS — a flat-bottomed punt moored at (14,13), a pole across it; an older punt beached in the mud at
(7,22); wicker traps half submerged at (17,17) and (27,7); mooring stakes with wound rope at (14,14) and
(21,20).

INHABITANTS
- (10,8) a lean young peat cutter, dark skin, close-cropped hair, rolled trousers, a cutting spade over
  his shoulder, walking LEFT along the branch walkway, FACING LEFT.
- (16,12) a wiry woman in her forties, tanned skin, wide straw hat, oiled coat, hauling a dripping wicker
  trap, standing on the walkway FACING RIGHT.
- (20,18) a child of about nine, brown skin, bare feet, crouched at the walkway edge FACING DOWN, peering
  into the water.
- CREATURES, each with its rune, and each with its relation to the water stated:
  - (6,15) a long-limbed pale creature WADING, its legs IN THE WATER touching the bottom, water up to its
    knees, FACING RIGHT, head lowered.
  - (25,11) a round mottled creature SUBMERGED except for its back and eyes, which break the surface.
  - (28,17) a slender creature with a paddle tail SWIMMING AT THE SURFACE, moving LEFT, its body half in
    the water, ripples spreading behind it.
  - (18,21) and (19,22) two OF THE SAME SPECIES, smooth olive skin with fringed crests — one large and
    dark hunched ON a mossy stump above the water, one small and pale sitting ON THE MUD BANK.
- THE MAJESTIC CREATURE at (7,3)-(8,4): TWO TILES of ground, standing in shallow water with its long stilt
  legs IN THE WATER touching the bottom — a tall heron-like being, pale grey-blue, a wide fan of
  translucent membranes along its back catching the light, its head crowned with a curved crest. Standing
  motionless FACING RIGHT. Its rune, a single glimmering stroke, at the base of its neck.
"""

PLATES = {"p1-campagne-v3": P1, "p4-marais-v3": P4}

arguments = []
for key, plate in PLATES.items():
    prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{plate}"
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/planche-{key}.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

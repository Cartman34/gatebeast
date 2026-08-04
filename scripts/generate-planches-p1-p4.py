#!/usr/bin/env python3
"""Plates P1 (countryside) and P4 (marsh), recomposed.

New in this pass: a majestic rare creature on each plate, every edge connection stated with its row or
column and its material, building sizes given in tiles AND in pixels because tile counts kept being
ignored, a busyness range rather than a ceiling, and — for the marsh — no real animals, no diagonal
buildings, no one-tile-wide houses.

Previous images are kept; these are written under new names.
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
    "STYLE REFERENCE — ./da-b4-r15-scene.png is the exact target. Reproduce ITS rendering with no "
    "deviation: same modelling of volumes, same crisp two-band cel shading, same frank saturated colours, "
    "same amount of surface detail, same degree of stylisation. PEOPLE AND CREATURES ARE RENDERED IN "
    "EXACTLY THAT SAME STYLE. Take ONLY the style from it; the composition below applies."
)

SCALE = """
FRAME AND SCALE — the image is 1536 x 1152 pixels for a grid of 32 columns by 24 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row), origin
(1,1) top left.

THE SCALE HAS BEEN WRONG EVERY SINGLE TIME. Check these before anything else:
- An adult human is 2 metres tall: 2 TILES HIGH, so about 96 PIXELS TALL on this image, standing on ONE
  tile of ground.
- A door is at least 2.5 tiles high — about 120 PIXELS — and one tile wide. If a person cannot walk
  through it, the building is wrong.
- A family dwelling covers at least 12 by 10 tiles — that is about 576 by 480 PIXELS of ground, more than
  a third of the image width. Anything smaller is a shed, not a home.
- Footprints are filled to their edges and never spill sideways or downwards onto neighbouring tiles. Only
  height rises above the footprint, hiding what is behind.
- EVERYTHING IS SQUARE TO THE GRID AXES. No building, fence or walkway is ever set at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point.

LIGHT — sun from the UPPER LEFT, every shadow falling to the LOWER RIGHT, simple and soft-edged, one per
object. Bright image, frank saturated colours, no deep shadow, no murk, no washed-out greys. Perfectly
sharp edge to edge.

THE WORLD HAS LIVED — weathered wood, moss and lichen at the foot of walls. WATER FLOWS: oriented ripples
show its direction.

COHERENCE — nothing ends in the void; a walkway lands on ground or on a building, a door opens onto an
access, a boat is moored or beached. Ground levels are consistent: an entrance is at the level of what
leads to it.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, boats or props. Only sparse
ground dressing is free.

NO REAL ANIMALS EXIST IN THIS WORLD — no birds, ducks, herons, frogs, dogs, cattle, insects or fish.
Everything alive that is not human is an invented CREATURE wearing a rune. A creature may take inspiration
from anything, real or fantastical, but is never a real animal recoloured, and none has a human face. Two
creatures of one species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body. It
GLIMMERS FAINTLY, casting no light and no halo; in daylight it reads as a marking slightly brighter than
the skin. About a QUARTER OF A TILE — roughly 12 pixels. No two creatures share a rune shape. Humans wear
none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair.
Ages, builds and genders vary.

No text, no interface, no logos, no grid lines.
"""

P1 = """
PLATE P1 — WOODED COUNTRYSIDE. Biome: rolling cultivated land, hedged fields, orchards, meadows, copses of
broadleaf trees, soft green tones.

BUSYNESS RANGE for this biome: fairly rich. Roughly seven tiles in ten should carry something — hedges,
crops, trees, buildings — while meadows stay plain and unbroken. Neither empty nor cluttered.

EDGE CONNECTIONS — both touch the very edge squarely, one tile wide, packed earth for their last four
tiles:
- a DIRT ROAD leaves at the RIGHT EDGE on ROW 16, heading to the town.
- a DIRT ROAD leaves at the BOTTOM EDGE on COLUMN 12, heading down to the marsh.

PATHS — the main dirt road runs along row 16 from (1,16) to (32,16). A branch runs from (12,16) down to
(12,24) to reach the bottom edge. A branch climbs from (8,16) to (8,11) to the farmhouse door, another
from (22,16) to (22,10) to the mill door, another from (17,16) to (17,20) to the cottage door.

WATER — a brook enters at (28,1), runs down to (28,13), then left along row 13 to (20,13), then down to
(20,24), flowing in that direction. Crossed at (20,16)-(21,16) by a small STONE BRIDGE whose both ends
land on the main road.

BUILDINGS
- FARMHOUSE at (2,2)-(13,11): twelve tiles by ten, a stone and timber dwelling with a tiled roof and a
  chimney, door on its lower side at (8,11), two and a half tiles high, state: worn and cared for.
- BARN at (15,3)-(24,9): ten by seven, red-boarded, wide double doors on its lower side at (19,9) three
  tiles high, hayloft opening above, state: weathered.
- WINDMILL at (26,4)-(31,10): a round stone mill with four sails, door at (28,10).
- COTTAGE at (12,20)-(23,24): twelve by five visible, the rest running off the bottom edge, thatched roof,
  door on its upper side at (17,20), two and a half tiles high.

FIELDS AND ORCHARD — a MIXED ORCHARD at (24,17)-(31,23), all adult, each tree a different height and
crown: two apple trees at 80% fruit, one pear at 50%, one plum at 30%, one cherry in blossom with no
fruit, one quince at 20%. A hedged vegetable plot at (2,12)-(7,15), well kept, half its rows planted. A
ripe wheat field at (26,11)-(31,15). Hedgerows along (2,16)-(7,16) and (14,12)-(19,12).

VEGETATION — one broad old oak, dense, at (10,18); three slim birches at (3,18), (15,14), (30,2); two dark
firs at (1,8) and (31,20). Plain grass elsewhere, dressing sparse.

OBJECTS — three haystacks of differing sizes at (25,10), (27,16), (29,16); a stone well at (14,10); a
wooden cart half loaded with sacks at (10,15); a water trough, full, at (16,10).

INHABITANTS
- (9,13) a farmer in his forties, deep brown skin, forking hay, FACING RIGHT.
- (14,16) a woman in her thirties, East Asian features, carrying a basket of apples, walking LEFT.
- (28,11) a miller, pale skin, grey hair, standing in the mill doorway FACING DOWN, a flour sack at his
  feet.
- (18,16) and (19,16) two children of different origins running RIGHT along the road.
- CREATURES, four ordinary ones, each one tile and each with its rune: at (24,16) a russet fox-like
  creature walking RIGHT; at (26,20) a stocky mossy-backed creature asleep under an orchard tree; at
  (21,14) a long-legged wading creature drinking from the brook bank, FACING LEFT; and at (5,17) and
  (6,18) two OF THE SAME SPECIES — pale cream, ringed tails — one larger and darker sitting, one smaller
  and paler trotting RIGHT.
- THE MAJESTIC CREATURE at (14,19)-(17,22): a rare and imposing creature, FOUR TILES across and three
  tall, twice the height of a man — a great antlered quadruped with a deep amber coat, a mane of long
  pale fur, and broad branching horns. It stands calmly in the meadow FACING LEFT, head raised. Its rune,
  a single luminous stroke, sits on its shoulder. It is remarkable but does not dominate the image.
"""

P4 = """
PLATE P4 — MARSH. Biome: flat still wetland, shallow open water and grey mud flats threaded by reed beds,
twisted willows and alders, floating green weed, thin ground mist.

BUSYNESS RANGE for this biome: rich. Reeds, water and vegetation cover most of the plate, but keep open
water and mud flats plain — the busyness must come from a few dense reed beds, not from clutter
everywhere.

EDGE CONNECTIONS — both touch the very edge squarely, one tile wide, plank walkway for their last four
tiles:
- a PLANK WALKWAY enters at the TOP EDGE on COLUMN 12, arriving from the countryside above.
- a PLANK WALKWAY leaves at the RIGHT EDGE on ROW 12, heading towards the cliff.

WALKWAYS — the walkway runs from (12,1) down to (12,12), then right along row 12 to (32,12). A branch runs
from (12,8) left to (5,8) and another from (20,12) down to (20,20). State: worn, a few boards replaced,
rope handrail on the water side. No branch ends in water.

WATER — still shallow water and mud flats cover most of the plate in irregular pools linked by slow
channels; the main channel drains from (30,3) towards (4,22), flowing DOWN-LEFT, its current shown by bent
reeds and drifting weed. Duckweed on the quiet pools.

BUILDINGS — all SQUARE to the grid, never at an angle:
- STILT HOUSE at (2,2)-(13,11): twelve tiles by ten, raised on stout wooden stilts above the water, reed
  thatch, a plank veranda on its lower side, door at (7,11) two and a half tiles high reached by the
  walkway, green algae marking the waterline on every post. State: worn.
- SECOND STILT HOUSE at (21,15)-(31,23): eleven by nine, visibly different — plank walls, a single-slope
  roof, an outside stair on its left side landing on the walkway branch at (20,20).
- FISH DRYING RACK at (15,6)-(18,8): an open timber frame, half full of drying racks.

VEGETATION — twisted willows, old, dense, trailing into the water at (4,17), (24,4), (29,20), each a
different girth and lean. Black alders standing in shallow water at (2,13), (9,21), (30,9). Dense reed
beds along the water edges at eight scattered points. Plain water elsewhere.

OBJECTS — a flat-bottomed punt moored at (14,13), a pole across it; a second, older punt beached in the
mud at (7,22); wicker traps half submerged at (17,17) and (27,7); mooring stakes with wound rope at
(14,14) and (21,20).

INHABITANTS
- (10,8) a lean young peat cutter, dark skin, close-cropped hair, rolled trousers, a cutting spade over
  his shoulder, walking LEFT along the branch walkway, FACING LEFT.
- (16,12) a wiry woman in her forties, tanned skin, wide straw hat, oiled coat, hauling a dripping wicker
  trap, standing FACING RIGHT.
- (20,18) a child of about nine, brown skin, bare feet, crouched at the walkway edge FACING DOWN, peering
  into the water.
- CREATURES, four ordinary ones, each with its rune: at (6,15) a long-limbed pale creature with webbed
  feet wading, FACING RIGHT, head lowered; at (25,11) a round mottled creature half sunk in mud, only its
  back and eyes above water; at (28,17) a slender creature with a paddle tail swimming LEFT; and at
  (17,21) and (18,22) two OF THE SAME SPECIES — smooth olive skin, fringed crests — one large and dark
  hunched on a stump, one small and pale sitting in the mud.
- THE MAJESTIC CREATURE at (7,3)-(11,7): a rare and imposing creature, FIVE TILES across — a great
  heron-like being standing in the shallows on long stilt legs, its body pale grey-blue, a wide fan of
  translucent membranes along its back catching the light, its head crowned with a curved crest. It stands
  motionless FACING RIGHT. Its rune, a single luminous stroke, sits at the base of its neck.
"""

PLATES = {"p1-campagne-v2": P1, "p4-marais-v2": P4}

arguments = []
for key, plate in PLATES.items():
    prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{plate}"
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/planche-{key}.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

#!/usr/bin/env python3
"""Plates P1 (countryside) and P2 (market town), recomposed with every rule established since their first
attempt.

What changes from the first attempt: tile-by-tile composition instead of prose, dwellings sized for what
they hold, a stated condition on every living or perishable element, mixed fruit species, real animals
without runes, individuals of one species that differ, at least three distinct human origins, runes that
glimmer rather than shine, figures rendered in the very same style as the scenery, and a connecting road
whose width and material are specified on both sides.

The previous images are kept: these are written under new file names.
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
    "same amount of surface detail, same degree of stylisation. PEOPLE, ANIMALS AND CREATURES ARE RENDERED "
    "IN EXACTLY THAT SAME STYLE — same volume, same shading, same light. A scene whose figures are drawn "
    "differently from its scenery is wrong. Take ONLY the style from that image; the layout below applies."
)

COMMON = """
FRAME — 1536 x 1152 pixels for a grid of 32 columns by 24 rows of square tiles. Do NOT draw the grid.
Positions are written (column,row), origin (1,1) top left. A standing human is exactly ONE tile tall — the
reference scale. Footprints are the ground covered: FILLED to their edges, never spilling sideways or
downwards onto neighbouring tiles; only height rises above the footprint on screen, hiding what is behind.
Everything is SQUARE to the grid axes. Nothing sits at an angle.

BUILDINGS ARE SIZED FOR WHAT THEY HOLD — a dwelling has a kitchen, a living room and at least one bedroom,
so it covers around ten tiles by eight, more for an inn or a hall. Only sheds and workshops are small.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point. Roofs and treetops seen
from above.

LIGHT — sun from the UPPER LEFT, every shadow falling to the LOWER RIGHT. Shadows are SIMPLE: plain,
soft-edged, one per object. Bright image, frank clear colours, no deep shadow, no murk. Perfectly sharp
edge to edge — no blur, no haze, no depth of field.

THE WORLD HAS LIVED — weathered wood, moss and lichen at the foot of walls, plants reclaiming corners.

WATER FLOWS — oriented ripples, eddies behind stones, grass bent by the current.

COHERENCE — nothing ends in the void. A bridge lands on a path or is broken and the path stops with it. A
door opens onto an access. A boat is moored or beached.

PEOPLE — humans of real humanity: AT LEAST THREE CLEARLY DIFFERENT ORIGINS are visible, with genuinely
different skin tones, features and hair — not shades of one. Ages and builds vary. Both genders.

REAL ANIMALS — ordinary animals live here as well as creatures: they wear NO RUNE, which is what tells
them apart at a glance.

CREATURES — original invented creatures, never a real animal recoloured; a real animal may inspire a
silhouette, nothing more. None has a human face. TWO CREATURES OF THE SAME SPECIES ARE NOT IDENTICAL:
size, tint, build, age and posture differ, as between two dogs of one breed.

RUNES — each creature wears ONE rune: ONE single continuous stroke, ONE colour, following the curve of the
body like a natural marking. It GLIMMERS FAINTLY — the dull sheen of a material that glows softly in the
dark, never a lamp: it casts no light on the body or ground, has no halo, and in daylight reads as a
marking slightly brighter than the skin. It fits in about a QUARTER OF A TILE — an absolute size, so it
looks tiny on a large creature. No two creatures wear the same rune shape. Humans and animals wear none.

No text, no interface, no logos, no grid lines.
"""

P1 = """
PLATE P1 — WOODED COUNTRYSIDE. Biome: rolling cultivated land, hedged fields, orchards, meadows, copses of
broadleaf trees, soft green tones.

EDGE CONNECTION — a DIRT ROAD, ONE tile wide, packed earth, leaves at the RIGHT EDGE on row 16, touching
the very edge squarely, continuing towards the town. The last four tiles before the edge are plain packed
earth, unchanged, so the two plates meet cleanly.

PATHS — the dirt road runs along row 16 from (1,16) to (32,16). A branch climbs from (8,16) up to (8,6) to
serve the farm, another from (20,16) up to (20,7) to serve the mill, another from (12,16) down to (12,22)
to serve the cottage.

WATER — a brook from (26,1) down to (26,13), then left along row 13 to (16,13), then down to (16,24),
flowing DOWNSTREAM in that direction. Crossed at (16,16)-(17,16) by a small STONE BRIDGE, both ends
landing on the dirt road. A pond at (22,18)-(27,22), fed by the brook, still, with lily pads on a third of
its surface.

BUILDINGS
- FARMHOUSE at (3,3)-(12,10): a large stone and timber dwelling, ten by eight, tiled roof, chimney, door
  on its lower side at (8,10). State: worn, cared for.
- BARN at (14,3)-(21,8): a big red-boarded barn, wide double doors on its lower side at (17,8), hayloft
  opening above, state: weathered. Fenced yard at (14,9)-(21,12).
- WINDMILL at (24,3)-(29,9): a round stone mill with four turning sails, door at (26,9), state: in use.
- COTTAGE at (4,18)-(13,24): a thatched dwelling, ten by seven, door at (9,18) opening onto its path,
  state: worn, flower boxes at the windows.

ORCHARD AND FIELDS — an orchard at (22,9)-(30,15) of DELIBERATELY MIXED SPECIES, all adult: two apple
trees at 80% fruit, one pear tree at 50% fruit, one plum tree at 30% fruit, one cherry tree in blossom
with no fruit, one quince tree at 20% fruit, each of a different height and crown shape. A hedged
vegetable plot at (2,12)-(7,15), well kept, half its rows planted. A wheat field at (28,17)-(32,23),
ripe, golden.

VEGETATION — a broad old oak, dense foliage, at (18,20); three slim birches at (2,17), (14,14), (31,4);
two dark firs at (30,10), (1,7); a hazel hedge along (2,11)-(8,11).

OBJECTS — three haystacks of differing sizes at (26,16), (28,15), (30,14); a stone well, in use, at
(19,12); a wooden cart, half loaded with sacks, at (12,11); a water trough, full, at (16,9).

INHABITANTS
- (9,11) a farmer in his forties, deep brown skin, forking hay, FACING RIGHT.
- (13,17) a woman in her thirties, East Asian features, carrying a basket of apples, walking LEFT, FACING
  LEFT.
- (26,10) a miller, pale skin, grey hair, standing in the mill doorway, FACING DOWN, a flour sack at his
  feet.
- (17,17) and (18,17) two children of visibly different origins running RIGHT along the road, FACING
  RIGHT, one ahead of the other.
- REAL ANIMALS: four cows of differing markings and sizes grazing in the yard at (15,10)-(20,12), heads
  down; a brown dog trotting LEFT at (11,16); six hens scattered around (6,11); five ducks on the pond at
  (24,20), three swimming, two dabbling; a cat asleep on the cottage doorstep at (9,17).
- CREATURES, four different species, each with its rune: at (21,16) a russet fox-like creature with large
  ears walking RIGHT along the road; at (25,14) a stocky creature with a mossy back asleep under an
  orchard tree, eyes closed; at (30,20) a long-legged wading creature at the pond edge, FACING LEFT, head
  lowered to drink from the bank; at (5,16) and (6,17) two creatures OF THE SAME SPECIES — pale cream,
  ringed tails — one larger and darker sitting FACING RIGHT, the other smaller and paler mid-trot moving
  RIGHT.
"""

P2 = """
PLATE P2 — MARKET TOWN. Biome: a built-up market town, paved ground almost everywhere, walled gardens
between houses, a few planted trees, warm stone and timber tones.

EDGE CONNECTION — a DIRT ROAD, ONE tile wide, packed earth, ENTERS at the LEFT EDGE on row 16, touching
the very edge squarely, arriving from the countryside. It stays packed earth for its first four tiles and
only becomes cobbled at (5,16).

PATHS — the main street runs along row 16 from (1,16) to (32,16): packed earth to (4,16), cobbles from
(5,16) onwards. A cobbled street runs from (12,16) up to (12,2), another from (24,16) up to (24,4), a
flagstone lane from (18,16) down to (18,24). Every door below opens onto one of these.

SQUARE — an open cobbled square at (13,7)-(23,15), with a round stone FOUNTAIN at (17,10)-(19,12), water
running, its basin two thirds full.

BUILDINGS — every one visibly different in width, roof shape, colour and materials:
- COVERED MARKET HALL at (13,2)-(23,6): a timber-framed open hall under a blue tiled roof, stalls beneath
  it, three quarters full of produce.
- SMITHY at (3,3)-(9,8): stone workshop, forge glowing, wide opening at (6,8), anvil outside, state: in
  use, soot-marked.
- BAKERY at (25,3)-(31,9): a dwelling with a domed bread oven on its side, ten by seven counting the
  living quarters, door at (28,9), state: worn.
- POTTER'S WORKSHOP at (25,11)-(30,15): open-fronted, drying racks half full of pots, door at (27,15).
- INN at (2,18)-(12,24): a large two-storey dwelling with a hanging sign, eleven by seven, door at (7,18),
  lit windows, state: well kept.
- TERRACED HOUSES at (19,18)-(32,24): four dwellings side by side, each ten tiles deep and of a different
  width, roof colour and material — one tiled orange, one slate grey, one thatched, one shingled — each
  with its own door on row 18 and a walled garden behind.

VEGETATION — two lime trees, adult, dense foliage, at (14,17) and (22,17); a climbing vine, well kept, on
the inn wall; window boxes in flower on five different houses; a small kitchen garden at (30,20)-(32,23),
half planted.

OBJECTS — market stalls under the hall, two of them with striped awnings of different colours; stacked
crates, half full, at (15,6); barrels at (10,9); a notice board, weathered, at (16,16); washing lines with
laundry behind the terraced houses; a hand cart, empty, at (21,16).

INHABITANTS
- (6,9) a blacksmith at the anvil, dark skin, leather apron, hammer raised, FACING RIGHT.
- (28,10) a baker, pale freckled skin, setting loaves on a stall, FACING DOWN.
- (27,14) a potter at the wheel, East Asian features, seated, FACING LEFT.
- (15,13) and (16,13) a merchant and a customer standing FACE TO FACE at a stall, in conversation, of
  different origins, the merchant gesturing.
- (18,13) a woman drawing water at the fountain, South Asian features, FACING UP.
- (21,14) a child running LEFT across the square, FACING LEFT.
- (11,16) a guard leaning on a spear at the street corner, FACING DOWN.
- REAL ANIMALS: a dog asleep in the sun at (13,16); two cats, one on a wall at (25,17), one crossing the
  square at (20,12); five pigeons around the fountain at (17,13); a horse harnessed to a cart at (23,16).
- CREATURES, four different species, each with its rune, all domesticated town creatures: at (9,16) a
  sturdy creature harnessed to a small cart, walking RIGHT; at (29,16) a small creature asleep on a warm
  doorstep, curled up; at (14,4) a winged creature perched on the market hall roof, FACING DOWN over the
  square; at (24,13) and (25,13) two creatures OF THE SAME SPECIES — short green fur, crested backs — one
  older and larger being fed at a stall FACING UP, the other younger and paler sitting FACING LEFT.
"""

PLATES = {"p1-campagne-v2": P1, "p2-bourg-v2": P2}

arguments = []
for key, plate in PLATES.items():
    prompt = f"{STYLE}\n\n{ANCHOR}\n{COMMON}\n{plate}"
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/planche-{key}.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

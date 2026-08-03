#!/usr/bin/env python3
"""Plate P4 marsh, fourth pass — P4 alone.

The third pass was right on structure (edge connections drawn, buildings correct, creatures stating their
relation to the water, greenery back) and wrong on measurement: 89 % busy tiles against 74 in the
reference, 20.6 % dark against 9, saturation down to 59.5 %. Both causes were in the instructions, not in
the production, and both are now fixed in the design itself:

- DRESSING IS NUMBERED. "Sparse" alone produced either bare ground or a continuous carpet. The rule is now
  a proportion: at most one tile in five carries dressing, the other four stay plain.
- WATER IS CLEAR AND DARKNESS IS CAPPED. Brown water over half the plate sank luminance, dark share and
  saturation at once. Water is now pale turquoise and water-green with the bottom visible through it, no
  ground mist, and no more than one tile in seven may be dark, water included.

Everything else is carried over unchanged from the third pass: it was not faulted.
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

TWO MEASURED LIMITS — these two were broken last time and they decide whether the plate is accepted:
1. DRESSING: grass tufts, flowers, pebbles, moss patches, fallen leaves, floating weed. AT MOST ONE TILE IN
   FIVE carries any dressing at all. The other four tiles in five are PLAIN UNBROKEN SURFACE — flat colour,
   no texture, no scatter. Do not carpet the ground. Wide plain areas are the style, not a mistake.
2. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark, and WATER COUNTS. No deep shadow, no dark
   undergrowth mass, no black water. If in doubt, make it lighter.

COHERENCE — nothing ends in the void. A walkway lands on ground or on a building; a door opens onto an
access at the same ground level; a boat is moored or beached.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, boats or props.

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

P4 = """
PLATE P4 — MARSH. Biome: a bright flat wetland of CLEAR SHALLOW WATER threaded by walkways, reed beds and
twisted trees.

THE WATER IS THE SUBJECT OF THIS PASS. It is CLEAR AND LIGHT: pale turquoise and water-green, the sandy
mud bottom VISIBLE THROUGH IT everywhere, gentle light rippling on the bottom. NOT brown, NOT olive, NOT
murky, NOT dark, NOT reflective like a mirror. THERE IS NO MIST — no ground fog, no haze, no atmospheric
veil of any kind; the air is perfectly clear and the whole image is sharp. Floating weed appears on TWO
small pools only, never across the open water.

DRAW THESE TWO EDGE CONNECTIONS FIRST:
1. A PLANK WALKWAY, one tile wide, running along COLUMN 12 and REACHING THE TOP EDGE OF THE IMAGE at
   (12,1). It must be visible touching the top border, cut off by it, not stopping short. Its last four
   tiles run over firm ground: this is where the countryside road becomes a walkway.
2. A PLANK WALKWAY, one tile wide, running along ROW 12 and REACHING THE RIGHT EDGE OF THE IMAGE at
   (32,12). It must be visible touching the right border, cut off by it.

OTHER WALKWAYS — from (12,12) the walkway continues down to (12,20); a branch runs from (12,8) left to
(5,8); another from (20,12) down to (20,20). State: worn, a few boards replaced, rope handrail on the
water side. No branch ends in water.

WATER — clear shallow water and pale sand-mud flats between the vegetation, in irregular pools linked by
slow channels draining from (30,3) towards (4,22), the current shown by bent reeds and drifting weed.

BUILDINGS — square to the grid, never at an angle:
- STILT HOUSE at (2,2)-(13,11): twelve by ten, raised on stout stilts above the water, reed thatch, a
  plank veranda on its lower side, door at (7,11) 2.5 tiles high reached by the walkway branch, green
  algae on every post. State: worn.
- SECOND STILT HOUSE at (21,15)-(31,23): eleven by nine, visibly different — plank walls, single-slope
  roof, an outside stair on its left side landing on the walkway at (20,20).
- FISH DRYING RACK at (15,6)-(18,8): an open timber frame, half full.

VEGETATION — present and green, but COUNTED, and it stays within the one-tile-in-five dressing limit:
- twisted willows, old, dense, trailing into the water at (4,17), (8,4), (17,19), (24,4), (29,20), each a
  different girth and lean; their foliage is a LIGHT fresh green, never a dark mass;
- black alders standing in shallow water at (2,13), (9,21), (16,16), (26,10), (30,6);
- REED BEDS in FOUR distinct clumps only, at (3,6), (14,18), (22,8) and (27,21), each about three tiles
  across, upright and light green. Reeds do NOT line every bank and do NOT fill the water edges.
- water lilies on TWO pools only, around (10,15) and (25,18);
- marsh grass on the banks, but only where the dressing limit allows: most bank tiles are plain.

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
    knees, FACING RIGHT, head lowered. Its submerged legs are VISIBLE through the clear water.
  - (25,11) a round mottled creature SUBMERGED except for its back and eyes, which break the surface; its
    body is visible through the clear water.
  - (28,17) a slender creature with a paddle tail SWIMMING AT THE SURFACE, moving LEFT, its body half in
    the water, ripples spreading behind it.
  - (18,21) and (19,22) two OF THE SAME SPECIES, smooth olive skin with fringed crests — one large and
    dark hunched ON a mossy stump above the water, one small and pale sitting ON THE MUD BANK.
- THE MAJESTIC CREATURE at (7,3)-(8,4): TWO TILES of ground, standing in shallow water with its long stilt
  legs IN THE WATER touching the bottom — a tall wading being, pale grey-blue, a wide fan of translucent
  membranes along its back catching the light, its head crowned with a curved crest. Standing motionless
  FACING RIGHT. Its rune, a single glimmering stroke, at the base of its neck.
"""

KEY = "p4-marais-v4"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P4}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

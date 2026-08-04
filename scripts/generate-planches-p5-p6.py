#!/usr/bin/env python3
"""Plates P5 (clifftop) and P6 (beach), composed tile by tile, with measurable targets stated.

Everything established so far applies: one tile is one metre, an adult is two tiles tall on one tile of
ground, doors are at least two and a half tiles high, dwellings cover at least a hundred and twenty square
metres, no real animals exist, nothing is added beyond the composition except sparse ground dressing, and
the art direction is anchored to the retained image.

The measurable targets are given to the generator rather than kept for checking afterwards.
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
    "EXACTLY THAT SAME STYLE — same volume, same shading, same light. Take ONLY the style from it; the "
    "composition below applies."
)

TARGETS = """
MEASURABLE TARGETS — this image will be measured against the reference image and rejected if it misses
them:
- VISUAL BUSYNESS: about three quarters of the ground should read as calm, plain surface. Large unbroken
  areas of grass, sand or rock. Ground dressing — grass tufts, small flowers, pebbles — PUNCTUATES; it
  never carpets. When in doubt, put less.
- BRIGHTNESS: mean brightness close to 40% of full white, and NO MORE THAN one tile in seven reading as
  dark. No deep shadow, no murky corner.
- COLOUR: strong frank saturation, comparable to the reference. Never muted, greyed, dusty or washed out.
- SHARPNESS: perfectly sharp edge to edge. No blur, no haze, no depth of field.
"""

COMMON = """
FRAME AND SCALE — 1536 x 1152 pixels for a grid of 32 columns by 24 rows of square tiles. Do NOT draw the
grid. Positions are written (column,row), origin (1,1) top left.
- ONE TILE IS ONE METRE.
- AN ADULT HUMAN IS TWO METRES TALL: exactly TWO TILES HIGH on screen, standing on ONE tile of ground.
  This is the reference measure and it has drifted before — check it first.
- A door is at least TWO AND A HALF TILES high and one tile wide, or nobody can go through it.
- A dwelling covers at least 120 square metres of ground — twelve tiles by ten. A two-by-two building is
  four square metres: a shed, never a home.
- Footprints are the ground covered, FILLED to their edges, never spilling sideways or downwards onto
  neighbouring tiles. Only height rises above the footprint on screen, hiding what is behind.
- Everything is SQUARE to the grid axes. Nothing sits at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point. Roofs seen from above.

LIGHT — sun from the UPPER LEFT, every shadow falling to the LOWER RIGHT. Shadows are SIMPLE: plain,
soft-edged, one per object.

THE WORLD HAS LIVED — weathered wood, salt-stained stone, moss and lichen at the foot of walls.

WATER FLOWS — oriented ripples and foam show which way the water moves.

COHERENCE — nothing ends in the void. Stairs lead somewhere, a jetty is reached by a path, a boat is
moored or beached, a door opens onto an access.

EXHAUSTIVE — draw exactly what is listed below and NOTHING ELSE. No extra people, no extra buildings, no
extra boats, no invented props. Only sparse ground dressing is free.

NO REAL ANIMALS — this world has none. No birds, no gulls, no fish, no dogs, no insects. Everything alive
that is not human is a CREATURE, invented, and wears a rune. Creatures may draw inspiration from anything,
real or fantastical, but are never a real animal recoloured, and none has a human face. Two creatures of
the same species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body like a
natural marking. It GLIMMERS FAINTLY — the dull sheen of a material that glows softly in the dark, never a
lamp: no light cast on body or ground, no halo; in daylight it reads as a marking slightly brighter than
the skin. It fits in about a QUARTER OF A TILE. No two creatures share a rune shape. Humans wear none.

PEOPLE — AT LEAST THREE CLEARLY DIFFERENT ORIGINS, with genuinely different skin tones, features and hair.
Ages, builds and genders vary.

No text, no interface, no logos, no grid lines.
"""

P5 = """
PLATE P5 — CLIFFTOP. Biome: a windswept clifftop of cropped salt turf over pale rock, everything leaning
inland, a sheer drop to the sea along the right side.

TERRAIN — turf plateau from column 1 to column 24. The CLIFF EDGE runs vertically down column 25, and
beyond it, columns 26 to 32 are open sea seen from above, deep blue-green with slow swell and white foam
against the rock foot.

EDGE CONNECTION — a STAIRWAY CUT INTO THE CLIFF at (25,18)-(27,22), ONE tile wide, its steps worn hollow,
a rope handrail on iron rings. It descends and LEAVES at the RIGHT EDGE on row 20, touching the very edge
squarely, continuing down to the beach.

PATHS — a packed-earth track, one tile wide, runs from (1,10) right to (14,10), then down to (14,20), then
right to (24,20) where it meets the top of the cliff stairway. A grass trail branches from (14,14) left to
(4,14). Every door below opens onto one of these.

BUILDINGS
- LIGHTHOUSE at (19,3)-(23,7): a tapering whitewashed tower with a red lantern room, an external iron
  stair, salt-stained walls.
- KEEPER'S DWELLING at (6,2)-(17,11): twelve tiles by ten, a stone house with a slate roof and a chimney,
  door on its lower side at (11,11) standing two and a half tiles high, opening onto a short branch path
  down to the track on row 10. State: worn, well kept.
- FISHERMEN'S STORE at (3,16)-(9,21): a tarred timber building, seven by six, wide plank door at (6,21),
  two and a half tiles high, lobster pots stacked outside, roof held by weighted ropes. State: worn.

AMENITIES — a low dry-stone wall runs along (2,12)-(13,12), state: partly collapsed at its middle. Three
drying frames hung with nets, half full, at (10,16), (12,17), (11,19).

VEGETATION — sparse gorse bushes in yellow flower at (5,7), (8,20), (21,14), (23,10), each a different
size. Two wind-bent stunted pines, old, sparse foliage, at (16,19) and (22,21). Cropped salt turf
everywhere else, plain and unbroken, with only occasional small white flowers.

OBJECTS — an iron bollard with coiled rope at (24,19); a stack of three lobster pots at (7,22); a
weathered handcart, empty, at (13,13); a stone marker at (14,9).

INHABITANTS
- (19,9) the lighthouse keeper, a heavy-set man in his sixties, ruddy pale skin, thick knitted jumper and
  peaked cap, standing FACING DOWN, a brass lamp in hand.
- (11,18) a net mender, a woman in her fifties, dark skin, headscarf, sitting cross-legged FACING RIGHT, a
  net across her knees and a wooden needle in hand.
- (14,20) a young fisher, East Asian features, oilskin trousers and braces, walking RIGHT towards the
  stairway, FACING RIGHT, a crate on one shoulder.
- CREATURES, three different species, each with its rune: at (20,16) a broad woolly creature with flat
  horns, grazing the turf, FACING LEFT, head down; at (6,10) a slender long-tailed creature perched on the
  dry-stone wall, FACING RIGHT, watching the sea; at (23,6) and (24,7) two creatures OF THE SAME SPECIES —
  pale grey, wing-like membranes along the flanks — one larger and darker standing at the cliff edge
  FACING RIGHT, the other smaller and paler crouched low FACING UP, clearly two individuals.
"""

P6 = """
PLATE P6 — BEACH. Biome: a sheltered shore. Firm damp sand near the water, loose dunes inland held by
marram grass, a pebble bank, shallow foam, scattered rocks.

TERRAIN — the SEA occupies rows 1 to 6 across the whole width, seen from above, turquoise shallows
darkening outwards, gentle foam lines parallel to the shore, the water advancing DOWNWARDS onto the sand.
Firm damp sand from row 7 to row 14. Loose dry sand and low dunes from row 15 to row 24.

EDGE CONNECTION — a STAIRWAY CUT INTO ROCK enters at the LEFT EDGE on row 20, ONE tile wide, touching the
very edge squarely, arriving from the clifftop above. It descends to (4,20) where it meets the sand.

PATHS — a packed damp sand track, one tile wide, runs from (4,20) right to (26,20), with a branch up from
(12,20) to (12,10) reaching the jetty, and another from (20,20) up to (20,16).

BUILDINGS
- FISHERMEN'S DWELLING at (14,15)-(25,24): a driftwood and plank house, twelve tiles by ten, a wide
  veranda facing the sea, faded blue paint, door on its upper side at (19,15) standing two and a half
  tiles high, opening onto the branch path. State: weathered, sand drifted against its lower wall.
- BOAT SHELTER at (5,14)-(10,19): an open-fronted shelter of grey planks, its floor a slipway of
  half-buried timbers running down towards the water.
- JETTY at (11,7)-(13,14): a wooden jetty on piles reaching from the sand into the shallows, deck planks
  silvered by salt, iron mooring rings, a small hand crane at its seaward end.

VEGETATION — marram grass tufts along the dune crests at (2,22), (7,23), (16,22), (23,21), (29,23), each
of a different size, leaning inland. Two low tamarisks, adult, sparse grey-green foliage, at (27,17) and
(30,21). Nothing else growing: the sand stays plain and unbroken.

OBJECTS — a clinker-built boat beached on the sand at (8,21), paint flaked, oars stowed inside; a second
boat moored at the jetty at (13,9); four lobster pots stacked at (11,15); a net spread on a frame to dry,
half full of floats, at (17,13); a bleached driftwood log at (24,12); a pebble bank along (26,7)-(32,10).

INHABITANTS
- (12,12) a boat carpenter, Mediterranean features, sleeves rolled, kneeling on the jetty FACING DOWN, an
  adze in hand.
- (19,14) a shell gatherer, a teenage girl, South Asian features, linen dress kilted up, a woven basket on
  her hip, walking UP towards the house, FACING UP.
- (7,20) a fisher in his forties, deep brown skin, close-cropped grey hair, standing beside the beached
  boat FACING RIGHT, coiling a rope.
- CREATURES, three different species, each with its rune: at (22,9) a long-legged wading creature standing
  in the shallow foam, FACING LEFT, head lowered to the water; at (9,17) a round armoured creature with a
  ridged shell, half buried in the dry sand, FACING RIGHT, at rest; at (15,19) and (16,20) two creatures OF
  THE SAME SPECIES — sleek, sand-coloured, with fringed tails — one larger and darker running LEFT, the
  other smaller and paler sitting FACING LEFT, clearly two individuals.
"""

PLATES = {"p5-falaise": P5, "p6-plage": P6}

arguments = []
for key, plate in PLATES.items():
    prompt = f"{STYLE}\n\n{ANCHOR}\n{TARGETS}\n{COMMON}\n{plate}"
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/planche-{key}.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

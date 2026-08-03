#!/usr/bin/env python3
"""Plate P4 marsh, fifth pass — marry the gains of v4 with the greenery of the first pass.

What v4 proved and keeps: clear water, no mist, dark share under control, edge connections, buildings.
What v4 broke and this fixes, per the owner's definitions (now in the design):
- greenery as abundant as the FIRST marsh pass: more algae, more reeds, more plants, more mangrove
  trees, more tall trees. The one-in-five dressing cap starved a biome that lives on vegetation — it is
  lifted for plants here; the darkness cap (one tile in seven, water included) stays.
- frank saturated colours anchored on da-gb-b4v6-scene, the true background reference; the
  "if in doubt, make it lighter" line washed the plate out and is removed.
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
    "deviation: same modelling of volumes, same crisp two-band cel shading, same FRANK SATURATED COLOURS "
    "— rich greens, warm earth tones, vivid water — same amount of surface detail, same degree of "
    "stylisation, same overall density of vegetation. PEOPLE AND CREATURES ARE RENDERED IN EXACTLY THAT "
    "SAME STYLE. Take ONLY the style and richness from it; the composition below applies."
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
image, FRANK SATURATED COLOURS — rich, vivid, never muted, greyed, pastel or washed out. No deep shadow.
Perfectly sharp edge to edge.

ONE MEASURED LIMIT — DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark, and WATER COUNTS. No deep
shadow, no black water. Saturated does not mean dark: colours are rich AND bright.

COHERENCE — nothing ends in the void. A walkway lands on ground or on a building; a door opens onto an
access at the same ground level; a boat is moored or beached.

EXHAUSTIVE ON THE COUNTABLE — draw the listed people, creatures, buildings, boats and props and no extra
ones. Vegetation is specified generously below and must be abundant.

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
PLATE P4 — MARSH. Biome: a LUSH, GREEN, overgrown wetland of CLEAR water threaded by walkways, dense
reed beds, mangrove-like trees and tall twisted willows. Vegetation is the rule, open water the exception.

THE WATER IS CLEAR AND VIVID: a rich water-green and turquoise, the sandy mud bottom VISIBLE THROUGH IT,
gentle light rippling on the bottom. NOT brown, NOT murky, NOT dark — but SATURATED, never pale or milky.
THERE IS NO MIST — no ground fog, no haze; the air is perfectly clear and the whole image is sharp.

DRAW THESE TWO EDGE CONNECTIONS FIRST:
1. A PLANK WALKWAY, one tile wide, running along COLUMN 12 and REACHING THE TOP EDGE OF THE IMAGE at
   (12,1). It must be visible touching the top border, cut off by it, not stopping short. Its last four
   tiles run over firm ground: this is where the countryside road becomes a walkway.
2. A PLANK WALKWAY, one tile wide, running along ROW 12 and REACHING THE RIGHT EDGE OF THE IMAGE at
   (32,12). It must be visible touching the right border, cut off by it.

OTHER WALKWAYS — from (12,12) the walkway continues down to (12,20); a branch runs from (12,8) left to
(5,8); another from (20,12) down to (20,20). State: worn, a few boards replaced, rope handrail on the
water side. No branch ends in water.

WATER — clear vivid shallow water and mud flats between the vegetation, in irregular pools linked by slow
channels draining from (30,3) towards (4,22), the current shown by bent reeds and drifting weed.

BUILDINGS — square to the grid, never at an angle:
- STILT HOUSE at (2,2)-(13,11): twelve by ten, raised on stout stilts above the water, reed thatch, a
  plank veranda on its lower side, door at (7,11) 2.5 tiles high reached by the walkway branch, green
  algae on every post. State: worn.
- SECOND STILT HOUSE at (21,15)-(31,23): eleven by nine, visibly different — plank walls, single-slope
  roof, an outside stair on its left side landing on the walkway at (20,20).
- FISH DRYING RACK at (15,6)-(18,8): an open timber frame, half full.

VEGETATION — ABUNDANT AND GENEROUS, this is the point of the plate; it should read as green as a living
marsh, comparable in density to a thriving wetland, while staying bright:
- TALL twisted willows, old, dense, trailing into the water at (4,17), (8,4), (17,19), (24,4), (29,20),
  each a different girth and lean, their crowns LARGE — three to four tiles across — in a fresh vivid
  green;
- MANGROVE-LIKE trees with arched exposed roots standing in the shallow water at (2,13), (9,21), (16,16),
  (26,10), (30,6), (15,3), (28,14) — seven of them, varied sizes, two of them TALL;
- DENSE REED BEDS lining most water edges and filling the shallows in thick clumps — along the banks of
  every pool and channel, upright, light and dark green mixed;
- GREEN ALGAE and floating weed drifting in the water in many patches, and mossy green tinting the mud
  banks; submerged plants visible through the clear water;
- water lilies with flowers on three pools, around (10,15), (25,18) and (6,6);
- marsh grass tufts generously scattered along every bank.

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

KEY = "p4-marais-v5"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P4}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

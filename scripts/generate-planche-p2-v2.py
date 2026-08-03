#!/usr/bin/env python3
"""Plate P2 town, second pass — first rewrite of the composition to the established format.

The first P2 predates the composition format. Known faults it must fix: people off the art direction,
buildings too small, real animals present. This pass applies everything established since:
- the composition format: 32x24 grid, buildings never under 8 tiles in their smallest dimension, doors
  2.5 tiles high, everything square to the grid, footprints filled;
- the three edge connections of the plate plan: P1 (left edge, row 16), P3 (right edge, row 8),
  P5 (bottom edge, column 18);
- no real animals — ever; creatures wear runes; people match the art direction;
- frank saturated colours anchored on da-gb-b4v6-scene, the true background reference;
- the measured limits: at most one tile in seven dark, dressing at most one tile in five.
Output goes to a NEW file; nothing is ever overwritten.
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
    "EXACTLY THAT SAME STYLE — never more realistic, never more photographic. Take ONLY the style from "
    "it; the composition below applies."
)

SCALE = """
FRAME AND SCALE — the image is 1536 x 1152 pixels for a grid of 32 columns by 24 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row), origin
(1,1) top left.

CHECK THESE FIRST — they have been wrong before:
- An adult human is 2 metres tall: 2 TILES, about 96 PIXELS on this image, standing on ONE tile of ground.
- A door is at least 2.5 tiles high, about 120 PIXELS, and one tile wide.
- A dwelling covers at least 12 by 10 tiles — about 576 by 480 PIXELS — and is NEVER narrower than
  8 tiles in its smallest dimension. No two-metre-wide houses. A building may be cut off by the image
  edge, showing only part of a larger footprint.
- Footprints are filled to their edges, never spilling sideways or downwards onto neighbouring tiles. Only
  height rises above the footprint, hiding what is behind.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. Bright
image, FRANK SATURATED COLOURS — rich, vivid, never muted, greyed, pastel or washed out. No deep shadow.
Perfectly sharp edge to edge.

TWO MEASURED LIMITS:
1. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark. No deep shadow, no dark alley masses.
2. DRESSING: flower boxes, weeds between cobbles, pebbles, fallen leaves. AT MOST ONE TILE IN FIVE carries
   any dressing; the other four are plain readable surface.

COHERENCE — nothing ends in the void. A street leads somewhere, a door opens onto an access at the same
ground level, a stair lands somewhere.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, carts or props.

NO REAL ANIMALS EXIST — no dogs, cats, horses, pigeons, chickens, ducks or insects. Everything alive that
is not human is an invented CREATURE wearing a rune. A creature may take inspiration from anything, real
or fantastical, but is never a real animal recoloured, and none has a human face. Two creatures of one
species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body. It
GLIMMERS FAINTLY, casts no light, has no halo; in daylight it reads as a marking slightly brighter than
the skin. About a QUARTER OF A TILE, roughly 12 pixels. No two share a rune shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair. Ages,
builds and genders vary. All rendered in the exact toon style of the reference, never realistic.

No text, no interface, no logos, no grid lines.
"""

P2 = """
PLATE P2 — TOWN. Biome: a small lively market town — cobbled streets, a paved square with a fountain, a
covered market hall, adjoining houses each visibly different, walled gardens. Warm stone, timber and tile,
every building distinct in shape, height, roof and colour.

DRAW THESE THREE EDGE CONNECTIONS FIRST — each is a street one tile wide that VISIBLY TOUCHES its border,
cut off by it, never stopping short:
1. A COBBLED STREET along ROW 16, reaching the LEFT EDGE at (1,16) — the country road from the west
   becomes a paved street here.
2. A COBBLED STREET along ROW 8, reaching the RIGHT EDGE at (32,8) — the road towards the foothills.
3. A COBBLED STREET along COLUMN 18, reaching the BOTTOM EDGE at (18,24) — the road down to the cliffs.

STREET NETWORK — street 1 runs from (1,16) to (18,16); street 3 runs up column 18 from (18,24) to (18,8);
street 2 runs from (18,8) to (32,8). All cobbled, all one tile wide, joined at their corners. Short paved
branches: from (22,7) down to the bakery door row; from (19,14) to the potter's door; from (4,17),
(8,17) and (12,17) up from street 1 to the terraced house doors.

TOWN SQUARE — a paved open square covering (10,9)-(17,15), joined to street 1 and street 3. In its centre
a ROUND STONE FOUNTAIN at (13,11)-(14,12), water clear and lively, basin edge worn. Two market stalls with
striped awnings, one at (11,10) half full of vegetables, one at (16,10) half full of cloth bolts.

BUILDINGS — all square to the grid, each one completely different from the others:
- COVERED MARKET HALL at (2,1)-(9,8): eight by eight, an open-sided timber hall on stout posts, steep
  tiled roof, no walls, market crates inside, half full. State: worn, cared for.
- ROW OF THREE ADJOINING TOWN HOUSES at (20,1)-(31,6), CUT OFF BY THE TOP EDGE — only their lower floors
  and doors visible; the row is 12 tiles wide. Left: a BAKERY, cream plaster, wide window, door at (22,6).
  Middle: a WEAVER'S HOUSE, timber-framed, dyed cloth hanging, door at (26,6). Right: an INN, stone ground
  floor, hanging sign bracket (no text), door at (30,6). Every door 2.5 tiles high, each house a different
  colour, height and roof. Their doors open onto a paved forecourt strip along row 7 joined to street 2.
- POTTER'S WORKSHOP at (22,10)-(31,19): ten by ten, brick with a rounded kiln chimney smoking gently,
  wide workshop door on its left side at (22,14), 2.5 tiles high, shelves of pots visible, reached by the
  branch from street 3.
- TERRACED PAIR OF HOUSES at (2,18)-(13,24), CUT OFF BY THE BOTTOM EDGE — two adjoining homes, 12 tiles
  wide together. Left: green-shuttered stone house, door at (4,18). Right: taller ochre house with a
  balcony, door at (8,18) and at (12,18) a shared garden gate. Doors 2.5 tiles high, opening onto the
  branches from street 1.

WALLED GARDEN — at (2,10)-(8,15), a low stone wall enclosing neat vegetable beds, half planted, a small
gate on its lower side at (5,15). State: well kept.

VEGETATION — two broad street trees in stone planters at (10,17) and (19,10), adult, dense, different
species and heights; espaliered fruit tree against the garden wall at (2,10), 40% fruit; flower boxes on
several windows, within the dressing limit.

OBJECTS — a handcart half loaded with sacks at (15,16); stacked crates at (9,9); a public well with a
bucket at (19,15); two barrels by the inn door at (29,7).

INHABITANTS
- (13,13) a stout baker in her fifties, warm brown skin, flour-dusted apron, filling a jug at the
  fountain, FACING UP.
- (11,11) a market vendor, East Asian features, grey-streaked hair, arranging vegetables at his stall,
  FACING LEFT.
- (23,14) a young potter, pale skin, red hair, clay-stained smock, carrying a stack of bowls out of the
  workshop door, walking LEFT.
- (16,16) and (17,16) two children of different origins chasing each other RIGHT along street 1.
- (30,8) an old traveller with a walking stick, dark skin, white beard, entering from the right edge
  along street 2, walking LEFT.
- CREATURES, each one tile, each with its rune: at (12,15) a small round amber creature dozing against
  the fountain base; at (20,16) a slim blue-grey creature trotting DOWN along street 3 beside the
  children; at (6,9) a mossy-backed creature sniffing at the market hall crates, FACING UP.
- THE MAJESTIC CREATURE at (14,9)-(15,10): TWO TILES of ground at rest — a tall elegant creature with a
  deep teal coat, a ruff of pale feather-like fur and a single sweeping horn, standing calmly at the top
  of the square, head high, FACING DOWN, watched shyly by the children. Its rune, a single glimmering
  stroke, along its neck.
"""

KEY = "p2-bourg-v2"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P2}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

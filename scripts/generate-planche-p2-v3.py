#!/usr/bin/env python3
"""Plate P2 town, third pass.

Carried corrections, each traced to the owner's review of v2:
- SCALE was prescribed and ignored by the production: hammered harder, per building, in pixels, and
  placed first.
- STALLS OF ONE TILE WERE AN IMPOSSIBLE ASK of my composition: every built structure now covers at
  least 2 tiles.
- THE BLACKSMITH, THE BAKER AND THE GUARD of the first version were lost: they are back, with a forge.
- FACING ANGLES VARY: humans facing straight down included, creatures facing straight, not only diagonal.
Everything else carries over from v2 unchanged: it was not faulted.
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
    "EXACTLY THAT SAME STYLE — never more realistic. Take ONLY the style from it; the composition below "
    "applies."
)

SCALE = """
FRAME AND SCALE — the image is 1536 x 1152 pixels for a grid of 32 columns by 24 rows. EACH TILE IS
48 x 48 PIXELS AND REPRESENTS ONE METRE. Do NOT draw the grid. Positions are written (column,row), origin
(1,1) top left.

SCALE IS THE FIRST THING CHECKED ON THE RESULT — respect it over everything else:
- An adult human is 2 metres tall: EXACTLY 2 TILES, 96 PIXELS, never more, standing on ONE tile of ground.
- EVERY DOOR IS 2.5 TILES HIGH — 120 PIXELS — and one tile wide. A human fits through with room above.
  Doors noticeably TALLER than the people passing them: this was wrong last time.
- A dwelling is NEVER narrower than 8 tiles (384 PIXELS) in its smallest dimension.
- NOTHING BUILT FITS IN ONE TILE: a market stall, a well, any structure covers AT LEAST 2 tiles. One tile
  holds sacks, a chair, a barrel — nothing built.
- Footprints are filled to their edges, never spilling onto neighbouring tiles. Only height rises above.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. Bright
image, FRANK SATURATED COLOURS — rich, vivid, never muted or washed out. No deep shadow, no dark alley
masses. Sharp edge to edge.

TWO MEASURED LIMITS:
1. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark.
2. DRESSING: flower boxes, weeds between cobbles, pebbles. AT MOST ONE TILE IN FIVE carries any dressing.

VARY THE FACING DIRECTIONS — recurring fault to avoid: humans never face down, creatures only in
diagonal. Here, SOME HUMANS FACE STRAIGHT DOWN towards the camera, face fully visible, and at least one
creature faces STRAIGHT DOWN too, not diagonally.

COHERENCE — nothing ends in the void. A street leads somewhere, a door opens onto an access.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings, carts or props.

NO REAL ANIMALS EXIST — no dogs, cats, horses, pigeons, chickens or insects. Everything alive that is not
human is an invented CREATURE wearing a rune, never a real animal recoloured, none with a human face.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body,
glimmering faintly, about a QUARTER OF A TILE (12 pixels). No two share a shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair.
All in the exact toon style of the reference, never realistic.

No text, no interface, no logos, no grid lines.
"""

P2 = """
PLATE P2 — TOWN. Biome: a small lively market town — cobbled streets, a paved square with a fountain, a
covered market hall, a forge, adjoining houses each visibly different, walled gardens. Warm stone, timber
and tile, every building distinct in shape, height, roof and colour.

DRAW THESE THREE EDGE CONNECTIONS FIRST — each a cobbled street one tile wide that VISIBLY TOUCHES its
border, cut off by it:
1. Along ROW 16, reaching the LEFT EDGE at (1,16).
2. Along ROW 8, reaching the RIGHT EDGE at (32,8).
3. Along COLUMN 18, reaching the BOTTOM EDGE at (18,24).

STREET NETWORK — street 1 runs from (1,16) to (18,16); street 3 runs up column 18 from (18,24) to (18,8);
street 2 runs from (18,8) to (32,8), all joined at their corners. Short paved branches: from (22,7) down
to the shop doors row; from (19,14) to the potter's door; from (4,17), (8,17) and (12,17) up from
street 1 to the terraced house doors.

TOWN SQUARE — a paved open square covering (10,9)-(17,15), joined to streets 1 and 3. In its centre a
ROUND STONE FOUNTAIN at (13,11)-(14,12), water clear and lively. Two MARKET STALLS, EACH TWO TILES with a
striped awning on posts: one at (11,10)-(12,10) half full of vegetables, one at (16,10)-(17,10) half full
of cloth bolts.

BUILDINGS — all square to the grid, each completely different, EVERY DOOR 2.5 TILES (120 PIXELS) HIGH:
- COVERED MARKET HALL at (2,1)-(9,8): eight by eight, open-sided timber hall on stout posts, steep tiled
  roof, market crates inside, half full. State: worn, cared for.
- ROW OF THREE ADJOINING SHOPS at (20,1)-(31,6), CUT OFF BY THE TOP EDGE — only their lower floors and
  doors visible; the row is 12 tiles wide. Left: a BAKERY, cream plaster, wide window with loaves, door
  at (22,6). Middle: a FORGE, dark timber, open smithy front showing the glowing hearth, an anvil
  outside, door at (26,6). Right: an INN, stone ground floor, hanging sign bracket (no text), door at
  (30,6). Their doors open onto a paved forecourt strip along row 7 joined to street 2.
- POTTER'S WORKSHOP at (22,10)-(31,19): ten by ten, brick, rounded kiln chimney smoking gently, wide
  workshop door on its left side at (22,14), shelves of pots, reached by the branch from street 3.
- TERRACED PAIR OF HOUSES at (2,18)-(13,24), CUT OFF BY THE BOTTOM EDGE — two adjoining homes, 12 tiles
  wide together: green-shuttered stone house, door at (4,18); taller ochre house with a balcony, door at
  (8,18); at (12,18) a shared garden gate.

WALLED GARDEN — at (2,10)-(8,15), low stone wall, neat vegetable beds half planted, gate at (5,15).

VEGETATION — two broad street trees in stone planters at (10,17) and (19,10), adult, dense, different
species; espaliered fruit tree against the garden wall, 40% fruit; flower boxes within the dressing limit.

OBJECTS — a HANDCART half loaded with sacks covering (15,16)-(16,16), two tiles; stacked crates at (9,9);
a PUBLIC WELL covering (19,15)-(20,15), two tiles, with a small roof and bucket; two barrels by the inn
door at (29,7).

INHABITANTS
- (13,13) the BAKER, a stout woman in her fifties, warm brown skin, flour-dusted apron, filling a jug at
  the fountain, FACING STRAIGHT DOWN towards the camera, face fully visible.
- (26,7) the BLACKSMITH, a broad man with dark skin and a leather apron, hammering at the anvil outside
  the forge, FACING DOWN.
- (17,12) the TOWN GUARD, a tall woman, olive skin, simple leather-and-cloth uniform, a staff in hand,
  standing at the edge of the square watching it, FACING LEFT.
- (11,11) a market vendor, East Asian features, grey-streaked hair, arranging vegetables, FACING LEFT.
- (23,14) a young potter, pale skin, red hair, clay-stained smock, carrying bowls out of the workshop,
  walking LEFT.
- (16,16) and (17,16) two children of different origins chasing each other RIGHT along street 1.
- CREATURES, each one tile, each with its rune: at (12,15) a small round amber creature dozing against
  the fountain base; at (20,16) a slim blue-grey creature FACING STRAIGHT DOWN towards the camera, not
  diagonally, trotting DOWN along street 3; at (6,9) a mossy-backed creature sniffing at the market hall
  crates, FACING UP.
- THE MAJESTIC CREATURE at (14,9)-(15,10): TWO TILES of ground at rest — a tall elegant creature with a
  deep teal coat, a ruff of pale feather-like fur and a single sweeping horn, standing calmly at the top
  of the square, head high, FACING DOWN. Its rune along its neck.
"""

KEY = "p2-bourg-v3"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P2}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

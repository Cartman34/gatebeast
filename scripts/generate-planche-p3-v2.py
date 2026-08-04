#!/usr/bin/env python3
"""Plate P3 foothills, second pass — first composition written to the format, from the plan the owner
retained. All established rules apply (scale in pixels, nothing built in one tile, buildings served,
no real animals, varied facing angles, measured limits, frank colours anchored on da-gb-b4v6-scene).
Edge connections per the plate plan: P2 (left edge, row 8), P6 (bottom edge, column 26)."""
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
  pickaxe, a lantern — nothing built.
- Footprints are filled to their edges, never spilling onto neighbouring tiles. Only height rises above.
- EVERYTHING IS SQUARE TO THE GRID AXES. Nothing at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point. The slopes read
through rock faces and terraces seen from above, never through a horizon.

LIGHT — sun from the UPPER LEFT, shadows to the LOWER RIGHT, simple and soft-edged, one per object. Bright
image, FRANK SATURATED COLOURS — never muted or washed out. No deep shadow. Sharp edge to edge.

TWO MEASURED LIMITS:
1. DARKNESS: AT MOST ONE TILE IN SEVEN may read as dark, the rock faces and the mine mouth included.
2. DRESSING: grass tufts, small stones, fallen needles. AT MOST ONE TILE IN FIVE carries any dressing.

VARY THE FACING DIRECTIONS — recurring fault to avoid: humans never face down, creatures only in
diagonal. Here, SOME HUMANS FACE STRAIGHT DOWN towards the camera, face fully visible, and at least one
creature faces STRAIGHT DOWN too, not diagonally.

COHERENCE — nothing ends in the void. Every building is reached by a path; the suspended bridge lands on
the path at both ends; the ravine passes under it.

EXHAUSTIVE — draw what is listed and NOTHING ELSE: no extra people, buildings or props.

NO REAL ANIMALS EXIST — no sheep, no goats, no birds, no marmots, no insects. Everything alive that is
not human is an invented CREATURE wearing a rune, never a real animal recoloured, none with a human face.
Two creatures of one species differ in size, tint, build, age and posture.

RUNES — one per creature: ONE single continuous stroke, ONE colour, following the curve of the body,
glimmering faintly, about a QUARTER OF A TILE (12 pixels). No two share a shape. Humans wear none.

PEOPLE — at least three clearly different origins, genuinely different skin tones, features and hair.

No text, no interface, no logos, no grid lines.
"""

P3 = """
PLATE P3 — FOOTHILLS. Biome: rocky mountain slopes seen from above — pale grey rock faces, scree,
terraced grass in vivid green, dark pines, a mountain stream in a ravine. Stone, timber, rope.

ROCK FIRST — the mountain shows through rock face bands, drawn as steep pale-grey stone seen from above:
one across the top left at (1,1)-(13,4); one around the mine at (16,1)-(19,9); one on the top right at
(28,1)-(32,8) with a SCREE SLOPE below it at (29,9)-(32,13). Boulders of varied sizes at (17,11)-(18,12),
(7,9)-(8,10), (23,17)-(24,18), (29,21)-(30,22), (12,16)-(13,17), (20,22)-(21,23).

DRAW THESE TWO EDGE CONNECTIONS FIRST — each a stony path one tile wide that VISIBLY TOUCHES its border,
cut off by it:
1. Along ROW 8, reaching the LEFT EDGE at (1,8) — the paved street of the town becomes a stony path.
2. Along COLUMN 26, reaching the BOTTOM EDGE at (26,24) — the path down towards the beach.

PATH NETWORK — winding in switchbacks: from (1,8) to (10,8), down column 10 from (10,8) to (10,14),
along row 14 from (10,14) to (26,14), down column 26 from (26,14) to (26,24). Branches: from (5,9) down
to (5,11) to the sheepfold door; from (23,8) down to (23,13) from the mine mouth to the path; from
(26,17) to (27,17) towards the ruined tower.

THE RAVINE — a mountain stream runs in a narrow ravine down column 14-15 from (14,5) to (15,13), white
water far below. A SUSPENDED BRIDGE at (14,14)-(15,14) carries the path over it: timber planks and rope,
slightly sagging, both ends landing on the path.

BUILDINGS — doors 2.5 tiles (120 pixels) high:
- CREATURE FOLD at (2,12)-(9,19): eight by eight, a low dry-stone barn with a timber roof, wide door on
  its upper side at (5,12), hay inside. Its walled ENCLOSURE at (2,20)-(9,23), dry-stone, gate to the
  barn. State: worn, cared for.
- MINE ENTRANCE at (20,1)-(27,7): a timbered gallery mouth cut into the rock face, eight tiles wide,
  stout beams, a lantern hung at the entrance (unlit), rails coming out to a MINE CART, two tiles, at
  (21,9)-(22,9), half full of ore.
- RUINED TOWER at (28,16)-(31,19): a broken round watchtower, four tiles across, collapsed on one side,
  moss on the stones. A ruin — no door required.

VEGETATION — dark pines, each a different height and lean, at (4,6), (8,6), (18,18), (22,20), (30,14),
(12,20); low mountain grass elsewhere, dressing within the one-in-five limit.

INHABITANTS
- (5,15) the HERDER, a weathered woman in her fifties, olive skin, braided grey hair, staff in hand,
  standing by the fold FACING STRAIGHT DOWN towards the camera, face fully visible.
- (23,8) a MINER, a stocky man with dark skin, helmet with a small lamp, pushing nothing — wiping his
  brow at the mine mouth, FACING DOWN.
- (12,14) a young hiker, East Asian features, small pack, crossing the suspended bridge RIGHTWARDS,
  holding the rope, FACING RIGHT.
- CREATURES, each one tile, each with its rune: at (4,21) and (7,21) two OF THE SAME SPECIES in the
  enclosure — round woolly creatures with curled horns, one large and cream, one small and brown, the
  large one FACING STRAIGHT DOWN towards the camera, not diagonally; at (16,10) a sure-footed slender
  creature standing on a boulder above the ravine, FACING LEFT; at (29,12) a pale grey creature hopping
  down the scree.
- THE MAJESTIC CREATURE at (21,10)-(22,11): TWO TILES of ground at rest — a powerful mountain creature
  with slate-blue stone-like plates along its back, a heavy calm head with two backswept horns, standing
  by the mine path FACING DOWN, watching the valley. Its rune, a single glimmering stroke, on its
  foreleg.
"""

KEY = "p3-contreforts-v2"
prompt = f"{STYLE}\n\n{ANCHOR}\n{SCALE}\n{P3}"
(ASSETS / f"prompt-{KEY}.txt").write_text(prompt, encoding="utf-8")

sys.exit(subprocess.run(
    ["php", TOOL, f"{TARGET}/planche-{KEY}.png", prompt], cwd=PROJECT
).returncode)

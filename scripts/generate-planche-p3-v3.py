#!/usr/bin/env python3
"""Plate P3 foothills, third pass — owner's review of v2: humans over 2 tiles, plan not respected,
colours lacking intensity. Corrections: standing-scale rule, ravine bounded to rows 5-13, the left-edge
joint frankly touching the border, colours pushed, and every inhabitant quoted from its sheet."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import creature, generate, human

COMPOSITION = f"""
PLATE P3 — FOOTHILLS. Biome: rocky mountain slopes seen from above — pale grey rock faces, scree,
terraced grass in VIVID SATURATED GREEN, dark pines, a mountain stream in a ravine. The grass is rich
and warm, the rock streaked with ochre and warm grey: this plate must NOT read grey or faded.

ROCK FIRST — steep rock face bands seen from above: across the top left at (1,1)-(13,4); around the
mine at (16,1)-(19,9); on the top right at (28,1)-(32,8) with a SCREE SLOPE below at (29,9)-(32,13).
Boulders of varied sizes at (17,11)-(18,12), (7,9)-(8,10), (23,17)-(24,18), (29,21)-(30,22),
(12,16)-(13,17), (20,22)-(21,23). None of them touches a path.

DRAW THESE TWO EDGE CONNECTIONS FIRST — each a stony path one tile wide, VISIBLY TOUCHING its border,
cut off by it, running over open grass, never lost in rocks:
1. Along ROW 8, REACHING THE LEFT EDGE at (1,8) — clearly visible against plain grass at the border.
2. Along COLUMN 26, REACHING THE BOTTOM EDGE at (26,24).

PATH NETWORK — switchbacks: from (1,8) to (10,8), down column 10 from (10,8) to (10,14), along row 14
from (10,14) to (26,14), down column 26 from (26,14) to (26,24). Branches: down column 5 from (5,9) to
(5,11), stopping AT the fold door; down column 23 from (23,8) to (23,13), linking the mine mouth to the
path; from (26,17) one step to (27,17) towards the ruined tower. No other paths exist.

THE RAVINE — the mountain stream runs in a narrow ravine down columns 14-15 ONLY from (14,5) to (15,13):
plain grass above it and below it, the ravine does NOT reach any edge. A SUSPENDED BRIDGE at
(14,14)-(15,14) carries the row-14 path over it: timber planks and rope, slightly sagging, both ends
landing on the path.

BUILDINGS — every door 2.5 tiles (120 pixels) high:
- CREATURE FOLD at (2,12)-(9,19): eight by eight, a low dry-stone barn with a timber roof, wide door on
  its upper side at (5,12) — the access path stops at this door. Hay inside. Its walled ENCLOSURE at
  (2,20)-(9,23), dry-stone, connected to the barn by a gate in the shared wall. State: worn, cared for.
- MINE ENTRANCE at (20,1)-(27,7): a timbered gallery mouth cut into the rock face, stout beams, a small
  unlit lantern hung at the entrance, rails coming out to a MINE CART, two tiles, at (21,9)-(22,9),
  half full of ore.
- RUINED TOWER at (28,16)-(31,19): a broken round watchtower, collapsed on one side, moss on the
  stones. A ruin — no door required.

VEGETATION — dark pines, each a different height and lean, at (4,6), (8,6), (18,18), (22,20), (30,14),
(12,20); low mountain grass elsewhere, dressing within the one-in-five limit.

INHABITANTS — humans and creatures quoted from their sheets, drawn EXACTLY as described:
- At (5,15), STANDING (EXACTLY 2 tiles tall, 96 pixels, never more), beside the fold, FACING STRAIGHT
  DOWN towards the camera, face fully visible: {human('HU-011')}
- At (23,8), STANDING (2 tiles), wiping his brow at the mine mouth, FACING DOWN: {human('HU-012')}
- At (12,14), STANDING (2 tiles), crossing towards the suspended bridge RIGHTWARDS, holding the rope,
  FACING RIGHT: {human('HU-014')}
- In the enclosure, grazing: at (4,21), the larger one, FACING STRAIGHT DOWN towards the camera, not
  diagonally: {creature('SP-016-1')} — and at (7,21), smaller and browner: {creature('SP-016-2')}
- At (17,11), perched on the boulder above the ravine, FACING LEFT: {creature('SP-007-1')}
- At (29,12), hopping down the scree: {creature('SP-005-1')}
- THE MAJESTIC CREATURE at (21,10)-(22,11), TWO TILES of ground, standing by the mine path, watching
  the valley, FACING DOWN: {creature('SP-014-1')}
"""

if __name__ == "__main__":
    sys.exit(generate("p3-contreforts-v3", COMPOSITION))

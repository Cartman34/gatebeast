#!/usr/bin/env python3
"""Plate P1 countryside, fifth pass — corrected plan (brook straight down column 14), witness sheets
quoted verbatim, standing-scale rule, style anchored hard after the flat-looking v4."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import creature, generate, human

COMPOSITION = f"""
PLATE P1 — WOODED COUNTRYSIDE. Biome: rolling cultivated land, hedged fields, an orchard, WIDE PLAIN
MEADOWS in vivid fresh green, broadleaf trees. Warm, bright, saturated.

DRAW THESE TWO EDGE EXITS FIRST — each visibly cut off by its border:
1. A DIRT ROAD, one tile wide, along ROW 16, from the LEFT EDGE at (1,16) to the RIGHT EDGE at (32,16).
2. A DIRT ROAD, one tile wide, down COLUMN 12 from (12,16), REACHING THE BOTTOM EDGE at (12,24).

THE BROOK — a clear brook, one tile wide, runs STRAIGHT DOWN COLUMN 14 from the top edge (14,1) to the
bottom edge (14,24), lively water. A STONE BRIDGE at (13,16)-(15,16) carries the main road over it, both
ends on the road. The brook crosses NOTHING else: no building, no field, no other path touches it.

ACCESS PATHS — dirt, one tile wide: up column 8 from (8,16) to the farmhouse door; up column 19 from
(19,15) to (19,10) to the barn doors; up column 25 from (25,16) to (25,10) then one step right to the
mill door; down column 17 from (17,16) to (17,18), stopping AT the cottage door. No other paths exist.

BUILDINGS — every door 2.5 tiles (120 pixels) high, one tile wide:
- FARMHOUSE at (2,2)-(13,11): twelve by ten, stone and timber, tiled roof, chimney, door on its lower
  side at (8,11). State: worn, cared for.
- BARN at (15,3)-(24,9): ten by seven, red-boarded, double doors at (19,9) three tiles high, hayloft.
- WINDMILL at (26,4)-(31,10): a round stone mill with four sails, door on its lower side at (26,10).
- COTTAGE at (15,19)-(23,24): nine by six visible, thatched, door on its upper side at (17,19).

FIELDS AND ORCHARD — a MIXED ORCHARD at (24,17)-(31,23), all adult trees, each a different height and
crown: two apple trees at 80% fruit, one pear at 50%, one plum at 30%, one cherry in blossom without
fruit, one quince at 20%. A hedged vegetable plot at (2,12)-(7,15), well kept, half its rows planted. A
ripe wheat field at (26,11)-(31,15). Hedgerows along (2,17)-(7,17) and (15,12)-(18,12).

VEGETATION — one broad old oak, dense, at (10,18); three slim birches at (3,18), (16,14), (30,2); two
dark firs at (1,8) and (31,20). Everywhere else: WIDE PLAIN MEADOW, dressing within the one-in-five
limit.

OBJECTS — three haystacks of differing sizes at (24,10), (27,16), (29,16); a STONE WELL with a small
roof covering (16,10)-(17,10), two tiles; a CART half loaded with sacks covering (10,15)-(11,15), two
tiles; a full water trough at (12,10).

INHABITANTS — humans and creatures quoted from their sheets, drawn EXACTLY as described:
- At (9,13), STANDING (2 tiles tall), forking hay, FACING STRAIGHT DOWN towards the camera, face fully
  visible: {human('HU-001')}
- At (18,16), STANDING, carrying a basket of apples, walking LEFT along the road: {human('HU-002')}
- At (27,11), STANDING in front of the mill door, a flour sack at his feet, FACING DOWN:
  {human('HU-003')}
- At (20,16) and (21,16), two children clearly SHORTER than adults, chasing each other RIGHT:
  {human('HU-013')} — and — {human('HU-015')}
- At (24,16), one tile, FACING STRAIGHT DOWN towards the camera, not diagonally: {creature('SP-001-1')}
- At (26,20), one tile, asleep curled under an orchard tree: {creature('SP-004-1')}
- At (13,14), ON THE BANK of the brook, front feet IN THE WATER touching the bottom, head lowered to
  drink, FACING RIGHT: {creature('SP-008-1')}
- At (5,19), sitting: {creature('SP-007-1')}
- At (6,19), trotting RIGHT: {creature('SP-007-2')}
- THE MAJESTIC CREATURE at (4,21)-(5,22), TWO TILES of ground, standing calmly in the open meadow away
  from the paths, head raised, FACING LEFT: {creature('SP-010-1')}
"""

if __name__ == "__main__":
    sys.exit(generate("p1-campagne-v5", COMPOSITION))

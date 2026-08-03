#!/usr/bin/env python3
"""Plate P6 beach, third pass — owner's review of v2: humans over 2 tiles, plan not respected (phantom
path rectangles, missing left-edge joint). Corrections: standing-scale rule, the exact path network and
nothing else, the row-20 joint with measure and axis, and every inhabitant quoted from its sheet —
the v2 creatures were real animals barely disguised (fish, hermit crab, horse), all replaced."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import creature, generate, human

COMPOSITION = f"""
PLATE P6 — BEACH. Biome: a bright golden sand beach with dunes, palms and coastal plants, a timber
jetty, two fishermen's cabins, a luminous turquoise sea with white foam.

DRAW THESE TWO EDGE CONNECTIONS FIRST — exact measure and axis, each VISIBLY TOUCHING its border:
1. A SANDY PATH, one tile wide, ALONG ROW 20 — the horizontal band 912 to 960 pixels from the top —
   REACHING THE LEFT EDGE at EXACTLY (1,20), cut off by the left border. This is the joint with the
   cliff plate.
2. A SANDY PATH, one tile wide, ALONG COLUMN 26, REACHING THE TOP EDGE at EXACTLY (26,1), cut off by
   the top border.

PATH NETWORK — EXACTLY these segments and NOTHING ELSE — no loops, no empty path rectangles, no other
paths anywhere: from (1,20) to (4,20); up column 4 from (4,20) to (4,16); along row 16 from (4,16) to
(15,16); down column 26 from (26,1) to (26,12); along row 12 from (26,12) to (15,12); down column 5
from (5,10) to (5,15); down column 15 from (15,11) to (15,16); along row 13 from (15,13) to (18,13) to
the jetty. THE SHORE HAS NO PATH: the beach between the paths and the sea is open golden sand.

THE SEA — luminous turquoise water with gentle white foam lines, covering (20,14)-(32,21) and the whole
bottom band (1,22)-(32,24). The waterline crosses the sand in a soft irregular curve. Creatures are
visible under the water through the transparency.

THE JETTY — timber, at (18,13)-(19,22): its deck FLAT AT BEACH LEVEL, boards worn, running from the
sand straight out over the water on stout posts, reached by the row-13 path. No steps, no raised
entrance.

BUILDINGS — doors 2.5 tiles (120 pixels) high, one tile wide:
- FISHERMAN'S CABIN 1 at (2,2)-(9,9): eight by eight, sun-bleached planks, flat driftwood roof, door on
  its lower side at (5,9), nets hung on the wall. State: weathered.
- FISHERMAN'S CABIN 2 at (12,3)-(19,10): eight by eight, visibly different — whitewashed walls, blue
  shutters, single-slope tiled roof, door on its lower side at (15,10).

DUNES AND VEGETATION — soft DUNES at (6,12)-(11,15), golden sand with GRASS TUFTS covering several
adjoining tiles on their crests; FOUR PALMS, each a different height and lean, at (2,11), (10,13),
(21,2), (29,4); a patch of MALCOLMIA — low coastal plants with small lilac flowers — at (12,18)-(14,19);
coastal shrubs at (23,6)-(25,7) and (30,9)-(31,10).

SHELLS — empty shells scattered ALONG THE WATERLINE: clusters at (4,21), (9,21), (15,21) and (24,20),
pale pink and cream, each shell a hand's width.

OBJECTS — a beached BOAT, two tiles, at (5,18)-(6,18), hull striped; an older beached BOAT, two tiles,
at (13,19)-(14,19); stacked wicker crates at (16,13) and (21,13); rocks streaked with white at
(28,12)-(29,13) and (2,16)-(3,17).

INHABITANTS — humans and creatures quoted from their sheets, drawn EXACTLY as described:
- At (10,20), STANDING (EXACTLY 2 tiles tall, 96 pixels, never more), walking RIGHT along the path:
  {human('HU-016')}
- At (19,16), KNEELING on the jetty coiling a rope — kneeling, so clearly LESS than 2 tiles high —
  FACING STRAIGHT DOWN towards the camera, face fully visible: {human('HU-017')}
- At (27,8), clearly SHORTER than an adult, running DOWN the foothill path, FACING DOWN:
  {human('HU-013')}
- At (7,19), dozing on the sand near the boat, FACING STRAIGHT DOWN towards the camera, not diagonally:
  {creature('SP-006-1')}
- At (24,18), fully UNDER THE WATER, its ribbon silhouette clearly visible through the turquoise
  transparency, undulating LEFT: {creature('SP-017-1')}
- At (30,22), SWIMMING AT THE SURFACE near the rocks, moving LEFT: {creature('SP-009-1')}
- THE MAJESTIC CREATURE at (12,13)-(13,14), TWO TILES of ground, standing on the dune crest overlooking
  the beach, FACING DOWN: {creature('SP-015-1')}
"""

if __name__ == "__main__":
    sys.exit(generate("p6-plage-v3", COMPOSITION))

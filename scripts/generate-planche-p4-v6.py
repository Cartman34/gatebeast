#!/usr/bin/env python3
"""Plate P4 marsh, sixth pass — owner's review of v5: more water, the stilt huts must have their feet
in the water at least partly, more tall trees, more light. Plus the served drying rack (coherence check)
and every inhabitant quoted from its sheet."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plate_common import creature, generate, human

COMPOSITION = f"""
PLATE P4 — MARSH. Biome: a LUSH, GREEN, BRIGHT wetland where WATER DOMINATES: wide pools of clear
vivid water linked by slow channels, threaded by walkways, dense reed beds and TALL trees. This plate
must read light and sunny — it was too dark last time.

WATER FIRST — MORE WATER THAN GROUND. Clear, vivid water-green and turquoise, the sandy bottom visible
through it, NEVER brown or dark, NO mist. Irregular pools draining from (30,3) towards (4,22): a pool
at (27,2)-(31,7), a channel at (21,6)-(27,10), a pool at (14,9)-(21,12), a channel at (8,11)-(14,16), a
pool at (3,14)-(9,18), a channel at (2,18)-(7,22), a pool at (23,12)-(28,14). Mud banks and grassy
hummocks between them. Water lilies with flowers on three pools, around (10,15), (25,18) and (6,6).

DRAW THESE TWO EDGE CONNECTIONS FIRST — plank walkways one tile wide, VISIBLY TOUCHING their border:
1. Along COLUMN 12, REACHING THE TOP EDGE at (12,1); its last four tiles run over firm ground.
2. Along ROW 12, REACHING THE RIGHT EDGE at (32,12).

WALKWAYS — from (12,12) down to (12,20); a branch from (5,8) to (12,8); a short branch (13,8)-(14,8) to
the drying rack; another branch down column 20 from (20,12) to (20,20). Worn boards, a few replaced,
rope handrail on the water side. No branch ends in water. No other paths exist.

BUILDINGS — square to the grid, doors 2.5 tiles (120 pixels) high:
- STILT HOUSE at (2,2)-(13,11): twelve by ten, reed thatch, plank veranda on its lower side, door at
  (7,11) reached by the walkway branch. IT STANDS IN THE WATER: its stout stilts rise straight out of
  the pool, green algae on every post — a stilt house has its feet in the water.
- SECOND STILT HOUSE at (21,15)-(31,23): eleven by nine, visibly different — plank walls, single-slope
  roof, outside stair on its left side landing on the walkway at (20,20). Its stilts too stand PARTLY
  IN THE WATER of the nearby pool.
- FISH DRYING RACK at (15,6)-(18,8): an open timber frame, half full, served by its short walkway.

VEGETATION — abundant AND TALL, in a light fresh green, never a dark mass:
- FIVE TALL twisted willows, old, their crowns LARGE (three to four tiles across) and HIGH, trailing
  into the water, at (4,17), (8,4), (17,19), (24,4), (29,20), each a different girth and lean;
- SEVEN mangrove-like trees with arched exposed roots standing in the shallow water at (2,13), (9,21),
  (16,16), (26,10), (30,6), (15,3), (28,14) — TWO OF THEM AS TALL AS THE WILLOWS;
- reed beds in thick clumps along the pool edges; marsh grass on the hummocks, generous but within the
  dressing limit; submerged plants visible through the clear water.

OBJECTS — a flat-bottomed punt moored at (14,13)-(14,14) with a pole across it; an older punt beached
in the mud at (7,22)-(8,22); wicker traps half submerged at (17,17) and (27,7).

INHABITANTS — humans and creatures quoted from their sheets, drawn EXACTLY as described:
- At (10,8), STANDING (EXACTLY 2 tiles tall), walking LEFT along the branch walkway, FACING LEFT:
  {human('HU-008')}
- At (16,12), STANDING (2 tiles), hauling a dripping wicker trap onto the walkway, FACING RIGHT:
  {human('HU-009')}
- At (20,18), CROUCHED at the walkway edge — crouched, so clearly LESS than 2 tiles high — peering into
  the water, FACING STRAIGHT DOWN: {human('HU-013')}
- At (6,15), WADING, legs IN THE WATER touching the bottom, water to its knees, visible through the
  clear water, head lowered, FACING RIGHT: {creature('SP-008-1')}
- At (28,17), SWIMMING AT THE SURFACE, moving LEFT, ripples spreading behind it: {creature('SP-009-1')}
- At (25,13), fully UNDER THE WATER of the pool, clearly visible through the transparency, undulating,
  FACING STRAIGHT DOWN towards the camera, not diagonally: {creature('SP-017-1')}
- At (18,21), hunched ON a mossy stump above the water: {creature('SP-002-1')}
- At (19,22), sitting ON THE MUD BANK beside it: {creature('SP-002-2')}
- THE MAJESTIC CREATURE at (7,3)-(8,4), TWO TILES of ground, standing motionless in the shallow pool,
  its stilt legs IN THE WATER touching the bottom, FACING RIGHT: {creature('SP-012-1')}
"""

if __name__ == "__main__":
    sys.exit(generate("p4-marais-v6", COMPOSITION))

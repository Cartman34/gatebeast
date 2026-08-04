#!/usr/bin/env python3
"""Plates P3 (foothills) and P4 (marsh), composed tile by tile.

Written to the conception's composition format: paths first, then structures with their footprints, then
vegetation and objects with a stated condition, then inhabitants with what they do and where they look.
Nothing is named without being qualified, real animals are present and rune-free, and no two individuals
of one species look alike.
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
    "same amount of surface detail, same degree of stylisation. PEOPLE, ANIMALS AND CREATURES ARE RENDERED "
    "IN EXACTLY THAT SAME STYLE — same volume, same shading, same light. A scene whose figures are drawn "
    "differently from its scenery is wrong. Take ONLY the style from that image; the layout below applies."
)

COMMON = """
FRAME — 1536 x 1152 pixels for a grid of 32 columns by 24 rows of square tiles. Do NOT draw the grid.
Positions are written (column,row), origin (1,1) top left. A standing human is exactly ONE tile tall — the
reference scale. Footprints are the ground covered: FILLED to their edges, never spilling sideways or
downwards onto neighbouring tiles; only height rises above the footprint on screen, hiding what is behind.
Everything is SQUARE to the grid axes: buildings, fences, walkways. Nothing sits at an angle.

BUILDINGS ARE SIZED FOR WHAT THEY HOLD — a dwelling has a kitchen, a living room and at least one bedroom,
so it covers around ten tiles by eight. Only sheds and workshops are small.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. The ground fills the frame. NO horizon, NO sky, NO clouds, no vanishing point. Roofs and treetops seen
from above.

LIGHT — sun from the UPPER LEFT, every shadow falling to the LOWER RIGHT. Shadows are SIMPLE: plain,
soft-edged, one per object. Bright image, frank clear colours, no deep shadow, no murk. Perfectly sharp
edge to edge — no blur, no haze, no depth of field.

THE WORLD HAS LIVED — weathered wood, moss and lichen at the foot of walls, plants reclaiming corners.

WATER FLOWS — oriented ripples, eddies behind stones, grass bent by the current.

COHERENCE — nothing ends in the void. A bridge lands on a path or is broken and the path stops with it. A
door opens onto an access. Stairs lead somewhere. A boat is moored or beached.

PEOPLE — humans of real humanity: AT LEAST THREE CLEARLY DIFFERENT ORIGINS are visible, with genuinely
different skin tones, features and hair — not shades of one. Ages and builds vary too. Both genders.

REAL ANIMALS — ordinary animals live here as well as creatures: they wear NO RUNE, which is what tells
them apart at a glance.

CREATURES — original invented creatures, never a real animal recoloured; a real animal may inspire a
silhouette, nothing more. None has a human face. TWO CREATURES OF THE SAME SPECIES ARE NOT IDENTICAL:
size, tint, build, age and posture differ, as between two dogs of one breed.

RUNES — each creature wears ONE rune: ONE single continuous stroke, ONE colour, following the curve of the
body like a natural marking. It GLOWS FAINTLY — the dull sheen of a material that glimmers in the dark,
never a lamp: it casts no light on the body or ground, has no halo, and in daylight reads as a marking
slightly brighter than the skin. It fits in about a QUARTER OF A TILE — an absolute size, so it looks tiny
on a large creature. No two creatures wear the same rune shape. Humans and animals wear none.

No text, no interface, no logos, no grid lines.
"""

P3 = """
PLATE P3 — FOOTHILLS. Biome: steep rocky foothills, grey rock breaking through short wiry yellow-green
grass, scree slopes, dark mountain pines, cold clear light.

EDGE CONNECTION — a stone-slab path enters at the LEFT EDGE on row 8, ONE tile wide, touching the very
edge, coming up from the town.

PATHS — from that entry, a stone path climbs in switchbacks: right along row 8 to (10,8), up to (10,5),
right to (18,5), down to (18,12), right to (26,12). A second grass trail runs from (10,8) down to (10,20).
Every building below is served by a short branch of one of these.

WATER — a mountain torrent runs from (22,1) down to (22,24), fast and white over rocks, flowing DOWNWARDS.
It is crossed at (18,12)-(18,13) by a rope-and-plank SUSPENSION BRIDGE, 4 tiles long, both ends landing on
stone path. Two planks are missing; state: used, sound.

BUILDINGS
- SHEEPFOLD at (3,3)-(10,7): a long low dry-stone sheepfold under a shallow slate roof, wide plank gate on
  its lower side at (6,7), thick moss on its shaded wall. State: worn. A fenced stone pen at (3,8)-(9,11).
- MOUNTAIN REFUGE at (12,15)-(21,22): a stout stone dwelling, ten tiles by eight, steep shingled roof
  weighted with stones, chimney smoking, small deep windows, door on its lower side at (16,22), woodpile
  under the eaves, state: worn but cared for.
- MINE ENTRANCE at (26,3)-(30,5): timbered opening in a rock face, rusted rail track running out to a
  spoil heap, lantern hook, state: in use.
- RUINED TOWER at (3,17)-(7,21): the broken stump of a round stone tower, half collapsed into rubble,
  young pines and ivy growing from the cracks, open to the sky. State: in ruin.

VEGETATION — mountain pines, adult, dense foliage, at (2,13), (8,14), (24,8), (29,14), (30,20), each of a
different height and lean. Wind-bent stunted pines, old, sparse foliage, at (25,20) and (28,7). Juniper
bushes at (5,12), (14,9), (23,17). Short alpine grass in patches between bare rock everywhere; grey and
orange lichen crusting the exposed stone.

OBJECTS — a shoulder-high stone cairn at (11,6); a hollowed stone drinking trough fed by a spring at
(9,12), full, moss at its base; a rusted ore cart on a short rail at (28,6), half full of grey rock, one
wheel seized.

INHABITANTS
- (6,10) a weathered shepherd in his fifties, deep brown skin, grey beard, felted cloak, long crook,
  standing still FACING DOWN-RIGHT, watching his flock.
- (16,23) a broad-shouldered miner woman in her thirties, light olive skin, hair under a cloth, leather
  apron, lamp at her belt, walking UP the path towards the refuge, FACING UP.
- (13,21) an older keeper, pale freckled skin, white braid, layered woollens, standing at the refuge door
  FACING RIGHT, an armful of split logs.
- REAL ANIMALS: five sheep of visibly different sizes and fleece tones grazing across (4,9)-(8,11), heads
  down; a black and white sheepdog at (7,12) trotting LEFT, ears up; two crows on the ruined tower at
  (5,17), one facing left, one facing right; a goat standing on a boulder at (24,15) FACING LEFT.
- CREATURES, all different species, each with its rune: at (12,9) a shaggy grey-blue quadruped with curled
  horns, walking RIGHT along the path; at (20,6) a small russet creature with long legs, mid-leap between
  two rocks, FACING RIGHT; at (27,17) a broad slate-coloured creature with a stone-like hide, asleep
  against a rock, eyes closed; at (15,12) two creatures OF THE SAME SPECIES — pale tawny, tufted ears — one
  larger and darker standing FACING LEFT, the other smaller and paler sitting FACING UP, clearly two
  individuals rather than copies.
"""

P4 = """
PLATE P4 — MARSH. Biome: flat still wetland, shallow open water and grey mud flats threaded by reed beds,
twisted willows and alders, a film of floating green weed, thin mist clinging to the ground.

EDGE CONNECTION — none. The plate closes on itself: open water at the top and right edges, dense reeds at
the bottom, alder thicket at the left.

WATER — still shallow water covers roughly half the plate, in irregular pools connected by slow channels;
the main channel drains from (30,4) towards (6,20), flowing DOWN-LEFT, its current shown by bent reeds and
drifting weed. Floating green weed covers the quieter pools, broken open where something has passed.

WALKWAYS — a raised plank walkway on short piles, ONE tile wide, runs from (2,12) right to (14,12), then
down to (14,20), then right to (24,20). State: worn, three boards rotted through and one missing, a rope
handrail on its water side. Every hut below is reached by a branch of this walkway; no branch ends in
water.

BUILDINGS
- STILT HUT at (5,4)-(12,10): a reed-thatched dwelling raised on stilts above the water, ten tiles by
  eight counting its plank porch, ladder down to a moored punt at (12,10), green algae marking the
  waterline on every post, state: worn.
- SECOND STILT HUT at (18,14)-(25,19): smaller and visibly different — plank walls rather than reed, a
  single-slope roof, an outside stair, state: patched. Reached from the walkway at (24,20).
- FISH DRYING RACK at (16,9)-(19,11): an open timber frame, HALF FULL of drying fish and eel traps, posts
  sunk into soft ground, planks warped by damp.

VEGETATION — twisted willows, old, dense foliage, trailing into the water at (3,17), (21,5), (27,21), each
of a different girth and lean. Black alders, adult, standing in shallow water at (2,7), (9,20), (29,12).
Reed clumps, tall and feathered, at more than a dozen points along every water edge. Duckweed on the still
pools.

OBJECTS — a flat-bottomed punt, dark planks, moored at (13,10), a pole across it, a finger of water in its
bottom; a second punt, paler and older, beached in the mud at (8,22); wicker eel traps, half submerged, at
(15,16) and (26,8); a rotted plank lying half in the water at (11,18); mooring stakes with wound rope at
(13,11) and (24,21).

INHABITANTS
- (10,13) a lean young peat cutter, dark skin, close-cropped hair, rolled trousers, bare muddy legs, a
  long cutting spade over his shoulder, walking RIGHT along the walkway, FACING RIGHT.
- (17,10) a wiry eel fisher in her forties, tanned skin, wide straw hat, oiled coat, hauling a dripping
  wicker trap, standing FACING LEFT.
- (22,20) a child of about nine, brown skin, bare feet, patched shorts, crouched at the walkway edge
  FACING DOWN, holding a frog in cupped hands.
- REAL ANIMALS: a heron standing motionless in shallow water at (28,16) FACING LEFT; five ducks of
  differing plumage on a pool at (20,7), two dabbling, three swimming; a marsh frog on a lily pad at
  (12,19); a dragonfly-thick air over the reeds.
- CREATURES, all different species, each with its rune: at (7,15) a long-limbed pale creature with webbed
  feet, wading, FACING RIGHT, head lowered; at (23,10) a round mottled creature half sunk in the mud, only
  its back and eyes above water, FACING UP; at (26,17) a slender creature with a flat paddle tail swimming
  LEFT; at (16,21) two creatures OF THE SAME SPECIES — smooth olive skin, fringed crests — one large and
  dark hunched on the walkway FACING LEFT, the other small and pale sitting in the mud below FACING RIGHT,
  clearly two individuals.
"""

PLATES = {"p3-contreforts": P3, "p4-marais": P4}

arguments = []
for key, plate in PLATES.items():
    prompt = f"{STYLE}\n\n{ANCHOR}\n{COMMON}\n{plate}"
    (ASSETS / f"prompt-{key}.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/planche-{key}.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

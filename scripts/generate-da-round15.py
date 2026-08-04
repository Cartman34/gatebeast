#!/usr/bin/env python3
"""Fifteenth art direction round — the toon direction alone, plus one new proposal.

Three directions were dropped in review; only the toon volume remains in the running, and it has never
quite matched the round-six image the owner wants. It is therefore anchored to that image as hard as words
allow, with the review's corrections applied: calm water, sparse flowers, simple shadows, frank colours,
smaller runes, buildings square to the map.

A second image is produced in parallel: a direction inspired by the look of village-building strategy
games — clean stylised volumes, tidy readable ground — proposed by the owner.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

CREATURES = """
CREATURES — draw exactly these animals, nothing else, no other species. None has a human face.

SP-001 AMBER FOX CUB: a small round quadruped the size of a fox cub. Warm amber fur (#D98A33) over back
and head, cream belly and muzzle (#F5E6CC), four short legs with cream paws, two large rounded ears amber
outside and cream inside, big dark friendly eyes, short thick tail with a cream tip. Rune on the MIDDLE OF
THE FOREHEAD: a turquoise ARCH.

SP-002 GREEN STUB: a small round mossy-green quadruped, barely taller than wide, smooth rounded back,
short stubby legs, wide friendly mouth, small dark eyes, no tail. Rune on the MIDDLE OF THE BACK, curving
with it. Two appear: one a pale yellow CRESCENT, the other a pale yellow SPIRAL.

SP-003 VIOLET BIRD: slender bird-like creature, deep violet plumage, long thin orange legs, short curved
beak, rounded head, large eyes, small wings held close. Rune UNDER THE LEFT WING, barely glimpsed: a white
HOOK.

SP-004 MOSSY SLEEPER: a plump low creature covered in soft moss-like fur, shaped like a rounded stone,
broad calm face, tiny ears, no visible legs at rest. Rune on the LEFT FLANK, faint: a sea-green WAVE.

SP-005 PALE BLUE WATCHER: a small pale-blue creature sitting up on its hind legs, long floppy ears, slim
body, tufted tail, alert pointed muzzle. Rune at the BASE OF THE RIGHT EAR: an orange CHEVRON.

SP-006 RUST SHELLBACK: a stocky rust-red quadruped with a rounded shell-like back, two short blunt horns,
thick legs. Rune in the CENTRE OF THE SHELL: a deep blue RING.

SP-007 SILVER PROWLER: a slim silver-grey creature with a long ringed tail, large round eyes, short dense
fur. Rune at the TIP OF THE TAIL: a pink TEARDROP.

RUNE RULES — absolute:
- SIZE: a rune is calibrated on a one-tile creature and keeps roughly that ABSOLUTE size on every creature.
  On a larger creature it therefore looks proportionally SMALLER. Runes must be small and modest, never
  large markings. Seen from afar they are barely noticeable, and that is intended.
- The rune is ON the body, never on top of it: it follows the curve of the surface and is interrupted by
  fur or a fold, like a natural marking. Never a sticker.
- ONE rune per creature. ONE single continuous stroke, drawable without lifting the pen. ONE colour.
- No two creatures wear the same rune shape. Humans wear no rune.
"""

MAP = """
FRAME AND SCALE — 1536 x 1152 pixels, representing a grid of 32 columns by 24 rows of square tiles. Do NOT
draw the grid.
- A standing human is 1 tile tall: ONE THIRTY-SECOND of the image width. Reference scale, everything else
  follows from it. A base creature is 1 tile.

FOOTPRINT RULE — CONTAINED SIDEWAYS: nothing sticks out laterally beyond the stated tiles. FILLED: the
silhouette reaches into the last twenty percent of the boundary tiles. Upwards it MAY overflow: tall
elements rise above their footprint and hide what is behind.

BUILDINGS ARE SQUARE TO THE MAP — every building faces the camera straight on, its walls parallel to the
grid axes. Never turned at an angle.

CAMERA — steeply down, about seventy degrees from horizontal, like a classic top-down role playing game
map. Ground fills the frame. NO horizon, NO sky, NO clouds, NO distant mountains, no vanishing point.
Roofs and treetops seen from above. Fixed framing.

LIGHT — the sun comes from the UPPER LEFT. Every shadow falls to the LOWER RIGHT. Shadows are SIMPLE:
plain, soft-edged, one per object, no elaborate gradient, no second light source. The image is BRIGHT and
its colours are FRANK and clear — never muted, greyed or washed out. No deep shadow anywhere.

SHARPNESS — perfectly sharp edge to edge. No blur, no haze, no depth of field, no soft focus.

RESTRAINT — the ground stays calm and readable: FEW flowers, plain grass without dense clutter, no carpet
of small details. Water is CALM with very few reflections and no sparkle.

BOTTOM LEFT CORNER — leave the very bottom left tile as plain ground.

ROADS FIRST:
- MAIN PATH: horizontal along row 16, edge to edge, 1 tile wide.
- CENTRE PATH: vertical along column 21, from the healing centre's door to the bottom edge, crossing the
  river on a bridge.
- COTTAGE PATH: vertical along column 6, from the cottage door to the river, crossed by a bridge.
No path ends in water or stops nowhere.

BUILDINGS:
- HEALING CENTRE, tiles (14,1) to (29,10): 16 tiles wide, HALF the image width, by far the largest, CUT
  OFF by the TOP edge — only its lower part and entrance visible. Wide doorway at tile (21,10), emblem
  above, lantern beside.
- COTTAGE, tiles (2,4) to (11,9): 10 tiles wide, just under a THIRD of the image width, 6 deep. Door at
  tile (6,9). Fenced vegetable garden on tiles (2,10) to (9,14), gate at tile (6,14).
- GATEWAY, tiles (25,12) to (28,16): 4 tiles wide, ONE EIGHTH of the image width. A tall vertical sheet of
  water upright in a stone frame, like a pool turned on its side, rippling slowly, faintly revealing
  another landscape behind it. Pale turquoise, calm.
- WATCHTOWER, tiles (2,18) to (5,22).

WATER — a narrow STREAM from tile (13,1) to tile (13,17), feeding a RIVER across rows 20 and 21, edge to
edge. Bridges on tiles (6,20)-(6,21) and (21,20)-(21,21).

PEOPLE — humans reflect real humanity: varied skin tones, hair types and body types, without exoticism.

PLACEMENT — for each, what it does, which way it FACES, which way it MOVES:
- tile (21,12): THE PLAYER CHARACTER, a young human just out of the healing centre, walking DOWNWARDS
  along the centre path, seen from behind, FACING DOWN, looking down the path.
- tile (21,13): SP-001 walking DOWNWARDS just ahead of them, FACING DOWN, clearly together.
- tiles (16,17) and (17,17): TWO humans standing on the main path FACING EACH OTHER, in conversation, the
  left one gesturing, both looking at each other.
- tile (5,12): a human kneeling in the vegetable garden, FACING RIGHT, looking DOWN at the soil, watering
  can beside them.
- tiles (11,18) and (12,18): the two SP-002 playing — the left one crouched low FACING RIGHT looking up at
  the other, the right one mid-leap moving LEFT, FACING LEFT.
- tile (14,18): SP-003 still at the stream's edge, FACING LEFT, head lowered, drinking.
- tile (25,18): SP-004 asleep in the grass, curled up, eyes closed.
- tile (9,7): SP-005 sitting up near the cottage, FACING UP-RIGHT, sniffing the air.
- tile (27,17): SP-006 walking slowly LEFT towards the gateway, FACING LEFT.
- tile (18,21): SP-007 sitting on a boulder by the river, FACING DOWN towards the water.

Creatures and people are drawn with the SAME level of simplification as the scenery.
No text, no interface, no logos, no grid lines.
"""

JOBS = {
    "b4": {
        "style": "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular "
                 "highlights and rim light, cel shading in two crisp bands, no outline.",
        "reference": "da-gb-b4v6-scene.png",
        "anchor": "STYLE REFERENCE — ./{ref} is the exact target. Reproduce ITS rendering with no "
                  "deviation whatsoever: the same modelling of volumes, the same crisp two-band cel "
                  "shading, the same frank saturated colours, the same amount of surface detail, the same "
                  "degree of stylisation. If anything you produce looks smoother, greyer, softer or more "
                  "photographic than that image, it is wrong. Take ONLY the style from it — its layout, "
                  "creatures and lighting do not apply; the map below does.",
    },
    "b10": {
        "style": "Art style: stylised village-strategy game look — clean sculpted volumes with smooth "
                 "matte surfaces, crisp readable silhouettes, warm saturated but natural colours, tidy "
                 "uncluttered ground, gentle ambient occlusion under objects, no outline, no texture "
                 "noise. Everything reads as a neat handcrafted miniature village seen from above.",
        "reference": None,
        "anchor": "",
    },
}

arguments = []
for key, job in JOBS.items():
    anchor = job["anchor"].format(ref=job["reference"]) if job["reference"] else ""
    prompt = f"{job['style']}\n\n{anchor}\n{CREATURES}\n{MAP}"
    (ASSETS / f"prompt-{key}-r15-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-{key}-r15-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

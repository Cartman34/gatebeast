#!/usr/bin/env python3
"""Fourteenth art direction round.

New in this round, from the review:
- runes follow the surface of the body instead of sitting on top of it, and the violet bird's rune moves
  under its wing, an easy flat spot;
- every character states what it does, which way it faces and which way it moves — the recurring "walking
  down while looking up" defect came from leaving that unsaid;
- humans reflect real humanity, all origins and body types;
- the human coming out of the healing centre is the player character;
- the flat-shaded direction must be perfectly sharp: the previous image had an odd ambient blur;
- the toon direction is anchored harder to its reference image, having drifted again.

Style wording and creature sheets come from the conception, word for word. The witness tile is stamped
afterwards, never drawn here.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

CREATURES = """
CREATURES — draw exactly these animals, nothing else, no other species. None of them has a human face.

A — AMBER FOX CUB: a small round quadruped the size of a fox cub. Warm amber fur (#D98A33) over back and
head, cream belly and muzzle (#F5E6CC), four short legs with cream paws, two large rounded ears amber
outside and cream inside, big dark friendly eyes, short thick tail with a cream tip. Rune on the MIDDLE OF
THE FOREHEAD, a flat area, clearly visible: a turquoise ARCH.

B — GREEN STUB: a small round mossy-green quadruped, barely taller than wide, smooth rounded back, short
stubby legs, wide friendly mouth, small dark eyes, no tail. Rune on the MIDDLE OF THE BACK, curving with
the back. Two of them appear: one wears a pale yellow CRESCENT, the other a pale yellow SPIRAL. Same
species, same position, same colour, different runes.

C — VIOLET BIRD: a slender bird-like creature, deep violet plumage, long thin orange legs, short curved
beak, rounded head with large eyes, small wings held close. Rune UNDER THE LEFT WING, on a flat hidden
area, barely glimpsed: a glowing white HOOK.

D — MOSSY SLEEPER: a plump low creature covered in soft moss-like fur, shaped like a rounded stone, broad
calm face, tiny ears, no visible legs when resting. Rune on the LEFT FLANK, faint, almost lost in the fur:
a sea-green WAVE.

E — PALE BLUE WATCHER: a small pale-blue creature sitting up on its hind legs, long floppy ears, slim body,
tufted tail, alert pointed muzzle. Rune at the BASE OF THE RIGHT EAR, clearly visible: an orange CHEVRON.

F — RUST SHELLBACK: a stocky rust-red quadruped with a rounded shell-like back, two short blunt horns,
thick legs, slow heavy stance. Rune in the CENTRE OF THE SHELL, a naturally flat plate: a deep blue RING.

G — SILVER PROWLER: a slim silver-grey creature with a long ringed tail, large round eyes, short dense fur,
light agile build. Rune at the TIP OF THE TAIL: a pink TEARDROP.

RUNE RULES — absolute, broken in every previous attempt:
- The rune is ON the body, never ON TOP of it: it follows the curve of the surface, bends with it, and is
  interrupted by fur or a fold like a marking would be. A rune drawn flat over a rounded volume reads as a
  sticker and ruins the animal.
- ONE rune per creature. Never two, never a repeated motif.
- ONE SINGLE CONTINUOUS STROKE, drawable without lifting the pen. Never several separate pieces, never a
  shape surrounded by dots or a frame.
- One single colour per rune.
- No two creatures wear the same rune shape.
- Humans wear no rune.
"""

MAP = """
FRAME AND SCALE — the image is 1536 x 1152 pixels and represents a grid of 32 columns by 24 rows of square
tiles. Do NOT draw the grid. Sizes are given in tiles and as a fraction of the frame; respect the fraction.
- A standing human is 1 tile tall: ONE THIRTY-SECOND of the image width. This is the reference scale and
  the one that keeps drifting — everything else follows from it.
- A base creature is 1 tile.

FOOTPRINT RULE — a footprint is the ground an element covers. CONTAINED SIDEWAYS: nothing sticks out
laterally beyond the stated tiles. FILLED: the silhouette reaches into the last twenty percent of the
boundary tiles, never floating small inside its box. Upwards it MAY overflow: tall elements rise above
their footprint on screen and hide what stands behind them.

CAMERA — looking steeply down at the ground, about seventy degrees from horizontal, like a classic
top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, NO clouds, NO distant
mountains, no vanishing point. Roofs and treetops seen from above. This framing is fixed.

LIGHT — the sun comes from the UPPER LEFT. Every shadow falls to the LOWER RIGHT, same length and softness
throughout. The image is BRIGHT: high open daylight, light values dominant, no deep or heavy shadow,
nothing murky. Contrast comes from brightening what matters, never from darkening the rest.

SHARPNESS — the whole image is perfectly sharp edge to edge. No blur, no haze, no depth of field, no soft
focus anywhere.

BOTTOM LEFT CORNER — leave the very bottom left tile as plain ground.

ROADS FIRST:
- MAIN PATH: horizontal along row 16, from the left edge to the right edge, 1 tile wide.
- CENTRE PATH: vertical along column 21, from the healing centre's door down to the bottom edge, crossing
  the river on a bridge.
- COTTAGE PATH: vertical along column 6, from the cottage door down to the river, crossed by a bridge.
No path ever ends in water or stops nowhere.

BUILDINGS — footprints on the ground:
- HEALING CENTRE, tiles (14,1) to (29,10): 16 tiles wide, HALF the image width — by far the largest
  building, CUT OFF by the TOP edge, only its lower part and entrance visible. Wide doorway at tile
  (21,10), emblem above, lantern beside.
- COTTAGE, tiles (2,4) to (11,9): 10 tiles wide, just under a THIRD of the image width, 6 deep. Door at
  tile (6,9). Fenced vegetable garden on tiles (2,10) to (9,14), gate at tile (6,14).
- GATEWAY, tiles (25,12) to (28,16): 4 tiles wide, ONE EIGHTH of the image width. A tall vertical sheet of
  water upright inside a stone frame, like a pool turned on its side, rippling slowly, faintly revealing
  another landscape behind it. Pale turquoise, calm.
- WATCHTOWER, tiles (2,18) to (5,22).

WATER — a narrow STREAM from tile (13,1) to tile (13,17), feeding a RIVER across rows 20 and 21 from edge
to edge. Bridges on tiles (6,20)-(6,21) and (21,20)-(21,21).

NATURE — grass, boulders, flower patches, tall grass, clusters of trees along the edges, reeds by the
river.

PEOPLE — humans reflect real humanity: different skin tones, hair types and body types, mixed without
exoticism, as an ordinary village population.

PLACEMENT — eight creatures and four humans. For each one, what it does, which way it FACES, and which way
it MOVES:
- tile (21,12): THE PLAYER CHARACTER, a young human who has just come out of the healing centre, walking
  DOWNWARDS along the centre path, seen from behind, FACING DOWN, looking DOWN the path ahead.
- tile (21,13): creature A walking DOWNWARDS just ahead of the player character, FACING DOWN, clearly
  together with them.
- tiles (16,17) and (17,17): TWO humans standing still on the main path, FACING EACH OTHER, in
  conversation, the left one gesturing with one hand, both looking at each other.
- tile (5,12): a human kneeling in the vegetable garden, FACING RIGHT and looking DOWN at the soil they
  are working, watering can beside them.
- tiles (11,18) and (12,18): the TWO creatures B playing — the left one crouched low FACING RIGHT and
  looking up at the other, the right one mid-leap moving LEFT, FACING LEFT.
- tile (14,18): creature C standing still at the stream's edge, FACING LEFT, head lowered, drinking.
- tile (25,18): creature D asleep in the grass, curled up, eyes closed, not looking anywhere.
- tile (9,7): creature E sitting up near the cottage, FACING UP-RIGHT, sniffing the air, not moving.
- tile (27,17): creature F walking slowly LEFT towards the gateway, FACING LEFT.
- tile (18,21): creature G sitting on a boulder by the river, FACING DOWN towards the water, watching it,
  not moving.

Creatures and people are drawn with exactly the SAME level of simplification as the scenery.
No text, no interface, no logos, no grid lines.
"""

STYLES = {
    "b4": "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and "
          "rim light, cel shading in two crisp bands, no outline.",
    "b7": "Art style: flat colour areas with no outline at all, given one soft volumetric shading pass so "
          "shapes feel rounded and lit. Restrained natural palette, no texture, low detail density. One "
          "single consistent treatment across the whole image.",
    "b8": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, restrained natural palette of greens and earth tones, low "
          "detail density. The outline is the defining feature: confident, even weight, always present.",
    "b9": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, low detail density — with a frankly POP palette: bright, "
          "luminous, saturated colours, cheerful and energetic, while staying natural enough to avoid a "
          "candy look. Bright saturated colour is reserved for what should draw the eye — the creatures, "
          "the people, the gateway; scenery stays calmer.",
}

STYLE_REFERENCES = {
    "b4": "da-gb-b4v6-scene.png",
    "b7": "da-b7-r13-scene.png",
    "b8": "da-b8-r13-scene.png",
    "b9": "da-b9-r13-scene.png",
}

arguments = []
for key, style in STYLES.items():
    prompt = (
        f"{style}\n\n"
        f"STYLE REFERENCE — look at ./{STYLE_REFERENCES[key]} and reproduce ITS rendering style exactly: "
        f"the same line treatment, the same shading, the same level of detail, the same degree of "
        f"stylisation. This is the strictest requirement of the whole job. Take ONLY the style from it — "
        f"its layout, its creatures and its lighting do not apply, the map below does.\n"
        f"{CREATURES}\n{MAP}"
    )
    (ASSETS / f"prompt-{key}-r14-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-{key}-r14-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

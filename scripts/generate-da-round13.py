#!/usr/bin/env python3
"""Thirteenth art direction round.

Every constraint that kept slipping is now stated the way the conception states it:
- footprints are given in tiles AND as an explicit fraction of the frame, since the generator reasons in
  proportions, not in coordinates;
- an element is contained horizontally, fills its footprint, and may overflow upwards — the footprint is
  the ground;
- the sun comes from the upper left, shadows fall to the lower right, everywhere and in every image;
- the image stays bright: high light, light values dominant, no deep shadow;
- creatures come from the conception's witness sheets, word for word, runes included;
- each direction receives its own validated image as a STYLE reference, because the wording alone let the
  toon direction drift into a 3D render.

The witness tile is stamped afterwards by stamp-witness-tile.py, never drawn here.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

CREATURES = """
CREATURES — draw exactly these animals, nothing else, no other species:

A — AMBER FOX CUB: a small round quadruped the size of a fox cub. Warm amber fur (#D98A33) over back and
head, cream belly and muzzle (#F5E6CC), four short legs with cream paws, two large rounded ears amber
outside and cream inside, big dark friendly eyes, short thick tail with a cream tip. Rune on the MIDDLE OF
THE FOREHEAD, clearly visible: a turquoise ARCH.

B — GREEN STUB: a small round mossy-green quadruped, barely taller than wide, smooth rounded back, short
stubby legs, wide friendly mouth, small dark eyes, no tail. Rune on the MIDDLE OF THE BACK. Two of them
appear: one wears a pale yellow CRESCENT, the other a pale yellow SPIRAL. Same species, same position,
same colour, different runes.

C — VIOLET BIRD: a slender bird-like creature, deep violet plumage, long thin orange legs, short curved
beak, rounded head with large eyes, small wings held close. Rune on the UPPER CHEST, discreet, half hidden
by plumage: a glowing white HOOK.

D — MOSSY SLEEPER: a plump low creature covered in soft moss-like fur, shaped like a rounded stone, broad
calm face, tiny ears, no visible legs when resting. Rune on the LEFT FLANK, faint, almost lost in the fur:
a sea-green WAVE.

E — PALE BLUE WATCHER: a small pale-blue creature sitting up on its hind legs, long floppy ears, slim body,
tufted tail, alert pointed muzzle. Rune at the BASE OF THE RIGHT EAR, clearly visible: an orange CHEVRON.

F — RUST SHELLBACK: a stocky rust-red quadruped with a rounded shell-like back, two short blunt horns,
thick legs, slow heavy stance. Rune in the CENTRE OF THE SHELL, clearly visible: a deep blue RING.

G — SILVER PROWLER: a slim silver-grey creature with a long ringed tail, large round eyes, short dense fur,
light agile build. Rune at the TIP OF THE TAIL: a pink TEARDROP.

RUNE RULES — absolute, they have been broken in every previous attempt:
- ONE rune per creature. Never two, never a repeated motif.
- Each rune is ONE SINGLE CONTINUOUS STROKE, drawable without lifting the pen. Never several separate
  pieces, never a shape surrounded by dots or a frame, never a composed pattern.
- One single colour per rune.
- No two creatures in this image wear the same rune shape.
- Humans wear no rune at all.
"""

MAP = """
FRAME AND SCALE — the image is 1536 x 1152 pixels and represents a grid of 32 columns by 24 rows of square
tiles. Do NOT draw the grid. Sizes below are given in tiles AND as a fraction of the frame; respect the
fraction.
- A standing human is 1 tile tall: ONE THIRTY-SECOND of the image width. This is the reference scale and
  the one that keeps drifting — everything else follows from it.
- A base creature is 1 tile.

FOOTPRINT RULE — a footprint is the ground the element covers. It is CONTAINED SIDEWAYS: nothing sticks
out laterally beyond the stated tiles. It is FILLED: the silhouette reaches into the last twenty percent
of the boundary tiles, never floating small inside its box. Upwards it MAY overflow: tall elements rise
above their footprint on screen and hide what stands behind them.

CAMERA — looking steeply down at the ground, about seventy degrees from horizontal, like a classic
top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, NO clouds, NO distant
mountains, no vanishing point. Roofs and treetops seen from above. This framing is fixed: never move the
camera closer or further.

LIGHT — the sun comes from the UPPER LEFT. Every shadow falls to the LOWER RIGHT, with the same length and
softness throughout, for buildings, trees, rocks, creatures and people alike. The image is BRIGHT: high
open daylight, light values dominant, no deep or heavy shadow anywhere, nothing murky. Contrast is gained
by brightening what matters, never by darkening the rest.

BOTTOM LEFT CORNER — leave the very bottom left tile as plain ground.

ROADS FIRST:
- MAIN PATH: horizontal along row 16, from the left edge to the right edge, 1 tile wide.
- CENTRE PATH: vertical along column 21, from the healing centre's door down to the bottom edge, crossing
  the river on a bridge.
- COTTAGE PATH: vertical along column 6, from the cottage door down to the river, crossed by a bridge.
No path ever ends in water or stops nowhere.

BUILDINGS — footprints on the ground:
- HEALING CENTRE, tiles (14,1) to (29,10): 16 tiles wide, HALF the image width — by far the largest
  building. CUT OFF by the TOP edge: only its lower part and entrance are visible. Wide doorway at tile
  (21,10), emblem above it, lantern beside it.
- COTTAGE, tiles (2,4) to (11,9): 10 tiles wide, just under a THIRD of the image width, 6 tiles deep.
  Door at tile (6,9). Fenced vegetable garden on tiles (2,10) to (9,14), gate at tile (6,14).
- GATEWAY, tiles (25,12) to (28,16): 4 tiles wide, ONE EIGHTH of the image width. A tall vertical sheet of
  water standing upright inside a stone frame, like a pool turned on its side, rippling slowly, faintly
  revealing another landscape behind it. Pale turquoise, calm.
- WATCHTOWER, tiles (2,18) to (5,22).

WATER — a narrow STREAM from tile (13,1) to tile (13,17), feeding a RIVER across rows 20 and 21 from edge
to edge. Bridges on tiles (6,20)-(6,21) and (21,20)-(21,21).

NATURE — grass, boulders, flower patches, tall grass, clusters of trees along the edges, reeds by the
river.

PLACEMENT — eight creatures and four humans, everyone busy, poses readable, the whole scene warm and
positive:
- tile (21,12): a human walking DOWN the centre path from the healing centre; on tile (21,13) creature A
  walking with them, clearly together.
- tiles (16,17) and (17,17): TWO humans face to face on the main path, in conversation, one gesturing.
- tile (5,12): a human kneeling in the vegetable garden, working the soil, watering can beside them.
- tiles (11,18) and (12,18): the TWO creatures B playing together — one crouched low, the other mid-leap
  over it.
- tile (14,18): creature C drinking at the stream's edge, head lowered.
- tile (25,18): creature D dozing in the grass near the gateway.
- tile (9,7): creature E sitting up near the cottage, sniffing the air.
- tile (27,17): creature F slowly crossing the grass towards the gateway.
- tile (18,21): creature G perched on a boulder by the river, watching the water.

Creatures and people are drawn with exactly the SAME level of simplification as the scenery.
No text, no interface, no logos, no grid lines.
"""

STYLES = {
    "b4": "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and "
          "rim light, cel shading in two crisp bands, no outline, subtle depth of field.",
    "b7": "Art style: flat colour areas with no outline at all, given one soft volumetric shading pass so "
          "shapes feel rounded and lit. Restrained natural palette, no texture, low detail density. One "
          "single consistent treatment across the whole image.",
    "b8": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, restrained natural palette of greens and earth tones, low "
          "detail density. The outline is the defining feature: confident, even weight, always present.",
    "b9": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, low detail density — with a frankly POP palette: bright, "
          "luminous, saturated colours, cheerful and energetic, while staying natural enough to avoid a "
          "candy look. The outline is the defining feature. Bright saturated colour is reserved for what "
          "should draw the eye — the creatures, the people, the gateway; scenery stays calmer.",
}

# Each direction is anchored to an image the owner judged, because wording alone let styles drift.
STYLE_REFERENCES = {
    "b4": "da-gb-b4v6-scene.png",
    "b7": "da-b7-r12-scene.png",
    "b8": "da-b8-r11-scene.png",
    "b9": "da-b9-r11-scene.png",
}

arguments = []
for key, style in STYLES.items():
    prompt = (
        f"{style}\n\n"
        f"STYLE REFERENCE — look at ./{STYLE_REFERENCES[key]} and reproduce ITS rendering style exactly: "
        f"the same line treatment, the same shading, the same level of detail, the same degree of "
        f"stylisation. Take ONLY the style from it. Its layout, its creatures and its lighting do not "
        f"apply — the map below does.\n"
        f"{CREATURES}\n{MAP}"
    )
    (ASSETS / f"prompt-{key}-r13-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-{key}-r13-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

#!/usr/bin/env python3
"""Twelfth art direction round: runes, eight creatures, and the three styles corrected.

Style descriptions are no longer written here: they are read from the conception, where they are frozen
(referentiels/visuel/directions-en-lice.md). Only the review's own corrections are applied on top, and each
one is stated explicitly.

New in this round:
- every creature from the other side wears its own RUNE, a small glowing symbol, different on each one and
  never the subject of the image;
- three more creatures of new, distinct species, bringing the scene to eight;
- b8 is less grainy, less dark, slightly less detailed — dosed, not stripped;
- b9's palette is hierarchised: bright colours only where the eye should go;
- b4 returns to its original round-six wording;
- b7 is untouched: the owner retained it.

The witness tile is NOT drawn here; it is stamped afterwards by stamp-witness-tile.py.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

SHEET = (
    "The amber creature: a small round quadruped the size of a fox cub. Warm amber fur (#D98A33) over back "
    "and head, cream belly and muzzle (#F5E6CC), four short legs with cream paws, two large rounded ears "
    "amber outside and cream inside, big dark friendly eyes, short thick tail with a cream tip, and one "
    "single glowing turquoise arch-shaped rune on the middle of its forehead."
)

RUNES = (
    "RUNES — every creature in this image comes from another world, and each one wears a RUNE: a small "
    "glowing symbol somewhere on its body. Each rune is DIFFERENT from every other — a distinct simple "
    "shape: an arch, a crescent, a spiral, a chevron, a ring, a teardrop, a wave, a hook. Every rune is "
    "ONE SINGLE CONTINUOUS STROKE — never several separate pieces, never a composed pattern — and ONE "
    "SINGLE COLOUR. A "
    "rune glows. How visible it is depends on the SPECIES: on some creatures it is bold and plain to see, "
    "on others faint or half hidden by fur — but within one species, the rune always sits on the SAME part "
    "of the body. Shape and colour differ from one creature to the next, even within a species. A rune "
    "must never look like a badge stuck onto the animal, and never become the subject of the image. The "
    "two creatures of the same green species share the same rune position but not the same rune. Humans "
    "wear no rune."
)

MAP = """
FRAME AND SCALE — absolute. The image is 1536 x 1152 pixels and represents a grid of 32 columns by 24 rows
of square tiles, each 48 x 48 pixels. Tile (1,1) is top left, tile (32,24) bottom right. A standing human
occupies exactly ONE tile. A base creature occupies ONE tile. Do NOT draw the grid. Do NOT move the camera
closer or further.

BUILDINGS ARE REALISTICALLY SIZED — compared to a one-tile human, buildings are huge. Footprints are given
in tiles below and must be respected literally. They are tall, so they hide what stands behind them.

CAMERA — looking steeply down at the ground, about seventy degrees from horizontal, like a classic
top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, NO clouds, NO distant
mountains, no vanishing point. Roofs and treetops seen from above.

BOTTOM LEFT CORNER — leave the very bottom left tile (1,24) as plain ground: a reference square is stamped
there afterwards.

ROADS FIRST:
- MAIN PATH: horizontal, along row 16, from the left edge to the right edge.
- CENTRE PATH: vertical, along column 21, from the healing centre's door down to the bottom edge, crossing
  the river on a bridge.
- COTTAGE PATH: vertical, along column 6, from the cottage door down to the river, crossed by a bridge.
No path ever ends in water or stops nowhere.

BUILDINGS — exact footprints:
- HEALING CENTRE, tiles (14,1) to (29,10), the largest by far, CUT OFF by the TOP edge: only its lower
  part and entrance are visible. Wide doorway at tile (21,10), emblem above, lantern beside. Its training
  ground lies behind it, off frame — do not show it.
- COTTAGE, tiles (2,4) to (11,9): ten tiles wide, six deep. Door at tile (6,9). Fenced vegetable garden on
  tiles (2,10) to (9,14), gate at tile (6,14).
- GATEWAY, tiles (25,12) to (28,16): a tall vertical sheet of water standing upright inside a stone frame,
  like a pool turned on its side, rippling slowly, faintly revealing another landscape behind it. Pale
  turquoise, calm.
- WATCHTOWER, tiles (2,18) to (5,22).

WATER — a narrow STREAM from tile (13,1) to tile (13,17), feeding a RIVER across rows 20 and 21 from edge
to edge. Bridges on tiles (6,20)-(6,21) and (21,20)-(21,21).

NATURE — grass, boulders, flower patches, tall grass, clusters of trees along the edges, reeds by the
river.

CHARACTERS — EIGHT creatures and four humans, everyone busy, every pose readable, the whole scene warm and
positive:
- tile (21,12): a human walking DOWN the centre path from the healing centre, and on tile (21,13) the
  amber creature from the reference walking with them — clearly together.
- tiles (16,17) and (17,17): TWO humans face to face on the main path, in conversation, one gesturing.
- tile (5,12): a fourth human kneeling in the vegetable garden, working the soil, watering can beside them.
- tiles (11,18) and (12,18): TWO creatures of the SAME species, small round and green, playing together —
  one crouched low, the other mid-leap over it.
- tile (14,18): a slender purple bird-like creature drinking at the stream's edge, head lowered.
- tile (25,18): a plump mossy creature dozing peacefully in the grass near the gateway.
- tile (9,7): a NEW species — a small pale-blue creature with long floppy ears and a tufted tail, sitting
  up on its hind legs, sniffing the air near the cottage.
- tile (27,17): a NEW species — a stocky rust-red creature with a rounded shell-like back and short horns,
  slowly crossing the grass towards the gateway.
- tile (18,21): a NEW species — a slim silver-grey creature with a long ringed tail and large eyes,
  perched on a boulder by the river, watching the water.

Late afternoon daylight, warm and bright, every element casting its own shadow. Characters and creatures
are drawn with exactly the SAME level of simplification as the scenery. The art style described above is
applied uniformly to every element, without exception.
No text, no interface, no logos, no grid lines.
"""

# Frozen in referentiels/visuel/directions-en-lice.md — reused word for word, never reformulated.
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
          "candy look. The outline is the defining feature.",
}

# Review corrections, applied on top of the frozen style and stated explicitly. Dosed, not stripped.
CORRECTIONS = {
    "b8": " CORRECTION for this round: lighten it. Slightly brighter overall, less dark in the shadows, no "
          "grain or speckled texture at all on the ground and foliage, and a little less small detail — a "
          "measured reduction, not a stripping down.",
    "b9": " CORRECTION for this round: hierarchise the palette. Bright saturated colour is reserved for "
          "what should draw the eye — the characters and the gateway. The scenery, grass, paths and trees "
          "stay clearly calmer and more muted, so the image has somewhere to look. Never let every colour "
          "compete.",
    "b4": "",
    "b7": "",
}

REFERENCES = {"b8": "da-gb-b8v8-creature.png", "b9": "da-gb-b8v8-creature.png",
              "b4": "da-gb-b4v7-creature.png", "b7": "da-gb-b7v7-creature.png"}

arguments = []
for key, style in STYLES.items():
    prompt = (
        f"{style}{CORRECTIONS[key]}\n\n"
        f"The reference image ./{REFERENCES[key]} tells you WHICH ANIMAL the amber creature is — colours, "
        f"proportions, markings — and nothing about the scene.\n\n{SHEET}\n\n{RUNES}\n{MAP}"
    )
    (ASSETS / f"prompt-{key}-r12-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-{key}-r12-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

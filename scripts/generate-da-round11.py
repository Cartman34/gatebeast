#!/usr/bin/env python3
"""Eleventh art direction round: realistic building scale, a livelier scene, four directions.

Naming convention adopted from this round on: da-<direction>-r<round>-<kind>.png, so files sort by
direction then round and read at a glance.

Frame: 1536 x 1152 pixels, 32 x 24 tiles of 48 pixels — exact in both directions.

What changes: buildings are sized realistically against a one-tile human — the cottage covers ten tiles by
six on the ground, the healing centre sixteen by ten and is cut off by the top edge, its training ground
hidden behind it and out of frame entirely. Five creatures and four humans, two of them in conversation,
two creatures interacting. Everything stays positive.
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
    "single glowing turquoise arch mark (#3FC3BD) on the middle of its forehead — nothing else turquoise."
)

MAP = """
FRAME AND SCALE — absolute. The image is 1536 x 1152 pixels and represents a grid of 32 columns by 24 rows
of square tiles, each 48 x 48 pixels. Tile (1,1) is top left, tile (32,24) bottom right. A standing human
occupies exactly ONE tile. A base creature occupies ONE tile. Do NOT draw the grid. Do NOT move the camera
closer or further.

BUILDINGS ARE REALISTICALLY SIZED — this is the point of this image and the previous attempt failed here.
Compared to a one-tile human, buildings are huge. Their footprint is given in tiles below and must be
respected literally. They are also TALL, so they hide whatever stands behind them, which is expected.

CAMERA — looking steeply down at the ground, about seventy degrees from horizontal, like a classic
top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, NO clouds, NO distant
mountains, no vanishing point. Roofs and treetops seen from above.

BOTTOM LEFT CORNER — leave the very bottom left tile (1,24) as plain ground, with no important element on
it. A scale reference square is stamped there afterwards and must not overlap anything meaningful.

ROADS FIRST — draw the paths before anything else, and let nothing contradict them:
- MAIN PATH: horizontal, along row 16, from the left edge to the right edge.
- CENTRE PATH: vertical, along column 21, from the healing centre's door down to the main path and on to
  the bottom edge, crossing the river on a bridge.
- COTTAGE PATH: vertical, along column 6, from the cottage door down to the main path and on to the river,
  crossed by a second bridge.
No path ever ends in water or stops nowhere.

BUILDINGS — exact footprints, all towering over people:
- HEALING CENTRE, tiles (14,1) to (29,10): the largest building by far, sixteen tiles wide and ten deep.
  It is CUT OFF by the TOP edge of the image: only its lower part and its entrance are visible. Wide
  doorway on its bottom side at tile (21,10), an emblem above it, a lantern beside it. Its training ground
  lies BEHIND it, off frame — do not show it.
- COTTAGE, tiles (2,4) to (11,9): ten tiles wide, six deep, a large family house. Door on its bottom side
  at tile (6,9). A fenced vegetable garden on tiles (2,10) to (9,14), gate on tile (6,14).
- GATEWAY, tiles (25,12) to (28,16): a tall vertical sheet of water standing upright inside a stone frame,
  like a pool turned on its side, rippling slowly, reflecting light, faintly revealing another landscape
  behind it. Pale turquoise, calm. A short branch path links it to the main path.
- WATCHTOWER, tiles (2,18) to (5,22): a wooden tower on stilts near the bottom left.

WATER — a narrow STREAM descends from tile (13,1) to tile (13,17), then feeds a wider RIVER running
horizontally across rows 20 and 21, from the left edge to the right edge. Water is crossed ONLY by bridges,
on tiles (6,20)-(6,21) and (21,20)-(21,21).

NATURE — grass, boulders, flower patches, tall grass, clusters of trees along the edges, reeds by the
river.

CHARACTERS — five creatures and four humans, everyone busy, every pose readable, the whole scene warm and
positive:
- tile (21,12): a human walking DOWN the centre path from the healing centre, and just ahead on tile
  (21,13) the amber creature from the reference walking with them — clearly together.
- tiles (16,17) and (17,17): TWO humans standing face to face on the main path, in conversation, one
  gesturing as they speak.
- tile (5,12): a fourth human kneeling in the vegetable garden, working the soil, watering can beside them.
- tiles (11,18) and (12,18): TWO creatures of the SAME species, small and round and green, playing
  together — one crouched low, the other mid-leap over it.
- tile (14,18): a slender purple bird-like creature drinking at the stream's edge, head lowered, tiny
  ripples at its beak.
- tile (25,18): a fifth creature, plump and mossy, dozing peacefully in the grass near the gateway.

Late afternoon daylight, warm and bright, every element casting its own shadow. Characters and creatures
are drawn with exactly the SAME level of simplification as the scenery. The art style described above is
applied uniformly to every single element of the image, without exception.
No text, no interface, no logos, no grid lines other than the filled witness tile.
"""

STYLES = {
    "b8": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, restrained natural palette of greens and earth tones, low "
          "detail density. The outline is the defining feature: confident, even weight, always present.",
    "b9": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, low detail density — with a frankly POP palette: bright, "
          "luminous, saturated colours, cheerful and energetic, while staying natural enough to avoid a "
          "candy look. The outline is the defining feature.",
    "b4": "Art style: warm toon render with soft sculpted volumes, painterly light, gentle gradients and "
          "readable surface detail, no outline anywhere. Rich and inviting rather than starkly simplified.",
    "b7": "Art style: flat colour areas with no outline at all, given one soft volumetric shading pass so "
          "shapes feel rounded and lit. Restrained natural palette, no texture, low detail density. One "
          "single consistent treatment across the whole image.",
}

REFERENCES = {"b8": "da-gb-b8v8-creature.png", "b9": "da-gb-b8v8-creature.png",
              "b4": "da-gb-b4v7-creature.png", "b7": "da-gb-b7v7-creature.png"}

arguments = []
for key, style in STYLES.items():
    prompt = (
        f"{style}\n\n"
        f"The reference image ./{REFERENCES[key]} tells you WHICH ANIMAL to draw — colours, proportions, "
        f"markings — and nothing about the scene.\n\n{SHEET}\n{MAP}"
    )
    (ASSETS / f"prompt-{key}-r11-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-{key}-r11-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

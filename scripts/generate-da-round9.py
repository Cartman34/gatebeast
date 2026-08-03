#!/usr/bin/env python3
"""Ninth art direction round: one single map, described tile by tile, rendered in three styles.

The scene is no longer described by zones but by grid coordinates, because the whole point of this round
is that the three directions show THE SAME map — only the rendering may differ.

Frame: 1536 x 1024 pixels, 24 x 16 tiles of 64 pixels. A human fits in one tile, a base creature too.
The camera framing of round six is locked: it is the framing the owner validated, and nothing here may
tighten it. Buildings grow in tiles, never by moving the camera closer.

Each direction's full prompt is written next to its image so the review page can display it.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"
ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"

SHEET = (
    "The amber creature: a small round quadruped the size of a fox cub. Warm amber fur (#D98A33) over back "
    "and head, cream belly and muzzle (#F5E6CC), four short legs with cream paws, two large rounded ears "
    "amber outside and cream inside, big dark friendly eyes, short thick tail with a cream tip, and one "
    "single glowing turquoise arch mark (#3FC3BD) on the middle of its forehead — nothing else turquoise."
)

MAP = """
FRAME AND SCALE — absolute, never negotiable. The image is 1536 x 1024 pixels and represents a grid of
24 columns by 16 rows of square tiles, each tile 64 x 64 pixels. Tile (1,1) is the top left corner, tile
(24,16) the bottom right. A standing human occupies exactly one tile. A base creature occupies one tile.
Do NOT draw the grid itself. Do NOT move the camera closer or further: the amount of ground visible is
fixed by this grid and must not change.

CAMERA — the camera looks steeply down at the ground, about seventy degrees from horizontal, like a
classic top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, NO clouds,
NO distant mountains, no vanishing point. Roofs and treetops are seen from above.

WITNESS TILE — in the very bottom left corner, on tile (1,16), draw a single clean square outline of one
tile, thin and discreet, as a scale reference. Nothing else marks the grid.

MAP LAYOUT — place every element on these exact tiles, identically in every version:
- COTTAGE, tiles (2,2) to (7,7): a large house, six tiles wide and six tall, clearly towering over people;
  its door is twice a human's height. Fenced vegetable garden on tiles (2,8) to (6,10).
- GATEWAY, tiles (11,1) to (14,5): a tall vertical sheet of water standing upright inside a stone frame,
  like a pool turned on its side. Its surface ripples slowly, reflects light and faintly reveals another
  landscape behind it. Pale turquoise, calm. The most striking object in the scene.
- WATCHTOWER, tiles (19,2) to (21,5): a wooden tower on stilts.
- HEALING CENTRE, tiles (18,10) to beyond the right edge of the image: a broad welcoming building, the
  largest structure of all, wide doorway with an emblem above it and a lantern beside it. It is CUT OFF by
  the right edge of the image — only part of it is visible, and that is intended.
- STREAM: a narrow stream running from tile (9,1) down to tile (11,11), then widening into a RIVER that
  runs from tile (8,12) to tile (20,14). A small wooden bridge crosses the river on tiles (11,12) to
  (12,13).
- PATHS: a dirt path runs horizontally along row 8 from the left edge to the right edge, and another runs
  vertically along column 15 from row 5 down to row 16. They cross on tile (15,8).
- NATURE elsewhere: grass, scattered boulders, flower patches, tall grass tufts, clusters of trees along
  the left and bottom edges.

CHARACTERS — everyone is doing something, motion readable in the pose:
- on tile (13,8), the amber creature from the reference, mid-stride, walking briskly towards the gateway,
  ears forward, tail up.
- on tile (11,10), a small round green creature crouched at the stream's edge, leaning down to drink, tiny
  ripples where its muzzle meets the water.
- on tile (6,12), a slender purple bird-like creature in mid-hop, wings half spread, chasing a butterfly.
- on tile (4,9), a human kneeling among the vegetable rows, working the soil, a watering can beside them.
- on tile (16,6), a second human walking the path towards the gateway, one arm raised mid-wave.

Late afternoon daylight, warm and bright, every element casting its own shadow on the ground.
No text, no interface, no logos, no grid lines other than the single witness tile.
"""

STYLES = {
    "b8": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, restrained natural palette, low detail density. The outline is "
          "the defining feature: confident, even weight, always present. Humans are drawn with exactly the "
          "same degree of simplification as the creatures.",
    "b4": "Art style: warm toon render with soft sculpted volumes, painterly light, gentle gradients and "
          "readable surface detail, no outline. Rich and inviting rather than starkly simplified. Humans "
          "are drawn with exactly the same degree of simplification as the creatures.",
    "b7": "Art style: hybrid of flat vector and toon render — clean flat colour areas with no outline, "
          "given one soft volumetric shading pass so shapes feel rounded and lit. Restrained natural "
          "palette, no texture. Humans must be simplified to the SAME level as the creatures: no fine "
          "facial detail, no fabric folds, no small accessories — plain rounded shapes.",
}

REFERENCES = {"b8": "da-gb-b8v8-creature.png", "b4": "da-gb-b4v7-creature.png",
              "b7": "da-gb-b7v7-creature.png"}

arguments = []
for key, style in STYLES.items():
    prompt = (
        f"{style}\n\n"
        f"The reference image ./{REFERENCES[key]} tells you WHICH ANIMAL to draw — colours, proportions, "
        f"markings — and nothing about the scene.\n\n{SHEET}\n{MAP}"
    )
    (ASSETS / f"prompt-{key}v9-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-gb-{key}v9-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

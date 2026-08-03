#!/usr/bin/env python3
"""Tenth art direction round: four directions, one map, described tile by tile.

Frame: 1536 x 1152 pixels, 32 x 24 tiles of 48 pixels — an exact division in both directions, so the grid
overlay of the review page falls true. A human occupies one tile, a base creature one tile.

The map is corrected so that it holds up tile by tile: no path ever ends in the water, every building
entrance opens onto a path, water is crossed only by bridges placed exactly where a path meets it, and the
healing centre has its own fenced training ground.

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
FRAME AND SCALE — absolute. The image is 1536 x 1152 pixels and represents a grid of 32 columns by 24 rows
of square tiles, each tile 48 x 48 pixels. Tile (1,1) is the top left corner, tile (32,24) the bottom
right. A standing human occupies exactly one tile; a base creature occupies one tile. Do NOT draw the grid.
Do NOT move the camera closer or further: the ground visible is fixed by this grid.

CAMERA — looking steeply down at the ground, about seventy degrees from horizontal, like a classic
top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, NO clouds, NO distant
mountains, no vanishing point. Roofs and treetops seen from above.

WITNESS TILE — on tile (1,24), the very bottom left corner, draw one SOLID FILLED square covering that
tile exactly, in a plain flat colour that contrasts with the ground. It is a scale reference: it must align
perfectly with the tile grid. Nothing else marks the grid.

ROADS FIRST — draw the paths before anything else, and let nothing contradict them:
- MAIN PATH: a dirt path running horizontally across the whole image along row 14, from the left edge to
  the right edge.
- SIDE PATH: a dirt path running vertically along column 20, from row 2 down to row 24, crossing the main
  path on tile (20,14).
- Every building entrance below connects to one of these two paths by a short branch path. NO path ever
  ends in water or stops in the middle of nowhere.

WATER — a narrow STREAM descends from tile (11,1) to tile (12,12), then turns and feeds a wider RIVER that
runs horizontally across rows 18 and 19 from the left edge to the right edge. Water is crossed ONLY by
bridges: a wooden bridge on tiles (20,18) to (20,19) where the side path crosses the river, and a second
small bridge on tiles (8,18) to (8,19) where a short branch path crosses it.

BUILDINGS — placed on these exact tiles, all clearly towering over people, their doors twice a human's
height:
- COTTAGE, tiles (3,3) to (8,8), with its door on the bottom side at tile (5,8); a short path leads from
  that door down column 5 to the main path. A FENCED VEGETABLE GARDEN on tiles (3,9) to (8,12), its gate
  on tile (6,12) opening onto the main path.
- GATEWAY, tiles (14,2) to (17,7): a tall vertical sheet of water standing upright inside a stone frame,
  like a pool turned on its side, its surface rippling slowly, reflecting light and faintly revealing
  another landscape behind it. Pale turquoise, calm. A short path runs from its base down column 16 to the
  main path. The most striking object of the scene.
- HEALING CENTRE, tiles (24,6) to (31,13): the largest building, a broad welcoming structure with a wide
  doorway on its bottom side at tile (27,13), opening directly onto the main path, an emblem above the
  door and a lantern beside it.
- TRAINING GROUND, tiles (21,7) to (23,13): a fenced open yard attached to the left of the healing centre,
  its gate on tile (22,13) opening onto the main path.
- WATCHTOWER, tiles (28,2) to (30,5): a wooden tower on stilts, a short path linking it to the side path.

NATURE — everywhere else: grass, scattered boulders, flower patches, tall grass tufts, clusters of trees
along the left, right and bottom edges, reeds along the river.

CHARACTERS — everyone doing something, motion readable in the pose:
- tile (16,14): the amber creature from the reference, mid-stride, walking briskly up the path towards the
  gateway, ears forward, tail up.
- tile (13,12): a small round green creature crouched at the stream's edge, leaning down to drink, tiny
  ripples where its muzzle meets the water.
- tile (9,16): a slender purple bird-like creature in mid-hop, wings half spread, chasing a butterfly.
- tile (5,10): a human kneeling among the vegetable rows, working the soil, a watering can beside them.
- tile (20,10): a second human walking down the side path, one arm raised mid-wave.

Late afternoon daylight, warm and bright, every element casting its own shadow on the ground.
Characters and creatures are drawn with the SAME level of simplification as the scenery — no more cartoon
than their surroundings, no less.
No text, no interface, no logos, no grid lines other than the single filled witness tile.
"""

STYLES = {
    "b8": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, restrained natural palette of greens and earth tones, low "
          "detail density. The outline is the defining feature: confident, even weight, always present.",
    "b9": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, low detail density — but a frankly POP palette: bright, "
          "luminous, saturated colours, cheerful and energetic, while staying natural enough to avoid a "
          "candy look. The outline is the defining feature.",
    "b4": "Art style: warm toon render with soft sculpted volumes, painterly light, gentle gradients and "
          "readable surface detail, no outline. Rich and inviting rather than starkly simplified.",
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
    (ASSETS / f"prompt-{key}v10-scene.txt").write_text(prompt, encoding="utf-8")
    arguments.append(f"{TARGET}/da-gb-{key}v10-scene.png")
    arguments.append(prompt)

sys.exit(subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode)

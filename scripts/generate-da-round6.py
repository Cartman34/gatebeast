#!/usr/bin/env python3
"""Sixth art direction round: keep round five's content, restore round three's camera angle.

Round five drifted: the camera tilted down towards eye level, a horizon and a sky appeared, and the map
stopped reading as a top-down world. Everything else about round five was right — the populated valley and
the water gateway — so only the camera is corrected here, and stated in terms that cannot drift: steep
downward angle, ground plane filling the frame, no horizon, no sky.

Nothing is ever deleted: each round writes its own files under its own version suffix.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"

SHEET = (
    "The amber creature, identical in every image: a small round quadruped the size of a fox cub. Warm "
    "amber fur (#D98A33) over the back and head, cream belly and muzzle (#F5E6CC), four short sturdy legs "
    "with cream paws. Two large rounded ears, amber outside, cream inside. Big dark friendly eyes, small "
    "rounded snout, short thick tail with a cream tip. One single glowing turquoise mark (#3FC3BD) shaped "
    "like a small arch on the middle of its forehead, and nothing else turquoise anywhere on the body."
)

SCENE_TEMPLATE = (
    "The reference image ./{reference} tells you WHICH ANIMAL to draw — colours, proportions, markings. "
    "It does NOT tell you how to draw the scene: the scene follows the art style stated above and nothing "
    "else.\n\n"
    f"{SHEET}\n\n"
    "CAMERA — this is the strictest requirement, and the previous attempt failed exactly here. The camera "
    "looks STEEPLY DOWN at the ground, about seventy degrees from horizontal, the way a classic top-down "
    "role playing game shows its world map. The ground plane fills the entire frame from edge to edge. "
    "There is NO horizon line, NO sky, NO clouds, NO distant mountains against the sky, and no vanishing "
    "point: you are looking down at the land, not across it. Trees and buildings are seen from above and "
    "slightly to the side, showing their roofs and tops.\n\n"
    "CONTENT — a wide, busy area of an inhabited valley, everything small in frame and none of it "
    "dominating:\n"
    "- THE GATEWAY: a tall vertical sheet of water standing upright inside a stone frame, like a pool "
    "turned on its side, its surface rippling slowly and faintly revealing another landscape behind it. "
    "Pale turquoise, calm. Seen from the same steep angle as everything else.\n"
    "- THREE creatures: the amber creature from the reference standing on a path, plus two other original "
    "small creatures of clearly different shapes and colours, in the same style.\n"
    "- TWO human characters, small, one walking a path, one near a building.\n"
    "- TWO buildings seen from above: a cottage with its garden, and a wooden watchtower or covered "
    "bridge.\n"
    "- NATURE: a stream feeding a wider river with a small bridge, boulders, tall grass and flower "
    "patches, clusters of trees, winding dirt paths linking everything.\n"
    "Late afternoon daylight, warm and bright, every element casting its own shadow on the ground. "
    "No text, no interface, no logos. Landscape format."
)

VARIANTS = {
    "b1": "Art style: hand-painted modern cartoon, round readable shapes, thin soft outlines, rich "
          "gradients and painterly texture, warm luminous palette, storybook feel.",
    "b2": "Art style: outline-free flat vector illustration, solid unshaded colour areas, hard-edged "
          "two-tone shading, no gradients and no texture at all, bright saturated palette.",
    "b4": "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and "
          "rim light, cel shading in two crisp bands, no outline, subtle depth of field.",
}


def run(arguments):
    return subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode


creatures = []
for key, style in VARIANTS.items():
    creatures.append(f"{TARGET}/da-gb-{key}v6-creature.png")
    creatures.append(f"{style} {SHEET} Draw the creature alone, three-quarter view, standing, plain very "
                     "light background. No text, no interface, no humans, no logos. Square format.")

print("--- creatures")
code = run(creatures)

scenes = []
for key, style in VARIANTS.items():
    scenes.append(f"{TARGET}/da-gb-{key}v6-scene.png")
    scenes.append(f"{style} {SCENE_TEMPLATE.format(reference=f'da-gb-{key}v6-creature.png')}")

print("--- scenes")
code = run(scenes) or code

sys.exit(code)

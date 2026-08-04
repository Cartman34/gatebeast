#!/usr/bin/env python3
"""Fourth art direction round: pull the camera properly back, and stop the creature looking pasted in.

Three corrections over the third round:
- the camera goes genuinely far: the creature is small on screen and a whole area of the map is visible,
  the way an overworld screen looks — the previous rounds kept creeping closer;
- the reference image constrains the creature's IDENTITY only, never the scene's rendering, because
  reusing it wholesale made two directions converge into the same picture;
- the creature must be drawn into the scene, lit by the scene's own light and casting its own shadow,
  rather than composited on top of it.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"

SHEET = (
    "The creature, always identical in every image: a small round quadruped the size of a fox cub. Warm "
    "amber fur (#D98A33) over the back and head, cream belly and muzzle (#F5E6CC), four short sturdy legs "
    "with cream paws. Two large rounded ears, amber outside, cream inside. Big dark friendly eyes, small "
    "rounded snout, short thick tail with a cream tip. One single glowing turquoise mark (#3FC3BD) shaped "
    "like a small arch on the middle of its forehead, and nothing else turquoise anywhere on the body."
)

SCENE_TEMPLATE = (
    "The reference image ./{reference} tells you WHICH ANIMAL to draw — its colours, proportions and "
    "markings. It does NOT tell you how to draw the scene: the scene's rendering must follow the art "
    "style stated above and nothing else. Do not copy the reference's background, lighting or framing.\n\n"
    f"{SHEET}\n\n"
    "Draw a wide overworld map screen, seen from a high top-down three-quarter camera, far enough that a "
    "whole area of the forest is visible at once: winding dirt paths crossing the clearing, several "
    "distinct patches of grass and flowers, a cluster of trees, scattered rocks, a small pond in one "
    "corner, and a faint glowing turquoise archway standing among the trees. This is a place to explore, "
    "not a close-up. The creature stands on a path and occupies barely one twelfth of the image height — "
    "small, but recognisable as the animal from the reference. It is drawn into the scene: lit by the "
    "same late afternoon daylight, casting its own soft shadow on the ground, never pasted on top. "
    "No text, no interface, no humans, no logos. Landscape format."
)

VARIANTS = {
    "b1": "Art style: hand-painted modern cartoon with round readable shapes, thin soft outlines, rich "
          "gradients and painterly texture, warm luminous palette, soft and storybook-like. Depth comes "
          "from painted light, not from line work.",
    "b2": "Art style: outline-free flat vector illustration, solid unshaded colour areas, hard-edged "
          "two-tone shading, no gradients and no texture at all, bright saturated palette, strong graphic "
          "simplicity. Everything reads as clean flat shapes.",
    "b4": "Art style: soft toon-shaded 3D render, sculpted rounded volumes, clear specular highlights and "
          "rim light, cel shading in two crisp bands, no outline, subtle depth of field. Everything looks "
          "modelled and lit in three dimensions rather than drawn.",
}


def run(arguments):
    return subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode


creatures = []
for key, style in VARIANTS.items():
    creatures.append(f"{TARGET}/da-gb-{key}v4-creature.png")
    creatures.append(f"{style} {SHEET} Draw the creature alone, three-quarter view, standing, plain very "
                     "light background. No text, no interface, no humans, no logos. Square format.")

print("--- creatures")
code = run(creatures)

scenes = []
for key, style in VARIANTS.items():
    scenes.append(f"{TARGET}/da-gb-{key}v4-scene.png")
    scenes.append(f"{style} {SCENE_TEMPLATE.format(reference=f'da-gb-{key}v4-creature.png')}")

print("--- scenes")
code = run(scenes) or code

sys.exit(code)

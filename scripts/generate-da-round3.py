#!/usr/bin/env python3
"""Third art direction round, built around one thread: the same creature must appear in every image.

Two guardrails, because a style sentence alone was not enough to keep a direction coherent:
- a written reference sheet, precise down to colours and proportions, reused word for word everywhere;
- the creature image itself, generated first, then handed to the scene generation as a visual reference —
  the scene is produced in the same directory, so the file is directly available to look at.

Framing is also pulled back: the previous round was too close to show the world.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"

# The reference sheet. Every image of every direction reuses this text unchanged.
SHEET = (
    "The creature, always identical in every image: a small round quadruped the size of a fox cub. Warm "
    "amber fur (#D98A33) over the back and head, cream belly and muzzle (#F5E6CC), four short sturdy legs "
    "with cream paws. Two large rounded ears, amber outside, cream inside. Big dark friendly eyes, small "
    "rounded snout, short thick tail with a cream tip. One single glowing turquoise mark (#3FC3BD) shaped "
    "like a small arch on the middle of its forehead, and nothing else turquoise anywhere on the body."
)

CREATURE = (
    f"{SHEET} Draw the creature alone, three-quarter view, standing, plain very light background. "
    "No text, no interface, no humans, no logos. Square format."
)

SCENE_TEMPLATE = (
    "First look carefully at the reference image ./{reference}, which shows the exact creature and the "
    "exact art style to reproduce. Reproduce both faithfully: same colours, same proportions, same "
    "markings, same rendering technique.\n\n"
    f"{SHEET}\n\n"
    "Draw a game map seen from a raised top-down three-quarter camera, at a comfortable distance: a forest "
    "clearing with a dirt path, grass tufts, scattered rocks and trees seen from above, and a faint glowing "
    "turquoise archway standing between two trees. The creature stands on the path and occupies about one "
    "eighth of the image height, small but clearly recognisable. Enough of the clearing is visible to "
    "understand the place. Late afternoon daylight, warm and bright. No text, no interface, no humans, no "
    "logos. Landscape format."
)

VARIANTS = {
    "b1": "Art style: modern cartoon with round readable shapes, thin soft outlines, gentle gradients "
          "instead of flat fills, warm luminous palette, soft and friendly rather than boldly graphic.",
    "b2": "Art style: outline-free modern flat illustration, solid shapes with no contour line, confident "
          "colour contrast and clear value structure, two-tone shading, bright palette, characterful.",
    "b4": "Art style: soft toon-shaded 3D look, rounded volumes with clear form and gentle rim light, cel "
          "shading with two tones, no visible outline, clean modern game look.",
}


def run(arguments):
    result = subprocess.run(["php", TOOL] + arguments, cwd=PROJECT)

    return result.returncode


creatures = []
for key, style in VARIANTS.items():
    creatures.append(f"{TARGET}/da-gb-{key}v3-creature.png")
    creatures.append(f"{style} {CREATURE}")

print("--- creatures")
code = run(creatures)

scenes = []
for key, style in VARIANTS.items():
    scenes.append(f"{TARGET}/da-gb-{key}v3-scene.png")
    scenes.append(f"{style} {SCENE_TEMPLATE.format(reference=f'da-gb-{key}v3-creature.png')}")

print("--- scenes")
code = run(scenes) or code

sys.exit(code)

#!/usr/bin/env python3
"""Generate art direction variants around the round pop family.

Two constraints drive this pass:
- the very same style sentence is reused for the creature and for the scene of one direction, so a direction
  is never judged on two inconsistent renderings;
- the scene uses the actual in-game camera: top-down, seen from a distance.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path("/home/sowapps/projects")
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"

CREATURE = (
    "Subject: an original friendly creature for a family video game, a small round quadruped with amber "
    "fur, large rounded ears and a glowing turquoise arch mark on its forehead, three-quarter view, plain "
    "very light background. No text, no interface, no humans, no logos. Square format."
)

SCENE = (
    "Subject: a top-down game map seen from above and from a distance, like a classic creature-collecting "
    "game: a small forest clearing at dusk with paths, grass patches and trees drawn from above, a faint "
    "glowing turquoise archway between two trees, and the same small amber creature standing on a path, "
    "small in frame. No text, no interface, no humans, no logos. Landscape format."
)

VARIANTS = {
    "b1": "Art style: modern cartoon with round readable shapes, thin soft outlines, gentle gradients "
          "instead of flat fills, warm luminous palette. Soft and friendly rather than bold and graphic.",
    "b2": "Art style: outline-free modern flat illustration, solid shapes with no contour line, soft "
          "two-tone shading, bright airy palette, strong silhouette readability.",
    "b3": "Art style: modern cartoon shapes finished with a light gouache texture, visible brush grain "
          "inside flat areas, slightly irregular hand-painted edges, warm palette.",
    "b4": "Art style: soft toon-shaded 3D look, rounded volumes with clear form and gentle rim light, "
          "cel shading with two tones, no visible outline, clean modern game look.",
    "b5": "Art style: geometric stylised cartoon, shapes built from clean angular facets and simple curves, "
          "confident graphic design, limited bold palette, crisp edges.",
    "b6": "Art style: soft painted illustration, no outlines, blended warm light, gentle atmospheric depth, "
          "storybook softness kept simple enough for game assets.",
}

arguments = []
for key, style in VARIANTS.items():
    arguments.append(f"{TARGET}/da-gb-{key}-creature.png")
    arguments.append(f"{style} {CREATURE}")
    arguments.append(f"{TARGET}/da-gb-{key}-scene.png")
    arguments.append(f"{style} {SCENE}")

result = subprocess.run(["php", TOOL] + arguments, cwd=PROJECT)
sys.exit(result.returncode)

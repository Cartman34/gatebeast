#!/usr/bin/env python3
"""Second art direction round: only the three surviving pop variants, with the owner's corrections applied.

Corrections carried into this round:
- the scene camera moves closer; the previous framing was too far to read anything at small size;
- every scene uses the same late afternoon daylight, so lighting never becomes a hidden variable;
- creature and scene of one direction still share the exact same style sentence.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[3]
TOOL = "conceptions/methode/outils/generate-image.php"
TARGET = "conceptions/gatebeast/assets/revue-da"

CREATURE = (
    "Subject: an original friendly creature for a family video game, a small round quadruped with warm "
    "amber and cream fur clearly dominant, large rounded ears, expressive lively face, and one small "
    "glowing turquoise arch mark on its forehead as the only turquoise element. Three-quarter view, plain "
    "very light background. No text, no interface, no humans, no logos. Square format."
)

SCENE = (
    "Subject: a game map seen from a raised top-down three-quarter camera, moderately close so that ground "
    "details are clearly readable: a forest clearing with a dirt path, grass tufts, a few trees and rocks "
    "seen from above, and a faint glowing turquoise archway between two trees. The same small amber "
    "creature stands on the path and occupies roughly one sixth of the image height, clearly visible. "
    "Late afternoon daylight, warm and bright. No text, no interface, no humans, no logos. Landscape format."
)

VARIANTS = {
    "b1": "Art style: modern cartoon with round readable shapes, thin soft outlines, gentle gradients "
          "instead of flat fills, warm luminous palette, soft and friendly rather than boldly graphic.",
    "b2": "Art style: outline-free modern flat illustration, solid shapes with no contour line, confident "
          "colour contrast and clear value structure so shapes read strongly, two-tone shading, bright "
          "palette, characterful rather than plain.",
    "b4": "Art style: soft toon-shaded 3D look, rounded volumes with clear form and gentle rim light, cel "
          "shading with two tones, no visible outline, clean modern game look with a distinct atmosphere.",
}

arguments = []
for key, style in VARIANTS.items():
    arguments.append(f"{TARGET}/da-gb-{key}v2-creature.png")
    arguments.append(f"{style} {CREATURE}")
    arguments.append(f"{TARGET}/da-gb-{key}v2-scene.png")
    arguments.append(f"{style} {SCENE}")

result = subprocess.run(["php", TOOL] + arguments, cwd=PROJECT)
sys.exit(result.returncode)

#!/usr/bin/env python3
"""Fifth art direction round: a populated world, seen wide.

What changes here:
- the scene must show the world, not a decor: three creatures, two human characters, two buildings, and
  several distinct natural features, so the owner can judge a real place;
- the camera pulls back further still;
- the gateway becomes a vertical sheet of water held in a frame, which is now the acted visual identity of
  the parallel plane;
- the reference image still constrains the creature's identity only, never the scene's rendering.
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
    "else. Never copy the reference's background, lighting or framing.\n\n"
    f"{SHEET}\n\n"
    "Draw a wide overworld map screen of a creature-collecting game, seen from a high top-down "
    "three-quarter camera, far enough that a whole inhabited valley fits in frame. It must contain, all "
    "clearly visible and none of them large in frame:\n"
    "- THE GATEWAY, the most striking element: a tall vertical sheet of water standing upright inside a "
    "stone frame, like a pool turned on its side. Its surface ripples slowly, reflects the light and "
    "faintly suggests another landscape behind it. Pale turquoise, calm, never a swirl and never a plain "
    "glow.\n"
    "- THREE creatures: the amber creature from the reference standing on a path, plus two other original "
    "small creatures of clearly different shapes and colours, drawn in the very same style.\n"
    "- TWO human characters, small in frame, drawn in the same style: one walking along a path, one "
    "standing near a building.\n"
    "- TWO buildings: a small cottage with a garden, and a larger structure such as a wooden watchtower or "
    "a covered bridge.\n"
    "- NATURE: a stream running into a wider river with a small bridge over it, boulders and rocky "
    "outcrops, tall grass and flower patches, a cluster of trees, and winding dirt paths connecting "
    "everything.\n"
    "Late afternoon daylight, warm and bright. Everything is drawn into one coherent illustration, each "
    "element lit by the same light and casting its own shadow. No text, no interface, no logos. "
    "Landscape format."
)

VARIANTS = {
    "b1": "Art style: hand-painted modern cartoon, round readable shapes, thin soft outlines, rich "
          "gradients and painterly texture, warm luminous palette, storybook feel. Depth comes from "
          "painted light, not from line work.",
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
    creatures.append(f"{TARGET}/da-gb-{key}v5-creature.png")
    creatures.append(f"{style} {SHEET} Draw the creature alone, three-quarter view, standing, plain very "
                     "light background. No text, no interface, no humans, no logos. Square format.")

print("--- creatures")
code = run(creatures)

scenes = []
for key, style in VARIANTS.items():
    scenes.append(f"{TARGET}/da-gb-{key}v5-scene.png")
    scenes.append(f"{style} {SCENE_TEMPLATE.format(reference=f'da-gb-{key}v5-creature.png')}")

print("--- scenes")
code = run(scenes) or code

sys.exit(code)

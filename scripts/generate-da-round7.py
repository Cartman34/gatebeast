#!/usr/bin/env python3
"""Seventh art direction round: same staging everywhere, but a scene that feels alive.

Corrections from the owner's review:
- every direction shows the EXACT same staging, so only the style differs — but within that staging the
  characters are doing things rather than standing still;
- buildings were far too small next to the humans: scale is now stated explicitly;
- the flat vector direction was too candy-coloured: its palette is toned down;
- the toon render was slightly too realistic: it is pushed towards stylisation;
- the painterly direction is dropped, replaced by a hybrid of the two survivors.
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
    "It does NOT tell you how to draw the scene: the scene follows the art style stated above.\n\n"
    f"{SHEET}\n\n"
    "CAMERA — strict. The camera looks STEEPLY DOWN at the ground, about seventy degrees from horizontal, "
    "like a classic top-down role playing game map. The ground fills the whole frame. NO horizon, NO sky, "
    "NO clouds, NO distant mountains, no vanishing point. Roofs and treetops are seen from above.\n\n"
    "SCALE — the previous attempt failed here: the cottage was smaller than the people. A human character "
    "must reach only about a third of the cottage's height, and its door must be clearly taller than the "
    "human standing beside it. The watchtower is taller still.\n\n"
    "STAGING — reproduce this exact arrangement, unchanged, and make it feel ALIVE. Nobody stands idle:\n"
    "- top right, THE GATEWAY: a tall vertical sheet of water upright inside a stone frame, like a pool "
    "turned on its side, rippling slowly and faintly revealing another landscape behind it. Pale "
    "turquoise, calm.\n"
    "- centre, on the crossing paths, the amber creature from the reference, caught mid-stride walking "
    "briskly towards the gateway, ears forward, tail up.\n"
    "- just below it, a small round green creature crouched at the stream's edge, leaning down to drink, "
    "with tiny ripples where its muzzle touches the water.\n"
    "- left of the path, a slender purple bird-like creature in mid-hop, wings half spread, chasing a "
    "butterfly above the flowers.\n"
    "- upper left, a cottage with a fenced vegetable garden; a human character kneels among the vegetable "
    "rows, working the soil, a watering can beside them.\n"
    "- right, a wooden watchtower; a second human walks along the path towards the gateway, one arm "
    "raised, mid-wave.\n"
    "- a stream running down the middle into a wider river crossed by a small wooden bridge, boulders, "
    "flower patches, tall grass, clusters of trees, winding dirt paths linking everything.\n"
    "Late afternoon daylight, warm and bright, every element casting its own shadow. Motion is readable in "
    "the poses: leaning, striding, hopping, kneeling. No text, no interface, no logos. Landscape format."
)

VARIANTS = {
    "b2": "Art style: outline-free flat vector illustration, solid unshaded colour areas, hard-edged "
          "two-tone shading, no gradients and no texture. Palette deliberately restrained and slightly "
          "muted — natural greens and earth tones rather than candy colours, saturation dialled back.",
    "b4": "Art style: stylised toon render, rounded sculpted volumes with simple cel shading in two crisp "
          "bands, soft rim light, no outline. Deliberately unrealistic: simplified surfaces, no fine "
          "texture detail, shapes reading as clean toy-like forms rather than a realistic render.",
    "b7": "Art style: a hybrid of flat vector and toon render — shapes are built as clean flat colour "
          "areas with no outline, but given a single soft volumetric shading pass so they feel rounded and "
          "lit. Restrained natural palette, no texture, no gradients beyond that shading. Graphic clarity "
          "of vector art with the gentle depth of a toon render.",
}


def run(arguments):
    return subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode


creatures = []
for key, style in VARIANTS.items():
    creatures.append(f"{TARGET}/da-gb-{key}v7-creature.png")
    creatures.append(f"{style} {SHEET} Draw the creature alone, three-quarter view, standing, plain very "
                     "light background. No text, no interface, no humans, no logos. Square format.")

print("--- creatures")
code = run(creatures)

scenes = []
for key, style in VARIANTS.items():
    scenes.append(f"{TARGET}/da-gb-{key}v7-scene.png")
    scenes.append(f"{style} {SCENE_TEMPLATE.format(reference=f'da-gb-{key}v7-creature.png')}")

print("--- scenes")
code = run(scenes) or code

sys.exit(code)

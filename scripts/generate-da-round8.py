#!/usr/bin/env python3
"""Eighth art direction round — scenes only, plus one new outlined direction.

What is reused untouched, because it was never criticised: the toon and hybrid creatures from round seven,
which also serve as visual references for their own scenes.
What is dropped: the outline-free flat direction, rejected — an outline is wanted.
What is new: an outlined direction, generated creature first then scene.
What is corrected in every scene: buildings are clearly imposing next to the humans, and a healing centre
now belongs to the world.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"

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
    "SCALE — the buildings must be IMPOSING. The cottage is wide and tall enough that a human character "
    "reaches barely a quarter of its height, and its door is clearly taller than the human beside it. The "
    "healing centre is larger still, the tallest structure in frame. Getting this wrong ruins the image.\n\n"
    "STAGING — reproduce this exact arrangement, unchanged, and make it feel ALIVE. Nobody stands idle:\n"
    "- top right, THE GATEWAY: a tall vertical sheet of water upright inside a stone frame, like a pool "
    "turned on its side, rippling slowly and faintly revealing another landscape behind it. Pale "
    "turquoise, calm.\n"
    "- centre, on the crossing paths, the amber creature from the reference, mid-stride walking briskly "
    "towards the gateway, ears forward, tail up.\n"
    "- just below it, a small round green creature crouched at the stream's edge, leaning down to drink, "
    "tiny ripples where its muzzle touches the water.\n"
    "- left of the path, a slender purple bird-like creature in mid-hop, wings half spread, chasing a "
    "butterfly above the flowers.\n"
    "- upper left, a large cottage with a fenced vegetable garden; a human kneels among the rows working "
    "the soil, a watering can beside them.\n"
    "- centre right, THE HEALING CENTRE: a broad welcoming building with a wide doorway and a clear "
    "emblem over it, plainly the largest structure in the scene, with a lantern by its door.\n"
    "- right, a wooden watchtower; a second human walks a path towards the gateway, one arm mid-wave.\n"
    "- a stream running down the middle into a wider river crossed by a small wooden bridge, boulders, "
    "flower patches, tall grass, clusters of trees, winding dirt paths linking everything.\n"
    "Late afternoon daylight, warm and bright, every element casting its own shadow. Motion is readable in "
    "the poses: leaning, striding, hopping, kneeling. No text, no interface, no logos. Landscape format."
)

STYLES = {
    "b4": "Art style: stylised toon render, rounded sculpted volumes with simple cel shading in two crisp "
          "bands, soft rim light, no outline. Deliberately low on detail: simplified surfaces, no fine "
          "texture, clean toy-like forms.",
    "b7": "Art style: hybrid of flat vector and toon render — clean flat colour areas with no outline, "
          "given a single soft volumetric shading pass so shapes feel rounded and lit. Restrained natural "
          "palette, no texture.",
    "b8": "Art style: modern cartoon with a clear dark outline around every shape, flat colour areas "
          "inside, simple two-tone shading, restrained natural palette, low detail density. The outline is "
          "the defining feature: confident, even-weight, always present.",
}

# Reused as is, never regenerated: these creatures were validated.
REFERENCES = {"b4": "da-gb-b4v7-creature.png", "b7": "da-gb-b7v7-creature.png"}


def run(arguments):
    return subprocess.run(["php", TOOL] + arguments, cwd=PROJECT).returncode


print("--- new creature for the outlined direction only")
code = run([
    f"{TARGET}/da-gb-b8v8-creature.png",
    f"{STYLES['b8']} {SHEET} Draw the creature alone, three-quarter view, standing, plain very light "
    "background. No text, no interface, no humans, no logos. Square format.",
])
REFERENCES["b8"] = "da-gb-b8v8-creature.png"

scenes = []
for key, style in STYLES.items():
    scenes.append(f"{TARGET}/da-gb-{key}v8-scene.png")
    scenes.append(f"{style} {SCENE_TEMPLATE.format(reference=REFERENCES[key])}")

print("--- scenes")
code = run(scenes) or code

sys.exit(code)

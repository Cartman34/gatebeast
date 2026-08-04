#!/usr/bin/env python3
"""Generate one identical scene per art direction, so directions can be compared in context.

Delegates every generation to the shared image tool.
"""
import subprocess
import sys
from pathlib import Path

PROJECT = Path("/home/sowapps/projects")
TOOL = "gatebeast/scripts/generate-image.php"
TARGET = "gatebeast/assets/revue-da"

SCENE = (
    "Same scene for every version: a small forest clearing at dusk, warm low light, soft mist near the "
    "ground, and a faint glowing archway of turquoise light standing between two trees in the middle "
    "distance. In the foreground stands a small round friendly quadruped creature with amber fur, large "
    "rounded ears and a glowing turquoise arch mark on its forehead, seen in three-quarter view. "
    "No text, no user interface, no humans, no logos. Landscape format."
)

DIRECTIONS = {
    "d": "Cut-paper collage style: layered flat colour shapes with crisp scissor-cut edges, soft drop "
         "shadows between layers, subtle paper texture.",
    "e": "Felt plush style: soft textile materials, visible stitching, padded volumes, glossy button eyes, "
         "soft studio lighting.",
    "f": "Coloured chalk on dark slate: deep night-blue background, luminous slightly powdery chalk "
         "strokes, bright colours that seem to glow in the dark.",
    "g": "Stained glass style: shapes outlined in black lead, translucent luminous colours, the look of "
         "coloured glass lit from behind.",
    "h": "Clean modern anime style: fine crisp linework, bold flat colours, soft cel shading, believable "
         "animal silhouette rather than a mascot, slightly desaturated grown-up palette.",
    "i": "Endearing movie-monster style: detailed skin textures, heavy volumes and real physical presence, "
         "cinematic lighting, yet a kind face and rounded proportions.",
    "a": "Illustrated storybook style: watercolour and ink, paper texture, hand-drawn outlines, warm soft "
         "colours.",
    "b": "Modern pop cartoon style: round readable shapes, bright flat colours, clean thick outlines, "
         "simple two-tone shading.",
    "c": "Cosy retro 16-bit pixel art: limited warm palette, crisp chunky pixels, no anti-aliasing.",
}

arguments = []
for key, style in DIRECTIONS.items():
    arguments.append(f"{TARGET}/da-gb-{key}-scene.png")
    arguments.append(f"{style} {SCENE}")

result = subprocess.run(["php", TOOL] + arguments, cwd=PROJECT)
sys.exit(result.returncode)

#!/usr/bin/env python3
"""Stamp the witness tile onto a scene, and verify the result.

The witness tile must never be drawn by the image generator: a generated square is approximate, and an
approximate reference proves nothing. It is stamped here instead — always the same colour, always the same
corner, aligned to the pixel by construction — then measured back to confirm.

Usage: python3 stamp-witness-tile.py <image.png> [...]
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TILE = 48
COLOUR = (255, 0, 144)
FRAME = 1536, 1152


def stamp(path: Path) -> bool:
    image = Image.open(path).convert("RGB")
    if (image.width, image.height) != FRAME:
        print(f"ÉCART {path.name}: image {image.width}x{image.height}, attendu {FRAME[0]}x{FRAME[1]}")

        return False
    if image.width % TILE or image.height % TILE:
        print(f"ÉCART {path.name}: la case de {TILE} px ne divise pas l'image exactement")

        return False

    draw = ImageDraw.Draw(image)
    draw.rectangle([0, image.height - TILE, TILE - 1, image.height - 1], fill=COLOUR)
    image.save(path)
    print(f"OK {path.name}: témoin {TILE}x{TILE} px en bas à gauche, "
          f"{image.width // TILE} x {image.height // TILE} cases")

    return True


failures = 0
for argument in sys.argv[1:]:
    failures += 0 if stamp(Path(argument)) else 1

sys.exit(1 if failures else 0)

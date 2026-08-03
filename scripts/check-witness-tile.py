#!/usr/bin/env python3
"""Check that the witness tile is exactly one grid tile, aligned to the grid.

The witness tile only proves anything if it is verified: this measures the filled square in the bottom
left corner and reports its real position and size in pixels against the expected tile.
"""
import sys
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
TILE = 48


def dominant_corner_colour(image, size):
    return image.getpixel((4, image.height - 5))


def measure(path: Path):
    image = Image.open(path).convert("RGB")
    target = dominant_corner_colour(image, TILE)

    def matches(x, y):
        pixel = image.getpixel((x, y))

        return all(abs(a - b) < 28 for a, b in zip(pixel, target))

    width = 0
    while width < image.width and matches(width, image.height - 5):
        width += 1
    height = 0
    while height < image.height and matches(4, image.height - 1 - height):
        height += 1

    print(f"{path.name}: image {image.width}x{image.height}, "
          f"témoin mesuré {width}x{height} px "
          f"(attendu {TILE}x{TILE}) — {'OK' if width == TILE and height == TILE else 'ÉCART'}")


for name in sys.argv[1:]:
    measure(ASSETS / name)

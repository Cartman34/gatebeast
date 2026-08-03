#!/usr/bin/env python3
"""Measure the human figures on the calibration image.

Background is plain green grass: any pixel clearly non-green belongs to a figure. Figures are separated
by empty columns, so connected column-runs give one bounding box per figure. Heights and widths are
reported in pixels and tiles (48 px = 1 tile) against the targets: standing adult 96 px, child 60 px,
sitting adult 60 px, width 48 px max for all.
"""
import sys
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
TILE = 48
TARGETS = ["standing man 96", "standing woman 96", "standing child 60", "sitting man 60"]

name = sys.argv[1] if len(sys.argv) > 1 else "calibration-humains.png"
image = Image.open(ASSETS / name).convert("RGB")
width, height = image.size
pixels = image.load()


def is_figure(r, g, b):
    # Grass is dominantly green, shadows included; skin, cloth and hair are not.
    return not (g > r and g > b * 1.1)


columns = []
for x in range(width):
    hit = any(is_figure(*pixels[x, y]) for y in range(height))
    columns.append(hit)

boxes = []
start = None
for x, hit in enumerate(columns + [False]):
    if hit and start is None:
        start = x
    elif not hit and start is not None:
        if x - start > 8:  # ignore noise slivers
            boxes.append((start, x - 1))
        start = None

print(f"image {width}x{height}, {len(boxes)} figures found (targets: {len(TARGETS)})")
for index, (x1, x2) in enumerate(boxes):
    ys = [y for x in range(x1, x2 + 1) for y in range(height) if is_figure(*pixels[x, y])]
    y1, y2 = min(ys), max(ys)
    h, w = y2 - y1 + 1, x2 - x1 + 1
    target = TARGETS[index] if index < len(TARGETS) else "?"
    print(f"  figure {index + 1} [{target}]: height {h}px = {h / TILE:.2f} tiles, "
          f"width {w}px = {w / TILE:.2f} tiles")

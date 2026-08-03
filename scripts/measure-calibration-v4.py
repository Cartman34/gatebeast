#!/usr/bin/env python3
"""Measure calibration v4: two rows of eight figures (standing above, same person sitting below).
The image is split horizontally; each half is measured like the previous calibrations."""
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "revue-da"
TILE = 48


def is_figure(r, g, b):
    return not (g > r and g > b * 1.1)


def measure(image, label):
    width, height = image.size
    pixels = image.load()
    columns = []
    for x in range(width):
        columns.append(any(is_figure(*pixels[x, y]) for y in range(height)))
    boxes = []
    start = None
    for x, hit in enumerate(columns + [False]):
        if hit and start is None:
            start = x
        elif not hit and start is not None:
            if x - start > 8:
                boxes.append((start, x - 1))
            start = None
    print(f"{label}: {len(boxes)} figures")
    for index, (x1, x2) in enumerate(boxes):
        ys = [y for x in range(x1, x2 + 1) for y in range(height) if is_figure(*pixels[x, y])]
        y1, y2 = min(ys), max(ys)
        h, w = y2 - y1 + 1, x2 - x1 + 1
        print(f"  figure {index + 1}: height {h / TILE:.2f} tiles, width {w / TILE:.2f} tiles")


image = Image.open(ASSETS / "calibration-humains-v4.png").convert("RGB")
width, height = image.size
measure(image.crop((0, 0, width, height // 2)), "top row (standing)")
measure(image.crop((0, height // 2, width, height)), "bottom row (sitting)")

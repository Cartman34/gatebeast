#!/usr/bin/env python3
"""Measure, on the produced sample, the geometry the generator actually drew.

Why: the first vector sketch was built on my assumptions about post diameter and rail spacing, and it
was wrong. This reads the numbers off the image instead — the only source that cannot be argued with.
What comes out feeds the vector sketch, so the sketch matches what the generator can produce.

Usage: python3 scripts/dev/measure-fence.py
"""
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parent.parent
IMAGE = REPO / "assets" / "poc" / "cloture" / "usage-OB-010-v2.png"
CELL = 192  # 1344 / 7 — the sample was ordered at exactly seven square cells


def spans(values, threshold=40):
    """The runs of opaque pixels along a line, as (start, length)."""
    found, start = [], None
    for index, value in enumerate(values):
        if value > threshold and start is None:
            start = index
        elif value <= threshold and start is not None:
            found.append((start, index - start))
            start = None
    if start is not None:
        found.append((start, len(values) - start))

    return found


image = Image.open(IMAGE).convert("RGBA")
alpha = image.split()[3]
print(f"image {image.size} · case {CELL} px")

# The top antenna stands alone (plan: column 5, row 1), so a box around it gives a WHOLE piece:
# its post's diameter and how far it rises above its own cell.
left, right = 4 * CELL, 5 * CELL
top, bottom = 0, 2 * CELL
box = [(x, y) for x in range(left, right) for y in range(top, bottom)
       if alpha.getpixel((x, y)) > 40]
if box:
    xs, ys = [p[0] for p in box], [p[1] for p in box]
    print(f"\nantenne du haut (colonne 5, rangée 1)")
    print(f"  largeur {max(xs) - min(xs) + 1} px = {(max(xs) - min(xs) + 1) / CELL:.3f} case")
    print(f"  sommet à y={min(ys)}, soit {(CELL - min(ys)) / CELL:.3f} case au-dessus de sa case")

# Horizontal cuts across the middle east-west run: low ones meet only posts, higher ones meet the
# rails running through. Where a cut suddenly spans the whole run, the rail is there.
print("\ncoupes horizontales sur la portée est-ouest du milieu")
for offset in range(-90, 20, 10):
    y = 4 * CELL + offset
    runs = spans([alpha.getpixel((x, y)) for x in range(image.width)])
    widest = max((length for _, length in runs), default=0)
    print(f"  y={y:>5} ({offset:+4} px de la ligne de sol) · {len(runs):>2} segments · "
          f"plus large {widest:>4} px = {widest / CELL:.2f} case")

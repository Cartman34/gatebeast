#!/usr/bin/env python3
"""Lay a ground material side by side so the owner can judge the seam and the repetition rhythm.

Usage: python3 local/tile-preview.py <image.png> <output.png> [times]
"""
import sys

from PIL import Image

source = Image.open(sys.argv[1]).convert("RGB")
times = int(sys.argv[3]) if len(sys.argv) > 3 else 4
width, height = source.size
sheet = Image.new("RGB", (width * times, height * times))
for column in range(times):
    for row in range(times):
        sheet.paste(source, (column * width, row * height))
sheet.save(sys.argv[2])
print(f"{sheet.size[0]}x{sheet.size[1]} written to {sys.argv[2]}")
